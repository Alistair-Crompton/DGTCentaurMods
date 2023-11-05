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
import { ref } from 'vue'
import { dequeue, emit, inbound } from '../socket'

const COLORS = [
  'black',
  'red',
  'blue',
  'green',
  'orange',
  'darkmagenta',
  'hotpink',
  'brown',
  'chocolate',
  'darkblue',
  'darkgreen',
]

export const useChatStore = defineStore('chat', () => {
  const items = ref<any[]>([])
  const colors = new Map()

  let current_colors: string[] = []
  let username = ''
  // let uuid = null

  const submit = (message) => {
    message = message.trim()
    if (message) {
      emit('web_message', {
        chat_message: {
          author: username || 'Anonymous',
          message: message
        }
      })
    }
  }

  dequeue(inbound.chat_message, (value) => {
    if (!value.cuuid) {
      return
    }

    if (current_colors.length == 0) {
      current_colors = [...COLORS]
    }

    value.color = colors[value.cuuid] || current_colors.pop()
    colors.set(value.cuuid, value.color)

    value.ts = new Date().toLocaleTimeString()

    while (items.value.length > 13) {
      items.value.shift()
    }

    items.value.push(value)
  })

  dequeue(inbound.cuuid, () => {
    // uuid = value
  })

  dequeue(inbound.username, (value) => {
    username = value
  })

  return {
    items,
    submit
  }
})
