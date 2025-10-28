import { defineStore } from 'pinia'
import purchasesService from '@/services/purchases'

export const usePurchasesStore = defineStore('purchases', {
  state: () => ({
    purchases: [],
    loading: false,
    error: null,
    searchTerm: '',
    filters: {
      status: ''
    }
  }),

  getters: {
    totalPurchases: (state) => state.purchases.length,
    filteredPurchases: (state) => {
      let items = [...state.purchases]
      if (state.searchTerm) {
        const term = state.searchTerm.toLowerCase()
        items = items.filter(p => p.code.toLowerCase().includes(term) || (p.supplier || '').toLowerCase().includes(term))
      }
      if (state.filters.status) {
        items = items.filter(p => p.status === state.filters.status)
      }
      return items
    }
  },

  actions: {
    async fetchPurchases() {
      this.loading = true
      this.error = null
      try {
        const res = await purchasesService.list()
        this.purchases = res.data || []
        this.loading = false
      } catch (err) {
        this.error = 'Erro ao buscar compras'
        this.loading = false
        throw err
      }
    },

    async createPurchase(payload) {
      this.loading = true
      this.error = null
      try {
        const res = await purchasesService.create(payload)
        this.purchases.unshift(res.data)
        this.loading = false
        return res.data
      } catch (err) {
        this.error = 'Erro ao criar compra'
        this.loading = false
        throw err
      }
    },

    async updatePurchase(id, updates) {
      this.loading = true
      this.error = null
      try {
        const res = await purchasesService.update(id, updates)
        const idx = this.purchases.findIndex(p => p.id === res.data.id)
        if (idx !== -1) this.purchases[idx] = res.data
        this.loading = false
        return res.data
      } catch (err) {
        this.error = 'Erro ao atualizar compra'
        this.loading = false
        throw err
      }
    },

    async deletePurchase(id) {
      this.loading = true
      this.error = null
      try {
        await purchasesService.remove(id)
        const idx = this.purchases.findIndex(p => p.id === Number(id))
        if (idx !== -1) this.purchases.splice(idx, 1)
        this.loading = false
      } catch (err) {
        this.error = 'Erro ao deletar compra'
        this.loading = false
        throw err
      }
    },

    setSearchTerm(term) { this.searchTerm = term },
    setFilters(filters) { this.filters = { ...this.filters, ...filters } }
  }
})
