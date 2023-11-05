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

import { computed, ref, watch } from 'vue'
import { defineStore } from 'pinia'
import { dequeue, inbound } from '../socket'

// Control and configure display of user-interface
export const useDisplayStore = defineStore('display', () => {
  // List of alert messages to display
  const alerts = ref([])

  // Display options for various dialogs
  const dialogs = ref({})

  // Display settings
  const settings = ref({
    activeBoard: false,
    centaurScreen: true,
    chatPanel: true,
    kingsChecks: false,
    liveEvaluation: true,
    pgnPanel: true,
    previousMove: true,
    reversedBoard: false
  })

  // Controls display of side-drawer
  const showDrawer = ref(false)

  // Controls display of editor panel
  const showEditor = ref(false)

  // Current release and document/display title
  const release = ref('')
  const title = computed(() => `DGTCentaurMods ${release.value}`)

  // Dismiss alert message
  const removeAlert = (message) => {
    alerts.value = alerts.value.filter((msg) => msg !== message)
  }

  // Add new alert message
  const showAlert = (message) => {
    const existingIndex = alerts.value.indexOf(message)
    if (existingIndex >= 0) {
      // Don't display duplicate alerts, keep only the most recent
      alerts.value.splice(existingIndex, 1)
    }
    alerts.value = [...alerts.value, message]
  }

  // Persist display settings
  const saveToLocalStorage = () => {
    localStorage.setItem('display', JSON.stringify(settings.value))
  }
  watch(settings, saveToLocalStorage, { deep: true })

  const initFromLocalStorage = () => {
    const json = localStorage.getItem('display')
    const data = json ? JSON.parse(json) : null
    if (data) {
      settings.value = { ...settings.value, ...data }
    }
  }
  initFromLocalStorage()

  const showWebSettings = () => {
    dialogs.value = {
      webSettings: [
        { id: 'previousMove', label: 'Previous move displayed' },
        { id: 'kingsChecks', label: 'Kings checks displayed' },
        { id: 'liveEvaluation', label: 'Live evaluation displayed' },
        { id: 'centaurScreen', label: 'Centaur screen displayed' },
        { id: 'pgnPanel', label: 'PGN panel displayed' },
        { id: 'chatPanel', label: 'Chat panel displayed' },
        { id: 'reversedBoard', label: 'Board is reversed' },
        { id: 'activeBoard', label: 'Board is active' }
      ]
    }
  }

  // Keep document title updated
  watch(
    title,
    (newTitle) => {
      document.title = newTitle
    },
    { immediate: true }
  )

  dequeue(inbound.evaluation_disabled, (value) => {
    settings.value = { ...settings.value, liveEvaluation: value }
  })

  dequeue(inbound.popup, showAlert)

  dequeue(inbound.release, ({ latest_tag, need_update, tag }) => {
    release.value = tag
    if (need_update) {
      showAlert(`The release ${latest_tag} is available!`)
    }
  })

  return {
    alerts,
    dialogs,
    settings,
    removeAlert,
    showAlert,
    showDrawer,
    showEditor,
    showWebSettings,
    title
  }
})
