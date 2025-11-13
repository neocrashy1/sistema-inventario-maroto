import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import paymentsAPI from '@/services/payments'

export const usePaymentsStore = defineStore('payments', () => {
  const items = ref([])
  const loading = ref(false)
  const error = ref(null)

  const mock = [
    { id: 1, reference: 'INV-2025-001', amount: 1250.00, date: '2025-01-15', vendor: 'Microsoft', method: 'Cartão' },
    { id: 2, reference: 'INV-2025-045', amount: 300.00, date: '2025-07-03', vendor: 'Zoom', method: 'Boleto' }
  ]

  const totalAmount = computed(() => items.value.reduce((s, p) => s + Number(p.amount || 0), 0))

  const fetchPayments = async () => {
    loading.value = true
    error.value = null
    try {
      const data = await paymentsAPI.fetchPayments()
      items.value = data
      return { success: true, data }
    } catch (err) {
      error.value = err?.message || 'Erro ao buscar pagamentos'
      items.value = mock
      return { success: false, error: error.value }
    } finally {
      loading.value = false
    }
  }

  const addPayment = async (payload) => {
    loading.value = true
    try {
      const res = await paymentsAPI.addPayment(payload)
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

  const updatePayment = async (id, payload) => {
    loading.value = true
    try {
      const res = await paymentsAPI.updatePayment(id, payload)
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

  const deletePayment = async (id) => {
    loading.value = true
    try {
      await paymentsAPI.deletePayment(id)
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
    totalAmount,
    fetchPayments,
    addPayment,
    updatePayment,
    deletePayment
  }
})
