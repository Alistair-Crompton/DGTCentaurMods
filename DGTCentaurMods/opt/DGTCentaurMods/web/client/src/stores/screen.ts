// This file is part of the DGTCentaur Mods open source software
// ( https://github.com/Alistair-Crompton/DGTCentaurMods )
//
// DGTCentaur Mods is free software: you can redistribute
// it and/or modify it under the terms of the GNU General Public
// License as published by the Free Software Foundation, either
// version 3 of the License, or (at your option) any later version.
//
// DGTCentaur Mods is distributed in the hope that it will
// be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
// of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this file.  If not, see
//
// https://github.com/Alistair-Crompton/DGTCentaurMods/blob/master/LICENSE.md
//
// This and any other notices must remain intact and unaltered in any
// distribution, modification, variant, or derivative of this software.

import blank from '../assets/images/blank_screen.png'
import { computed, shallowRef } from 'vue'
import { defineStore } from 'pinia'
import { dequeue, inbound } from '../socket'

export const useScreenStore = defineStore('screen', () => {
  const bytes = shallowRef(null)

  dequeue(inbound.centaur_screen, (value) => {
    bytes.value = value
  })

  const image = computed(() => {
    if (!bytes.value) {
      return blank
    }
    const base64 = btoa(String.fromCharCode(...new Uint8Array(bytes.value)))
    return `data:image/png;base64,${base64}`
  })

  return {
    image
  }
})
