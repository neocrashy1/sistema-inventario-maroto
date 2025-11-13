// Serviço simulado para registros de pagamentos (aquisições, renovações de licenças)
export default {
  async fetchPayments() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          { id: 1, reference: 'INV-2025-001', amount: 1250.00, date: '2025-01-15', vendor: 'Microsoft', method: 'Cartão' },
          { id: 2, reference: 'INV-2025-045', amount: 300.00, date: '2025-07-03', vendor: 'Zoom', method: 'Boleto' }
        ])
      }, 150)
    })
  },

  async addPayment(payment) {
    return new Promise((resolve) => setTimeout(() => resolve({ ...payment }), 80))
  },

  async updatePayment(id, data) {
    return new Promise((resolve) => setTimeout(() => resolve({ id, ...data }), 80))
  },

  async deletePayment(id) {
    return new Promise((resolve) => setTimeout(() => resolve(true), 80))
  }
}
