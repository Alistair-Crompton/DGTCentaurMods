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

import { Chess, Move } from 'chess.js'
import { computed, shallowRef } from 'vue'
import { defineStore } from 'pinia'
import { dequeue, inbound } from '../socket'
import { useChessboardStore } from './chessboard'

export const useHistoryStore = defineStore('history', () => {
  const chessboard = useChessboardStore()

  const chess = new Chess()
  const fens = shallowRef<string[]>([])
  const history = shallowRef<Move[]>([])
  const index = shallowRef(0)
  const pgn = shallowRef('')

  const pgnlist = computed(() => {
    return pgn.value.split('\n').map((row, i) => {
      const items = row.split(' ')
      return {
        move: i,
        wsan: items[1],
        bsan: items[2] ?? ''
      }
    })
  })

  const go = (position) => {
    // Support e.g., go(-1) to go to last move
    const newIndex = position < 0 ? fens.value.length + position : position
    index.value = Math.max(0, Math.min(fens.value.length - 1, newIndex))

    // Uncomment for an easy way to test drawing code
    // chessboard.moveHighlight = { uci_move: history.value[index.value]?.lan }
  }

  const current_fen = computed<string>({
    get: () => fens.value[index.value],
    set: (value) => {
      fens.value = [value]
      go(0)
    }
  })

  const backward = () => {
    if (index.value > 0) {
      go(index.value - 1)
    }
  }
  const forward  = () => go(index.value + 1)

  const initFromPGN = (newPgn) => {
    chess.loadPgn(newPgn)
    pgn.value = newPgn
    history.value = chess.history({ verbose: true })
    fens.value = history.value.map(({ after }) => after)
    go(-1)
  }

  const initFromMoves = (uciMoves) => {
    chess.reset()
    uciMoves.forEach((move) => {
      if (move) {
        chess.move(move)
      }
    })
    const pgn = chess.pgn({ maxWidth: 5, newline: '\n' })
    initFromPGN(pgn)
  }

  dequeue(inbound.game_moves, (moves) => {
    chessboard.moveHighlight = { }
    initFromMoves(moves)
  })

  return {
    backward,
    current_fen,
    forward,
    go,
    index,
    initFromPGN,
    pgn,
    pgnlist
  }
})
