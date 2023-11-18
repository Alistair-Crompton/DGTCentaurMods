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
  <dialog :class="['modal', { 'modal-open': sounds.length }]">
    <div class="modal-box">
      <h3 class="font-bold">🎵 Board sounds</h3>
      <div><ul class="menu">
        <li v-for="sound in sounds" :key="sound">
          <label>
            <input
              @change="updateAppSetings(sound)"
              class="toggle"
              type="checkbox"
              v-model="sound.value"
            />
            {{ sound.label }}
          </label>
        </li>
      </ul></div>
      <div class="modal-action">
        <button @click="sounds = []" class="btn btn-primary">Close</button>
      </div>
    </div>
  </dialog>
</template>

<script setup lang="ts">
import { dequeue, emit, inbound } from '../socket'
import { shallowRef } from 'vue'

const sounds = shallowRef([])

dequeue(inbound.sounds_settings, (value) => {
  sounds.value = value
})

const updateAppSetings = (sound) => {
  emit('request', { data: 'sounds_settings_set', sound })
}
</script>
