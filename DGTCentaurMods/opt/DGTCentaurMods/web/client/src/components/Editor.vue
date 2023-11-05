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
  <div>
    <div class="join">
      <div class="flex flex-col join-item justify-center mx-4">
        <label v-if="editor.editableName">
          <input
            class="input input-bordered"
            v-model="editor.newFile"
          />.{{ editor.extension }}
        </label>
        <h2
          v-else
          class="font-bold"
        >{{ editor.file }}<span v-if="editor.extension">.{{ editor.extension }}</span></h2>
      </div>
      <button
        v-if="!editor.canExecute"
        @click="onSave()"
        :class="['btn', 'join-item', { 'btn-disabled': parseError }]"
      >Save</button>
      <button
        v-if="editor.canDelete"
        @click="onDelete()"
        class="btn join-item"
      >Delete</button>
      <button
        v-if="editor.canExecute"
        @click="onExecute()"
        class="btn join-item"
      >Execute</button>
      <button
        @click="onClose()"
        class="btn btn-primary join-item"
      >Back</button>
      <div class="flex flex-col join-item justify-center mx-4">
        <h2 class="font-bold text-error">{{ parseError }}</h2>
      </div>
    </div>
    <Codemirror
      :autofocus="true"
      :extensions="extensions"
      :tab-size="4"
      v-model="editor.text"
    />
  </div>
</template>

<script setup lang="ts">
import { Chess } from 'chess.js'
import { Codemirror } from 'vue-codemirror'
import { StreamLanguage } from '@codemirror/language'
import { basicSetup } from 'codemirror'
import { computed } from 'vue'
import { emit } from '../socket'
import { properties } from '@codemirror/legacy-modes/mode/properties'
import { python } from '@codemirror/lang-python'
import { useDisplayStore } from '../stores/display'
import { useEditorStore } from '../stores/editor'

const display = useDisplayStore()
const editor = useEditorStore()

// Inform user if PGN is invalid
const parseError = computed(() => {
  if (editor.extension !== 'pgn') {
    return ''
  }

  try {
    new Chess().loadPgn(editor.text, { strict: true })
    return ''
  } catch (err: any) {
    return err.message
  }
})

// Load Codemirror extensions appropriate to filetype
const extensions = computed(() => {
  const extensions = [basicSetup]
  if (editor.extension === 'ini' || editor.extension === 'uci') {
    extensions.push(StreamLanguage.define(properties))
  } else if (editor.id === 'live_script') {
    extensions.push(python())
  }
  return extensions
})

let busy = false
let dirty = false

const debounce = (fn) => {
  if (busy) {
    return
  }
  busy = true
  try {
    fn()
  } finally {
    busy = false
  }
}

const onClose = () => {
  if (dirty) {
    // Web menu might be updated
    emit('request', { web_menu: true })
  }

  // Close UI
  display.showEditor = false

  // Cleanup
  busy  = false
  dirty = false
}

const onDelete = () => {
  debounce(() => {
    editor.deleteFile()
    dirty = true // Mark as removed from server
    onClose()
  })
}

const onExecute = () => {
  editor.execute()
  onClose()
}

const onSave = () => {
  debounce(() => {
    editor.save()
    dirty = true // Mark as updated on server
  })
}
</script>
