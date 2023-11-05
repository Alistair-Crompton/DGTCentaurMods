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
import { dequeue, emit, inbound } from '../socket'
import { ref, watchEffect } from 'vue'
import { useBoardStore } from './board'
import { useDisplayStore } from './display'
import { useEditorStore } from './editor'
import { useHistoryStore } from './history'

export const useMenuStore = defineStore('menu', () => {
  // Menus unfortunately touch a lot of things...
  const board = useBoardStore()
  const display = useDisplayStore()
  const editor = useEditorStore()
  const history = useHistoryStore()

  // For display in menubar
  const menuItems = ref<any[]>([])

  const mapMenuItems = (fn, items: any[] | undefined = undefined) => {
    if (items === undefined) {
      menuItems.value = mapMenuItems(fn, menuItems.value)
      return menuItems.value
    }
    return items.map((item) => {
      if (item.items) {
        item = { ...item, items: mapMenuItems(fn, item.items) }
      }
      return fn(item)
    })
  }

  const disableMenuItem = (pred, disabled) => {
    mapMenuItems((item) => {
      if (pred(item)) {
        return { ...item, disabled }
      }
      return item
    })
  }
  const enableMenuItem = (pred, enabled) => disableMenuItem(pred, !enabled)

  watchEffect(() => {
    enableMenuItem((it) => it.label === 'View current PGN', !!history.pgn)
  })

  dequeue(inbound.disable_menu, (value) => disableMenuItem((it) => it.id === value, true))
  dequeue(inbound.enable_menu, (value) => enableMenuItem((it) => it.id === value, true))

  // ---------------------------------------------------------------------------
  // BEGIN Exported to JS

  // Provides "me.board" interface expected by JS menu items
  class BoardProxy {
    get plugin() {
      return board.plugin
    }
  }

  // Provides "me.editor" interface expected by JS menu items
  class EditorProxy {
    set value({ can_execute, file, id, text }) {
      editor.canDelete = false
      editor.canExecute = can_execute
      editor.editableName = false
      editor.extension = ''
      editor.file = file
      editor.id = id
      editor.newFile = ''
      editor.text = text
    }

    set visible(value) {
      display.showEditor = value
    }
  }

  class MainController {
    get board() {
      return new BoardProxy()
    }

    get current_fen() {
      return history.current_fen
    }

    get editor() {
      return new EditorProxy()
    }

    viewCurrentPGN() {
      if (history.pgn) {
        display.dialogs = { viewPgn: history.pgn }
      }
    }
  }

  window['SOCKET'] = { emit, }
  window['$store'] = {
    get(key) {
      return localStorage.getItem(key)
    }
  }
  window['me'] = new MainController()

  // END Exported to JS
  // ---------------------------------------------------------------------------

  const menuInitializers = {
    js(item, value) {
      try {
        item.action = eval?.(value)
      } catch (_) {
        console.error('ERROR while building JS item!')
        console.error(item)
      }
    },

    js_variable(item, value) {
      if (value === 'displaySettings') {
        item.action = () => display.showWebSettings()
      } else {
        console.error('ERROR while building JS_VARIABLE item!')
        console.error(item)
      }
    },

    socket_data(item, data) {
      item.action = () => emit('request', { data })
    },

    socket_execute(item, value) {
      if (item.action?.dialogbox) {
        const id = item.action.dialogbox
        item.action = () => {
          display.dialogs = { [id]: value }
        }
      } else {
        item.action = () => emit('request', { execute: value })
      }
    },

    socket_plugin(item, plugin_execute) {
      item.action = () => emit('request', { plugin_execute })
    },

    socket_read(item, read) {
      item.action = () => emit('request', { read })
    },

    socket_sys(item, sys) {
      const message = item.action?.message
      item.action = () => {
        emit('request', { sys })
        if (message) {
          display.showAlert(message)
        }
      }
    },

    socket_write(item, write) {
      item.action = () => emit('request', { write })
    }
  }

  const initializeMenu = (item) => {
    if (item.action?.type) {
      const initializer = menuInitializers[item.action.type]
      if (initializer) {
        initializer(item, item.action.value)
      }
    }
    if (item.items) {
      item.items = item.items.map(initializeMenu)
    }
    return item
  }

  dequeue(inbound.update_menu, (value) => {
    menuItems.value = value.map(initializeMenu)
  })

  return {
    menuItems
  }
})
