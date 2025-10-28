/**
 * purchases service - placeholder
 * Fornece chamadas simuladas à API para compras / orçamentos.
 */

class PurchasesService {
  constructor() {
    this.purchases = [
      {
        id: 1,
        code: 'PR-2025-001',
        supplier: 'Fornecedor A',
        items: [{ description: 'SSD 512GB', qty: 2, unitPrice: 350 }],
        total: 700,
        status: 'quote', // quote, ordered, received, cancelled
        createdAt: new Date().toISOString(),
        notes: 'Orçamento inicial'
      }
    ]
  }

  async list(params = {}) {
    // Simula latência
    await new Promise(r => setTimeout(r, 300))
    return { data: this.purchases.slice() }
  }

  async get(id) {
    await new Promise(r => setTimeout(r, 200))
    const p = this.purchases.find(x => x.id === Number(id))
    return { data: p || null }
  }

  async create(payload) {
    await new Promise(r => setTimeout(r, 300))
    const id = Date.now()
    const total = (payload.items || []).reduce((s, it) => s + (it.qty || 0) * (it.unitPrice || 0), 0)
    const newP = { id, code: `PR-${new Date().getFullYear()}-${String(this.purchases.length + 1).padStart(3, '0')}`, ...payload, total, createdAt: new Date().toISOString() }
    this.purchases.unshift(newP)
    return { data: newP }
  }

  async update(id, updates) {
    await new Promise(r => setTimeout(r, 250))
    const idx = this.purchases.findIndex(x => x.id === Number(id))
    if (idx === -1) return { data: null }
    this.purchases[idx] = { ...this.purchases[idx], ...updates }
    return { data: this.purchases[idx] }
  }

  async remove(id) {
    await new Promise(r => setTimeout(r, 200))
    const idx = this.purchases.findIndex(x => x.id === Number(id))
    if (idx !== -1) this.purchases.splice(idx, 1)
    return { success: true }
  }
}

const purchasesService = new PurchasesService()
export default purchasesService
