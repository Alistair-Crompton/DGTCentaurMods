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
  <dialog :class="['modal', { 'modal-open': !!display.dialogs['webSettings'] }]">
    <div class="modal-box">
      <h3 class="font-bold">🕸 Web settings</h3>
      <div><ul class="menu">
        <li v-for="{ id, label } in display.dialogs['webSettings']" :key="id">
          <label>
            <input class="toggle" type="checkbox" v-model="display.settings[id]"/>
            {{ label }}
          </label>
        </li>
      </ul></div>
      <div class="modal-action">
        <button @click="display.dialogs = {}" class="btn btn-primary">Close</button>
      </div>
    </div>
  </dialog>
</template>

<script setup lang="ts">
import { useDisplayStore } from '../stores/display'
const display = useDisplayStore()
</script>
