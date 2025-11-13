// Serviço simulado para Licenças (substituir por chamadas reais à API)
export default {
  async fetchLicenses() {
    // Simula latência e retorno
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          { id: 1, name: 'Windows 10 Pro', vendor: 'Microsoft', key: 'XXXXX-XXXXX-XXXXX-XXXXX', seats: 10, expiry: null },
          { id: 2, name: 'Office 365 E3', vendor: 'Microsoft', key: 'N/A', seats: 50, expiry: '2026-05-01' }
        ])
      }, 150)
    })
  },

  async addLicense(license) {
    return new Promise((resolve) => setTimeout(() => resolve({ ...license }), 100))
  },

  async updateLicense(id, data) {
    return new Promise((resolve) => setTimeout(() => resolve({ id, ...data }), 100))
  },

  async deleteLicense(id) {
    return new Promise((resolve) => setTimeout(() => resolve(true), 100))
  }
}
