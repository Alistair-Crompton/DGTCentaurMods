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
  <Panel class="w-60" display-setting="chatPanel">
    <div class="flex flex-col items-stretch h-full bg-base-200 text-sm">
      <div class="flex-1 overflow-y-auto">
        <div v-for="{ author, color, message, ts } in chat.items" :key="message">
          <div :style="{ color }">{{ ts }} {{ author }}:</div>
          <div :style="{ color }">{{ message }}</div>
        </div>
      </div>
      <label class="flex-none">
        Send message
        <input
          @keyup.enter="submit"
          class="input input-bordered w-full"
          v-model="composing"
        />
      </label>
    </div>
  </Panel>
</template>

<script setup lang="ts">
import Panel from './Panel.vue'
import { ref } from 'vue'
import { useChatStore } from '../stores/chat'

// Contains chat history
const chat = useChatStore()

// Current composition
const composing = ref('')

const submit = () => {
  if (composing.value) {
    chat.submit(composing.value)
    composing.value = ''
  }
}
</script>
