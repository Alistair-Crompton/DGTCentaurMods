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
  <div class="collapse collapse-arrow">
    <input type="checkbox" v-model="show"/>
    <div class="collapse-title">
      Log events
    </div>
    <div class="collapse-content" ref="content" style="overflow-y: scroll;">
      <div>
        <div v-for="event in events">{{  event  }}</div>
      </div>
      <div class="join">
        <button @click="refresh()" class="btn btn-sm join-item">Refresh</button>
        <button @click="newWindow()" class="btn btn-sm join-item">New window</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { dequeue, emit, inbound } from '../socket'
import { nextTick, ref, watch } from 'vue'

const content = ref(null)
const events = ref([])
const show = ref(false)

const newWindow = () => {
  const logEvents = events.value.join('')
  const data = new Blob([logEvents], { type: 'text/plain' })
  const url  = window.URL.createObjectURL(data)
  window.open(url)
  window.URL.revokeObjectURL(url)
}

const refresh = () => {
  emit('request', { sys: 'log_events' })
}

watch(show, (newShow) => {
  if (newShow) {
    refresh()
  }
})

dequeue(inbound.log_events, (value) => {
  events.value = value
  show.value = true
  nextTick(() => {
    content.value.scrollTop = content.value.scrollHeight
  })
})
</script>
