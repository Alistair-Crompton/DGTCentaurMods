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

from DGTCentaurMods.classes.Plugin import Plugin, Centaur
from DGTCentaurMods.consts import Enums, fonts

import chess, random

HUMAN_COLOR = chess.WHITE

# The plugin must inherits of the Plugin class.
# Filename must match the class name.
class RandomBot(Plugin):

    # Constructor for initialization stuff
    # The id is the name of the plugin/class
    def __init__(self, id:str):
        super().__init__(id)

    # This function is automatically invoked when
    # the user launches the plugin.
    def start(self):
        super().start()

        self._started:bool = False

        Centaur.clear_screen()
        Centaur.print("RANDOM", row=2)
        Centaur.print("BOT", font=fonts.DIGITAL_FONT, row=4)
        Centaur.print("Push PLAY", row=8)
        Centaur.print("to")
        Centaur.print("start")
        Centaur.print("the game!")


    # This function is (automatically) invoked when
    # the user stops the plugin
    def stop(self):

        # Back to the main menu.
        super().stop()

    # This function is automatically invoked each
    # time the player pushes a key.
    # Except the BACK key which is handled by the engine.
    def key_callback(self, key:Enums.Btn):

        if key == Enums.Btn.PLAY and not self._started:
            Centaur.sound(Enums.Sound.COMPUTER_MOVE)

            # Start chess engine
            self.start_engine(white="You", black="Random bot", event="Bots chess event 2024",flags=Enums.BoardOption.CAN_UNDO_MOVES)


        # If the user pushes HELP,
        # we display an hint using Stockfish engine.
        if key == Enums.Btn.HELP and self._started:
            self.hint()

            # Key has been handled.
            return True
        
        # Key can be handled by the engine.
        return False
        
    # This function is automatically invoked
    # when the game engine state is affected.
    def event_callback(self, event:Enums.Event):

        # If the user chooses to leave,
        # we quit the plugin.
        if event == Enums.Event.QUIT:
            self.stop()

        if event == Enums.Event.PLAY:

            turn = self.board().turn

            current_player = "You" if turn == chess.WHITE else "Random bot"

            # We display the board header.
            Centaur.header(f"{current_player} {'W' if turn == chess.WHITE else 'B'}")

            if turn == (not HUMAN_COLOR):

                # We choose a random move
                uci_move = str(random.choice(list(self.board().legal_moves)))

                self.play_computer_move(uci_move)


    # This function is automatically invoked
    # when the we physically play a move.
    def move_callback(self, uci_move:str, san_move:str, color:chess.Color, field_index:chess.Square):
        
        # Nothing to do there...

        if color == (not HUMAN_COLOR):
            # Black move is accepted
            return True

        # White move is accepted
        return True
