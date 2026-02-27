# This file is part of the DGTCentaur Mods open source software
# ( https://github.com/Alistair-Crompton/DGTCentaurMods )
#
# DGTCentaur Mods is free software: you can redistribute
# it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either
# version 3 of the License, or (at your option) any later version.
#
# DGTCentaur Mods is distributed in the hope that it will
# be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this file.  If not, see
#
# https://github.com/Alistair-Crompton/DGTCentaurMods/blob/master/LICENSE.md
#
# This and any other notices must remain intact and unaltered in any
# distribution, modification, variant, or derivative of this software.

# Created by chemtech1

# Chess960 Plugin edit by Chemtech1 - New Chess960 bot plugin that generates random Chess960 positions and plays with Stockfish engine

import chess, random, os, configparser, subprocess, time, select, threading
from pathlib import Path

from PIL import ImageDraw

from DGTCentaurMods.classes.Plugin import Plugin, Centaur
from DGTCentaurMods.classes import Log, ChessEngine, CentaurBoard, CentaurScreen
from DGTCentaurMods.classes.GameFactoryChess960 import Engine
from DGTCentaurMods.consts import Enums, fonts, consts
from DGTCentaurMods.plugins.lib.Chess960Tutorial import Chess960Tutorial

from typing import Optional

# The plugin must inherits of the Plugin class.
# Filename must match the class name.
class Chess960(Plugin):

    def __init__(self, id:str):
        super().__init__(id)
        self._chess960_fen = None

        # Menu state management
        self._menu_state = None      # "engine" | "strength" | "color" | None
        self._ignore_next_play = False  # Ignore first PLAY after menu start
        self._engines = []           # Available FRC engines
        self._current_index = 0      # Menu navigation
        self._selected_engine = None
        self._strengths = []         # Engine strength levels
        self._selected_strength = None
        self._selected_color = chess.WHITE

        # Centaur board instance
        self._centaur_board = CentaurBoard.get()
        self._centaur_screen = CentaurScreen.get()

        # Position input state
        self._input_str = []  # List for editable digits ['1','2','3']
        self._cursor_pos = 0  # 0=hundreds, 1=tens, 2=ones
        self._ziffer_map = {32:'1',33:'2',34:'3',35:'4',36:'5',37:'6',38:'7',39:'8',27:'9',28:'0'}

        # Menu display optimization
        self._menu_initialized = False
        self._prev_state = None
        self._prev_cursor_pos = None

        # No BACK navigation saves - BACK just goes back one level with defaults

    def __event_callback(self, event:Enums.Event, outcome:Optional[chess.Outcome]):
        try:
            if self._started:
                self.event_callback(event, outcome)
        except Exception as e:
            Log.error(f"Exception in event_callback: {str(e)}")
            self.stop()

    def __move_callback(self, uci_move:str, san_move:str, color:chess.Color, field_index:chess.Square):
        try:
            if self._started:
                return self.move_callback(uci_move, san_move, color, field_index)
        except Exception as e:
            Log.error(f"Exception in move_callback: {str(e)}")
            self.stop()
        return False

    def __undo_callback(self, uci_move:str, san_move:str, field_index:chess.Square):
        try:
            if self._started:
                return self.undo_callback(uci_move, san_move, field_index)
        except Exception as e:
            Log.error(f"Exception in undo_callback: {str(e)}")
            self.stop()
        return False

    def __socket_callback(self, data:dict, _) -> bool:
        try:
            if len(data.keys())>0:
                if consts.BOT_MESSAGE in data:
                    self.on_bot_request(data[consts.BOT_MESSAGE])
                    return True
                if self._started:
                    return self.on_socket_request(data)
        except Exception as e:
            Log.error(f"Exception in socket_callback: {str(e)}")
            self.stop()
        return False

    def __key_callback(self, key:Enums.Btn):
        try:
            if key == Enums.Btn.BACK:
                if self._menu_state is None:  # Only stop if not in menu
                    if self._game_engine:
                        self._game_engine.end()
                    else:
                        self.stop()
                    return True
                # Else, let menu handle BACK

            if not self._started:
                self._started = self.on_start_callback(key)
                if self._started:
                    return True  # Event was handled by on_start_callback, don't process again

            if not self._started:
                return False

            return self.key_callback(key)
        except Exception as e:
            Log.error(f"Exception in key_callback: {str(e)}")
            self.stop()

    def _scan_frc_engines(self):
        """Find engines that support UCI_Chess960"""
        engines_dir = consts.ENGINES_DIRECTORY
        self._engines = []

        if not os.path.exists(engines_dir):
            Log.info(f"Chess960: Engines directory not found: {engines_dir}")
            return

        for f in os.scandir(engines_dir):
            if f.name.endswith('.uci'):
                try:
                    # Test if engine binary exists
                    engine_binary = f.path[:-4]  # Remove .uci extension
                    if os.path.exists(engine_binary):
                        engine_name = f.name[:-4]  # Remove .uci extension
                        self._engines.append({
                            'name': engine_name,
                            'uci_path': f.path,
                            'binary_path': engine_binary
                        })
                        Log.info(f"Chess960: Found FRC engine: {engine_name}")
                except Exception as e:
                    Log.debug(f"Chess960: Skipping invalid engine {f.name}: {e}")

        if not self._engines:
            Log.info("Chess960: No FRC engines found!")
        else:
            Log.info(f"Chess960: Found {len(self._engines)} FRC engines")

    def _load_engine_strengths(self, uci_path):
        """Load strength levels from UCI file"""
        parser = configparser.ConfigParser()
        parser.read(uci_path)

        self._strengths = list(parser.sections())

        # Sort by ELO rating (DEFAULT first, then E-XXXX)
        self._strengths.sort(key=lambda x: int(x[2:]) if x.startswith('E-') else 0)

        Log.info(f"Chess960: Loaded {len(self._strengths)} strength levels")

    def check_chess960_support(self, engine_binary: str) -> bool:
        try:
            Log.info(f"Starting Chess960 support test for {Path(engine_binary).stem}")
            proc = subprocess.Popen(
                [engine_binary],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1
            )

            def send(cmd):
                Log.info(f"Sending UCI command: {cmd}")
                proc.stdin.write(cmd + "\n")
                proc.stdin.flush()

            Log.info("Sending 'uci' command")
            send("uci")
            uci_response = self._read_until(proc, "uciok", 5)
            Log.info(f"UCI response: {uci_response.strip()}")

            Log.info("Setting UCI_Chess960 to true")
            send("setoption name UCI_Chess960 value true")
            send("isready")
            ready_response = self._read_until(proc, "readyok", 5)
            Log.info(f"Ready response: {ready_response.strip()}")

            Log.info("Setting position")
            send("position fen rk6/ppp1pppp/8/8/8/8/PPP1PPPP/2RKR3 b kq - 1 1")
            Log.info("Starting analysis with go movetime 500")
            send("go movetime 500")  # 0.5 s reicht völlig

            output = self._read_until(proc, "bestmove", 2)
            Log.info(f"Analysis output: {output.strip()}")

            Log.info("Terminating engine process")
            proc.terminate()
            proc.wait(timeout=2)

            if "bestmove b8a8" in output:
                Log.info("Bestmove b8a8 erkannt → PASS")
                result = True
            elif "pv b8a8" in output:
                Log.info("PV b8a8 erkannt → PASS")
                result = True
            else:
                result = False
            Log.info(f"Chess960 support test result: {'PASS' if result else 'FAIL'}")
            return result

        except Exception as e:
            Log.info(f"Chess960 support test exception: {e}")
            return False

    def _read_until(self, proc, keyword: str, timeout: float) -> str:
        output = ""
        start = time.time()
        while time.time() - start < timeout:
            ready, _, _ = select.select([proc.stdout, proc.stderr], [], [], 0.2)
            if ready:
                if proc.stdout in ready:
                    line = proc.stdout.readline()
                    if line:
                        Log.info(f"Gelesen stdout: {line.strip()}")
                        output += line
                        if keyword in output:
                            break
                if proc.stderr in ready:
                    line = proc.stderr.readline()
                    if line:
                        Log.info(f"Gelesen stderr: {line.strip()}")
                        output += line
                        if keyword in output:
                            break
            if proc.poll() is not None:
                break
        Log.info(f"Vollständige Antwort: {output.strip()}")
        return output

    # This function is automatically invoked when
    # the user launches the plugin.
    def start(self):
        self._scan_frc_engines()
        super().start()

    # This function is automatically invoked when
    # the user stops the plugin.
    def stop(self):
        # Reset to standard starting position for board and web
        standard_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        Log.info(f"Chess960: Stop called, FEN before reset: {self._game_engine._chessboard.fen() if self._game_engine else 'No engine'}")
        if self._game_engine:
            self._game_engine._chessboard.set_fen(standard_fen)
            Log.info(f"Chess960: FEN after set_fen: {self._game_engine._chessboard.fen()}")
            self._game_engine.display_board()  # Update physical board
        Log.info(f"Chess960: FEN before super.stop(): {self._game_engine._chessboard.fen() if self._game_engine else 'No engine'}")
        # Auto-send standard FEN (post 518) via super
        super().stop()

    # When exists, this function is automatically invoked
    # when the player physically plays a move.
    def move_callback(self, uci_move:str, san_move:str, color:chess.Color, field_index:chess.Square):

        if color == (not self._selected_color):
            # Computer move is accepted
            return True

        # Human move is accepted
        return True

    def _update_menu_display(self):
        """Update the screen to show current menu state with partial updates"""
        # Full clear and static elements only on state change or first call
        if self._menu_state != self._prev_state or not self._menu_initialized:
            Centaur.clear_screen()

            # Print title based on state
            if self._menu_state == "engine":
                Centaur.print("Select Engine", row=1)
            elif self._menu_state == "strength":
                Centaur.print("Select Strength", row=1)
            elif self._menu_state == "color":
                Centaur.print("Select Color", row=1)

            # Print static navigation instructions
            Centaur.print("UP/DOWN: Navigate", row=8)
            Centaur.print("PLAY: Select", row=9)
            Centaur.print("BACK: Exit", row=10)

            self._prev_state = self._menu_state
            self._menu_initialized = True

        # Always update dynamic content (item and counter)
        if self._menu_state == "engine":
            if self._engines:
                engine_name = self._engines[self._current_index]['name'].ljust(11)
                Centaur.print(f"{engine_name}", row=4, font=fonts.MAIN_FONT)
                Centaur.print(f"{self._current_index + 1}/{len(self._engines)}", row=6)
            else:
                Centaur.print("No engines found!", row=4)

        elif self._menu_state == "strength":
            if self._strengths:
                strength = self._strengths[self._current_index]
                Centaur.print(f"{strength}", row=4, font=fonts.MAIN_FONT)
                Centaur.print(f"{self._current_index + 1}/{len(self._strengths)}", row=6)
            else:
                Centaur.print("No strengths found!", row=4)

        elif self._menu_state == "color":
            colors = ["White", "Black"]
            color_name = colors[self._current_index]
            Centaur.print(f"{color_name}", row=4, font=fonts.DIGITAL_FONT)
            Centaur.print(f"{self._current_index + 1}/{len(colors)}", row=6)

    def _handle_menu_navigation(self, key:Enums.Btn) -> bool:
        """Handle menu navigation keys"""
        Log.info(f"Chess960: _handle_menu_navigation called with key={key}, state={self._menu_state}, index={self._current_index}")

        if self._menu_state == "engine":
            max_items = len(self._engines)
        elif self._menu_state == "strength":
            max_items = len(self._strengths)
        elif self._menu_state == "color":
            max_items = 2  # White or Black
        else:
            Log.info(f"Chess960: Invalid menu state: {self._menu_state}")
            return False

        if key == Enums.Btn.UP:
            self._current_index = (self._current_index - 1) % max_items
            Log.info(f"Chess960: UP pressed, new index: {self._current_index}")
            self._update_menu_display()
            return True
        elif key == Enums.Btn.DOWN:
            self._current_index = (self._current_index + 1) % max_items
            Log.info(f"Chess960: DOWN pressed, new index: {self._current_index}")
            self._update_menu_display()
            return True
        elif key == Enums.Btn.PLAY:
            if self._ignore_next_play:
                Log.info(f"Chess960: Ignoring PLAY event (menu just started)")
                self._ignore_next_play = False  # Reset flag
                return True  # Ignore this PLAY event
            Log.info(f"Chess960: PLAY pressed, calling _handle_menu_selection")
            self._handle_menu_selection()
            return True
        elif key == Enums.Btn.BACK:
            if self._menu_state == "strength":
                self._menu_state = "engine"
                self._current_index = 0  # Start from first engine
                self._update_menu_display()
                return True
            elif self._menu_state == "color":
                self._menu_state = "position"
                self._chess960_pos = random.randint(0, 959)  # New random position
                self._input_str = list(str(self._chess960_pos).zfill(3))
                self._cursor_pos = 0
                self._centaur_board.subscribe_events(self._position_key_callback, self._position_field_callback)
                self._update_pos_display()
                return True
            else:
                # For engine or other, stop plugin
                self.stop()
                return True

        Log.info(f"Chess960: Key {key} not handled in menu navigation")
        return False

    def _handle_menu_selection(self):
        """Handle menu selection and state transitions"""
        Log.info(f"Chess960: _handle_menu_selection called, state={self._menu_state}, index={self._current_index}")

        if self._menu_state == "engine":
            if self._engines:
                engine = self._engines[self._current_index]
                Log.info(f"Chess960: Checking {engine['name']} for Chess960 support")
                Centaur.print("Testing engine...", row=4)
                if self.check_chess960_support(engine['binary_path']):
                    self._selected_engine = engine
                    Log.info(f"Chess960: Selected engine: {self._selected_engine['name']}")
                    self._load_engine_strengths(self._selected_engine['uci_path'])
                    self._menu_state = "strength"
                    self._current_index = 0
                    self._update_menu_display()
                else:
                    Centaur.print("The engine cannot", row=4, font=fonts.DIGITAL_FONT)
                    Centaur.print("play Chess960", row=5, font=fonts.DIGITAL_FONT)
                    Centaur.print("          ", row=6)
                    time.sleep(3)
                    Centaur.clear_screen()
                    self._menu_initialized = False
                    self._update_menu_display()
            else:
                Log.info("Chess960: No engines available for selection")

        elif self._menu_state == "strength":
            if self._strengths:
                self._selected_strength = self._strengths[self._current_index]
                Log.info(f"Chess960: Selected strength: {self._selected_strength}")
                self._menu_state = "position"
                self._chess960_pos = random.randint(0, 959)
                self._input_str = list(str(self._chess960_pos).zfill(3))
                self._cursor_pos = 0
                Centaur.clear_screen()
                self._menu_initialized = False
                self._centaur_board.subscribe_events(self._position_key_callback, self._position_field_callback)
                self._update_pos_display()
            else:
                Log.info("Chess960: No strengths available for selection")

        elif self._menu_state == "color":
            self._selected_color = chess.WHITE if self._current_index == 0 else chess.BLACK
            Log.info(f"Chess960: Selected color: {'WHITE' if self._selected_color == chess.WHITE else 'BLACK'}")
            self._menu_state = None  # Exit menu, start game
            Log.info(f"Chess960: Starting game...")
            self._start_selected_game()

    def _get_keyboard_array(self):
        keyboard = [' '] * 64
        # Zeile 5 h5-a5 reversed: '87654321' (visual 12345678 left to right)
        keyboard[24:32] = list('87654321')
        # Zeile 4 d4: '0'
        keyboard[35] = '0'
        # e4: '9'
        keyboard[36] = '9'
        return keyboard

    def _update_pos_display(self):
        # Titel
        Centaur.print("starting position", row=1, font=fonts.MAIN_FONT)

        # Brett mit Zahlen zeichnen
        self._centaur_screen.draw_board(self._get_keyboard_array(), 1.75, is_keyboard=True)

        # Dreistellige Zahl - separate draws mit x-Offset (nach clear, um Overlaps zu vermeiden)
        pos_str = ''.join(self._input_str)
        x_digits = [10, 45, 80]  # Hunderter +5px rechts, Zehner, Einer -5px links  # Vor clear definieren!
        y_pos = 200  # row=10 * HEADER_HEIGHT

        # Clear digit area to avoid overlap
        draw = ImageDraw.Draw(self._centaur_screen._buffer)
        draw.rectangle((0, 195, 100, 235), fill=255)

        # Clear alten Rahmen falls Cursor gewechselt
        if self._prev_cursor_pos is not None and self._prev_cursor_pos != self._cursor_pos:
            old_x_start = x_digits[self._prev_cursor_pos] - 10
            self._centaur_screen.draw_rectangle(old_x_start, 197, old_x_start + 40, 232, fill=255)
        font = fonts.DIGITAL_FONT
        for i in range(3):
            draw.text((x_digits[i], y_pos), pos_str[i], font=font, fill=0)

        # Highlight selected Ziffer mit Rahmen - zentriert auf Ziffer, 2px tiefer
        frame_width = 40
        digit_center_offset = 10  # (frame_width - digit_width) // 2, digit_width~20px
        x_start = x_digits[self._cursor_pos] - digit_center_offset
        y_top = 197  # 2px tiefer
        y_bottom = 232  # 2px tiefer, Höhe=35px
        self._centaur_screen.draw_rectangle(x_start, y_top, x_start + frame_width, y_bottom, outline=0)

        # Anleitung
        Centaur.print("UP/DOWN: Navigate", row=12, font=fonts.MAIN_FONT)
        Centaur.print("PLAY: Select", row=13, font=fonts.MAIN_FONT)
        Centaur.print("BACK: Exit", row=14, font=fonts.MAIN_FONT)

        self._prev_cursor_pos = self._cursor_pos

    def _position_field_callback(self, field_index, action):
        Log.info(f"PLACE on field {field_index}, action {action}")
        if action != Enums.PieceAction.PLACE or field_index not in self._ziffer_map:
            Log.info(f"Ignored: action={action}, field in map={field_index in self._ziffer_map}")
            return
        ziffer = self._ziffer_map[field_index]
        Log.info(f"Setting ziffer {ziffer} at cursor {self._cursor_pos}")
        self._input_str[self._cursor_pos] = ziffer
        Centaur.sound(Enums.Sound.CORRECT_MOVE)

        # Validate position: if >959, reset tens to 0 and move cursor there
        pos_str = ''.join(self._input_str)
        try:
            pos = int(pos_str)
            if pos > 959:
                self._input_str[1] = '0'  # Reset tens
                self._cursor_pos = 1  # Move to tens
                Centaur.sound(Enums.Sound.CORRECT_MOVE)  # Indicate correction
        except ValueError:
            pass  # Invalid, ignore

        # Auto-advance cursor to next position (0->1->2->0)
        self._cursor_pos = (self._cursor_pos + 1) % 3

        self._update_pos_display()
        Log.info(f"Pos updated: {''.join(self._input_str)}, cursor={self._cursor_pos}")

    def _position_key_callback(self, key):
        if key == Enums.Btn.PLAY:
            pos_str = ''.join(self._input_str)
            while len(pos_str) < 3:
                pos_str += '0'  # Pad with 0
            try:
                pos = int(pos_str)
                if 0 <= pos <= 959:
                    board = chess.Board.from_chess960_pos(pos)
                    self._chess960_fen = board.fen()
                    self._centaur_board.unsubscribe_events()
                    self._menu_state = "color"
                    self._current_index = 0
                    self._update_menu_display()
                    Log.info(f"Pos {pos} confirmed, FEN: {self._chess960_fen}")
                else:
                    Centaur.sound(Enums.Sound.WRONG_MOVE)
                    Centaur.print("Invalid 0-959!", row=6)
                    time.sleep(2)
                    self._update_pos_display()
            except ValueError:
                Centaur.sound(Enums.Sound.WRONG_MOVE)
                Centaur.print("Invalid digits!", row=6)
                time.sleep(2)
                self._update_pos_display()
            return True
        elif key == Enums.Btn.UP:
            self._cursor_pos = (self._cursor_pos - 1) % 3
            self._update_pos_display()
            return True
        elif key == Enums.Btn.DOWN:
            self._cursor_pos = (self._cursor_pos + 1) % 3
            self._update_pos_display()
            return True
        elif key == Enums.Btn.BACK:
            self._centaur_board.unsubscribe_events()
            self._menu_state = "strength"
            self._current_index = 0  # Start from first strength
            self._update_menu_display()
            return True
        return False

    def _start_selected_game(self):
        """Start the game with selected parameters"""
        # Use selected position if available, else random
        if not hasattr(self, '_chess960_fen') or not self._chess960_fen:
            chess960_pos = random.randint(0, 959)
            board = chess.Board.from_chess960_pos(chess960_pos)
            self._chess960_fen = board.fen()
            Log.info(f"Chess960: Generated random position {chess960_pos}")
        else:
            Log.info(f"Chess960: Using selected position")

        Log.info(f"Chess960: FEN: {self._chess960_fen}")

        # Set up selected engine
        engine_name = self._selected_engine['name']
        Centaur.set_main_chess_engine(engine_name)

        # Configure engine with selected strength
        config = {}
        if self._selected_strength != "DEFAULT":
            parser = configparser.ConfigParser()
            parser.read(self._selected_engine['uci_path'])
            if parser.has_section(self._selected_strength):
                for key, value in parser.items(self._selected_strength):
                    config[key] = value

        Centaur.configure_main_chess_engine(config)

        Log.info(f"Chess960: Engine configured: {engine_name} with {self._selected_strength}")

        # Determine player names based on color selection
        if self._selected_color == chess.WHITE:
            white_player = "You"
            black_player = f"{engine_name} {self._selected_strength}"
        else:
            white_player = f"{engine_name} {self._selected_strength}"
            black_player = "You"

        # Start a new game with Chess960 position
        self._start_game(
            event="Chess960 Event",
            site="",
            white=white_player,
            black=black_player,
            flags=Enums.BoardOption.CAN_UNDO_MOVES | Enums.BoardOption.CAN_FORCE_MOVES,
            chess_engine=None,
            custom_fen=self._chess960_fen
        )

        Log.info("Chess960: Game started with selected parameters")

    # This function is automatically invoked each
    # time the player pushes a key.
    # Except the BACK key which is handled by the engine.
    def key_callback(self, key:Enums.Btn):
        Log.info(f"Chess960: key_callback called with key={key}, menu_state={self._menu_state}")

        # Handle position input if in position state
        if self._menu_state == "position":
            return self._position_key_callback(key)

        # Handle menu navigation if we're still in menu mode
        if self._menu_state is not None:
            Log.info(f"Chess960: Calling _handle_menu_navigation")
            return self._handle_menu_navigation(key)

        # If the user pushes HELP,
        # we display an hint using Stockfish engine.
        if key == Enums.Btn.HELP:
            Centaur.hint()
            # Key has been handled.
            return True

        # Key can be handled by the engine.
        Log.info(f"Chess960: Key not handled, returning False")
        return False

    # When exists, this function is automatically invoked
    # when the game engine state is affected.
    def event_callback(self, event:Enums.Event, outcome:Optional[chess.Outcome]):

        # If the user chooses to leave,
        # we quit the plugin.
        if event == Enums.Event.QUIT:
            Log.info(f"Chess960: QUIT event, current FEN: {self._game_engine._chessboard.fen() if self._game_engine else 'No engine'}")
            self.stop()

        if event == Enums.Event.TERMINATION:
            if outcome.winner == self._selected_color:
                Centaur.sound(Enums.Sound.VICTORY)
            else:
                Centaur.sound(Enums.Sound.GAME_LOST)

        if event == Enums.Event.PLAY:

            turn = self.chessboard.turn

            current_player = "You" if turn == self._selected_color else f"{self._selected_engine['name']} {self._selected_strength}"

            # We display the board header.
            Centaur.header(f"{current_player} {'W' if turn == chess.WHITE else 'B'}")

            if turn == (not self._selected_color):
                # Computer turn - request move from Stockfish
                Centaur.request_chess_engine_move(self._on_engine_move_ready)

    def _start_game(self, event:str, site:str, white:str, black:str, flags:Enums.BoardOption, chess_engine: Optional[ChessEngine.ChessEngineWrapper] = None, custom_fen:str = None):
        from DGTCentaurMods.classes.GameFactoryChess960 import Engine
        self._game_engine = Engine(
            undo_callback = self.__undo_callback,
            event_callback = self.__event_callback,
            key_callback = self.__key_callback,
            move_callback = self.__move_callback,
            socket_callback = self.__socket_callback,
            flags = flags,
            chess_engine = chess_engine,
            game_informations = {
                "event" : event,
                "site"  : site,
                "round" : "",
                "white" : white,
                "black" : black,
            },
            custom_fen = custom_fen
        )
        self._game_engine.start()

    def _on_engine_move_ready(self, result):
        """Callback when Stockfish move is ready"""
        Log.info(f"DEBUG Chess960 Engine: result={result}")
        if result and result.move:
            uci_move = result.move.uci()
            Log.info(f"DEBUG Chess960 Engine UCI: '{uci_move}' (promo={len(uci_move)>4})")
            Centaur.play_computer_move(uci_move)
        else:
            Log.info("Chess960: Engine error - no move available")
            Centaur.send_bot_response("Engine error - no move available")

     # When exists, this function is automatically invoked
     # at start, after splash screen, on PLAY button.
    def on_start_callback(self, key:Enums.Btn) -> bool:
        Log.info(f"Chess960: on_start_callback called with key={key}")

        # HELP key starts the castling tutorial
        if key == Enums.Btn.HELP:
            Log.info(f"Chess960: HELP pressed, starting tutorial")
            self._start_tutorial()
            return False  # Stay in pre-start mode (splash screen state)

        # Start the menu system
        if key == Enums.Btn.PLAY:
            Log.info(f"Chess960: Setting menu_state to 'engine'")
            self._menu_state = "engine"  # Now activate menu
            self._ignore_next_play = True  # Ignore the next PLAY event
            self._update_menu_display()
            Log.info(f"Chess960: Returning True from on_start_callback")
            return True  # Plugin is now started, menu is active

        Log.info(f"Chess960: Returning False from on_start_callback")
        return False

    # -------------------------------------------------------------------------
    # Tutorial
    # -------------------------------------------------------------------------

    def _start_tutorial(self):
        """Start the castling tutorial."""
        Log.info("Chess960: Starting castling tutorial")
        tutorial = Chess960Tutorial(self)
        tutorial.start()

    # -------------------------------------------------------------------------
    # Plugin lifecycle
    # -------------------------------------------------------------------------

     # When exists, this function is automatically invoked
     # when the plugin starts.
    def splash_screen(self) -> bool:

        print = Centaur.print

        Centaur.clear_screen()

        print("CHESS960", row=2)
        print("BOT", font=fonts.DIGITAL_FONT, row=4)
        print("Push PLAY", row=6)
        print("to start!")
        print("")
        print("Push HELP")
        print("for Castling")
        print("Tutorial")

        # The splash screen is activated.
        return True
