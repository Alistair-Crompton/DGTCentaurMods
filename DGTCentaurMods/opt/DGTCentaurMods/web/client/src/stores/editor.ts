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
import { ref } from 'vue'
import { useDisplayStore } from './display'

// Used to edit files on the server
export const useEditorStore = defineStore('editor', () => {
  // We show the editor in response to a message from the server
  const display = useDisplayStore()

  const canDelete = ref(false)
  const canExecute = ref(false)
  const editableName = ref(false)
  const extension = ref('')
  const file = ref('')
  const id = ref('')
  const newFile = ref('')
  const text = ref('')

  // Handle incoming "editor" message
  dequeue(inbound.editor, (value) => {
    // Read editor state from message
    canDelete.value = value.can_delete
    canExecute.value = value.can_execute
    editableName.value = value.editable_name
    extension.value = value.extension
    file.value = value.file
    id.value = value.id
    newFile.value = value.file
    text.value = value.text

    // Show the UI
    display.showEditor = true
  })

  // Request server remove file
  const deleteFile = () => {
    emit('request', {
      write: {
        id: id.value,
        file: file.value,
        new_file: '__delete__'
      }
    })
  }

  // Send script to server for execution
  const execute = () => {
    localStorage.setItem('live_script', text.value)
    emit('request', { live_script: text.value })
  }

  // Send edited file back to server
  const save = () => {
    emit('request', {
      write: {
        id: id.value,
        file: file.value,
        new_file: newFile.value,
        text: text.value
      }
    })
  }

  return {
    canDelete,
    canExecute,
    deleteFile,
    editableName,
    execute,
    extension,
    file,
    id,
    newFile,
    save,
    text
  }
})
