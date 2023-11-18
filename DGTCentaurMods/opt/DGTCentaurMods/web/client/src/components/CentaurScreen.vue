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
  <Panel display-setting="centaurScreen">
    <div class="flex flex-col align-items-center">
      <img :src="screen.image" />
      <hr class="border-2 border-black border-solid w-full" />
      <div class="grid grid-cols-3">
        <ChevronUpIcon @click="pushButton(3)" class="btn btn-outline btn-sm m-1 col-start-2" />
        <ArrowUturnLeftIcon @click="pushButton(1)" class="btn btn-outline btn-sm m-1 col-start-1" />
        <CheckIcon @click="pushButton(6)" class="btn btn-outline btn-sm m-1 col-start-3" />
        <ChevronDownIcon @click="pushButton(4)" class="btn btn-outline btn-sm m-1 col-start-2" />
        <QuestionMarkCircleIcon @click="pushButton(5)" class="btn btn-outline btn-sm m-1 col-start-1" />
        <PlayPauseIcon @click="pushButton(2)" class="btn btn-outline btn-sm m-1 col-start-3" />
      </div>
      <div>&nbsp;</div>
    </div>
  </Panel>
</template>

<script setup lang="ts">
import {
  ArrowUturnLeftIcon,
  CheckIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  PlayPauseIcon,
  QuestionMarkCircleIcon
} from '@heroicons/vue/24/solid'
import Panel from './Panel.vue'
import { emit } from '../socket'
import { useScreenStore } from '../stores/screen'

const screen = useScreenStore()
const pushButton = (web_button: number) => emit('request', { web_button })
</script>
