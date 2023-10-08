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

import chess, time

from DGTCentaurMods.classes import Log
from DGTCentaurMods.classes.Plugin import Plugin, Centaur, TPlayResult
from DGTCentaurMods.consts import Enums, fonts, consts

from typing import Optional, List

from enum import Enum

# Local constants.
(SPECIFIC_GAME_REQUEST, GAME_REQUEST, GAME_ACK, GAME_MOVE, GAME_MOVE_ACK, GAME_ABORTED, GAME_START) = range(0,7)

(INITIALIZING, MASTER, SLAVE, GAME_RUNNING, PENDING_MOVE_ACK, PENDING_COMPUTER_MOVE) = range(0,6) 

# Player types
(NONE,YOU,P1,P2,P3,P4,P5,P6,CPU) = range(0,9)

# Only there for conversion purposes...
# TODO: use it everywere and handle enum serialization.
PlayerType = Enum('PlayerType', ['YOU','P1','P2','P3','P4','P5','P6','CPU'])

WAIT_FOR_REQUEST = -1

# Field names.
PLAYER_DATA = "player_data"
PLAYER_ID = "player_id"
MASTER_CUUID = "master_cuuid"
USERNAME = "username"
COLOR = "color"

# Centaur UUID
CUUID = Centaur.configuration().get_system_settings("cuuid", "")

if not CUUID:
    raise Exception("Unable to read your CUUID!")

# Shortcuts.
print = Centaur.print
button = Centaur.print_button_label
option = Centaur.print_option_label

# We pick the Lichess username when exists.
LICHESS_USERNAME = Centaur.configuration().get_lichess_settings("username") or "anonymous"

COMPUTER_NAME = "Maia"

# Max retries when no move acknowledgement.
MAX_ACK_RETRIES = 20

# Move acknowledgement class.
class _MoveAck():

    def __init__(self) -> None:
        self._time = time.time()
        self._tries = 0
        self._cuuids = []

    def update(self, cuuids:List[str], move_message:dict) -> None:

        for field in ("type", MASTER_CUUID, USERNAME, COLOR, "san_move", "uci_move", PLAYER_ID):
            if field not in move_message:
                raise Exception(f"Move message must contain field '{field}'!")

        self._cuuids = cuuids.copy()

        self._move_message = move_message
        self._time = time.time()
        self._tries = 0

    def __str__(self) -> str:
        return str(self._move_message["uci_move"])
    
    # Every 5 seconds we can retry to send the move.
    def is_outdated(self) -> bool:
        result = time.time() - self._time > 5
        if result:
            self._time = time.time()
        return result
    
    def check(self, uci_move, cuuid) -> bool:
        result = uci_move == self._move_message["uci_move"]
        if result:
            if cuuid in self._cuuids:
                self._cuuids.remove(cuuid)
        return result
    
    def done(self):
        return len(self._cuuids) == 0
    
    def retry(self) -> None:
        self._tries += 1
        if self._tries > MAX_ACK_RETRIES:
            raise Exception(f'Tried {MAX_ACK_RETRIES} times to send the move "{self._move_message["san_move"]}" to the opponent but received no ACK!')
        
        Log.debug(f'Retry #{self._tries} : resending your move "{self._move_message["san_move"]}"...')
        Centaur.send_external_request(self._move_message)


GAME_SEQUENCES = (
    {
        "label":"You versus 2",
        "sequence":(YOU,P1,YOU,P2)
    },
    {
        "label":"2 versus you",
        "sequence":(P1,YOU,P2,YOU)
    },
    {
        "label":"You+1 versus 1",
        "sequence":(YOU,P1,P2,P1)
    },
    {
        "label":"You+1 versus 2",
        "sequence":(YOU,P1,P2,P3)
    },
    {
        "label":"2 versus you+1",
        "sequence":(P1,YOU,P2,P3)
    },
    {
        "label":f"You+1 versus {COMPUTER_NAME}",
        "sequence":(YOU,CPU,P1,CPU)
    },
    {
        "label":f"{COMPUTER_NAME} versus you+1",
        "sequence":(CPU,YOU,CPU,P1)
    },
    {
        "label":f"You+{COMPUTER_NAME} versus 1",
        "sequence":(YOU,P1,CPU,P1)
    },
    {
        "label":f"You+{COMPUTER_NAME} versus 2",
        "sequence":(YOU,P1,CPU,P2)
    },
    {
        "label":f"1 versus You+{COMPUTER_NAME}",
        "sequence":(P1,YOU,P1,CPU)
    },
    {
        "label":f"2 versus You+{COMPUTER_NAME}",
        "sequence":(P1,YOU,P2,CPU)
    },
)


# Main plugin
class TeamPlay(Plugin):

    _status = INITIALIZING
    _expected_ack = _MoveAck()

    _game = WAIT_FOR_REQUEST

    _player_id:int = NONE

    _sequence_index = 0
    
    _players_sequence = []
    _players_cuuid:List[str] = []

    _teams_displayed = False

    # The master CUUID is the current game ID.
    _master_cuuid:Optional[str] = None

    def _display_teams(self):

        if self._teams_displayed:
            return
        
        self._teams_displayed = True

        text_lines = []

        for player in self._teams[chess.WHITE]:
            text_lines.append(player)

        text_lines.append("vs")

        for player in self._teams[chess.BLACK]:
            text_lines.append(player)

        Centaur.messagebox(text_lines=text_lines, row=0)

    def _init_players_cuuid_from_players_sequence(self):
        self._players_cuuid = list(dict.fromkeys(list(p["cuuid"] for p in self._players_sequence)))
        if CUUID in self._players_cuuid:
            self._players_cuuid.remove(CUUID)

    def _increase_sequence_index(self):
        # Next player to play...
        self._sequence_index += 1
        if self._sequence_index == len(self._players_sequence):
            self._sequence_index = 0

        Log.debug(f"current_player ->  {self._players_sequence[self._sequence_index]}")

    # This function is automatically invoked each
    # time the player pushes a key.
    # Except the BACK key which is handled by the engine.
    def key_callback(self, key:Enums.Btn):
        
        # Key can be handled by the engine.
        return False
    
    # This function is automatically invoked each
    # time the player send a bot command from the chat window.
    def on_bot_request(self, data:List[str]):

        if self._started:
            return

        global LICHESS_USERNAME

        if data[0] == "@username" and len(data)>1:
            LICHESS_USERNAME = data[1]
            Log.info(f'Username has been updated to "{LICHESS_USERNAME}"')

        if data[0] == "@start" and len(data)>2:

            data.pop(0)

            def _to_int(value:str) -> int:
                try:
                    return PlayerType[value.upper()].value
                except:
                    return NONE
                
            # We convert to integer values.
            int_values = list(map(_to_int, data))

            # We keep only the correct values.
            sequence = list(filter(lambda item:item != NONE, int_values))

            # If we have an odd sequence, we add a player.
            if len(sequence) %2 == 1:
                sequence.append(CPU)

            if len(sequence)>1:

                Log.info(f"Game sequence has been updated to {sequence}")

                self._launch_game_request(sequence)
                self._started = True
                
                # Ready to go?
                # If we don't need external players,
                # then we start right now.
                if 0 == len(list(
                    filter(lambda p:p not in (YOU, CPU), sequence)
                )):
                    self._handle_slave_request(None, None)

    # When exists, this function is automatically invoked
    # when the game engine state is affected.
    def event_callback(self, event:Enums.Event, outcome:Optional[chess.Outcome]):

        # If the user chooses to leave,
        # we quit the plugin.
        if event == Enums.Event.QUIT:
            # We send a notification to the opponent.
            Centaur.send_external_request({
                "type":GAME_ABORTED,
                MASTER_CUUID:self._master_cuuid,
                USERNAME:LICHESS_USERNAME,
                PLAYER_ID:self._player_id })

            self.stop()

        # End game.
        if event == Enums.Event.TERMINATION:

            if outcome.winner == self.YOUR_COLOR:
                Centaur.sound(Enums.Sound.VICTORY)
                Centaur.messagebox(("YOU","WIN!",None))
            else:
                Centaur.sound(Enums.Sound.GAME_LOST)
                Centaur.messagebox(("YOU","LOOSE!",None))

        # Player must physically play a move.
        if event == Enums.Event.PLAY:

            self._display_teams()

            current_player = self._players_sequence[self._sequence_index]

            # We display the board header.
            Centaur.header(
                text=f"{current_player[USERNAME]} {'W' if current_player[COLOR] == chess.WHITE else 'B'}",
                web_text=f"turn → {current_player[USERNAME]} {'(WHITE)' if current_player[COLOR]  == chess.WHITE else '(BLACK)'}")

            Centaur.messagebox(("Waiting","for other","players..."))

            if self._status == PENDING_MOVE_ACK:
                Log.debug("Pending for move acknowledgement...")

                # Pending for move acknowledgement?
                # TODO make that part asynchronous.
                while self._status == PENDING_MOVE_ACK and self._running():
                    if self._expected_ack.is_outdated():
                        self._expected_ack.retry()
                    time.sleep(.1)

                Log.debug("All players acknowledged the move...")

            color = 'white' if current_player[COLOR] else 'black'

            if current_player[PLAYER_ID] == self._player_id:
                Centaur.messagebox((
                    "You are",
                    "playing.",
                    f"({color})"))
            else:
                Centaur.messagebox((
                    current_player[USERNAME],
                    "is playing.",
                    f"({color})"))

            # Do we need to make the computer play?
            if self._is_master and current_player[PLAYER_ID] == CPU:

                self._status = PENDING_COMPUTER_MOVE

                def engine_move_callback(result:TPlayResult):
                    Centaur.play_computer_move(str(result.move))

                    Centaur.messagebox((
                        current_player[USERNAME],
                        "found a move!",
                        None))

                    self._status = GAME_RUNNING

                Log.debug("Pending for computer move...")

                # Computer is going to play asynchronously.
                Centaur.request_chess_engine_move(engine_move_callback)

    # When exists, this function is automatically invoked
    # when the player physically plays a move.
    def move_callback(self, uci_move:str, san_move:str, color:chess.Color, field_index:chess.Square):

        current_player = self._players_sequence[self._sequence_index]

        # Waiting for computer move?
        if self._status == PENDING_COMPUTER_MOVE:
            return False
        
        def _send_move_to_other_players(username:str, player_id:int):

            # If the game has players from outside,
            # then we send the move and ask for a move acknowledgement
            # for each player.
            if len(self._players_cuuid) >0:

                # We send the move to all players but us.
                Log.debug(f'Sending the move "{uci_move}/{san_move}"...')

                move_message = {
                    "type":GAME_MOVE,
                    MASTER_CUUID:self._master_cuuid,
                    USERNAME:username,
                    COLOR:color,
                    "san_move":san_move,
                    "uci_move":uci_move,
                    PLAYER_ID:player_id }
                
                # Waiting for acks.
                self._status = PENDING_MOVE_ACK
                self._expected_ack.update(self._players_cuuid, move_message)

        # Your move?
        if self._player_id == current_player[PLAYER_ID]:

            _send_move_to_other_players(LICHESS_USERNAME, self._player_id)

            # Next player to play...
            self._increase_sequence_index()

            return True
        
        # Computer move?
        elif self._is_master and current_player[PLAYER_ID] == CPU and Centaur.computer_move_is_ready():

            _send_move_to_other_players(COMPUTER_NAME, CPU)

            # Next player to play...
            self._increase_sequence_index()

            return True
        
        # External player move?
        elif Centaur.computer_move_is_ready():

            # We send back the move acknowledgement.
            Centaur.send_external_request({
                "type":GAME_MOVE_ACK,
                MASTER_CUUID:self._master_cuuid,
                PLAYER_ID:self._player_id,
                USERNAME:LICHESS_USERNAME,
                "uci_move":uci_move,
                "fen":self.chessboard.fen() }#, target_cuuid=REQUEST_CUUID
            )

            # Next player to play...
            self._increase_sequence_index()

            return True

        return False
    
    # When exists, this function is automatically invoked
    # on socket messages.
    def on_socket_request(self, data:dict):

        # External request?
        if consts.EXTERNAL_REQUEST in data:

            request:dict = data[consts.EXTERNAL_REQUEST]
            request_type:int = request.get("type", None)

            #Log.debug(request)

            # We read the CUUID of the request.
            # Who sent the request?
            REQUEST_CUUID = request.get("cuuid", None)

            # Game running or waiting for move acknowledgement.
            if self._status in (GAME_RUNNING, PENDING_MOVE_ACK):

                # Only move requests are valid during a game.
                if request_type not in (GAME_ABORTED, GAME_MOVE, GAME_MOVE_ACK):
                    return

                # Correct request CUUID?
                if REQUEST_CUUID not in self._players_cuuid:
                    return
                
                # Correct master CUUID?
                if request.get(MASTER_CUUID, None) != self._master_cuuid:
                    return
                
                # A player left the game...
                if request_type == GAME_ABORTED:
                    Centaur.sound(Enums.Sound.COMPUTER_MOVE)
                    Centaur.messagebox((request.get(USERNAME, "Anonymous"),"LEFT THE","GAME!"))
                    return

                # What is the owner of the game move?
                request_player_id:int = request.get(PLAYER_ID, None)

                # The move need contains a player_id.
                if request_player_id == None:
                    return

                # Simple move.
                if request_type == GAME_MOVE:

                    uci_move = request.get("uci_move", None)
                    san_move = request.get("san_move", None)

                    current_player = self._players_sequence[self._sequence_index]

                    # Current player turn?
                    if current_player[PLAYER_ID] == request_player_id:

                        Log.debug(f'Receiving the move "{uci_move}/{san_move}" from "{request[USERNAME]}"...')

                        # We play the move.
                        Centaur.play_computer_move(uci_move)

                        Centaur.messagebox((
                            current_player[USERNAME],
                            "found a move!",
                            None))

                    else:
                        # Move already received.
                        # We send back again the move acknowledgement.

                        # We send back the move acknowledgement.
                        Centaur.send_external_request({
                            "type":GAME_MOVE_ACK,
                            MASTER_CUUID:self._master_cuuid,
                            PLAYER_ID:self._player_id,
                            USERNAME:LICHESS_USERNAME,
                            "uci_move":uci_move,
                            "fen":self.chessboard.fen() }#, target_cuuid=REQUEST_CUUID
                        )

                # Move acknowledgement.
                # Players received your move.
                elif request_type == GAME_MOVE_ACK:

                    uci_move = request.get("uci_move", None)
                    #fen = request.get("fen", None)

                    # Are you waiting for a move acknowledgement?
                    if self._status == PENDING_MOVE_ACK:

                        # Is the move acknowledgement matching with yours?
                        if self._expected_ack.check(uci_move, REQUEST_CUUID):
                            if self._expected_ack.done():
                                self._status = GAME_RUNNING
                        else:
                            Log.info(f'ERROR: Received ACK "{uci_move}" / Expecting "{self._expected_ack}"!')
                    else:
                        Log.info(f'ERROR: Received ACK "{uci_move}" / Expecting none!')

            # Game not started - waiting for players.
            elif self._status in (SLAVE, MASTER):

                # SPECIFIC_GAME_REQUEST == You choose specific game and color.
                # GAME_REQUEST == You don't care about the game and color.

                # Only simple game requests and game acknowledgements are accepted there.
                if self._status == MASTER and request_type not in (GAME_REQUEST, GAME_ACK, GAME_START):
                    return
                
                # Only specific game requests and game acknowledgements are accepted there.
                if self._status == SLAVE and request_type not in (SPECIFIC_GAME_REQUEST, GAME_ACK, GAME_START):
                    return

                # We get the player name.
                PLAYER_NAME:str = request.get(USERNAME, "Anonymous")

                # Did we start a game as master?
                if self._status == MASTER:
                    if request_type in (GAME_ACK, GAME_REQUEST):
                        self._handle_slave_request(PLAYER_NAME, REQUEST_CUUID)

                        return

                # Do we wait for a game?
                if self._status == SLAVE:

                    if not self._master_cuuid and request_type == SPECIFIC_GAME_REQUEST:

                        # We accept the request.
                        Centaur.send_external_request({ "type":GAME_ACK, USERNAME:LICHESS_USERNAME }, target_cuuid=REQUEST_CUUID)

                        self._master_cuuid = REQUEST_CUUID

                        self._screen_found_game_request()

                        return

                    # Correct master CUUID?
                    if self._master_cuuid and self._master_cuuid != REQUEST_CUUID:
                        return

                    # Master response.
                    # We get a color and an index.
                    if request_type == GAME_ACK and PLAYER_DATA in request:

                        self.YOUR_COLOR = request[PLAYER_DATA].get(COLOR, None)

                        if self.YOUR_COLOR == None:
                            # Unable to get the color from the game acknowledgement.
                            # Should never happen.
                            return
                        
                        self._player_id = request[PLAYER_DATA].get(PLAYER_ID, None)

                        if self._player_id == None:
                            # Unable to get the player_id from the game acknowledgement.
                            # Should never happen.
                            return

                        # If you are black, we reverse the screen.
                        if self.YOUR_COLOR == chess.BLACK:
                            Centaur.reverse_board()
                        
                        self._master_cuuid = REQUEST_CUUID

                        self._screen_found_game_request()

                        return
                        
                    if self._master_cuuid and request_type == GAME_START and "players" in request:

                        self._status = GAME_RUNNING
                        self._players_sequence = request.get("players", None)

                        self._init_players_cuuid_from_players_sequence()

                        # We can start the game.
                        self._go()

    def _handle_slave_request(self, player_name:str, request_cuuid:str):

        sequence = self._game_sequence

        Log.debug(f"game sequence={sequence}")

        def _add_player() -> bool:

            index = len(self._players_sequence)

            # If index is even - color is white.
            current_color = (index % 2) == 0

            player_id = sequence[index]

            if index<len(sequence) and player_id == YOU:
                # You.
                self._players_sequence.append({
                    USERNAME:LICHESS_USERNAME,
                    PLAYER_ID:YOU,
                    COLOR:current_color,
                    "cuuid":CUUID,
                })

                return True
            
            if index<len(sequence) and player_id == CPU:
                # Computer.
                self._players_sequence.append({
                    USERNAME:COMPUTER_NAME,
                    PLAYER_ID:CPU,
                    COLOR:current_color,
                    "cuuid":CUUID,
                })
                return True
            
            # Player already connected?
            connected_player = list(filter(lambda p:p[PLAYER_ID] == player_id, self._players_sequence))
            
            if len(connected_player):
                self._players_sequence.append(connected_player[0])
                return True

            if self._player_added:
                return False

            # If request_cuuid is None, means that the function
            # has been invoked only to build the first players of the sequence.
            if request_cuuid is None:
                return False

            # Ready to go?
            if len(self._players_sequence) == len(sequence):
                return False

            # New player.
            p = {
                USERNAME:player_name,
                PLAYER_ID:player_id,
                COLOR:current_color,
                "cuuid":request_cuuid,
            }
            self._players_sequence.append(p)

            # We send back the player data.
            Centaur.send_external_request({ "type":GAME_ACK, PLAYER_DATA:p }, target_cuuid=request_cuuid)

            self._player_added = True

            return True

        self._player_added = False
        
        while _add_player():
            if len(self._players_sequence)==len(sequence):
                break

        del self._player_added

        self._print_connected_players()

        # Ready to go?
        if len(self._players_sequence) == len(sequence):
            # We send the game players to all the players.
            Centaur.send_external_request({ "type":GAME_START, "players":self._players_sequence })

            self._status = GAME_RUNNING

            self._init_players_cuuid_from_players_sequence()

            # We can start the game.
            self._go()

            return

    # When exists, this function is automatically invoked
    # at start, after splash screen, on PLAY button.
    def on_start_callback(self, key:Enums.Btn) -> bool:

        if key in (Enums.Btn.UP, Enums.Btn.DOWN):
            # We choose the game mode.

            if key == Enums.Btn.UP:
                self._game -= 1

            if key == Enums.Btn.DOWN:
                self._game += 1

            if self._game == -2:
                self._game = len(GAME_SEQUENCES) -1

            if self._game == len(GAME_SEQUENCES):
                self._game = WAIT_FOR_REQUEST

            self._print_game_modes()

            return False

        # Game mode has been chosen.
        if key in (Enums.Btn.TICK, Enums.Btn.PLAY):

            if self._game == WAIT_FOR_REQUEST:
                self._screen_any_game_request()

                self._status = SLAVE
                self._is_master = False

                Centaur.send_external_request({ "type":GAME_REQUEST, USERNAME:LICHESS_USERNAME })

                return True
            
            # We launch a new game request.
            self._launch_game_request(GAME_SEQUENCES[self._game]["sequence"])

            return True

        return False

    def _launch_game_request(self, sequence:List[int]):

        self._game_sequence = sequence

        your_color = chess.WHITE

        # We set your color
        for n in sequence:
            if n == YOU:
                break

            your_color = not your_color

        self.YOUR_COLOR = your_color

        Log.info(f"You are {'WHITE' if your_color else 'BLACK'}.")

        # If you are black, we reverse the screen.
        if self.YOUR_COLOR == chess.BLACK:
            Centaur.reverse_board()

        self._screen_specific_game_request()
        
        self._status = MASTER
        self._player_id = YOU
        self._master_cuuid = CUUID
        self._is_master = True

        Centaur.send_external_request({ "type":SPECIFIC_GAME_REQUEST, USERNAME:LICHESS_USERNAME })

    def _go(self):

        # The master handles computer moves.
        if self._is_master:
            Centaur.set_chess_engine("maia")
            Centaur.configure_chess_engine({ \
                "WeightsFile": f"{consts.ENGINES_DIRECTORY}/maia_weights/maia-1500.pb.gz" })

        self._teams = {
            chess.WHITE: list(set(p[1][USERNAME] for p in filter(lambda p:p[0] %2 == 0, enumerate(self._players_sequence)))),
            chess.BLACK: list(set(p[1][USERNAME] for p in filter(lambda p:p[0] %2 == 1, enumerate(self._players_sequence)))),
        }

        Log.debug(f"teams={self._teams}")

        # Start a new game.
        Centaur.start_game(
            white=",".join(self._teams[chess.WHITE]),
            black=",".join(self._teams[chess.BLACK]),
            event="Centaur chess team games event 2024",
            flags=Enums.BoardOption.EVALUATION_DISABLED | Enums.BoardOption.RESUME_DISABLED | Enums.BoardOption.PARTIAL_PGN_DISABLED)

    def _screen_header(self):
        Centaur.clear_screen()

        print("Team Play", font=fonts.PACIFICO_FONT, row=.8)
    
    def _print_connected_players(self):

        Log.debug(f"players_sequence={self._players_sequence}")

        count = len(list(filter(lambda p:p[PLAYER_ID] not in (YOU, CPU), self._players_sequence)))
        total = len(list(filter(lambda id:id not in (YOU, CPU), self._game_sequence)))

        print("Players", row=11)
        print(f"connected:{count}/{total}")

    def _screen_specific_game_request(self):
        self._screen_header()
        print("You just", row=3)
        print("sent")
        print("a new")
        print("game request!")
        print()
        print("Waiting for")
        print("players...")
        
        button(Enums.Btn.BACK, row=13.75, x=6, text="Back home")

    def _screen_found_game_request(self):
        self._screen_header()
        print("A game", row=4)
        print("request")
        print("has been")
        print("found...")
        print()
        print("Waiting for")
        print("players...")

        button(Enums.Btn.BACK, row=13.75, x=6, text="Back home")

    def _screen_any_game_request(self):
        self._screen_header()
        print("You are", row=5)
        print("waiting")
        print("for a game")
        print("request...")

        button(Enums.Btn.BACK, row=13.75, x=6, text="Back home")

    def _print_game_modes(self):

        print("Choose and send", font=fonts.SMALL_MAIN_FONT, row=2.75)
        print("a game request", font=fonts.SMALL_MAIN_FONT, row=3.4)

        option("Accept any request", row=4.4, checked=self._game==-1)
    
        for index, gs in enumerate(GAME_SEQUENCES):
            option(gs["label"], checked=self._game==index, row=5.5+(index*.65))

    # When exists, this function is automatically invoked
    # when the plugin starts.
    def splash_screen(self) -> bool:

        self._screen_header()

        self._print_game_modes()

        button(Enums.Btn.PLAY, row=12.75, x=34, text="GO!")

        button(Enums.Btn.BACK, row=13.75, x=6, text="Back home")

        # The splash screen is activated.
        return True