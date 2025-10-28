import { defineStore } from 'pinia'

export const useServiceOrdersStore = defineStore('serviceOrders', {
  state: () => ({
    orders: [
      {
        id: 1,
        code: 'OS-2024-001',
        title: 'Manutenção Preventiva - Notebook',
        description: 'Limpeza interna, atualização de drivers e verificação de hardware',
        type: 'preventive',
        priority: 'medium',
        status: 'completed',
        assetId: 1,
        assetCode: 'NB-001',
        assetName: 'Notebook Dell Latitude',
        assignedTo: 'João Silva',
        department: 'TI',
        createdAt: '2024-01-15T08:00:00Z',
        dueDate: '2024-01-20T17:00:00Z',
        startedAt: '2024-01-16T09:00:00Z',
        completedAt: '2024-01-19T16:30:00Z',
        notes: 'Manutenção preventiva conforme cronograma',
        resolution: 'Limpeza realizada, drivers atualizados, hardware funcionando perfeitamente.',
        estimatedHours: 2,
        actualHours: 1.5,
        cost: 0
      },
      {
        id: 2,
        code: 'OS-2024-002',
        title: 'Reparo - Monitor com Defeito',
        description: 'Monitor apresentando falhas na imagem, necessário diagnóstico e reparo',
        type: 'corrective',
        priority: 'high',
        status: 'in_progress',
        assetId: 2,
        assetCode: 'MON-015',
        assetName: 'Monitor Samsung 24"',
        assignedTo: 'Maria Santos',
        department: 'TI',
        createdAt: '2024-02-01T10:30:00Z',
        dueDate: '2024-02-05T17:00:00Z',
        startedAt: '2024-02-02T08:00:00Z',
        completedAt: null,
        notes: 'Usuário relatou falhas intermitentes na imagem',
        resolution: null,
        estimatedHours: 4,
        actualHours: 2,
        cost: 150
      },
      {
        id: 3,
        code: 'OS-2024-003',
        title: 'Emergência - Servidor Principal',
        description: 'Servidor principal apresentando instabilidade, necessário intervenção imediata',
        type: 'emergency',
        priority: 'urgent',
        status: 'open',
        assetId: 3,
        assetCode: 'SRV-001',
        assetName: 'Servidor Dell PowerEdge',
        assignedTo: 'Carlos Oliveira',
        department: 'TI',
        createdAt: '2024-02-10T14:45:00Z',
        dueDate: '2024-02-10T18:00:00Z',
        startedAt: null,
        completedAt: null,
        notes: 'Problema crítico afetando operações',
        resolution: null,
        estimatedHours: 6,
        actualHours: 0,
        cost: 0
      },
      {
        id: 4,
        code: 'OS-2024-004',
        title: 'Instalação - Novo Software',
        description: 'Instalação e configuração de novo software de gestão',
        type: 'preventive',
        priority: 'low',
        status: 'open',
        assetId: 4,
        assetCode: 'CPU-025',
        assetName: 'Desktop HP ProDesk',
        assignedTo: 'Ana Costa',
        department: 'TI',
        createdAt: '2024-02-08T11:00:00Z',
        dueDate: '2024-02-15T17:00:00Z',
        startedAt: null,
        completedAt: null,
        notes: 'Instalação agendada para próxima semana',
        resolution: null,
        estimatedHours: 3,
        actualHours: 0,
        cost: 0
      },
      {
        id: 5,
        code: 'OS-2024-005',
        title: 'Substituição - Disco Rígido',
        description: 'Substituição de disco rígido com falhas por SSD',
        type: 'corrective',
        priority: 'high',
        status: 'open',
        assetId: 5,
        assetCode: 'NB-002',
        assetName: 'Notebook Lenovo ThinkPad',
        assignedTo: 'João Silva',
        department: 'TI',
        createdAt: '2024-02-09T09:15:00Z',
        dueDate: '2024-02-12T17:00:00Z',
        startedAt: null,
        completedAt: null,
        notes: 'Disco apresentando setores defeituosos',
        resolution: null,
        estimatedHours: 2,
        actualHours: 0,
        cost: 300
      }
    ],
    technicians: [
      { id: 1, name: 'João Silva', department: 'TI', specialties: ['Hardware', 'Redes'] },
      { id: 2, name: 'Maria Santos', department: 'TI', specialties: ['Software', 'Sistemas'] },
      { id: 3, name: 'Carlos Oliveira', department: 'TI', specialties: ['Servidores', 'Infraestrutura'] },
      { id: 4, name: 'Ana Costa', department: 'TI', specialties: ['Software', 'Treinamento'] },
      { id: 5, name: 'Pedro Alves', department: 'Manutenção', specialties: ['Elétrica', 'Mecânica'] }
    ],
    availableAssets: [
      {
        id: 1,
        code: 'NB-001',
        name: 'Notebook Dell Latitude',
        category: 'Informática',
        location: 'Sala 101'
      },
      {
        id: 2,
        code: 'MON-015',
        name: 'Monitor Samsung 24"',
        category: 'Informática',
        location: 'Sala 102'
      },
      {
        id: 3,
        code: 'SRV-001',
        name: 'Servidor Dell PowerEdge',
        category: 'Infraestrutura',
        location: 'Data Center'
      },
      {
        id: 4,
        code: 'CPU-025',
        name: 'Desktop HP ProDesk',
        category: 'Informática',
        location: 'Sala 201'
      },
      {
        id: 5,
        code: 'NB-002',
        name: 'Notebook Lenovo ThinkPad',
        category: 'Informática',
        location: 'Sala 105'
      }
    ],
    loading: false,
    error: null,
    searchTerm: '',
    filters: {
      status: '',
      priority: '',
      type: '',
      assignedTo: '',
      dateRange: { start: '', end: '' }
    }
  }),

  getters: {
    // Estatísticas gerais
    totalOrders: (state) => state.orders.length,
    
    ordersInProgress: (state) => 
      state.orders.filter(order => order.status === 'in_progress').length,
    
    overdueOrders: (state) => {
      const now = new Date()
      return state.orders.filter(order => 
        order.status !== 'completed' && 
        order.status !== 'cancelled' && 
        new Date(order.dueDate) < now
      ).length
    },
    
    completedOrders: (state) => 
      state.orders.filter(order => order.status === 'completed').length,

    // Ordens por status
    ordersByStatus: (state) => {
      return state.orders.reduce((acc, order) => {
        acc[order.status] = (acc[order.status] || 0) + 1
        return acc
      }, {})
    },

    // Ordens por tipo
    ordersByType: (state) => {
      return state.orders.reduce((acc, order) => {
        acc[order.type] = (acc[order.type] || 0) + 1
        return acc
      }, {})
    },

    // Ordens por prioridade
    ordersByPriority: (state) => {
      return state.orders.reduce((acc, order) => {
        acc[order.priority] = (acc[order.priority] || 0) + 1
        return acc
      }, {})
    },

    // Ordens por técnico
    ordersByTechnician: (state) => {
      return state.orders.reduce((acc, order) => {
        acc[order.assignedTo] = (acc[order.assignedTo] || 0) + 1
        return acc
      }, {})
    },

    // Tempo médio de resolução
    averageResolutionTime: (state) => {
      const completedOrders = state.orders.filter(order => 
        order.status === 'completed' && order.startedAt && order.completedAt
      )
      
      if (completedOrders.length === 0) return 0
      
      const totalHours = completedOrders.reduce((sum, order) => {
        const start = new Date(order.startedAt)
        const end = new Date(order.completedAt)
        const hours = (end - start) / (1000 * 60 * 60)
        return sum + hours
      }, 0)
      
      return Math.round(totalHours / completedOrders.length * 10) / 10
    },

    // Custo total das ordens
    totalCost: (state) => {
      return state.orders.reduce((sum, order) => sum + (order.cost || 0), 0)
    },

    // Ordens filtradas
    filteredOrders: (state) => {
      let filtered = [...state.orders]

      // Filtro por termo de busca
      if (state.searchTerm) {
        const term = state.searchTerm.toLowerCase()
        filtered = filtered.filter(order =>
          order.code.toLowerCase().includes(term) ||
          order.title.toLowerCase().includes(term) ||
          order.description.toLowerCase().includes(term) ||
          order.assignedTo.toLowerCase().includes(term) ||
          order.assetCode.toLowerCase().includes(term) ||
          order.assetName.toLowerCase().includes(term)
        )
      }

      // Filtro por status
      if (state.filters.status) {
        filtered = filtered.filter(order => order.status === state.filters.status)
      }

      // Filtro por prioridade
      if (state.filters.priority) {
        filtered = filtered.filter(order => order.priority === state.filters.priority)
      }

      // Filtro por tipo
      if (state.filters.type) {
        filtered = filtered.filter(order => order.type === state.filters.type)
      }

      // Filtro por técnico
      if (state.filters.assignedTo) {
        filtered = filtered.filter(order => order.assignedTo === state.filters.assignedTo)
      }

      // Filtro por período
      if (state.filters.dateRange.start && state.filters.dateRange.end) {
        filtered = filtered.filter(order => {
          const createdDate = new Date(order.createdAt)
          const filterStart = new Date(state.filters.dateRange.start)
          const filterEnd = new Date(state.filters.dateRange.end)
          return createdDate >= filterStart && createdDate <= filterEnd
        })
      }

      // Ordenar por prioridade e data de criação
      return filtered.sort((a, b) => {
        const priorityOrder = { urgent: 4, high: 3, medium: 2, low: 1 }
        const priorityDiff = priorityOrder[b.priority] - priorityOrder[a.priority]
        
        if (priorityDiff !== 0) return priorityDiff
        
        return new Date(b.createdAt) - new Date(a.createdAt)
      })
    }
  },

  actions: {
    // Buscar ordens
    async fetchOrders() {
      this.loading = true
      this.error = null
      
      try {
        // Simular chamada à API
        await new Promise(resolve => setTimeout(resolve, 1000))
        // Os dados já estão no state inicial
        this.loading = false
      } catch (error) {
        this.error = 'Erro ao carregar ordens de serviço'
        this.loading = false
        throw error
      }
    },

    // Criar nova ordem
    async createOrder(orderData) {
      this.loading = true
      this.error = null

      try {
        // Simular chamada à API
        await new Promise(resolve => setTimeout(resolve, 500))

        // Buscar dados do ativo selecionado
        const asset = this.availableAssets.find(a => a.id === parseInt(orderData.assetId))
        const technician = this.technicians.find(t => t.name === orderData.assignedTo)

        const newOrder = {
          id: Date.now(),
          code: `OS-${new Date().getFullYear()}-${String(this.orders.length + 1).padStart(3, '0')}`,
          ...orderData,
          assetCode: asset?.code || '',
          assetName: asset?.name || '',
          department: technician?.department || 'TI',
          status: 'open',
          createdAt: new Date().toISOString(),
          startedAt: null,
          completedAt: null,
          resolution: null,
          estimatedHours: 0,
          actualHours: 0,
          cost: 0
        }

        this.orders.unshift(newOrder)
        this.loading = false
        return newOrder
      } catch (error) {
        this.error = 'Erro ao criar ordem de serviço'
        this.loading = false
        throw error
      }
    },

    // Atualizar ordem
    async updateOrder(id, updates) {
      this.loading = true
      this.error = null

      try {
        // Simular chamada à API
        await new Promise(resolve => setTimeout(resolve, 500))

        const index = this.orders.findIndex(order => order.id === id)
        if (index !== -1) {
          // Se mudou o ativo, atualizar informações do ativo
          if (updates.assetId) {
            const asset = this.availableAssets.find(a => a.id === parseInt(updates.assetId))
            if (asset) {
              updates.assetCode = asset.code
              updates.assetName = asset.name
            }
          }

          // Se mudou o técnico, atualizar departamento
          if (updates.assignedTo) {
            const technician = this.technicians.find(t => t.name === updates.assignedTo)
            if (technician) {
              updates.department = technician.department
            }
          }

          this.orders[index] = {
            ...this.orders[index],
            ...updates
          }
        }

        this.loading = false
      } catch (error) {
        this.error = 'Erro ao atualizar ordem de serviço'
        this.loading = false
        throw error
      }
    },

    // Iniciar ordem
    async startOrder(id) {
      await this.updateOrder(id, { 
        status: 'in_progress',
        startedAt: new Date().toISOString()
      })
    },

    // Concluir ordem
    async completeOrder(id, resolution = '') {
      await this.updateOrder(id, { 
        status: 'completed',
        completedAt: new Date().toISOString(),
        resolution: resolution || 'Ordem concluída com sucesso.'
      })
    },

    // Cancelar ordem
    async cancelOrder(id, reason = '') {
      await this.updateOrder(id, { 
        status: 'cancelled',
        resolution: reason || 'Ordem cancelada.'
      })
    },

    // Deletar ordem
    async deleteOrder(id) {
      this.loading = true
      this.error = null

      try {
        // Simular chamada à API
        await new Promise(resolve => setTimeout(resolve, 500))

        const index = this.orders.findIndex(order => order.id === id)
        if (index !== -1) {
          this.orders.splice(index, 1)
        }

        this.loading = false
      } catch (error) {
        this.error = 'Erro ao deletar ordem de serviço'
        this.loading = false
        throw error
      }
    },

    // Buscar
    setSearchTerm(term) {
      this.searchTerm = term
    },

    // Filtros
    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
    },

    clearFilters() {
      this.filters = {
        status: '',
        priority: '',
        type: '',
        assignedTo: '',
        dateRange: { start: '', end: '' }
      }
      this.searchTerm = ''
    },

    // Exportar dados
    async exportOrders(format = 'csv') {
      try {
        const orders = this.filteredOrders
        
        if (format === 'csv') {
          const csvContent = this.generateCSV(orders)
          this.downloadFile(csvContent, `ordens_servico_${new Date().toISOString().split('T')[0]}.csv`, 'text/csv')
        }
        
        return true
      } catch (error) {
        this.error = 'Erro ao exportar dados'
        throw error
      }
    },

    // Gerar CSV
    generateCSV(orders) {
      const headers = [
        'Código',
        'Título',
        'Descrição',
        'Tipo',
        'Prioridade',
        'Status',
        'Ativo',
        'Técnico',
        'Departamento',
        'Data Criação',
        'Data Vencimento',
        'Data Início',
        'Data Conclusão',
        'Horas Estimadas',
        'Horas Reais',
        'Custo',
        'Observações',
        'Resolução'
      ]

      const rows = orders.map(order => [
        order.code,
        order.title,
        order.description,
        this.getTypeLabel(order.type),
        this.getPriorityLabel(order.priority),
        this.getStatusLabel(order.status),
        `${order.assetCode} - ${order.assetName}`,
        order.assignedTo,
        order.department,
        new Date(order.createdAt).toLocaleString('pt-BR'),
        new Date(order.dueDate).toLocaleString('pt-BR'),
        order.startedAt ? new Date(order.startedAt).toLocaleString('pt-BR') : '',
        order.completedAt ? new Date(order.completedAt).toLocaleString('pt-BR') : '',
        order.estimatedHours,
        order.actualHours,
        order.cost,
        order.notes || '',
        order.resolution || ''
      ])

      return [headers, ...rows]
        .map(row => row.map(field => `"${field}"`).join(','))
        .join('\n')
    },

    // Download de arquivo
    downloadFile(content, filename, contentType) {
      const blob = new Blob([content], { type: contentType })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    },

    // Obter label do status
    getStatusLabel(status) {
      const statusLabels = {
        open: 'Aberta',
        in_progress: 'Em Andamento',
        completed: 'Concluída',
        cancelled: 'Cancelada'
      }
      return statusLabels[status] || status
    },

    // Obter label do tipo
    getTypeLabel(type) {
      const typeLabels = {
        preventive: 'Preventiva',
        corrective: 'Corretiva',
        emergency: 'Emergencial'
      }
      return typeLabels[type] || type
    },

    // Obter label da prioridade
    getPriorityLabel(priority) {
      const priorityLabels = {
        low: 'Baixa',
        medium: 'Média',
        high: 'Alta',
        urgent: 'Urgente'
      }
      return priorityLabels[priority] || priority
    },

    // Obter cor do status
    getStatusColor(status) {
      const statusColors = {
        open: 'blue',
        in_progress: 'orange',
        completed: 'green',
        cancelled: 'gray'
      }
      return statusColors[status] || 'gray'
    },

    // Obter cor da prioridade
    getPriorityColor(priority) {
      const priorityColors = {
        low: 'blue',
        medium: 'yellow',
        high: 'red',
        urgent: 'purple'
      }
      return priorityColors[priority] || 'gray'
    },

    // Estatísticas avançadas
    getOrdersThisMonth() {
      const now = new Date()
      const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1)
      
      return this.orders.filter(order => 
        new Date(order.createdAt) >= startOfMonth
      ).length
    },

    getCompletionRate() {
      const totalOrders = this.orders.length
      if (totalOrders === 0) return 0
      
      const completedOrders = this.orders.filter(order => order.status === 'completed').length
      return Math.round((completedOrders / totalOrders) * 100)
    },

    getAverageResponseTime() {
      const startedOrders = this.orders.filter(order => 
        order.startedAt && order.createdAt
      )
      
      if (startedOrders.length === 0) return 0
      
      const totalHours = startedOrders.reduce((sum, order) => {
        const created = new Date(order.createdAt)
        const started = new Date(order.startedAt)
        const hours = (started - created) / (1000 * 60 * 60)
        return sum + hours
      }, 0)
      
      return Math.round(totalHours / startedOrders.length * 10) / 10
    }
  }
})