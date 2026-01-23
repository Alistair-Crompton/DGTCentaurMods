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

import chess, random, os, configparser
from pathlib import Path

from DGTCentaurMods.classes.Plugin import Plugin, Centaur
from DGTCentaurMods.classes import Log, ChessEngine
from DGTCentaurMods.consts import Enums, fonts, consts

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

    def __event_callback(self, event:Enums.Event, outcome:Optional[chess.Outcome]):
        try:
            if self._started:
                self.event_callback(event, outcome)
        except:
            SOCKET.send_web_message({ "script_output":Log.last_exception() })
            self.stop()

    def __move_callback(self, uci_move:str, san_move:str, color:chess.Color, field_index:chess.Square):
        try:
            if self._started:
                return self.move_callback(uci_move, san_move, color, field_index)
        except:
            SOCKET.send_web_message({ "script_output":Log.last_exception() })
            self.stop()
        return False

    def __undo_callback(self, uci_move:str, san_move:str, field_index:chess.Square):
        try:
            if self._started:
                return self.undo_callback(uci_move, san_move, field_index)
        except:
            SOCKET.send_web_message({ "script_output":Log.last_exception() })
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
        except:
            SOCKET.send_web_message({ "script_output":Log.last_exception() })
            self.stop()
        return False

    def __key_callback(self, key:Enums.Btn):
        try:
            if key == Enums.Btn.BACK:
                if self._game_engine:
                    self._game_engine.end()
                else:
                    self.stop()
                return True

            if not self._started:
                self._started = self.on_start_callback(key)
                if self._started:
                    return True  # Event was handled by on_start_callback, don't process again

            if not self._started:
                return False

            return self.key_callback(key)
        except:
            SOCKET.send_web_message({ "script_output":Log.last_exception() })
            self.stop()

    def _scan_frc_engines(self):
        """Find engines that support UCI_Chess960"""
        engines_dir = consts.ENGINES_CHESS960_DIRECTORY
        self._engines = []

        if not os.path.exists(engines_dir):
            Log.error(f"Chess960: Engines directory not found: {engines_dir}")
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
            Log.error("Chess960: No FRC engines found!")
        else:
            Log.info(f"Chess960: Found {len(self._engines)} FRC engines")

    def _load_engine_strengths(self, uci_path):
        """Load strength levels from UCI file"""
        parser = configparser.ConfigParser()
        parser.read(uci_path)

        self._strengths = []
        for section in parser.sections():
            if section.startswith('E-') or section.startswith('DEFAULT'):
                self._strengths.append(section)

        # Sort by ELO rating (DEFAULT first, then E-XXXX)
        self._strengths.sort(key=lambda x: int(x[2:]) if x.startswith('E-') else 0)

        Log.info(f"Chess960: Loaded {len(self._strengths)} strength levels")

    # This function is automatically invoked when
    # the user launches the plugin.
    def start(self):
        self._scan_frc_engines()
        super().start()

    # This function is automatically invoked when
    # the user stops the plugin.
    def stop(self):
        # Back to the main menu.
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
        """Update the screen to show current menu state"""
        Centaur.clear_screen()

        if self._menu_state == "engine":
            Centaur.print("Select Engine", row=1)
            if self._engines:
                engine_name = self._engines[self._current_index]['name']
                Centaur.print(f"{engine_name}", row=4, font=fonts.DIGITAL_FONT)
                Centaur.print(f"{self._current_index + 1}/{len(self._engines)}", row=6)
            else:
                Centaur.print("No engines found!", row=4)

        elif self._menu_state == "strength":
            Centaur.print("Select Strength", row=1)
            if self._strengths:
                strength = self._strengths[self._current_index]
                Centaur.print(f"{strength}", row=4, font=fonts.DIGITAL_FONT)
                Centaur.print(f"{self._current_index + 1}/{len(self._strengths)}", row=6)
            else:
                Centaur.print("No strengths found!", row=4)

        elif self._menu_state == "color":
            Centaur.print("Select Color", row=1)
            colors = ["White", "Black"]
            color_name = colors[self._current_index]
            Centaur.print(f"{color_name}", row=4, font=fonts.DIGITAL_FONT)
            Centaur.print(f"{self._current_index + 1}/{len(colors)}", row=6)

        Centaur.print("UP/DOWN: Navigate", row=8)
        Centaur.print("PLAY: Select", row=9)
        Centaur.print("BACK: Exit", row=10)

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

        Log.info(f"Chess960: Key {key} not handled in menu navigation")
        return False

    def _handle_menu_selection(self):
        """Handle menu selection and state transitions"""
        Log.info(f"Chess960: _handle_menu_selection called, state={self._menu_state}, index={self._current_index}")

        if self._menu_state == "engine":
            if self._engines:
                self._selected_engine = self._engines[self._current_index]
                Log.info(f"Chess960: Selected engine: {self._selected_engine['name']}")
                self._load_engine_strengths(self._selected_engine['uci_path'])
                self._menu_state = "strength"
                self._current_index = 0
                self._update_menu_display()
            else:
                Log.error("Chess960: No engines available for selection")

        elif self._menu_state == "strength":
            if self._strengths:
                self._selected_strength = self._strengths[self._current_index]
                Log.info(f"Chess960: Selected strength: {self._selected_strength}")
                self._menu_state = "color"
                self._current_index = 0
                self._update_menu_display()
            else:
                Log.error("Chess960: No strengths available for selection")

        elif self._menu_state == "color":
            self._selected_color = chess.WHITE if self._current_index == 0 else chess.BLACK
            Log.info(f"Chess960: Selected color: {'WHITE' if self._selected_color == chess.WHITE else 'BLACK'}")
            self._menu_state = None  # Exit menu, start game
            Log.info(f"Chess960: Starting game...")
            self._start_selected_game()

    def _start_selected_game(self):
        """Start the game with selected parameters"""
        # Generate random Chess960 position
        chess960_pos = random.randint(0, 959)
        board = chess.Board.from_chess960_pos(chess960_pos)
        self._chess960_fen = board.fen()

        Log.info(f"Chess960: Generated position {chess960_pos}")
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

        config["Threads"] = 1
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
            Log.error("Chess960: Engine error - no move available")
            Centaur.send_bot_response("Engine error - no move available")

     # When exists, this function is automatically invoked
     # at start, after splash screen, on PLAY button.
    def on_start_callback(self, key:Enums.Btn) -> bool:
        Log.info(f"Chess960: on_start_callback called with key={key}")
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

     # When exists, this function is automatically invoked
     # when the plugin starts.
    def splash_screen(self) -> bool:

        print = Centaur.print

        Centaur.clear_screen()

        print("CHESS960", row=2)
        print("BOT", font=fonts.DIGITAL_FONT, row=4)
        print("Push PLAY", row=8)
        print("to")
        print("configure!")

        # The splash screen is activated.
        return True
