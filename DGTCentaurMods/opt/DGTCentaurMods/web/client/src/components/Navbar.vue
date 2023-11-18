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
  <div class="bg-base-100 navbar w-full z-10">
    <div>
      <label class="btn btn-ghost">
        <span>{{ display.title }}</span>
      </label>
      <!-- Show top-level menu persistently in navigation -->
      <Menu class="menu-horizontal" :menuItems="menu.menuItems"/>
    </div>
  </div>
</template>

<script setup lang="ts">
import Menu from './Menu.vue'
import { useDisplayStore } from '../stores/display'
import { useMenuStore } from '../stores/menu'

const display = useDisplayStore()
const menu    = useMenuStore()
</script>
