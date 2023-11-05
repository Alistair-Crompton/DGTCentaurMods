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
  <div class="drawer">
    <!-- Hidden checkbox toggles display of side drawer -->
    <input
      class="drawer-toggle"
      id="showDrawer"
      type="checkbox"
      v-model="display.showDrawer"
    />

    <!-- Main content -->
    <div class="drawer-content" style="height: 100vh;">
      <Editor v-if="display.showEditor"/>
      <div v-else class="flex flex-col" style="height: 100%;">
        <Navbar/>
        <Content/>
        <div class="flex-1"></div>
        <hr/>
        <LogEvents/>
      </div>
      <Dialogs/>
    </div>

    <!-- Sidebar displays menu of previous games -->
    <div class="drawer-side">
      <label for="showDrawer" class="drawer-overlay"></label>
      <PreviousGames/>
    </div>
    <Toasts />
  </div>
</template>

<script setup lang="ts">
import Content from './components/Content.vue'
import Dialogs from './components/Dialogs.vue'
import Editor from './components/Editor.vue'
import LogEvents from './components/LogEvents.vue'
import Navbar from './components/Navbar.vue'
import PreviousGames from './components/PreviousGames.vue'
import Toasts from './components/Toasts.vue'
import { useDisplayStore } from './stores/display'

const display = useDisplayStore()
</script>
