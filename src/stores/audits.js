import { defineStore } from 'pinia'

export const useAuditsStore = defineStore('audits', {
  state: () => ({
    audits: [
      {
        id: 1,
        code: 'AUD-2024-001',
        title: 'Auditoria Anual de Inventário',
        description: 'Auditoria completa do inventário de ativos da empresa',
        type: 'inventory',
        status: 'in_progress',
        priority: 'high',
        progress: 65,
        auditor: {
          id: 1,
          name: 'Ana Silva',
          email: 'ana.silva@empresa.com'
        },
        team: [
          { id: 1, name: 'Ana Silva', role: 'Auditor Principal' },
          { id: 2, name: 'João Santos', role: 'Auditor Assistente' }
        ],
        location: {
          id: 1,
          name: 'Sede Principal',
          address: 'Av. Paulista, 1000'
        },
        startDate: '2024-01-15',
        endDate: '2024-02-15',
        plannedHours: 120,
        actualHours: 78,
        objectives: [
          'Verificar a precisão do inventário de ativos',
          'Identificar discrepâncias entre sistema e físico',
          'Avaliar controles de movimentação de ativos'
        ],
        scope: 'Todos os ativos de TI da sede principal',
        methodology: 'Contagem física e reconciliação com sistema',
        findings: [
          {
            id: 1,
            type: 'discrepancy',
            title: 'Notebooks não localizados',
            description: '5 notebooks não foram encontrados no setor de TI',
            severity: 'high',
            status: 'open',
            assignedTo: 'João Santos',
            dueDate: '2024-02-01',
            createdAt: '2024-01-18T10:30:00Z'
          },
          {
            id: 2,
            type: 'control_weakness',
            title: 'Controle de acesso inadequado',
            description: 'Almoxarifado sem controle adequado de entrada e saída',
            severity: 'medium',
            status: 'in_progress',
            assignedTo: 'Ana Silva',
            dueDate: '2024-01-30',
            createdAt: '2024-01-20T14:15:00Z'
          }
        ],
        recommendations: [
          'Implementar sistema de rastreamento RFID',
          'Melhorar controles de acesso ao almoxarifado',
          'Realizar inventários trimestrais'
        ],
        attachments: [
          { id: 1, name: 'checklist_auditoria.pdf', size: '2.5 MB' },
          { id: 2, name: 'fotos_evidencias.zip', size: '15.2 MB' }
        ],
        createdAt: '2024-01-10T10:00:00Z',
        updatedAt: '2024-01-20T15:30:00Z'
      },
      {
        id: 2,
        code: 'AUD-2024-002',
        title: 'Auditoria de Conformidade SOX',
        description: 'Verificação de conformidade com regulamentações SOX',
        type: 'compliance',
        status: 'planned',
        priority: 'high',
        progress: 0,
        auditor: {
          id: 2,
          name: 'Carlos Santos',
          email: 'carlos.santos@empresa.com'
        },
        team: [
          { id: 2, name: 'Carlos Santos', role: 'Auditor Principal' },
          { id: 3, name: 'Maria Oliveira', role: 'Especialista SOX' }
        ],
        location: {
          id: 2,
          name: 'Filial São Paulo',
          address: 'Rua Augusta, 500'
        },
        startDate: '2024-02-01',
        endDate: '2024-02-28',
        plannedHours: 200,
        actualHours: 0,
        objectives: [
          'Garantir conformidade com controles internos SOX',
          'Avaliar eficácia dos controles financeiros',
          'Identificar gaps de conformidade'
        ],
        scope: 'Controles financeiros e de TI relacionados ao SOX',
        methodology: 'Testes de controles e revisão documental',
        findings: [],
        recommendations: [],
        attachments: [],
        createdAt: '2024-01-05T09:00:00Z',
        updatedAt: '2024-01-05T09:00:00Z'
      },
      {
        id: 3,
        code: 'AUD-2023-015',
        title: 'Auditoria de Segurança da Informação',
        description: 'Avaliação dos controles de segurança da informação',
        type: 'security',
        status: 'completed',
        priority: 'high',
        progress: 100,
        auditor: {
          id: 3,
          name: 'Maria Oliveira',
          email: 'maria.oliveira@empresa.com'
        },
        team: [
          { id: 3, name: 'Maria Oliveira', role: 'Auditor Principal' },
          { id: 4, name: 'Pedro Costa', role: 'Especialista Segurança' }
        ],
        location: {
          id: 1,
          name: 'Sede Principal',
          address: 'Av. Paulista, 1000'
        },
        startDate: '2023-12-01',
        endDate: '2023-12-31',
        plannedHours: 160,
        actualHours: 155,
        objectives: [
          'Avaliar eficácia dos controles de segurança',
          'Verificar conformidade com políticas de segurança',
          'Identificar vulnerabilidades'
        ],
        scope: 'Infraestrutura de TI e políticas de segurança',
        methodology: 'Testes de penetração e revisão de políticas',
        findings: [
          {
            id: 3,
            type: 'vulnerability',
            title: 'Senhas fracas em sistemas',
            description: 'Identificadas senhas fracas em alguns sistemas críticos',
            severity: 'medium',
            status: 'resolved',
            assignedTo: 'Pedro Costa',
            dueDate: '2023-12-20',
            createdAt: '2023-12-10T09:00:00Z'
          },
          {
            id: 4,
            type: 'non_compliance',
            title: 'Backup não testado',
            description: 'Backup não foi testado nos últimos 6 meses',
            severity: 'high',
            status: 'resolved',
            assignedTo: 'Maria Oliveira',
            dueDate: '2023-12-25',
            createdAt: '2023-12-12T14:30:00Z'
          }
        ],
        recommendations: [
          'Implementar política de senhas mais rigorosa',
          'Estabelecer cronograma regular de testes de backup',
          'Realizar treinamentos de segurança'
        ],
        attachments: [
          { id: 3, name: 'relatorio_seguranca.pdf', size: '5.8 MB' },
          { id: 4, name: 'evidencias_testes.zip', size: '25.1 MB' }
        ],
        createdAt: '2023-11-15T14:00:00Z',
        updatedAt: '2024-01-05T16:45:00Z'
      },
      {
        id: 4,
        code: 'AUD-2024-003',
        title: 'Auditoria de Processos Operacionais',
        description: 'Revisão dos processos operacionais da empresa',
        type: 'operational',
        status: 'draft',
        priority: 'medium',
        progress: 0,
        auditor: {
          id: 4,
          name: 'Roberto Lima',
          email: 'roberto.lima@empresa.com'
        },
        team: [
          { id: 4, name: 'Roberto Lima', role: 'Auditor Principal' }
        ],
        location: {
          id: 3,
          name: 'Filial Rio de Janeiro',
          address: 'Av. Copacabana, 200'
        },
        startDate: '2024-03-01',
        endDate: '2024-03-31',
        plannedHours: 100,
        actualHours: 0,
        objectives: [
          'Avaliar eficiência dos processos operacionais',
          'Identificar oportunidades de melhoria',
          'Verificar aderência aos procedimentos'
        ],
        scope: 'Processos de produção e logística',
        methodology: 'Observação direta e entrevistas',
        findings: [],
        recommendations: [],
        attachments: [],
        createdAt: '2024-01-25T11:00:00Z',
        updatedAt: '2024-01-25T11:00:00Z'
      }
    ],
    filters: {
      search: '',
      type: '',
      status: '',
      priority: '',
      auditor: '',
      location: ''
    },
    loading: false,
    error: null
  }),

  getters: {
    // Filtros básicos
    filteredAudits: (state) => {
      let filtered = [...state.audits]

      if (state.filters.search) {
        const search = state.filters.search.toLowerCase()
        filtered = filtered.filter(audit => 
          audit.title.toLowerCase().includes(search) ||
          audit.code.toLowerCase().includes(search) ||
          audit.description.toLowerCase().includes(search) ||
          audit.auditor.name.toLowerCase().includes(search)
        )
      }

      if (state.filters.type) {
        filtered = filtered.filter(audit => audit.type === state.filters.type)
      }

      if (state.filters.status) {
        filtered = filtered.filter(audit => audit.status === state.filters.status)
      }

      if (state.filters.priority) {
        filtered = filtered.filter(audit => audit.priority === state.filters.priority)
      }

      if (state.filters.auditor) {
        filtered = filtered.filter(audit => audit.auditor.id === parseInt(state.filters.auditor))
      }

      if (state.filters.location) {
        filtered = filtered.filter(audit => audit.location.id === parseInt(state.filters.location))
      }

      return filtered
    },

    // Estatísticas
    totalAudits: (state) => state.audits.length,
    
    auditsByStatus: (state) => {
      const statusCount = {}
      state.audits.forEach(audit => {
        statusCount[audit.status] = (statusCount[audit.status] || 0) + 1
      })
      return statusCount
    },

    activeAudits: (state) => state.audits.filter(audit => audit.status === 'in_progress'),
    
    completedAudits: (state) => state.audits.filter(audit => audit.status === 'completed'),
    
    plannedAudits: (state) => state.audits.filter(audit => audit.status === 'planned'),
    
    draftAudits: (state) => state.audits.filter(audit => audit.status === 'draft'),

    // Por tipo
    auditsByType: (state) => {
      const typeCount = {}
      state.audits.forEach(audit => {
        typeCount[audit.type] = (typeCount[audit.type] || 0) + 1
      })
      return typeCount
    },

    // Por prioridade
    auditsByPriority: (state) => {
      const priorityCount = {}
      state.audits.forEach(audit => {
        priorityCount[audit.priority] = (priorityCount[audit.priority] || 0) + 1
      })
      return priorityCount
    },

    // Auditorias com problemas
    auditsWithIssues: (state) => {
      return state.audits.filter(audit => 
        audit.findings.some(finding => finding.status === 'open' && finding.severity === 'high')
      )
    },

    // Progresso médio
    averageProgress: (state) => {
      if (state.audits.length === 0) return 0
      const totalProgress = state.audits.reduce((sum, audit) => sum + audit.progress, 0)
      return Math.round(totalProgress / state.audits.length)
    },

    // Auditores únicos
    uniqueAuditors: (state) => {
      const auditors = state.audits.map(audit => audit.auditor)
      return auditors.filter((auditor, index, self) => 
        index === self.findIndex(a => a.id === auditor.id)
      )
    },

    // Localizações únicas
    uniqueLocations: (state) => {
      const locations = state.audits.map(audit => audit.location)
      return locations.filter((location, index, self) => 
        index === self.findIndex(l => l.id === location.id)
      )
    },

    // Tipos disponíveis
    availableTypes: () => [
      { value: 'inventory', label: 'Inventário' },
      { value: 'compliance', label: 'Conformidade' },
      { value: 'security', label: 'Segurança' },
      { value: 'operational', label: 'Operacional' },
      { value: 'financial', label: 'Financeira' },
      { value: 'quality', label: 'Qualidade' }
    ],

    // Status disponíveis
    availableStatuses: () => [
      { value: 'draft', label: 'Rascunho' },
      { value: 'planned', label: 'Planejada' },
      { value: 'in_progress', label: 'Em Andamento' },
      { value: 'completed', label: 'Concluída' },
      { value: 'cancelled', label: 'Cancelada' }
    ],

    // Prioridades disponíveis
    availablePriorities: () => [
      { value: 'low', label: 'Baixa' },
      { value: 'medium', label: 'Média' },
      { value: 'high', label: 'Alta' },
      { value: 'critical', label: 'Crítica' }
    ]
  },

  actions: {
    // Adicionar auditoria
    addAudit(auditData) {
      const newAudit = {
        id: Math.max(...this.audits.map(a => a.id), 0) + 1,
        code: this.generateAuditCode(),
        ...auditData,
        progress: 0,
        findings: [],
        recommendations: [],
        attachments: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
      
      this.audits.push(newAudit)
      return newAudit
    },

    // Atualizar auditoria
    updateAudit(id, updates) {
      const index = this.audits.findIndex(audit => audit.id === id)
      if (index !== -1) {
        this.audits[index] = {
          ...this.audits[index],
          ...updates,
          updatedAt: new Date().toISOString()
        }
        return this.audits[index]
      }
      return null
    },

    // Excluir auditoria
    deleteAudit(id) {
      const index = this.audits.findIndex(audit => audit.id === id)
      if (index !== -1) {
        this.audits.splice(index, 1)
        return true
      }
      return false
    },

    // Buscar auditoria por ID
    findAuditById(id) {
      return this.audits.find(audit => audit.id === id)
    },

    // Iniciar auditoria
    startAudit(id) {
      const audit = this.findAuditById(id)
      if (audit && audit.status === 'planned') {
        audit.status = 'in_progress'
        audit.updatedAt = new Date().toISOString()
        return audit
      }
      return null
    },

    // Concluir auditoria
    completeAudit(id) {
      const audit = this.findAuditById(id)
      if (audit && audit.status === 'in_progress') {
        audit.status = 'completed'
        audit.progress = 100
        audit.updatedAt = new Date().toISOString()
        return audit
      }
      return null
    },

    // Cancelar auditoria
    cancelAudit(id) {
      const audit = this.findAuditById(id)
      if (audit && ['planned', 'in_progress'].includes(audit.status)) {
        audit.status = 'cancelled'
        audit.updatedAt = new Date().toISOString()
        return audit
      }
      return null
    },

    // Atualizar progresso
    updateProgress(id, progress) {
      const audit = this.findAuditById(id)
      if (audit) {
        audit.progress = Math.min(100, Math.max(0, progress))
        audit.updatedAt = new Date().toISOString()
        return audit
      }
      return null
    },

    // Adicionar achado
    addFinding(auditId, findingData) {
      const audit = this.findAuditById(auditId)
      if (audit) {
        const newFinding = {
          id: Math.max(...audit.findings.map(f => f.id), 0) + 1,
          ...findingData,
          createdAt: new Date().toISOString()
        }
        audit.findings.push(newFinding)
        audit.updatedAt = new Date().toISOString()
        return newFinding
      }
      return null
    },

    // Atualizar achado
    updateFinding(auditId, findingId, updates) {
      const audit = this.findAuditById(auditId)
      if (audit) {
        const findingIndex = audit.findings.findIndex(f => f.id === findingId)
        if (findingIndex !== -1) {
          audit.findings[findingIndex] = {
            ...audit.findings[findingIndex],
            ...updates
          }
          audit.updatedAt = new Date().toISOString()
          return audit.findings[findingIndex]
        }
      }
      return null
    },

    // Gerar código de auditoria
    generateAuditCode() {
      const year = new Date().getFullYear()
      const count = this.audits.filter(a => a.code.includes(year.toString())).length + 1
      return `AUD-${year}-${count.toString().padStart(3, '0')}`
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

    setPriorityFilter(priority) {
      this.filters.priority = priority
    },

    setAuditorFilter(auditor) {
      this.filters.auditor = auditor
    },

    setLocationFilter(location) {
      this.filters.location = location
    },

    clearFilters() {
      this.filters = {
        search: '',
        type: '',
        status: '',
        priority: '',
        auditor: '',
        location: ''
      }
    },

    // Exportar dados
    exportAudits() {
      return this.filteredAudits.map(audit => ({
        Código: audit.code,
        Título: audit.title,
        Tipo: this.availableTypes.find(t => t.value === audit.type)?.label || audit.type,
        Status: this.availableStatuses.find(s => s.value === audit.status)?.label || audit.status,
        Prioridade: this.availablePriorities.find(p => p.value === audit.priority)?.label || audit.priority,
        Auditor: audit.auditor.name,
        Localização: audit.location.name,
        'Data Início': audit.startDate,
        'Data Fim': audit.endDate,
        'Progresso (%)': audit.progress,
        'Achados': audit.findings.length,
        'Data Criação': new Date(audit.createdAt).toLocaleDateString('pt-BR')
      }))
    }
  }
})