import { defineStore } from 'pinia'

export const useSchedulesStore = defineStore('schedules', {
  state: () => ({
    schedules: [
      {
        id: 1,
        title: 'Manutenção Preventiva - Servidores',
        description: 'Verificação geral dos servidores, limpeza e atualização de sistema',
        type: 'preventive',
        frequency: 'monthly',
        priority: 'high',
        status: 'active',
        assetId: 1,
        assetCode: 'SRV-001',
        assetName: 'Servidor Dell PowerEdge',
        assignedTo: 'Carlos Oliveira',
        department: 'TI',
        startDate: '2024-01-01',
        nextExecution: '2024-03-01',
        lastExecution: '2024-02-01',
        estimatedDuration: 4, // horas
        notes: 'Verificar temperatura, logs de erro e performance',
        createdAt: '2024-01-01T08:00:00Z',
        updatedAt: '2024-02-01T10:30:00Z',
        executionHistory: [
          {
            id: 1,
            executedAt: '2024-02-01T08:00:00Z',
            completedAt: '2024-02-01T12:00:00Z',
            status: 'completed',
            notes: 'Manutenção realizada com sucesso',
            technician: 'Carlos Oliveira'
          },
          {
            id: 2,
            executedAt: '2024-01-01T08:00:00Z',
            completedAt: '2024-01-01T11:30:00Z',
            status: 'completed',
            notes: 'Primeira execução do cronograma',
            technician: 'Carlos Oliveira'
          }
        ]
      },
      {
        id: 2,
        title: 'Backup e Verificação - Notebooks',
        description: 'Backup de dados e verificação de integridade dos notebooks',
        type: 'preventive',
        frequency: 'weekly',
        priority: 'medium',
        status: 'active',
        assetId: 2,
        assetCode: 'NB-001',
        assetName: 'Notebook Dell Latitude',
        assignedTo: 'João Silva',
        department: 'TI',
        startDate: '2024-01-15',
        nextExecution: '2024-02-19',
        lastExecution: '2024-02-12',
        estimatedDuration: 2,
        notes: 'Verificar backup automático e integridade dos dados',
        createdAt: '2024-01-15T09:00:00Z',
        updatedAt: '2024-02-12T14:00:00Z',
        executionHistory: [
          {
            id: 3,
            executedAt: '2024-02-12T09:00:00Z',
            completedAt: '2024-02-12T11:00:00Z',
            status: 'completed',
            notes: 'Backup verificado, tudo funcionando',
            technician: 'João Silva'
          }
        ]
      },
      {
        id: 3,
        title: 'Limpeza e Calibração - Impressoras',
        description: 'Limpeza interna e calibração das impressoras',
        type: 'preventive',
        frequency: 'quarterly',
        priority: 'low',
        status: 'active',
        assetId: 3,
        assetCode: 'IMP-001',
        assetName: 'Impressora HP LaserJet',
        assignedTo: 'Maria Santos',
        department: 'TI',
        startDate: '2024-01-01',
        nextExecution: '2024-04-01',
        lastExecution: '2024-01-01',
        estimatedDuration: 1,
        notes: 'Verificar qualidade de impressão e nível de toner',
        createdAt: '2024-01-01T10:00:00Z',
        updatedAt: '2024-01-01T10:00:00Z',
        executionHistory: [
          {
            id: 4,
            executedAt: '2024-01-01T10:00:00Z',
            completedAt: '2024-01-01T11:00:00Z',
            status: 'completed',
            notes: 'Limpeza realizada, calibração ok',
            technician: 'Maria Santos'
          }
        ]
      },
      {
        id: 4,
        title: 'Atualização de Antivírus',
        description: 'Atualização e verificação do sistema antivírus',
        type: 'preventive',
        frequency: 'daily',
        priority: 'high',
        status: 'paused',
        assetId: 4,
        assetCode: 'CPU-025',
        assetName: 'Desktop HP ProDesk',
        assignedTo: 'Ana Costa',
        department: 'TI',
        startDate: '2024-02-01',
        nextExecution: '2024-02-16',
        lastExecution: '2024-02-15',
        estimatedDuration: 0.5,
        notes: 'Verificação automática pausada para investigação',
        createdAt: '2024-02-01T08:00:00Z',
        updatedAt: '2024-02-15T16:00:00Z',
        executionHistory: []
      },
      {
        id: 5,
        title: 'Verificação de Rede',
        description: 'Teste de conectividade e performance da rede',
        type: 'preventive',
        frequency: 'weekly',
        priority: 'medium',
        status: 'active',
        assetId: 5,
        assetCode: 'SW-001',
        assetName: 'Switch Cisco 24 portas',
        assignedTo: 'Pedro Alves',
        department: 'TI',
        startDate: '2024-01-08',
        nextExecution: '2024-02-19',
        lastExecution: '2024-02-12',
        estimatedDuration: 3,
        notes: 'Verificar latência e throughput',
        createdAt: '2024-01-08T08:00:00Z',
        updatedAt: '2024-02-12T15:00:00Z',
        executionHistory: [
          {
            id: 5,
            executedAt: '2024-02-12T08:00:00Z',
            completedAt: '2024-02-12T11:00:00Z',
            status: 'completed',
            notes: 'Rede funcionando normalmente',
            technician: 'Pedro Alves'
          }
        ]
      }
    ],
    technicians: [
      { id: 1, name: 'João Silva', department: 'TI', specialties: ['Hardware', 'Backup'] },
      { id: 2, name: 'Maria Santos', department: 'TI', specialties: ['Impressoras', 'Periféricos'] },
      { id: 3, name: 'Carlos Oliveira', department: 'TI', specialties: ['Servidores', 'Infraestrutura'] },
      { id: 4, name: 'Ana Costa', department: 'TI', specialties: ['Software', 'Segurança'] },
      { id: 5, name: 'Pedro Alves', department: 'TI', specialties: ['Redes', 'Conectividade'] }
    ],
    availableAssets: [
      { id: 1, code: 'SRV-001', name: 'Servidor Dell PowerEdge', category: 'Infraestrutura' },
      { id: 2, code: 'NB-001', name: 'Notebook Dell Latitude', category: 'Informática' },
      { id: 3, code: 'IMP-001', name: 'Impressora HP LaserJet', category: 'Periféricos' },
      { id: 4, code: 'CPU-025', name: 'Desktop HP ProDesk', category: 'Informática' },
      { id: 5, code: 'SW-001', name: 'Switch Cisco 24 portas', category: 'Rede' }
    ],
    searchTerm: '',
    filters: {
      status: '',
      type: '',
      frequency: '',
      priority: '',
      assignedTo: '',
      dateRange: {
        start: '',
        end: ''
      }
    },
    loading: false,
    error: null
  }),

  getters: {
    // Estatísticas
    totalSchedules: (state) => state.schedules.length,
    activeSchedules: (state) => state.schedules.filter(s => s.status === 'active'),
    pausedSchedules: (state) => state.schedules.filter(s => s.status === 'paused'),
    overdueSchedules: (state) => {
      const today = new Date().toISOString().split('T')[0]
      return state.schedules.filter(s => 
        s.status === 'active' && s.nextExecution < today
      )
    },

    // Agendamentos por frequência
    schedulesByFrequency: (state) => {
      const frequencies = {}
      state.schedules.forEach(schedule => {
        frequencies[schedule.frequency] = (frequencies[schedule.frequency] || 0) + 1
      })
      return frequencies
    },

    // Agendamentos por prioridade
    schedulesByPriority: (state) => {
      const priorities = {}
      state.schedules.forEach(schedule => {
        priorities[schedule.priority] = (priorities[schedule.priority] || 0) + 1
      })
      return priorities
    },

    // Próximas execuções (próximos 7 dias)
    upcomingExecutions: (state) => {
      const today = new Date()
      const nextWeek = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
      
      return state.schedules
        .filter(s => s.status === 'active')
        .filter(s => {
          const nextExec = new Date(s.nextExecution)
          return nextExec >= today && nextExec <= nextWeek
        })
        .sort((a, b) => new Date(a.nextExecution) - new Date(b.nextExecution))
    },

    // Agendamentos filtrados
    filteredSchedules: (state) => {
      let filtered = state.schedules

      // Filtro de busca
      if (state.searchTerm) {
        const term = state.searchTerm.toLowerCase()
        filtered = filtered.filter(schedule =>
          schedule.title.toLowerCase().includes(term) ||
          schedule.description.toLowerCase().includes(term) ||
          schedule.assetCode.toLowerCase().includes(term) ||
          schedule.assetName.toLowerCase().includes(term) ||
          schedule.assignedTo.toLowerCase().includes(term)
        )
      }

      // Filtros específicos
      if (state.filters.status) {
        filtered = filtered.filter(s => s.status === state.filters.status)
      }

      if (state.filters.type) {
        filtered = filtered.filter(s => s.type === state.filters.type)
      }

      if (state.filters.frequency) {
        filtered = filtered.filter(s => s.frequency === state.filters.frequency)
      }

      if (state.filters.priority) {
        filtered = filtered.filter(s => s.priority === state.filters.priority)
      }

      if (state.filters.assignedTo) {
        filtered = filtered.filter(s => s.assignedTo === state.filters.assignedTo)
      }

      // Filtro de data
      if (state.filters.dateRange.start && state.filters.dateRange.end) {
        filtered = filtered.filter(s => {
          const nextExec = s.nextExecution
          return nextExec >= state.filters.dateRange.start && 
                 nextExec <= state.filters.dateRange.end
        })
      }

      return filtered
    }
  },

  actions: {
    // Buscar agendamentos
    async fetchSchedules() {
      this.loading = true
      this.error = null

      try {
        // Simular chamada à API
        await new Promise(resolve => setTimeout(resolve, 500))
        this.loading = false
      } catch (error) {
        this.error = 'Erro ao carregar agendamentos'
        this.loading = false
        throw error
      }
    },

    // Criar agendamento
    async createSchedule(scheduleData) {
      this.loading = true
      this.error = null

      try {
        // Simular chamada à API
        await new Promise(resolve => setTimeout(resolve, 300))

        const newSchedule = {
          id: Date.now(),
          ...scheduleData,
          status: 'active',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          executionHistory: []
        }

        this.schedules.unshift(newSchedule)
        this.loading = false
      } catch (error) {
        this.error = 'Erro ao criar agendamento'
        this.loading = false
        throw error
      }
    },

    // Atualizar agendamento
    async updateSchedule(id, scheduleData) {
      this.loading = true
      this.error = null

      try {
        // Simular chamada à API
        await new Promise(resolve => setTimeout(resolve, 300))

        const index = this.schedules.findIndex(s => s.id === id)
        if (index !== -1) {
          this.schedules[index] = {
            ...this.schedules[index],
            ...scheduleData,
            updatedAt: new Date().toISOString()
          }
        }

        this.loading = false
      } catch (error) {
        this.error = 'Erro ao atualizar agendamento'
        this.loading = false
        throw error
      }
    },

    // Pausar/Reativar agendamento
    async toggleScheduleStatus(id) {
      this.loading = true
      this.error = null

      try {
        // Simular chamada à API
        await new Promise(resolve => setTimeout(resolve, 300))

        const schedule = this.schedules.find(s => s.id === id)
        if (schedule) {
          schedule.status = schedule.status === 'active' ? 'paused' : 'active'
          schedule.updatedAt = new Date().toISOString()
        }

        this.loading = false
      } catch (error) {
        this.error = 'Erro ao alterar status do agendamento'
        this.loading = false
        throw error
      }
    },

    // Executar agendamento manualmente
    async executeSchedule(id, notes = '') {
      this.loading = true
      this.error = null

      try {
        // Simular chamada à API
        await new Promise(resolve => setTimeout(resolve, 500))

        const schedule = this.schedules.find(s => s.id === id)
        if (schedule) {
          // Adicionar execução ao histórico
          const execution = {
            id: Date.now(),
            executedAt: new Date().toISOString(),
            completedAt: new Date().toISOString(),
            status: 'completed',
            notes: notes || 'Execução manual',
            technician: schedule.assignedTo
          }

          schedule.executionHistory.unshift(execution)
          schedule.lastExecution = new Date().toISOString().split('T')[0]
          
          // Calcular próxima execução
          schedule.nextExecution = this.calculateNextExecution(schedule.frequency, schedule.lastExecution)
          schedule.updatedAt = new Date().toISOString()
        }

        this.loading = false
      } catch (error) {
        this.error = 'Erro ao executar agendamento'
        this.loading = false
        throw error
      }
    },

    // Deletar agendamento
    async deleteSchedule(id) {
      this.loading = true
      this.error = null

      try {
        // Simular chamada à API
        await new Promise(resolve => setTimeout(resolve, 300))

        const index = this.schedules.findIndex(s => s.id === id)
        if (index !== -1) {
          this.schedules.splice(index, 1)
        }

        this.loading = false
      } catch (error) {
        this.error = 'Erro ao deletar agendamento'
        this.loading = false
        throw error
      }
    },

    // Calcular próxima execução
    calculateNextExecution(frequency, lastExecution) {
      const last = new Date(lastExecution)
      
      switch (frequency) {
        case 'daily':
          last.setDate(last.getDate() + 1)
          break
        case 'weekly':
          last.setDate(last.getDate() + 7)
          break
        case 'monthly':
          last.setMonth(last.getMonth() + 1)
          break
        case 'quarterly':
          last.setMonth(last.getMonth() + 3)
          break
        case 'yearly':
          last.setFullYear(last.getFullYear() + 1)
          break
        default:
          last.setDate(last.getDate() + 1)
      }
      
      return last.toISOString().split('T')[0]
    },

    // Exportar dados
    async exportSchedules() {
      this.loading = true
      this.error = null

      try {
        // Simular chamada à API
        await new Promise(resolve => setTimeout(resolve, 500))

        const csvData = this.generateCSV()
        this.downloadFile(csvData, 'agendamentos.csv', 'text/csv')

        this.loading = false
      } catch (error) {
        this.error = 'Erro ao exportar dados'
        this.loading = false
        throw error
      }
    },

    // Gerar CSV
    generateCSV() {
      const headers = [
        'Código',
        'Título',
        'Tipo',
        'Frequência',
        'Prioridade',
        'Status',
        'Ativo',
        'Responsável',
        'Próxima Execução',
        'Última Execução'
      ]

      const rows = this.filteredSchedules.map(schedule => [
        schedule.id,
        schedule.title,
        schedule.type,
        schedule.frequency,
        schedule.priority,
        schedule.status,
        `${schedule.assetCode} - ${schedule.assetName}`,
        schedule.assignedTo,
        schedule.nextExecution,
        schedule.lastExecution || 'Nunca'
      ])

      return [headers, ...rows]
        .map(row => row.map(cell => `"${cell}"`).join(','))
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

    // Definir termo de busca
    setSearchTerm(term) {
      this.searchTerm = term
    },

    // Definir filtros
    setFilters(filters) {
      this.filters = { ...this.filters, ...filters }
    },

    // Limpar filtros
    clearFilters() {
      this.searchTerm = ''
      this.filters = {
        status: '',
        type: '',
        frequency: '',
        priority: '',
        assignedTo: '',
        dateRange: {
          start: '',
          end: ''
        }
      }
    },

    // Obter labels
    getStatusLabel(status) {
      const labels = {
        active: 'Ativo',
        paused: 'Pausado',
        inactive: 'Inativo'
      }
      return labels[status] || status
    },

    getTypeLabel(type) {
      const labels = {
        preventive: 'Preventiva',
        corrective: 'Corretiva'
      }
      return labels[type] || type
    },

    getFrequencyLabel(frequency) {
      const labels = {
        daily: 'Diário',
        weekly: 'Semanal',
        monthly: 'Mensal',
        quarterly: 'Trimestral',
        yearly: 'Anual'
      }
      return labels[frequency] || frequency
    },

    getPriorityLabel(priority) {
      const labels = {
        low: 'Baixa',
        medium: 'Média',
        high: 'Alta',
        urgent: 'Urgente'
      }
      return labels[priority] || priority
    }
  }
})