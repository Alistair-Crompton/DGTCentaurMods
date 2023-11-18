// This file is part of the DGTCentaur Mods open source software
// ( https://github.com/Alistair-Crompton/DGTCentaurMods )
//
// DGTCentaur Mods is free software: you can redistribute
// it and/or modify it under the terms of the GNU General Public
// License as published by the Free Software Foundation, either
// version 3 of the License, or (at your option) any later version.
//
// DGTCentaur Mods is distributed in the hope that it will
// be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
// of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this file.  If not, see
//
// https://github.com/Alistair-Crompton/DGTCentaurMods/blob/master/LICENSE.md
//
// This and any other notices must remain intact and unaltered in any
// distribution, modification, variant, or derivative of this software.

import { defineStore } from 'pinia'
import { dequeue, inbound } from '../socket'
import { nextTick, ref } from 'vue'
import { useDisplayStore } from './display'
import { useHistoryStore } from './history'

// Used to score current position
const stockfish = new Worker('/stockfish/stockfish.js')

// Current state of the "board" (i.e., game)
export const useBoardStore = defineStore('board', () => {
  const display = useDisplayStore()

  // Move history is part of the game state
  const history = useHistoryStore()

  const evaluation = ref(50)
  const loading = ref(false)
  const plugin = ref(null)
  const synchronized = ref(true)
  const turn = ref(1)
  const turnCaption = ref('--')

  let lasteval: number = 0
  stockfish.onmessage = (event) => nextTick(() => {
    if (!event.data) {
      return
    }

    // Stockfish evaluation finishes with the bestmove message
    if (event.data.includes('bestmove')) {
      evaluation.value = 50 + lasteval
    }

    // Stockfish evaluation feedback
    if (event.data.includes('score cp')) {
      // info depth 1 seldepth 1 multipv 1 score cp -537 nodes
      const regexp = /score\ cp\ ([^ ]+)\ /gi
      const matches = regexp.exec(event.data)

      const MAX_VALUE = 1500
      if (matches?.length) {
        let value = parseInt(matches[1])

        // black plays?
        if (turn.value === 0) {
          value = -value
        }
        value = Math.max(-MAX_VALUE, Math.min(MAX_VALUE, value))
        lasteval = value / (MAX_VALUE * 2) * 100
      }
    }

    // Stockfish detected (future) mat state
    if (event.data.includes('score mate')) {
      let value = 50

      // black plays?
      if (turn.value == 0) {
        value = -value
      }
      lasteval = value
      evaluation.value = 50+value
    }
  })

  dequeue(inbound.loading_screen, (value) => {
    loading.value = value
  })

  dequeue(inbound.plugin, (value) => {
    plugin.value = value
  })

  dequeue(inbound.fen, (value: string) => {
    if (!synchronized.value || history.current_fen !== value) {
      synchronized.value = true

      // We determinate from the FEN which color plays
      turn.value = value.includes(' w ') ? 1 : 0
      turnCaption.value = `turn → ${turn.value ? 'white' : 'black'}`

      history.current_fen = value

      // We trigger the evaluation on new FEN only
      if (display.settings.liveEvaluation) {
        stockfish.postMessage(`position fen ${value}`)
        stockfish.postMessage('go depth 12')
      }
    }
  })

  dequeue(inbound.pgn, (newPgn) => {
    loading.value = false
    history.initFromPGN(newPgn)
  })

  dequeue(inbound.turn_caption, (value) => {
    turnCaption.value = value
    loading.value = false
  })

  return {
    evaluation,
    loading,
    plugin,
    synchronized,
    turn,
    turnCaption
  }
})
