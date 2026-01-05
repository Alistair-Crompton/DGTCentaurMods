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

<!-- *edit by Chemtech1* - Hint settings component -->
<template>
  <dialog :class="['modal', { 'modal-open': hints.length }]">
    <div class="modal-box">
      <h3 class="font-bold">💡 Hint on/off</h3>
      <div><ul class="menu">
        <li v-for="hint in hints" :key="hint">
          <label>
            <input
              @change="updateAppSetings(hint)"
              class="toggle"
              type="checkbox"
              v-model="hint.value"
            />
            {{ hint.label }}
          </label>
        </li>
      </ul></div>
      <div class="modal-action">
        <button @click="hints = []" class="btn btn-primary">Close</button>
      </div>
    </div>
  </dialog>
</template>

<script setup lang="ts">
import { dequeue, emit, inbound } from '../socket'
import { shallowRef } from 'vue'

const hints = shallowRef([])

dequeue(inbound.hint_settings, (value) => {
  hints.value = value
})

const updateAppSetings = (hint) => {
  emit('request', { data: 'hint_settings_set', value: hint })
}
</script>
