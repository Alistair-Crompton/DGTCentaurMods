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

import { Socket, io } from 'socket.io-client'
import { reactive, ref, toRaw, watch } from 'vue'

export const inbound = reactive({
  centaur_screen: [],
  chat_message: [],
  checkers: [],
  clear_board_graphic_moves: [],
  computer_uci_move: [],
  cuuid: [],
  disable_menu: [],
  editor: [],
  enable_menu: [],
  evaluation_disabled: [],
  fen: [],
  game_moves: [],
  loading_screen: [],
  log_events: [],
  pgn: [],
  ping: [],
  plugin: [],
  popup: [],
  previous_games: [],
  release: [],
  script_output: [],
  sounds_settings: [],
  tip_uci_move: [],
  tip_uci_moves: [],
  turn_caption: [],
  uci_move: [],
  uci_undo_move: [],
  update_menu: [],
  username: []
})

const createUUID = () => {
  let dt = new Date().getTime()
  const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
    const r = (dt + Math.random()*16)%16 | 0
    dt = Math.floor(dt/16)
    return (c=='x' ? r :(r&0x3|0x8)).toString(16)
  })
  return uuid
}

export const connected = ref(false)
export const url = ref('')
const uuid = createUUID()

let socket: Socket | null = null

const initFromLocalStorage = () => {
  const data = localStorage.getItem('socket')
  if (data) {
    url.value = data
  }
}
initFromLocalStorage()

export const dequeue = (queue, fn) => {
  watch(queue, () => {
    const value = queue.shift()
    if (value !== undefined) {
      fn(value)
    }
  })
}

export const emit = (id, message) => {
  if (!socket) {
    return
  }

  const packet = toRaw({ ...message, uuid })
  console.log('>>>', packet)
  socket.emit(id, packet)
}

dequeue(inbound.ping, () => emit('request', { pong: true }))

dequeue(inbound.script_output, (value) => {
  const data = new Blob([value], { type: 'text/plain' })
  const url = window.URL.createObjectURL(data)
  window.open(url)
  window.URL.revokeObjectURL(url)
})

const onConnect = () => {
  connected.value = true
  localStorage.setItem('socket', url.value)
  emit('request', {
    fen: true,
    pgn: true,
    uci_move: true,
    web_menu: true
  })
}

const onDisconnect = () => {
  connected.value = false
  socket?.connect()
}

const onWebMessage = (message) => {
  if (message.uuid && message.uuid != uuid) {
    return
  }

  for (const key in inbound) {
    const value = message[key]
    if (value !== undefined) {
      console.log('<<<', key, structuredClone(value))
      if (key === 'checkers') {
        // Special case, needs access to more data from message
        (inbound[key] as any[]).push([value, message])
      } else {
        inbound[key].push(value)
      }
    }
  }
}

const disconnect = () => {
  if (!socket) {
    return
  }
  socket.off('connect', onConnect)
  socket.off('disconnect', onDisconnect)
  socket.off('web_message', onWebMessage)
  socket.disconnect()
  socket = null
}

const connect = () => {
  disconnect()
  if (url.value) {
    socket = io(url.value, { reconnection: false })
  } else {
    socket = io()
  }
  socket.on('connect', onConnect)
  socket.on('disconnect', onDisconnect)
  socket.on('web_message', onWebMessage)
}

watch(url, connect, { immediate: true })
