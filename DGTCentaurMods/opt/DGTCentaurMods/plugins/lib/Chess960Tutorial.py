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

"""Chess960 Castling Tutorial - Interactive tutorial for Chess960 castling rules."""

import threading
import time

from DGTCentaurMods.classes import Log
from DGTCentaurMods.classes.Plugin import Centaur
from DGTCentaurMods.consts import Enums, fonts


class Chess960Tutorial:
    """Interactive tutorial demonstrating Chess960 castling mechanics.
    
    This tutorial teaches users how castling works in Chess960 by guiding them
    through queenside and kingside castling sequences on the DGT Centaur board.
    """

    def __init__(self, plugin):
        """Initialize the tutorial with references to plugin resources.
        
        Args:
            plugin: The Chess960 plugin instance (for accessing board, screen, and splash_screen)
        """
        self._plugin = plugin
        self._centaur_board = plugin._centaur_board
        self._centaur_screen = plugin._centaur_screen

        # Tutorial state management
        self._tutorial_active = False
        self._tutorial_state = None  # 'intro' | 'setup' | 'queenside_...' | 'kingside_...' | 'complete'
        
        # LED blinking management
        self._tutorial_blink_fields = []     # Fields currently blinking
        self._tutorial_stop_blink = False    # Stop flag for blink thread
        self._tutorial_blink_thread = None   # Reference to blink daemon thread
        
        # Tracking sets for piece placement
        self._tutorial_placed_fields = set()  # Which target fields (1,5,6) have pieces placed
        self._tutorial_qs_placed = set()      # Queenside place_pieces: tracks c1(2) and d1(3)
        self._tutorial_ks_placed = set()      # Kingside place_pieces: tracks f1(5) and g1(6)

        # Tutorial FENs (for reference/display)
        self._tutorial_fen = "8/8/8/8/8/8/8/1R3KR1 w - - 0 1"    # Setup: Rb1, Kf1, Rg1
        self._tutorial_fen_qs = "8/8/8/8/8/8/8/2KR2R1 w - - 0 1"  # After queenside: Kc1, Rd1, Rg1
        self._tutorial_fen_ks = "8/8/8/8/8/8/8/1R3RK1 w - - 0 1"  # After kingside: Rb1, Rf1, Kg1
        
        # Tutorial board state: 64-char array for dynamic piece display
        # Index 0=a1, 7=h1, 8=a2, ..., 63=h8
        self._tutorial_board_array = [' '] * 64

    def start(self):
        """Start the castling tutorial with intro screen."""
        Log.info("Chess960Tutorial: Starting castling tutorial")
        self._tutorial_active = True
        self._tutorial_state = 'intro'
        
        # Reset tracking sets for fresh start
        self._tutorial_placed_fields = set()
        self._tutorial_qs_placed = set()
        self._tutorial_ks_placed = set()

        # Subscribe tutorial-specific event callbacks
        self._centaur_board.subscribe_events(
            self._key_callback,
            self._field_callback
        )

        # Draw the intro screen
        self._draw_intro_screen()
        Log.info("Chess960Tutorial: Intro screen displayed")

    # -------------------------------------------------------------------------
    # Event Callbacks
    # -------------------------------------------------------------------------

    def _key_callback(self, key: Enums.Btn):
        """Handle key events during the tutorial."""
        Log.info(f"Chess960Tutorial: Key callback: key={key}, state={self._tutorial_state}")
        
        if key == Enums.Btn.BACK:
            Log.info("Chess960Tutorial: Tutorial exited via BACK")
            self._exit()
            return True
        
        elif key == Enums.Btn.PLAY and self._tutorial_state == 'intro':
            # PLAY pressed on intro screen → start setup
            Log.info("Chess960Tutorial: PLAY pressed on intro, starting setup")
            self._start_setup()
            return True
        
        return False

    def _field_callback(self, field_index, action):
        """Handle field (piece lift/place) events during the tutorial."""
        Log.info(f"Chess960Tutorial: Field callback: field={field_index}, action={action}, state={self._tutorial_state}")
        
        # Route to appropriate state handler
        if self._tutorial_state == 'setup':
            self._handle_setup(field_index, action)
        elif self._tutorial_state == 'queenside_lift_rook':
            self._handle_queenside_lift_rook(field_index, action)
        elif self._tutorial_state == 'queenside_lift_king':
            self._handle_queenside_lift_king(field_index, action)
        elif self._tutorial_state == 'queenside_place_king':
            self._handle_queenside_place_king(field_index, action)
        elif self._tutorial_state == 'queenside_place_pieces':
            self._handle_queenside_place_pieces(field_index, action)
        elif self._tutorial_state == 'reset_to_start':
            self._handle_reset(field_index, action)
        elif self._tutorial_state == 'kingside_lift_rook':
            self._handle_kingside_lift_rook(field_index, action)
        elif self._tutorial_state == 'kingside_lift_king':
            self._handle_kingside_lift_king(field_index, action)
        elif self._tutorial_state == 'kingside_place_king':
            self._handle_kingside_place_king(field_index, action)
        elif self._tutorial_state == 'kingside_place_pieces':
            self._handle_kingside_place_pieces(field_index, action)

    # -------------------------------------------------------------------------
    # State Handlers
    # -------------------------------------------------------------------------

    def _handle_setup(self, field_index, action):
        """Handle setup phase: place Rook b1 (1), King f1 (5), Rook g1 (6)."""
        target_fields = {1, 5, 6}
        
        if action == Enums.PieceAction.PLACE:
            if field_index in target_fields:
                Centaur.sound(Enums.Sound.CORRECT_MOVE)
                self._tutorial_placed_fields.add(field_index)
                Log.info(f"Chess960Tutorial: Piece placed on {field_index}, placed={self._tutorial_placed_fields}")
                
                remaining = target_fields - self._tutorial_placed_fields
                if remaining:
                    self._start_blink(list(remaining))
                else:
                    self._stop_blink_thread()
                
                if len(self._tutorial_placed_fields) == 3:
                    Log.info("Chess960Tutorial: All pieces placed, setup complete!")
                    threading.Timer(0.5, self._setup_complete).start()
            else:
                Centaur.sound(Enums.Sound.WRONG_MOVE)
                Log.info(f"Chess960Tutorial: Wrong field {field_index}")
        
        elif action == Enums.PieceAction.LIFT:
            if field_index in target_fields and field_index in self._tutorial_placed_fields:
                self._tutorial_placed_fields.remove(field_index)
                Log.info(f"Chess960Tutorial: Piece lifted from {field_index}")
                remaining = target_fields - self._tutorial_placed_fields
                if remaining:
                    self._start_blink(list(remaining))

    def _handle_queenside_lift_rook(self, field_index, action):
        """Handle queenside: lift rook from b1."""
        if action == Enums.PieceAction.LIFT and field_index == 1:
            Centaur.sound(Enums.Sound.CORRECT_MOVE)
            self._update_piece(1, ' ')
            self._stop_blink_thread()
            Log.info("Chess960Tutorial: Rook lifted from b1 → queenside_lift_king")
            self._tutorial_state = 'queenside_lift_king'
            self._update_text_only(
                (9.0, "Good!"),
                (10.5, "Now lift"),
                (11.5, "King from"),
                (12.5, "f1")
            )
            self._start_blink([5])
        elif action == Enums.PieceAction.LIFT:
            Centaur.sound(Enums.Sound.WRONG_MOVE)

    def _handle_queenside_lift_king(self, field_index, action):
        """Handle queenside: lift king from f1."""
        if action == Enums.PieceAction.LIFT and field_index == 5:
            Centaur.sound(Enums.Sound.CORRECT_MOVE)
            self._update_piece(5, ' ')
            self._update_piece(1, 'K')  # Show target
            self._stop_blink_thread()
            Log.info("Chess960Tutorial: King lifted from f1 → queenside_place_king")
            self._tutorial_state = 'queenside_place_king'
            self._update_text_only(
                (9.0, "Perfect!"),
                (10.5, "Place King"),
                (11.5, "on b1")
            )
            self._start_blink([1])
        elif action == Enums.PieceAction.LIFT:
            Centaur.sound(Enums.Sound.WRONG_MOVE)

    def _handle_queenside_place_king(self, field_index, action):
        """Handle queenside: place king on b1."""
        if action == Enums.PieceAction.PLACE and field_index == 1:
            Centaur.sound(Enums.Sound.CORRECT_MOVE)
            self._stop_blink_thread()
            Log.info("Chess960Tutorial: King placed on b1 → queenside_place_pieces")
            self._tutorial_state = 'queenside_place_pieces'
            self._tutorial_qs_placed.clear()
            
            # Show target positions
            self._tutorial_board_array = [' '] * 64
            self._tutorial_board_array[2] = 'K'
            self._tutorial_board_array[3] = 'R'
            self._tutorial_board_array[6] = 'R'
            self._centaur_screen.draw_board(self._tutorial_board_array, start_row=1.6)
            self._update_text_only(
                (9.0, "Queenside:"),
                (10.5, "Place King"),
                (11.5, "c1, Rook d1")
            )
            self._start_blink([2, 3])
        elif action == Enums.PieceAction.PLACE:
            Centaur.sound(Enums.Sound.WRONG_MOVE)

    def _handle_queenside_place_pieces(self, field_index, action):
        """Handle queenside: place pieces on c1/d1."""
        if action == Enums.PieceAction.PLACE and field_index in {2, 3}:
            Centaur.sound(Enums.Sound.CORRECT_MOVE)
            self._tutorial_qs_placed.add(field_index)
            piece = 'K' if field_index == 2 else 'R'
            self._update_piece(field_index, piece)
            
            remaining = {2, 3} - self._tutorial_qs_placed
            if remaining:
                self._start_blink(list(remaining))
            else:
                self._stop_blink_thread()
                Log.info("Chess960Tutorial: Queenside complete!")
                threading.Timer(0.5, self._queenside_complete).start()
        elif action == Enums.PieceAction.PLACE:
            Centaur.sound(Enums.Sound.WRONG_MOVE)
        elif action == Enums.PieceAction.LIFT and field_index in {2, 3} and field_index in self._tutorial_qs_placed:
            self._tutorial_qs_placed.remove(field_index)
            self._update_piece(field_index, ' ')
            remaining = {2, 3} - self._tutorial_qs_placed
            if remaining:
                self._start_blink(list(remaining))

    def _handle_reset(self, field_index, action):
        """Handle reset phase: reset to starting position."""
        target_fields = {1, 5, 6}
        
        if action == Enums.PieceAction.PLACE and field_index in target_fields:
            Centaur.sound(Enums.Sound.CORRECT_MOVE)
            self._tutorial_placed_fields.add(field_index)
            piece = 'R' if field_index in {1, 6} else 'K'
            self._update_piece(field_index, piece)
            
            remaining = target_fields - self._tutorial_placed_fields
            if remaining:
                self._start_blink(list(remaining))
            else:
                self._stop_blink_thread()
            
            if len(self._tutorial_placed_fields) == 3:
                Log.info("Chess960Tutorial: Reset complete!")
                threading.Timer(0.5, self._reset_complete).start()
        elif action == Enums.PieceAction.PLACE:
            Centaur.sound(Enums.Sound.WRONG_MOVE)
        elif action == Enums.PieceAction.LIFT:
            if field_index in target_fields and field_index in self._tutorial_placed_fields:
                self._tutorial_placed_fields.remove(field_index)
                self._update_piece(field_index, ' ')
                remaining = target_fields - self._tutorial_placed_fields
                if remaining:
                    self._start_blink(list(remaining))
            elif field_index in {2, 3}:  # Allow lifting queenside pieces
                self._update_piece(field_index, ' ')

    def _handle_kingside_lift_rook(self, field_index, action):
        """Handle kingside: lift rook from g1."""
        if action == Enums.PieceAction.LIFT and field_index == 6:
            Centaur.sound(Enums.Sound.CORRECT_MOVE)
            self._update_piece(6, ' ')
            self._stop_blink_thread()
            Log.info("Chess960Tutorial: Rook lifted from g1 → kingside_lift_king")
            self._tutorial_state = 'kingside_lift_king'
            self._update_text_only(
                (9.0, "Good!"),
                (10.5, "Now lift"),
                (11.5, "King from"),
                (12.5, "f1")
            )
            self._start_blink([5])
        elif action == Enums.PieceAction.LIFT:
            Centaur.sound(Enums.Sound.WRONG_MOVE)

    def _handle_kingside_lift_king(self, field_index, action):
        """Handle kingside: lift king from f1."""
        if action == Enums.PieceAction.LIFT and field_index == 5:
            Centaur.sound(Enums.Sound.CORRECT_MOVE)
            self._update_piece(5, ' ')
            self._update_piece(6, 'K')  # Show target
            self._stop_blink_thread()
            Log.info("Chess960Tutorial: King lifted from f1 → kingside_place_king")
            self._tutorial_state = 'kingside_place_king'
            self._update_text_only(
                (9.0, "Perfect!"),
                (10.5, "Place King"),
                (11.5, "on g1")
            )
            self._start_blink([6])
        elif action == Enums.PieceAction.LIFT:
            Centaur.sound(Enums.Sound.WRONG_MOVE)

    def _handle_kingside_place_king(self, field_index, action):
        """Handle kingside: place king on g1."""
        if action == Enums.PieceAction.PLACE and field_index == 6:
            Centaur.sound(Enums.Sound.CORRECT_MOVE)
            self._update_piece(6, 'K')
            self._stop_blink_thread()
            Log.info("Chess960Tutorial: King placed on g1 → kingside_place_pieces")
            self._tutorial_state = 'kingside_place_pieces'
            self._tutorial_ks_placed = {6}
            self._centaur_screen.draw_fen(self._tutorial_fen_ks, startrow=1.6)
            self._update_text_only(
                (9.0, "Kingside:"),
                (10.5, "Place Rook"),
                (11.5, "on f1")
            )
            self._start_blink([5])
        elif action == Enums.PieceAction.PLACE:
            Centaur.sound(Enums.Sound.WRONG_MOVE)

    def _handle_kingside_place_pieces(self, field_index, action):
        """Handle kingside: place rook on f1."""
        if action == Enums.PieceAction.PLACE and field_index == 5:
            Centaur.sound(Enums.Sound.CORRECT_MOVE)
            self._tutorial_ks_placed.add(field_index)
            self._update_piece(5, 'R')
            
            if len(self._tutorial_ks_placed) == 2:
                self._stop_blink_thread()
                Log.info("Chess960Tutorial: Kingside complete - Tutorial finished!")
                threading.Timer(0.5, self._kingside_complete).start()
        elif action == Enums.PieceAction.PLACE:
            Centaur.sound(Enums.Sound.WRONG_MOVE)
        elif action == Enums.PieceAction.LIFT and field_index == 5 and field_index in self._tutorial_ks_placed:
            self._tutorial_ks_placed.remove(field_index)
            self._update_piece(5, ' ')
            self._start_blink([5])

    # -------------------------------------------------------------------------
    # State Transitions
    # -------------------------------------------------------------------------

    def _setup_complete(self):
        """Called when all 3 pieces are correctly placed."""
        Log.info("Chess960Tutorial: Setup complete → queenside")
        Centaur.sound(Enums.Sound.CORRECT_MOVE)
        self._update_text_only(
            (9.0, "Well done!"),
            (10.5, "Next:"),
            (11.5, "Queenside"),
            (12.5, "castling")
        )
        threading.Timer(2.0, self._start_queenside).start()

    def _start_queenside(self):
        """Start queenside castling sequence."""
        Log.info("Chess960Tutorial: Starting queenside castling")
        self._tutorial_state = 'queenside_lift_rook'
        self._update_text_only(
            (9.0, "Queenside"),
            (10.0, "castling:"),
            (11.5, "Lift Rook"),
            (12.5, "from b1")
        )
        self._start_blink([1])

    def _queenside_complete(self):
        """Called when queenside castling is complete."""
        Log.info("Chess960Tutorial: Queenside complete")
        Centaur.sound(Enums.Sound.CORRECT_MOVE)
        self._update_text_only(
            (9.0, "Queenside"),
            (10.0, "complete!"),
            (11.5, "Next:"),
            (12.5, "Kingside!")
        )
        threading.Timer(4.0, self._start_reset).start()

    def _start_reset(self):
        """Start reset phase."""
        Log.info("Chess960Tutorial: Starting reset phase")
        self._tutorial_state = 'reset_to_start'
        self._tutorial_placed_fields.clear()
        
        self._tutorial_board_array = [' '] * 64
        self._tutorial_board_array[1] = 'R'
        self._tutorial_board_array[5] = 'K'
        self._tutorial_board_array[6] = 'R'
        self._centaur_screen.draw_board(self._tutorial_board_array, start_row=1.6)
        
        self._update_text_only(
            (9.0, "Reset pieces"),
            (10.0, "to start:"),
            (11.0, "Rook b1"),
            (12.0, "King f1"),
            (13.0, "Rook g1")
        )
        self._start_blink([1, 5, 6])

    def _reset_complete(self):
        """Called when reset is complete."""
        Log.info("Chess960Tutorial: Reset complete → kingside")
        Centaur.sound(Enums.Sound.CORRECT_MOVE)
        self._update_text_only(
            (9.0, "Good!"),
            (10.5, "Now:"),
            (11.5, "Kingside"),
            (12.5, "castling")
        )
        threading.Timer(2.0, self._start_kingside).start()

    def _start_kingside(self):
        """Start kingside castling sequence."""
        Log.info("Chess960Tutorial: Starting kingside castling")
        self._tutorial_state = 'kingside_lift_rook'
        self._tutorial_ks_placed.clear()
        self._update_text_only(
            (9.0, "Kingside"),
            (10.0, "castling:"),
            (11.5, "Lift Rook"),
            (12.5, "from g1")
        )
        self._start_blink([6])

    def _kingside_complete(self):
        """Called when kingside castling is complete."""
        Log.info("Chess960Tutorial: Kingside complete - Tutorial finished!")
        Centaur.sound(Enums.Sound.VICTORY)
        self._update_text_only(
            (9.0, "Perfect!"),
            (10.5, "Tutorial"),
            (11.5, "complete!"),
            (13.0, "BACK: exit")
        )
        self._tutorial_state = 'complete'

    # -------------------------------------------------------------------------
    # Screen Drawing Helpers
    # -------------------------------------------------------------------------

    def _draw_intro_screen(self):
        """Draw intro screen explaining castling trigger."""
        Centaur.clear_screen()
        self._centaur_screen.write_text(1.0, "CHESS960", font=fonts.MAIN_FONT)
        self._centaur_screen.write_text(3.0, "Castling:", font=fonts.MAIN_FONT)
        self._centaur_screen.write_text(4.0, "move is", font=fonts.MAIN_FONT)
        self._centaur_screen.write_text(5.0, "triggered", font=fonts.MAIN_FONT)
        self._centaur_screen.write_text(6.0, "by king's", font=fonts.MAIN_FONT)
        self._centaur_screen.write_text(7.0, "move to", font=fonts.MAIN_FONT)
        self._centaur_screen.write_text(8.0, "rook square", font=fonts.MAIN_FONT)
        self._centaur_screen.write_text(10.0, "PLAY: start", font=fonts.MAIN_FONT)
        self._centaur_screen.write_text(11.0, "BACK: exit", font=fonts.MAIN_FONT)

    def _start_setup(self):
        """Start setup phase after intro."""
        Log.info("Chess960Tutorial: Starting setup phase")
        self._tutorial_state = 'setup'
        
        self._tutorial_board_array = [' '] * 64
        self._tutorial_board_array[1] = 'R'
        self._tutorial_board_array[5] = 'K'
        self._tutorial_board_array[6] = 'R'
        
        self._draw_setup_screen()
        self._start_blink([1, 5, 6])

    def _draw_setup_screen(self):
        """Draw setup screen."""
        Centaur.clear_screen()
        self._centaur_screen.draw_fen(self._tutorial_fen, startrow=1.6)
        self._centaur_screen.write_text(9.0, "Place pieces:", font=fonts.MAIN_FONT)
        self._centaur_screen.write_text(10.0, "Rook b1", font=fonts.MAIN_FONT)
        self._centaur_screen.write_text(11.0, "King f1", font=fonts.MAIN_FONT)
        self._centaur_screen.write_text(12.0, "Rook g1", font=fonts.MAIN_FONT)
        self._centaur_screen.write_text(13.5, "BACK: exit", font=fonts.MAIN_FONT)

    def _update_piece(self, field_index, piece_char):
        """Update single piece on board array and redraw."""
        self._tutorial_board_array[field_index] = piece_char
        self._centaur_screen.draw_board(self._tutorial_board_array, start_row=1.6)

    def _update_text_only(self, *line_tuples):
        """Update only text area, keeping board intact."""
        for row in [9.0, 10.0, 10.5, 11.0, 11.5, 12.0, 12.5, 13.0, 13.5, 14.0, 14.5, 15.0]:
            self._centaur_screen.write_text(row, " ", font=fonts.MAIN_FONT)
        for row, text in line_tuples:
            self._centaur_screen.write_text(row, text, font=fonts.MAIN_FONT)

    # -------------------------------------------------------------------------
    # LED Blinking
    # -------------------------------------------------------------------------

    def _start_blink(self, fields):
        """Start LED blinking for given fields."""
        self._stop_blink_thread()
        self._tutorial_blink_fields = list(fields)
        self._tutorial_stop_blink = False
        self._tutorial_blink_thread = threading.Thread(
            target=self._blink_leds, daemon=True)
        self._tutorial_blink_thread.start()

    def _stop_blink_thread(self):
        """Stop LED blink thread."""
        if self._tutorial_blink_thread and self._tutorial_blink_thread.is_alive():
            self._tutorial_stop_blink = True
            self._tutorial_blink_thread.join(timeout=2.0)
            self._tutorial_blink_thread = None
        self._centaur_board.leds_off()

    def _blink_leds(self):
        """Background thread: cycle through fields."""
        while not self._tutorial_stop_blink:
            fields = list(self._tutorial_blink_fields)
            if not fields:
                time.sleep(0.1)
                continue
            for field in fields:
                if self._tutorial_stop_blink:
                    break
                self._centaur_board.led_array([field], speed=3, intensity=5)
                time.sleep(0.5)
                if self._tutorial_stop_blink:
                    break
                self._centaur_board.leds_off()
                time.sleep(0.1)

    # -------------------------------------------------------------------------
    # Exit
    # -------------------------------------------------------------------------

    def _exit(self):
        """Exit tutorial and return to plugin splash screen."""
        Log.info("Chess960Tutorial: Exiting tutorial")
        self._tutorial_active = False
        self._tutorial_state = None
        self._stop_blink_thread()
        self._centaur_board.unsubscribe_events()
        # Call plugin's splash_screen to return
        self._plugin.splash_screen()
