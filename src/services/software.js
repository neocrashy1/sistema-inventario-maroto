// Serviço simulado para Software (inventário de aplicações, versões, licenças vinculadas)
export default {
  async fetchSoftware() {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve([
          { id: 1, name: 'Google Chrome', version: '120.0', license: 'Free', installedOn: 120 },
          { id: 2, name: 'Zoom', version: '5.15', license: 'Commercial', installedOn: 34 }
        ])
      }, 120)
    })
  },

  async addSoftware(item) {
    return new Promise((resolve) => setTimeout(() => resolve({ ...item }), 80))
  },

  async updateSoftware(id, data) {
    return new Promise((resolve) => setTimeout(() => resolve({ id, ...data }), 80))
  },

  async deleteSoftware(id) {
    return new Promise((resolve) => setTimeout(() => resolve(true), 80))
  }
}
