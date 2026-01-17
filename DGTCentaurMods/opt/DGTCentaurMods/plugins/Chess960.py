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

import chess, random

from DGTCentaurMods.classes.Plugin import Plugin, Centaur
from DGTCentaurMods.classes import Log, ChessEngine
from DGTCentaurMods.consts import Enums, fonts

from typing import Optional

HUMAN_COLOR = chess.WHITE

# The plugin must inherits of the Plugin class.
# Filename must match the class name.
class Chess960(Plugin):

    def __init__(self, id:str):
        super().__init__(id)
        self._chess960_fen = None

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
            
            if not self._started:
                return False

            return self.key_callback(key)
        except:
            SOCKET.send_web_message({ "script_output":Log.last_exception() })
            self.stop()

    # This function is automatically invoked when
    # the user launches the plugin.
    def start(self):
        super().start()

    # This function is automatically invoked when
    # the user stops the plugin.
    def stop(self):
        # Back to the main menu.
        super().stop()

    # When exists, this function is automatically invoked
    # when the player physically plays a move.
    def move_callback(self, uci_move:str, san_move:str, color:chess.Color, field_index:chess.Square):

        if color == (not HUMAN_COLOR):
            # Computer move is accepted
            return True

        # Human move is accepted
        return True

    # This function is automatically invoked each
    # time the player pushes a key.
    # Except the BACK key which is handled by the engine.
    def key_callback(self, key:Enums.Btn):

        # If the user pushes HELP,
        # we display an hint using Stockfish engine.
        if key == Enums.Btn.HELP:
            Centaur.hint()
            # Key has been handled.
            return True

        # Key can be handled by the engine.
        return False

    # When exists, this function is automatically invoked
    # when the game engine state is affected.
    def event_callback(self, event:Enums.Event, outcome:Optional[chess.Outcome]):

        # If the user chooses to leave,
        # we quit the plugin.
        if event == Enums.Event.QUIT:
            self.stop()

        if event == Enums.Event.TERMINATION:
            if outcome.winner == HUMAN_COLOR:
                Centaur.sound(Enums.Sound.VICTORY)
            else:
                Centaur.sound(Enums.Sound.GAME_LOST)

        if event == Enums.Event.PLAY:

            turn = self.chessboard.turn

            current_player = "You" if turn == chess.WHITE else "Chess960 bot"

            # We display the board header.
            Centaur.header(f"{current_player} {'W' if turn == chess.WHITE else 'B'}")

            if turn == (not HUMAN_COLOR):
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

        # Generate random Chess960 position
        # chess960_pos = random.randint(0, 959)
        chess960_pos = 537
        board = chess.Board.from_chess960_pos(chess960_pos)
        # Chess960 Plugin edit by Chemtech1 - Castling rights are automatically set correctly by from_chess960_pos()
        self._chess960_fen = board.fen()

        Log.info(f"Chess960: Generated position {chess960_pos}")
        Log.info(f"Chess960: FEN: {self._chess960_fen}")

        # Log Chess960 mode status
        if 'KQkq' in self._chess960_fen:
            Log.info("Chess960: Engine is in Chess960 mode (FRC castling rights detected)")
        else:
            Log.debug("Chess960: Engine may not be in Chess960 mode (no FRC castling rights)")

        Centaur.print(f"Chess960 pos: {chess960_pos}", row=6)

        # Set up Stockfish engine for Chess960 BEFORE starting the game
        # Note: UCI_Chess960 is automatically managed by python-chess based on FEN
        Centaur.set_main_chess_engine("stockfish")
        Centaur.configure_main_chess_engine({
            "UCI_Elo": 1350,       # Set exact ELO rating
            "Threads": 1
        })

        Log.info("Chess960: Engine configured (Chess960 mode auto-detected from FEN)")

        # Start a new game with Chess960 position
        self._start_game(
            event="Chess960 Event",
            site="",
            white="You",
            black="Chess960 bot",
            flags=Enums.BoardOption.CAN_UNDO_MOVES | Enums.BoardOption.CAN_FORCE_MOVES,
            chess_engine=None,
            custom_fen=self._chess960_fen  # Chess960 Plugin edit by Chemtech1 - Pass custom FEN for Chess960 starting position
        )

        Log.info("Chess960: Game started with custom FEN")

        # Chess960 Plugin edit by Chemtech1 - Ensure Chess960 FEN is sent to web interface for correct board display (handled by update_web_ui)

        # Game started.
        return True

     # When exists, this function is automatically invoked
     # when the plugin starts.
    def splash_screen(self) -> bool:

        print = Centaur.print

        Centaur.clear_screen()

        print("CHESS960", row=2)
        print("BOT", font=fonts.DIGITAL_FONT, row=4)
        print("Push PLAY", row=8)
        print("to")
        print("start")
        print("the game!")

        # The splash screen is activated.
        return True
        return True
