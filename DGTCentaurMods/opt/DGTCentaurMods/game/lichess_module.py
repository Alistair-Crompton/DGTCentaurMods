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

from DGTCentaurMods.game.classes import Log, GameFactory, CentaurScreen, CentaurBoard
from DGTCentaurMods.game.classes.CentaurConfig import CentaurConfig
from DGTCentaurMods.game.consts import Enums, fonts

import time, chess, berserk, threading, datetime

exit_requested = False
stream_game_state = None
stream_incoming_events = None

SCREEN = CentaurScreen.get()
CENTAUR_BOARD = CentaurBoard.get()

_YOUR_LAST_BOARD_MOVE = "your_last_board_move"
_USERNAME = "username"
_OPPONENT = "opponent"
_PERFS = "perfs"
_ID = "id"
_COLOR = "color"

def main():

    global exit_requested
    global stream_game_state

    exit_requested = False

    class Criteria():

        def __init__(self, id, caption, format, value, values):
            self.row = 0
            self.id = id
            self.caption = caption
            self.format = format
            self.value = value
            self.values = values

    class SeekingEngine():

        _current_index = 0
        _seeking_worker = None

        def __init__(self):

            stored_criterias = CentaurConfig.get_lichess_seeking_params()

            if len(stored_criterias) != 6:
                stored_criterias = ("random","casual",200,200,10,0)

            self._params = (
                Criteria(_COLOR, "Select color", "{0}", stored_criterias[0], ("random", "white", "black")),
                Criteria("mode", "Select mode", "{0}", stored_criterias[1], ("rated", "casual")),
                Criteria("range_low", "Low relative range", "-{0}", stored_criterias[2], (100,200,300,400,500,600,700,800)),
                Criteria("range_high", "High relative range", "+{0}", stored_criterias[3], (100,200,300,400,500,600,700,800)),
                Criteria("clock", "Select clock", "{0} minutes", stored_criterias[4], (3,5,10,15,20,30,45,60)),
                Criteria("increment", "Select increment", "+{0} seconds", stored_criterias[5], (0,1,2,5,10,30)),
            )

        def current(self):
            return self._params[self._current_index]

        def next_value(self):

            current_index = self.current().values.index(self.current().value)

            current_index += 1
            if current_index == len(self.current().values):
                current_index = 0

            self.current().value = self.current().values[current_index]

            W(self.current().row+1, self.current().format.format(self.current().value), option=True)

            return self.current().value

        def next(self):

            W(self.current().row+1, self.current().format.format(self.current().value), option=False)

            self._current_index += 1
            if self._current_index == len(self._params):
                self._current_index = 0

            W(self.current().row+1, self.current().format.format(self.current().value), option=True)

            return self.current()

        def previous(self):

            W(self.current().row+1, self.current().format.format(self.current().value), option=False)

            self._current_index -= 1
            if self._current_index == -1:
                self._current_index = len(self._params)-1

            W(self.current().row+1, self.current().format.format(self.current().value), option=True)

            return self.current()

        def print_all(self, starting_row = 3):

            row = starting_row

            for p in self._params:

                p.row = row

                W(row, p.caption, bordered=True)
                W(row+1, p.format.format(p.value), option=self.current() == p)

                row += 2

        def get_all(self):

            values = []

            for p in self._params:
                values.append(p.value)

            return values
        
        def stop(self):
            if self._seeking_worker != None:
                self._seeking_worker.join()
        
        def start(self):
            def seeking_thread():

                criterias = self.get_all()

                # To calculate the time class, LiChess uses the following algorithm:
                # Take the increment and multiply it by 40
                # Then add the initial time on the clock
                # If this total is 25 minutes or more, it's considered Classical
                # 25:00 - 5:00:00 is Classical
                # 8:00 - 24:59 is Rapid
                # 3:00 - 7:59 is Blitz
                # 0:30 - 2:59 is Bullet
                total_time = (criterias[5] * 40) + (criterias[4] * 60)

                cadence = "bullet"
                if total_time>=(3 * 60):
                    cadence = "blitz"
                if total_time>=(8 * 60):
                    cadence = "rapid"
                if total_time>=(25 * 60):
                    cadence = "classical"

                your_rating = current_game[_PERFS][cadence]["rating"]

                rating_range = f"{your_rating-criterias[2]}-{your_rating+criterias[3]}"

                Log.info(f"Seeking Lichess {cadence} game - [{rating_range}]")

                lichess_client.board.seek(
                    criterias[4], #time
                    criterias[5], #increment
                    rated = criterias[1] == "rated", 
                    variant = 'standard', 
                    color = criterias[0], 
                    rating_range=rating_range)


            self.stop()

            self._seeking_worker = threading.Thread(target=seeking_thread)
            self._seeking_worker.daemon = True
            self._seeking_worker.start()

    seeking_engine = SeekingEngine()

    W = SCREEN.write_text

    def _missing_token_screen():
        SCREEN.clear_area()
        W(2, "Please set")
        W(3, "a valid token")
        W(4, "using the web")
        W(5, "interface or")
        W(6, "editing the")
        W(7, '"centaur.ini"')
        W(8, "config file!")

    def _incorrect_token_screen():
        SCREEN.clear_area()
        W(2, "SORRY :(")
        W(3, "")
        W(4, "Unable to")
        W(5, "connect to")
        W(6, "Lichess using")
        W(7, "your token!")
    
    def _welcome_screen():
        SCREEN.clear_area()
        W(2, "WELCOME")
        W(3, f"{current_game['username'] }!")
        W(4, "")
        W(5, "Please create")
        W(6, "a game from")
        W(7, "the Lichess")
        W(8, "web interface,")
        W(9, "")
        W(10, "or press")
        W(11, "PLAY")
        W(12, "to seek")
        W(13, 'a player!')

        CENTAUR_BOARD.led_array([27,28,36,35])

    def _seeking_screen():
        SCREEN.clear_area()
        W(2, "WELCOME")
        W(3, f"{current_game['username'] }!")
        W(4, "")
        W(5, "Seeking a")
        W(6, "player that")
        W(7, "matches your")
        W(8, "criterias...")

        CENTAUR_BOARD.led_array([27,28,36,35])

    def _criterias_screen():
        SCREEN.clear_area()
        W(1, "Fill criterias")
        W(2, "then press PLAY!")

        seeking_engine.print_all(3)

    def _key_callback(key_index):
        global exit_requested
        global stream_incoming_events

        if key_index == Enums.Btn.PLAY or key_index == Enums.Btn.TICK:

            seeking_engine.stop()
            CENTAUR_BOARD.leds_off()
            _criterias_screen()

            def _seeking_key_callback(key_index):

                if key_index == Enums.Btn.BACK:

                    seeking_engine.stop()

                    CENTAUR_BOARD.unsubscribe_events()
                    _welcome_screen()

                if key_index == Enums.Btn.PLAY:
                    CENTAUR_BOARD.unsubscribe_events()
                    _seeking_screen()
                    CentaurConfig.update_lichess_seeking_params(seeking_engine.get_all())
                    seeking_engine.start()

                if key_index == Enums.Btn.UP:
                    seeking_engine.previous()

                if key_index == Enums.Btn.DOWN:
                    seeking_engine.next()

                if key_index == Enums.Btn.TICK:
                    seeking_engine.next_value()

            CENTAUR_BOARD.subscribe_events(_seeking_key_callback, None)


        if key_index == Enums.Btn.BACK:

            seeking_engine.stop()

            CENTAUR_BOARD.leds_off()
            CENTAUR_BOARD.unsubscribe_events()

            exit_requested = True
            del stream_incoming_events

    CENTAUR_BOARD.subscribe_events(_key_callback, None)

    current_game = {
        _USERNAME:None,
        _OPPONENT: None,
        _PERFS:None,
        _YOUR_LAST_BOARD_MOVE:None,
        _ID:None,
        _COLOR:None,
    }

    lichess_token = CentaurConfig.get_lichess_settings("token")

    if lichess_token == None or len(lichess_token) == 0:

        _missing_token_screen()
        lichess_token = None

    if lichess_token != None:

        lichess_session = berserk.TokenSession(lichess_token)
        lichess_client = berserk.Client(lichess_session)

        Log.info(f"Lichess token:'{lichess_token}'")

        try:

            lichess_profile = lichess_client.account.get()
            
            # We get the PERFS to compute a correct ELO range
            # from the creation page
            current_game[_PERFS] = lichess_profile[_PERFS]
            current_game[_USERNAME] = lichess_profile[_USERNAME]

        except Exception as e:

            Log.exception(main, e)

            _incorrect_token_screen()
            lichess_token = None

            pass

        if lichess_token != None:

            _welcome_screen()

            stream_incoming_events = lichess_client.board.stream_incoming_events()

            # Waiting for new standard game created from Lichess UI
            while True:
                """
                {
                    "type": "challenge",
                    "challenge": {
                        _ID: "GAME_ID",
                        "url": "https://lichess.org/GAME_ID",
                        "status": "created",
                        "challenger": {
                            _ID: "jack_bauer",
                            "name": "Jack_Bauer",
                            "title": None,
                            "rating": 1498,
                            "online": True,
                            "lag": 4,
                        },
                        "destUser": {
                            _ID: "maia1",
                            "name": "maia1",
                            "title": "BOT",
                            "rating": 1493,
                            "online": True,
                        },
                        "variant": {"key": "standard", "name": "Standard", "short": "Std"},
                        "rated": False,
                        "speed": "rapid",
                        "timeControl": {"type": "clock", "limit": 600, "increment": 5, "show": "10+5"},
                        _COLOR: "white",
                        "finalColor": "white",
                        "perf": {"icon": "\ue017", "name": "Rapid"},
                    },
                    "compat": {"bot": False, "board": True},
                }
                {
                    "type": "gameStart",
                    "game": {
                        "fullId": "GAME_ID_EX",
                        "gameId": "GAME_ID",
                        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                        _COLOR: "white",
                        "lastMove": "",
                        "source": "friend",
                        "status": {_ID: 20, "name": "started"},
                        "variant": {"key": "standard", "name": "Standard"},
                        "speed": "rapid",
                        "perf": "rapid",
                        "rated": False,
                        "hasMoved": False,
                        _OPPONENT: {_ID: "maia1", _USERNAME: "BOT maia1", "rating": 1493},
                        "isMyTurn": True,
                        "secondsLeft": 600,
                        "compat": {"bot": False, "board": True},
                        _ID: "GAME_ID",
                    },
                }

                """

                time.sleep(.5)

                try:
                    event = stream_incoming_events.next()
                except:
                    event = None
                    pass

                if exit_requested:
                    break

                def _set_game_data(id, color, opponent):
                    current_game[_ID]  = id
                    current_game[_COLOR]  = chess.WHITE if color == "white" else chess.BLACK 
                    current_game[_OPPONENT] = opponent

                if event and 'type' in event.keys():
                    if event.get('type') == "gameStart":
                        if 'game' in event.keys():

                            game_node = event.get('game')

                            if 'variant' in game_node.keys() and game_node.get('variant').get('key') == "standard":
                                _set_game_data(
                                    game_node.get('id'),
                                    game_node.get('color'),
                                    game_node.get('opponent').get('username'))

                                break
                
                if event == None:

                    """
                    [{
                        'fullId': 'GAME_ID_FULL', 
                        'gameId': 'GAME_ID', 
                        'fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1', 
                        'color': 'white', 
                        'lastMove': '', 
                        'source': 'lobby', 
                        'status': {'id': 20, 'name': 'started'}, 
                        'variant': {'key': 'standard', 'name': 'Standard'}, 
                        'speed': 'rapid',
                        'perf': 'rapid',
                        'rated': False,
                        'hasMoved': False, 
                        'opponent': {'id': 'jack_bauer', 'username': 'Jack_Bauer', 'rating': 1521},
                        'isMyTurn': True,
                        'secondsLeft': 600}]
                    """

                    ongoing_games = lichess_client.games.get_ongoing(1)
                    if len(ongoing_games) >0:

                        _set_game_data(
                            ongoing_games[0].get('gameId'),
                            ongoing_games[0].get('color'),
                            ongoing_games[0].get('opponent').get('username'))
                        break

            def key_callback(args):

                assert "key" in args, "key_callback args needs to contain the 'key' entry!"

                key = args["key"]

                # Nothing to do there - we keep the Factory default keys...
                # Key has not been handled, Factory will handle it!
                return False


            def event_callback(args):

                assert "event" in args, "event_callback args needs to contain the 'event' entry!"

                global exit_requested
                global stream_game_state

                if args["event"] == Enums.Event.QUIT:

                    SCREEN.enable_clocks(False)

                    exit_requested = True
                    del stream_game_state

                if args["event"] == Enums.Event.PLAY:

                    SCREEN.push_clock(gfe.get_board().turn)

                    current_player = current_game[_USERNAME] if gfe.get_board().turn == current_game[_COLOR] else current_game[_OPPONENT]

                    gfe.display_board_header(f"{current_player} {'W' if gfe.get_board().turn == chess.WHITE else 'B'}")

                    gfe.send_to_web_clients({ 
                        "turn_caption":f"turn → {current_player} ({'WHITE' if gfe.get_board().turn == chess.WHITE else 'BLACK'})"
                    })

            
            def move_callback(args):

                # field_index, san_move, uci_move are available
                assert "uci_move" in args, "args needs to contain 'uci_move' key!"
                assert "san_move" in args, "args needs to contain 'san_move' key!"
                assert "color" in args, "args needs to contain 'color' key!"
                assert "field_index" in args, "args needs to contain 'field_index' key!"

                current_game[_YOUR_LAST_BOARD_MOVE] = None

                # Your turn?
                if args[_COLOR] == current_game[_COLOR]:
                    
                    Log.info(f'Sending move of "{current_game[_USERNAME]}".')

                    current_game[_YOUR_LAST_BOARD_MOVE] = args["uci_move"]
                    
                    lichess_client.board.make_move(current_game[_ID], args["uci_move"])

                    return True

                # Lichess opponent move is accepted
                # only if we received a move from Lichess

                # From GameFactory perspective,
                # Computer move == Lichess opponent move
                return gfe.computer_move_available()

            # Subscribe to the game factory
            gfe = GameFactory.Engine(
                
                event_callback = event_callback,
                move_callback = move_callback,
                key_callback = key_callback,

                flags = Enums.BoardOption.EVALUATION_DISABLED | Enums.BoardOption.DB_RECORD_DISABLED | Enums.BoardOption.PARTIAL_PGN_DISABLED,

                game_informations = {
                    "event" : "Lichess",
                    "site"  : "",
                    "round" : "",
                    "white" : current_game[_OPPONENT] if current_game[_COLOR] == chess.BLACK else current_game[_USERNAME] ,
                    "black" : current_game[_OPPONENT] if current_game[_COLOR] == chess.WHITE else current_game[_USERNAME] ,
                })
            
            # If you are black, we reverse the screen
            SCREEN.set_reversed(not current_game[_COLOR])

            SCREEN.enable_clocks(True)

            # Game stream
            stream_game_state = lichess_client.board.stream_game_state(current_game[_ID])
            
            # The game starts or is being resumed
            while True:

                try:
                    state = next(stream_game_state)
                except:
                    state = None
                    pass

                if exit_requested:
                    break

                if state:
                    #print(state)
                    """
                    {
                        "type": "gameState",
                        "moves": "e2e4",
                        "wtime": datetime.datetime(1970, 1, 1, 0, 10, tzinfo=datetime.timezone.utc),
                        "btime": datetime.datetime(1970, 1, 1, 0, 10, tzinfo=datetime.timezone.utc),
                        "winc": datetime.datetime(1970, 1, 1, 0, 0, 5, tzinfo=datetime.timezone.utc),
                        "binc": datetime.datetime(1970, 1, 1, 0, 0, 5, tzinfo=datetime.timezone.utc),
                        "status": "started",
                    }
                    {
                        "type": "chatLine",
                        "room": "player",
                        _USERNAME: "maia1",
                        "text": "Hi Jack Bauer, I'm currently taking my time like a human. If you type 'go' or 'fast' in the chat I'll play faster. gl hf",
                    }
                    {
                        "type": "gameState",
                        "moves": "e2e4 e7e5 b1c3 g8f6 f2f4 e5f4 e4e5 f6g8 g1f3 d7d6 d2d4 d6e5 f3e5 f8d6 c1f4 d6e5 f4e5 f7f6 e5g3 d8e7 d1e2 e7e2 f1e2 b8c6 e1c1 g8e7 h1e1 e8g8 e2c4 g8h8 g3c7 c8g4 d1d2 a8c8 c7d6 f8e8 d4d5 c6a5 c4b5 e8d8 d6e7 d8e8 b5e8 c8e8 d5d6 a5c4 d2d4 c4e5 h2h3 g4h5 e1e5 f6e5 d4d5 h5f7 d5e5 h7h6 e5f5 f7e6 f5f8 e8f8 e7f8 h8g8 f8e7 g8f7 a2a3 f7e8 b2b4 e8d7 c1d2 g7g5 d2e3 h6h5 c3a4 g5g4 a4c5 d7c6 c5e6 g4h3 g2h3 h5h4 c2c4 c6d7 e6c5 d7c6 d6d7 c6c7 d7d8q c7c6 d8d7 c6b6 d7b7",
                        "wtime": datetime.datetime(
                            1970, 1, 1, 0, 5, 17, 950000, tzinfo=datetime.timezone.utc
                        ),
                        "btime": datetime.datetime(
                            1970, 1, 1, 0, 9, 8, 370000, tzinfo=datetime.timezone.utc
                        ),
                        "winc": datetime.datetime(1970, 1, 1, 0, 0, 5, tzinfo=datetime.timezone.utc),
                        "binc": datetime.datetime(1970, 1, 1, 0, 0, 5, tzinfo=datetime.timezone.utc),
                        "status": "mate",
                        "winner": "white",
                    }
                    """

                    # Clocks initialization then synchronization
                    if 'wtime' in state.keys():
                        SCREEN.intialize_clocks(state.get('wtime'), None)

                    if 'btime' in state.keys():
                        SCREEN.intialize_clocks(None, state.get('btime'))
                    
                    if gfe.is_started() == False:

                        seeking_engine.stop()

                        CENTAUR_BOARD.leds_off()

                        if 'state' in state.keys():

                            # Game is being resumed...
                            uci_moves = state.get('state').get('moves').split()

                            gfe.start(uci_moves)


                    if 'wdraw' in state.keys() or 'bdraw' in state.keys():
                        # TODO handle draw proposal
                        lichess_client.board.decline_draw(current_game[_ID])
                        pass

                    else:
                        if 'type' in state.keys() and state.get('type') == "gameState" and 'moves' in state.keys():
                            
                            # We take the last move of the list
                            uci_move = state.get('moves').split()[-1]

                            if uci_move == current_game[_YOUR_LAST_BOARD_MOVE]:
                                Log.info(f'Last board move "{uci_move}" validated by Lichess.')

                            else:
                                SCREEN.push_clock(not gfe.get_board().turn)

                                Log.info(f'Player "{current_game[_OPPONENT]}" played "{uci_move}".')

                                gfe.set_computer_move(uci_move)

                            if 'status' in state.keys() and state.get('status') != "started":
                                # Might be mate...

                                SCREEN.stop_clocks()

                                gfe.update_evaluation(force=True, text=state.get('status'))
                                pass

    while exit_requested == False:
        time.sleep(0.1)

    SCREEN.enable_clocks(False)

if __name__ == '__main__':
    main()