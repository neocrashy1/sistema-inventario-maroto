import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import softwareAPI from '@/services/software'

export const useSoftwareStore = defineStore('software', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  const mock = [
    { id: 1, name: 'Google Chrome', version: '120.0', license: 'Free', installedOn: 120 },
    { id: 2, name: 'Zoom', version: '5.15', license: 'Commercial', installedOn: 34 }
  ]

  const total = computed(() => items.value.length)

  const fetchSoftware = async () => {
    loading.value = true
    error.value = null
    try {
      const data = await softwareAPI.fetchSoftware()
      items.value = data
      return { success: true, data }
    } catch (err) {
      error.value = err?.message || 'Erro ao buscar software'
      items.value = mock
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const addSoftware = async (payload) => {
    loading.value = true
    try {
      const res = await softwareAPI.addSoftware(payload)
      const newItem = { id: Date.now(), ...res }
      items.value.push(newItem)
      return { success: true, data: newItem }
    } catch (err) {
      error.value = err?.message
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const updateSoftware = async (id, payload) => {
    loading.value = true
    try {
      const res = await softwareAPI.updateSoftware(id, payload)
      const idx = items.value.findIndex(i => i.id === id)
      if (idx !== -1) items.value[idx] = { ...items.value[idx], ...res }
      return { success: true, data: res }
    } catch (err) {
      error.value = err?.message
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const deleteSoftware = async (id) => {
    loading.value = true
    try {
      await softwareAPI.deleteSoftware(id)
      items.value = items.value.filter(i => i.id !== id)
      return { success: true }
    } catch (err) {
      error.value = err?.message
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  return {
    items,
    loading,
    error,
    total,
    fetchSoftware,
    addSoftware,
    updateSoftware,
    deleteSoftware
  }
})
