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
  <div class="relative" :style="`height: ${boardSize}px; max-width: 80vh`">
    <div ref="board" class="absolute left-0 top-0 w-full h-full"></div>
    <ChessboardArrows
      :canvas-size="boardSize"
      class="absolute left-0 top-0 p-0 opacity-70 pointer-events-none"
    />
    <img
      v-if="boardStore.loading"
      class="absolute left-0 top-0 p-0 z-10"
      :height="boardSize"
      :width="boardSize"
      :src="loading"
    />
  </div>
</template>

<script setup lang="ts">
import '@chrisoakman/chessboardjs/dist/chessboard-1.0.0.css'
import '@chrisoakman/chessboardjs/dist/chessboard-1.0.0.js'
import ChessboardArrows from './ChessboardArrows.vue'
import loading from '../assets/images/anya-taylor-joy.gif'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { emit } from '../socket'
import { pieceTheme } from '../pieces'
import { storeToRefs } from 'pinia'
import { useBoardStore } from '../stores/board'
import { useChessboardStore } from '../stores/chessboard'
import { useDisplayStore } from '../stores/display'
import { useHistoryStore } from '../stores/history'

const display = useDisplayStore()
const history = useHistoryStore()

// Long names to avoid conflicts below
const boardStore = useBoardStore()
const chessboardStore = useChessboardStore()

const { boardSize } = storeToRefs(chessboardStore)

const board = ref<HTMLDivElement | null>(null)
let chessboard

const resizeObserver = new ResizeObserver(() => {
  chessboard?.resize()

  const actualBoard = board.value?.querySelector('.board-b72b1')
  const boardBounds = actualBoard?.getBoundingClientRect()
  boardSize.value = boardBounds?.width ?? 0
})

// Keyboard interface
// ------------------

const onKeyDown = (e: KeyboardEvent) => {
  switch (e.code) {
    case 'ArrowLeft':
      history.backward()
      e.preventDefault()
      break
    case 'ArrowRight':
      history.forward()
      e.preventDefault()
      break
  }
}

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeyDown)
  if (board.value) {
    resizeObserver.unobserve(board.value)
  }
})

onMounted(() => {
  document.addEventListener('keydown', onKeyDown)
  if (board.value) {
    resizeObserver.observe(board.value)
  }
})

// Mouse interface
// ---------------

const onDragStart = () => display.settings.activeBoard

const onDrop = (source: string, target: string) => {
  boardStore.synchronized = false
  emit('request', { web_move: { source, target } })
  return true
}

const onSnapEnd = () => 'snapback'

// Chessboardjs initialization
// ---------------------------

onMounted(() => {
  const Chessboard = window['Chessboard']
  chessboard = Chessboard(board.value, {
    onDragStart,
    onDrop,
    onSnapEnd,
    pieceTheme,
    showNotation: true
  })

  watch(
    () => display.settings.activeBoard,
    (active) => {
      chessboard.draggable = active
      chessboard.resize()
    },
    { immediate: true })

  watch(
    () => display.settings.reversedBoard,
    (reversed) => {
      chessboard.orientation(reversed ? 'black' : 'white')
      chessboard.resize()
    },
    { immediate: true })

  watch(
    () => history.current_fen,
    (newFen) => {
      if (newFen) {
        chessboard.position(newFen)
      }
    },
    { immediate: true })
})
</script>

<style>
.black-3c85d {
  background-color: #b2b2b2;
  color: #131313;
}
.white-1e1d7 {
  background-color: #e5e5e5;
  color: #131313;
}
</style>
