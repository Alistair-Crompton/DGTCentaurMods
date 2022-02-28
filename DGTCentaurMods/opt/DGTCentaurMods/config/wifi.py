# Connect to a Wifi Network
#
# This file is part of the DGTCentaur Mods open source software
# ( https://github.com/EdNekebno/DGTCentaur )
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
# https://github.com/EdNekebno/DGTCentaur/blob/master/LICENSE.md
#
# This and any other notices must remain intact and unaltered in any
# distribution, modification, variant, or derivative of this software.

from DGTCentaurMods.board import board
import os
import time
import sys
import re

board.initScreen()
time.sleep(2)

command = """iwlist wlan0 scan | grep -i 'essid:"' | cut -c28-500"""
result = os.popen(command)
result = list(result)
networks = {}
for i in range(0,len(result)):
	result[i] = result[i].replace("\n","")
	result[i] = result[i].replace("\"","")
	result[i] = result[i].replace("\\x00",".")
	result[i] = result[i].replace("\\\\","\\")
	result[i] = result[i].replace("\\xE2",'\xE2')
	result[i] = result[i].replace("\\x80",'\x80')
	result[i] = result[i].replace("\\x99",'\x99')
	networks[result[i]] = result[i]

print(networks)
answer = board.doMenu(networks,1)

print(answer)

if answer == "BACK":
	sys.exit()

#board.initScreen()
#time.sleep(2)
board.epd.init()

# If the answer is not "BACK" then answer contains our SSID
# Now we n