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

from flags import Flags
from enum import Enum

class Sound(Enum):
    GENERAL = 1
    FACTORY = 2
    POWER_OFF = 3
    POWER_ON = 4
    WRONG = 5
    WRONG_MOVE = 6

class Btn(Enum):
    NONE = 0
    BACK = 1
    TICK = 2
    UP = 3
    DOWN = 4
    HELP = 5
    PLAY = 6
    LONGPLAY = 7

class Event(Enum):
    NEW_GAME = 1
    RESUME_GAME = 2,
    PLAY = 3,
    REQUEST_DRAW = 4
    RESIGN_GAME = 5
    QUIT = 6
    TERMINATION = 7

class PieceAction(Enum):
    LIFT = 1
    PLACE = 2

class SquareType(Enum):
    ORIGIN = 1
    TARGET = 2

class BoardOption(Flags):
    CAN_FORCE_MOVES = 1
    CAN_UNDO_MOVES = 2
    DB_RECORD_DISABLED = 4
    CAN_DO_COFFEE = 8