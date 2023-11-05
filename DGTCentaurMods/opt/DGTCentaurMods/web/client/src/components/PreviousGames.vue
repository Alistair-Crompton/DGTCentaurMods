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
  <div class="bg-base-100 h-full overflow-y-auto">
    <!-- Menu of previous games for user to select -->
    <ul class="menu">
      <li v-for="{ black, created_at, id, result, white } in games">
        <div>
          <button
            @click="removeGame(id)"
            class="btn btn-circle btn-error btn-outline btn-xs"
          >🗑</button>
          <div @click="loadGame(id)">
            <h3 class="font-bold">
              {{ white  }} vs. {{ black }} {{ result }}
            </h3>
            {{ created_at }}
          </div>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { dequeue, emit, inbound } from '../socket'
import { ref } from 'vue'
import { useBoardStore } from '../stores/board'
import { useDisplayStore } from '../stores/display'

type Game = {
  black: string
  created_at: string
  event: string
  id: number
  result: string
  round: string
  site: string
  source: string
  white: string
}

const board = useBoardStore()
const display = useDisplayStore()
const games = ref<Game[]>([])

dequeue(inbound.previous_games, (value: Game[]) => {
  games.value = value
  display.showDrawer = true
})

const loadGame = (id: number) => {
  emit('request', { data: 'game_moves', id })
  board.synchronized = false
  display.showDrawer = false
}

const removeGame = (id: number) => {
  emit('request', { data: 'remove_game', id })
  games.value = games.value.filter((each) => each.id !== id)
}
</script>
