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
  <dialog :class="['modal', { 'modal-open': display.dialogs['viewPgn'] }]">
    <div class="modal-box">
      <h3 class="font-bold">View current PGN</h3>
      <Codemirror
        :autofocus="true"
        :read-only="true"
        :tab-size="4"
        v-model="display.dialogs['viewPgn']"
      />
      <div class="modal-action">
        <button v-if="hasClipboard()" @click="onCopy" class="btn">Copy</button>
        <button v-if="hasClipboard()" @click="onCopyAndGo" class="btn">Copy &amp; go</button>
        <button v-if="!hasClipboard()" @click="openLichess" class="btn">Lichess</button>
        <button @click="onClose" class="btn btn-primary">Close</button>
      </div>
    </div>
  </dialog>
</template>

<script setup lang="ts">
import { Codemirror } from 'vue-codemirror';
import { useDisplayStore } from '../stores/display'

const display = useDisplayStore()

// Only available in secure contexts
const hasClipboard = () => navigator?.clipboard !== undefined

const onCopy = () => navigator.clipboard.writeText(display.dialogs['viewPgn'])
const onClose = () => (display.dialogs = {})

const openLichess = () => window.open('https://lichess.org/paste', '_blank')

const onCopyAndGo = async () => {
  await onCopy()
  openLichess()
  onClose()
}
</script>
