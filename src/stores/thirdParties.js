import { defineStore } from 'pinia'

export const useThirdPartiesStore = defineStore('thirdParties', {
  state: () => ({
    thirdParties: [
      {
        id: 1,
        name: 'TechSolutions Ltda',
        type: 'company',
        document: '12.345.678/0001-90',
        email: 'contato@techsolutions.com.br',
        phone: '(11) 3456-7890',
        contact: 'João Silva',
        contactPhone: '(11) 99876-5432',
        address: {
          street: 'Av. Paulista, 1000',
          city: 'São Paulo',
          state: 'SP',
          zipCode: '01310-100'
        },
        status: 'active',
        category: 'fornecedor',
        notes: 'Empresa parceira para serviços de TI',
        createdAt: '2024-01-15T10:30:00Z',
        updatedAt: '2024-01-15T10:30:00Z'
      },
      {
        id: 2,
        name: 'Maria Santos',
        type: 'person',
        document: '123.456.789-00',
        email: 'maria.santos@email.com',
        phone: '(11) 98765-4321',
        contact: 'Maria Santos',
        contactPhone: '(11) 98765-4321',
        address: {
          street: 'Rua das Flores, 123',
          city: 'São Paulo',
          state: 'SP',
          zipCode: '04567-890'
        },
        status: 'active',
        category: 'consultor',
        notes: 'Consultora especializada em processos',
        createdAt: '2024-01-20T14:15:00Z',
        updatedAt: '2024-01-20T14:15:00Z'
      },
      {
        id: 3,
        name: 'InnovaCorp',
        type: 'company',
        document: '98.765.432/0001-10',
        email: 'comercial@innovacorp.com.br',
        phone: '(11) 2345-6789',
        contact: 'Carlos Oliveira',
        contactPhone: '(11) 99123-4567',
        address: {
          street: 'Rua da Inovação, 500',
          city: 'São Paulo',
          state: 'SP',
          zipCode: '05678-901'
        },
        status: 'inactive',
        category: 'prestador',
        notes: 'Empresa de prestação de serviços especializados',
        createdAt: '2024-02-01T09:00:00Z',
        updatedAt: '2024-02-15T16:30:00Z'
      }
    ],
    filters: {
      search: '',
      type: '',
      status: '',
      category: ''
    }
  }),

  getters: {
    // Filtros básicos
    filteredThirdParties: (state) => {
      let filtered = [...state.thirdParties]

      if (state.filters.search) {
        const search = state.filters.search.toLowerCase()
        filtered = filtered.filter(party => 
          party.name.toLowerCase().includes(search) ||
          party.email.toLowerCase().includes(search) ||
          party.document.includes(search) ||
          party.contact.toLowerCase().includes(search)
        )
      }

      if (state.filters.type) {
        filtered = filtered.filter(party => party.type === state.filters.type)
      }

      if (state.filters.status) {
        filtered = filtered.filter(party => party.status === state.filters.status)
      }

      if (state.filters.category) {
        filtered = filtered.filter(party => party.category === state.filters.category)
      }

      return filtered
    },

    // Estatísticas
    totalThirdParties: (state) => state.thirdParties.length,
    
    activeThirdParties: (state) => state.thirdParties.filter(party => party.status === 'active'),
    
    inactiveThirdParties: (state) => state.thirdParties.filter(party => party.status === 'inactive'),

    // Por tipo
    companies: (state) => state.thirdParties.filter(party => party.type === 'company'),
    
    persons: (state) => state.thirdParties.filter(party => party.type === 'person'),

    // Por categoria
    byCategory: (state) => {
      const categories = {}
      state.thirdParties.forEach(party => {
        if (!categories[party.category]) {
          categories[party.category] = []
        }
        categories[party.category].push(party)
      })
      return categories
    },

    // Categorias únicas
    availableCategories: (state) => {
      const categories = [...new Set(state.thirdParties.map(party => party.category))]
      return categories.sort()
    }
  },

  actions: {
    // Adicionar terceiro
    addThirdParty(thirdPartyData) {
      const newThirdParty = {
        id: Math.max(...this.thirdParties.map(p => p.id), 0) + 1,
        ...thirdPartyData,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      
      this.thirdParties.push(newThirdParty)
      return newThirdParty
    },

    // Atualizar terceiro
    updateThirdParty(id, updates) {
      const index = this.thirdParties.findIndex(party => party.id === id)
      if (index !== -1) {
        this.thirdParties[index] = {
          ...this.thirdParties[index],
          ...updates,
          updatedAt: new Date().toISOString()
        }
        return this.thirdParties[index]
      }
      return null
    },

    // Excluir terceiro
    deleteThirdParty(id) {
      const index = this.thirdParties.findIndex(party => party.id === id)
      if (index !== -1) {
        this.thirdParties.splice(index, 1)
        return true
      }
      return false
    },

    // Buscar terceiro por ID
    findThirdPartyById(id) {
      return this.thirdParties.find(party => party.id === id)
    },

    // Buscar terceiro por documento
    findThirdPartyByDocument(document) {
      return this.thirdParties.find(party => party.document === document)
    },

    // Ativar/Desativar terceiro
    toggleThirdPartyStatus(id) {
      const party = this.findThirdPartyById(id)
      if (party) {
        party.status = party.status === 'active' ? 'inactive' : 'active'
        party.updatedAt = new Date().toISOString()
        return party
      }
      return null
    },

    // Filtros
    setSearchFilter(search) {
      this.filters.search = search
    },

    setTypeFilter(type) {
      this.filters.type = type
    },

    setStatusFilter(status) {
      this.filters.status = status
    },

    setCategoryFilter(category) {
      this.filters.category = category
    },

    clearFilters() {
      this.filters = {
        search: '',
        type: '',
        status: '',
        category: ''
      }
    },

    // Exportar dados
    exportThirdParties() {
      return this.filteredThirdParties.map(party => ({
        Nome: party.name,
        Tipo: party.type === 'company' ? 'Empresa' : 'Pessoa Física',
        Documento: party.document,
        Email: party.email,
        Telefone: party.phone,
        Contato: party.contact,
        Status: party.status === 'active' ? 'Ativo' : 'Inativo',
        Categoria: party.category,
        'Data de Cadastro': new Date(party.createdAt).toLocaleDateString('pt-BR')
      }))
    }
  }
})