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
  <ul class="menu menu-sm">
    <li
      v-for="{ action, disabled, id, items, label, type } in menuItems"
      :class="{disabled}"
    >
      <!-- Submenus -->
      <details v-if="items?.length" class="w-40" @click="closeOther">
        <summary>{{ label }}</summary>
        <Menu :menuItems="items" class="menu-vertical"/>
      </details>
      <!-- Checkboxes -->
      <label v-else-if="type === 'checkbox'">
        <input type="checkbox" v-model="display.settings[id]"/>
        {{ label }}
      </label>
      <!-- Dividers -->
      <hr v-else-if="type === 'divider'"/>
      <!-- Actions -->
      <a  v-else @click="executeAction(action, $event)">{{ label }}</a>
    </li>
  </ul>
</template>

<script setup lang="ts">
import { useDisplayStore } from '../stores/display'

const display = useDisplayStore()
defineProps(['menuItems'])

const closeMenus = (excluding: HTMLElement[]) => {
  const navbar  = document.querySelector('.navbar')
  const details = navbar?.querySelectorAll('details') ?? []
  details.forEach((detail: HTMLElement) => {
    if (!excluding.includes(detail)) {
      detail.removeAttribute('open')
    }
  })
}

// Close all menus not direct ancestors of clicked element
const closeOther = (event: MouseEvent) => {
  const ancestors = []
  let { target } = event
  while (!(<HTMLElement>target).classList.contains('navbar')) {
    if ((<HTMLElement>target).tagName === 'DETAILS') {
      ancestors.push(target)
    }
    target = (<HTMLElement>target).parentElement
  }
  closeMenus(ancestors)
}

// Close all menus
const closeAll = (event) => {
  let { target } = event
  if (target.tagName === 'SUMMARY') {
    while (target.tagName !== 'DETAILS') {
      target = target.parentElement
    }
  }
  closeMenus([target])
}

// Close all menus before running action
const executeAction = (action, event) => {
  closeAll(event)
  if (action) {
    action()
  }
}
</script>
