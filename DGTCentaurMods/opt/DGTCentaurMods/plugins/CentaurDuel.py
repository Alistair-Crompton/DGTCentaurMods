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

from DGTCentaurMods.classes.Plugin import Centaur
from DGTCentaurMods.plugins.TeamPlay import TeamPlay, YOU, P1, GAME_REQUEST, FLD_USERNAME, LICHESS_USERNAME, button, print
from DGTCentaurMods.consts import Enums, fonts

# Main plugin
class CentaurDuel(TeamPlay):

    # When exists, this function is automatically invoked
    # at start, after splash screen, on PLAY button.
    def on_start_callback(self, key:Enums.Btn) -> bool:

        Centaur.sound(Enums.Sound.COMPUTER_MOVE)

        if key == Enums.Btn.UP:
               
            # We launch a new game request.
            self._launch_game_request([YOU, P1])

            return True

        elif key == Enums.Btn.DOWN:
               
            # We launch a new game request.
            self._launch_game_request([P1, YOU])

            return True

        elif key in (Enums.Btn.TICK, Enums.Btn.PLAY):

            # We take any duel request.
            self._listen_to_game_request()

            return True
        
        return False

    def _screen_header(self):
        Centaur.clear_screen()

        print("Centaur", font=fonts.PACIFICO_FONT, row=1)
        print("Duel", font=fonts.PACIFICO_FONT, row=3)

    def _messagebox_waiting_for_players(self):
        Centaur.messagebox(("Waiting","for","opponent..."))
    
    def _screen_found_game_request(self):
        return

    def _screen_specific_game_request(self):
        self._screen_header()
        print("You just", row=6)
        print("sent")
        print("a new")
        print("duel request!")
        print()
        print("Waiting for")
        print("opponent...")
        
        button(Enums.Btn.BACK, row=13.5, x=6, text="Back home")

    def _screen_any_game_request(self):
        self._screen_header()
        print("You are", row=6)
        print("waiting")
        print("for a duel")
        print("request...")

        button(Enums.Btn.BACK, row=13.5, x=6, text="Back home")

    # When exists, this function is automatically invoked
    # when the plugin starts.
    def splash_screen(self) -> bool:

        self._screen_header()

        print("Send a", font=fonts.SMALL_MAIN_FONT, row=5.5)
        print("duel request", font=fonts.SMALL_MAIN_FONT, row=6.1)

        button(Enums.Btn.UP, x=6, text="Play white")
        button(Enums.Btn.DOWN, x=6, text="Play black")

        print("or", font=fonts.SMALL_MAIN_FONT, row=9.5)
        print("accept any", font=fonts.SMALL_MAIN_FONT, row=10)
        print("duel request", font=fonts.SMALL_MAIN_FONT, row=10.7)

        button(Enums.Btn.PLAY, x=34, text="GO!")

        button(Enums.Btn.BACK, row=13.5, x=6, text="Back home")

        # The splash screen is activated.
        return True