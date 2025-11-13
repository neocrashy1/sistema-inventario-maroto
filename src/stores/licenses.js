import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import licensesAPI from '@/services/licenses'

export const useLicensesStore = defineStore('licenses', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  const mock = [
    { id: 1, name: 'Windows 10 Pro', vendor: 'Microsoft', key: 'XXXXX-XXXXX', seats: 10, expiry: null },
    { id: 2, name: 'Office 365 E3', vendor: 'Microsoft', key: 'N/A', seats: 50, expiry: '2026-05-01' }
  ]

  const total = computed(() => items.value.length)

  const fetchLicenses = async () => {
    loading.value = true
    error.value = null
    try {
      const data = await licensesAPI.fetchLicenses()
      items.value = data
      return { success: true, data }
    } catch (err) {
      error.value = err?.message || 'Erro ao buscar licenças'
      items.value = mock
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const addLicense = async (payload) => {
    loading.value = true
    try {
      const res = await licensesAPI.addLicense(payload)
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

  const updateLicense = async (id, payload) => {
    loading.value = true
    try {
      const res = await licensesAPI.updateLicense(id, payload)
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

  const deleteLicense = async (id) => {
    loading.value = true
    try {
      await licensesAPI.deleteLicense(id)
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
    fetchLicenses,
    addLicense,
    updateLicense,
    deleteLicense
  }
})
