<!--
This file is part of the DGTCentaur Mods open source software
( https://github.com/Alistair-Crompton/DGTCentaurMods )

DGTCentaur Mods is free software: you can redistribute
it and/or modify it under the terms of the GNU General Public
License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.

DGTCentaur Mods is distributed in the hope that it will
be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this file.  If not, see

https://github.com/Alistair-Crompton/DGTCentaurMods/blob/master/LICENSE.md

This and any other notices must remain intact and unaltered in any
distribution, modification, variant, or derivative of this software.
-->

<template>
  <div class="flex items-stretch" :style="`max-height: ${maxHeight}px`">
    <BoardPanel class="flex-auto" />
    <PgnPanel class="flex-initial" />
    <CentaurScreen class="flex-none" />
    <ChatPanel class="flex-initial" />
  </div>
</template>

<script setup lang="ts">
import BoardPanel from './BoardPanel.vue'
import CentaurScreen from './CentaurScreen.vue'
import ChatPanel from './ChatPanel.vue'
import PgnPanel from './PgnPanel.vue'
import { computed } from 'vue'
import { useChessboardStore } from '../stores/chessboard'

// Space to comfortably display centaur screen and buttons.  Can hardcode (for
// now) because screen on centaur is fixed.
const centaurHeight = 450

const chessboard = useChessboardStore()
const maxHeight = computed(() => Math.max(centaurHeight, chessboard.boardSize * 1.15))
</script>
