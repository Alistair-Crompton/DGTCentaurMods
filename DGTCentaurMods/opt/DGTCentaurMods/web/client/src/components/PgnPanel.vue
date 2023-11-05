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
  <Panel class="w-40" display-setting="pgnPanel">
    <div class="h-full overflow-y-auto">
      <div v-for="{ move, wsan, bsan } in history.pgnlist" :key="move">
        <span :class="{ current: move === Math.floor(history.index / 2) }">{{ move + 1 }}.</span
        >&nbsp;
        <a
          :class="['cursor-pointer', { current: history.index === 2 * move }]"
          @click="history.go(2 * move)"
          >{{ wsan }}</a
        >&nbsp;
        <a
          :class="['cursor-pointer', { current: history.index === 2 * move + 1 }]"
          @click="history.go(2 * move + 1)"
          >{{ bsan }}</a
        >
      </div>
    </div>
  </Panel>
</template>

<script setup lang="ts">
import Panel from './Panel.vue'
import { useHistoryStore } from '../stores/history'

const history = useHistoryStore()
</script>

<style scoped>
.current {
  background-color: yellow;
  font-weight: bold;
}
</style>
