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
  <div v-if="display.settings[displaySetting]" class="flex flex-col relative border-2 border-black border-solid">
    <button
      class="absolute btn btn-xs top-0 right-0"
      @click="display.settings[displaySetting] = false"
    >✘</button>
    <slot class="absolute top-0 left-0" />
  </div>
</template>

<script setup lang="ts">
import { useDisplayStore } from '../stores/display'

const display = useDisplayStore()

defineProps({
  displaySetting: {
    type: String,
    required: true
  }
})
</script>
