import logger from '@/utils/logger'
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useThirdPartyLoansStore = defineStore('thirdPartyLoans', () => {
  // Estado
  const loans = ref([
    {
      id: 1,
      code: 'TER001',
      thirdParty: {
        id: 1,
        name: 'TechSolutions Ltda',
        type: 'Empresa',
        document: '12.345.678/0001-90',
        contactName: 'Roberto Mendes',
        contactEmail: 'roberto@techsolutions.com',
        contactPhone: '(11) 98765-4321',
        address: 'Rua das Flores, 123 - São Paulo/SP'
      },
      asset: {
        id: 1,
        name: 'Projetor Epson PowerLite',
        code: 'PROJ001',
        category: 'Audiovisual',
        serialNumber: 'EP789123456'
      },
      loanDate: '2024-01-10',
      expectedReturnDate: '2024-01-20',
      returnDate: '2024-01-18',
      status: 'Devolvido',
      purpose: 'Apresentação de projeto para cliente',
      notes: 'Empréstimo para evento corporativo',
      condition: 'Perfeito',
      returnNotes: 'Devolvido em perfeitas condições após evento',
      createdAt: '2024-01-10T09:00:00Z',
      updatedAt: '2024-01-18T17:30:00Z'
    },
    {
      id: 2,
      code: 'TER002',
      thirdParty: {
        id: 2,
        name: 'João Carlos Silva',
        type: 'Pessoa Física',
        document: '123.456.789-00',
        contactName: 'João Carlos Silva',
        contactEmail: 'joao.carlos@email.com',
        contactPhone: '(11) 99876-5432',
        address: 'Av. Paulista, 456 - São Paulo/SP'
      },
      asset: {
        id: 2,
        name: 'Notebook Dell Latitude 5520',
        code: 'NB001',
        category: 'Informática',
        serialNumber: 'DL123456789'
      },
      loanDate: '2024-01-15',
      expectedReturnDate: '2024-02-15',
      returnDate: null,
      status: 'Ativo',
      purpose: 'Trabalho freelance de desenvolvimento',
      notes: 'Empréstimo para projeto de 30 dias',
      condition: null,
      returnNotes: null,
      createdAt: '2024-01-15T14:00:00Z',
      updatedAt: '2024-01-15T14:00:00Z'
    },
    {
      id: 3,
      code: 'TER003',
      thirdParty: {
        id: 3,
        name: 'Consultoria ABC',
        type: 'Prestador de Serviço',
        document: '98.765.432/0001-10',
        contactName: 'Maria Fernanda',
        contactEmail: 'maria@consultoriaabc.com',
        contactPhone: '(11) 97654-3210',
        address: 'Rua Augusta, 789 - São Paulo/SP'
      },
      asset: {
        id: 3,
        name: 'Tablet iPad Pro',
        code: 'TAB001',
        category: 'Informática',
        serialNumber: 'IP456789123'
      },
      loanDate: '2024-01-05',
      expectedReturnDate: '2024-01-12',
      returnDate: null,
      status: 'Em Atraso',
      purpose: 'Auditoria de processos',
      notes: 'Empréstimo para consultoria externa',
      condition: null,
      returnNotes: null,
      createdAt: '2024-01-05T10:30:00Z',
      updatedAt: '2024-01-05T10:30:00Z'
    },
    {
      id: 4,
      code: 'TER004',
      thirdParty: {
        id: 4,
        name: 'EventPro Produções',
        type: 'Empresa',
        document: '11.222.333/0001-44',
        contactName: 'Carlos Eduardo',
        contactEmail: 'carlos@eventpro.com',
        contactPhone: '(11) 96543-2109',
        address: 'Rua dos Eventos, 321 - São Paulo/SP'
      },
      asset: {
        id: 4,
        name: 'Câmera Canon EOS R6',
        code: 'CAM001',
        category: 'Audiovisual',
        serialNumber: 'CN987654321'
      },
      loanDate: '2024-01-20',
      expectedReturnDate: '2024-01-25',
      returnDate: null,
      status: 'Ativo',
      purpose: 'Cobertura fotográfica de evento corporativo',
      notes: 'Empréstimo para evento de lançamento',
      condition: null,
      returnNotes: null,
      createdAt: '2024-01-20T11:15:00Z',
      updatedAt: '2024-01-20T11:15:00Z'
    }
  ])

  const availableAssets = ref([
    { id: 1, name: 'Projetor Epson PowerLite', code: 'PROJ001', category: 'Audiovisual', status: 'Disponível' },
    { id: 2, name: 'Notebook Dell Latitude 5520', code: 'NB001', category: 'Informática', status: 'Emprestado' },
    { id: 3, name: 'Tablet iPad Pro', code: 'TAB001', category: 'Informática', status: 'Emprestado' },
    { id: 4, name: 'Câmera Canon EOS R6', code: 'CAM001', category: 'Audiovisual', status: 'Emprestado' },
    { id: 5, name: 'Monitor LG UltraWide', code: 'MON001', category: 'Informática', status: 'Disponível' },
    { id: 6, name: 'Impressora HP LaserJet', code: 'IMP001', category: 'Informática', status: 'Disponível' },
    { id: 7, name: 'Smartphone Samsung Galaxy', code: 'CEL001', category: 'Comunicação', status: 'Disponível' },
    { id: 8, name: 'Microfone Shure SM58', code: 'MIC001', category: 'Audiovisual', status: 'Disponível' },
    { id: 9, name: 'Switch Cisco 24 portas', code: 'SW001', category: 'Rede', status: 'Disponível' }
  ])

  const loading = ref(false)
  const error = ref(null)

  // Getters
  const totalLoans = computed(() => loans.value.length)
  
  const activeLoans = computed(() => {
    return loans.value.filter(loan => loan.status === 'Ativo')
  })

  const overdueLoans = computed(() => {
    const today = new Date()
    return loans.value.filter(loan => {
      if (loan.status !== 'Ativo') return false
      const expectedDate = new Date(loan.expectedReturnDate)
      return expectedDate < today
    })
  })

  const returnedLoans = computed(() => {
    return loans.value.filter(loan => loan.status === 'Devolvido')
  })

  const loansByType = computed(() => {
    const types = {}
    loans.value.forEach(loan => {
      const type = loan.thirdParty.type
      if (!types[type]) {
        types[type] = 0
      }
      types[type]++
    })
    return types
  })

  const loansByStatus = computed(() => {
    const statuses = {}
    loans.value.forEach(loan => {
      if (!statuses[loan.status]) {
        statuses[loan.status] = 0
      }
      statuses[loan.status]++
    })
    return statuses
  })

  const assetsOnLoan = computed(() => {
    return loans.value
      .filter(loan => loan.status === 'Ativo')
      .map(loan => loan.asset.id)
  })

  const availableAssetsForLoan = computed(() => {
    return availableAssets.value.filter(asset => 
      asset.status === 'Disponível' && !assetsOnLoan.value.includes(asset.id)
    )
  })

  const loansByMonth = computed(() => {
    const months = {}
    loans.value.forEach(loan => {
      const month = new Date(loan.loanDate).toISOString().slice(0, 7) // YYYY-MM
      if (!months[month]) {
        months[month] = 0
      }
      months[month]++
    })
    return months
  })

  // Actions
  const fetchLoans = async () => {
    loading.value = true
    error.value = null
    
    try {
      // Simular chamada à API
      await new Promise(resolve => setTimeout(resolve, 1000))
      // Em uma aplicação real, aqui seria feita a chamada à API
      // const response = await api.get('/third-party-loans')
      // loans.value = response.data
      
      loading.value = false
    } catch (err) {
      error.value = err.message
      loading.value = false
      throw err
    }
  }

  const createLoan = async (loanData) => {
    loading.value = true
    error.value = null

    try {
      // Validações
      const asset = availableAssets.value.find(a => a.id === loanData.assetId)
      
      if (!asset) {
        throw new Error('Ativo não encontrado')
      }
      
      if (asset.status !== 'Disponível') {
        throw new Error('Ativo não está disponível para empréstimo')
      }

      // Validar datas
      const loanDate = new Date(loanData.loanDate)
      const expectedReturnDate = new Date(loanData.expectedReturnDate)
      
      if (expectedReturnDate <= loanDate) {
        throw new Error('A data prevista de devolução deve ser posterior à data do empréstimo')
      }

      // Validar campos obrigatórios
      if (!loanData.thirdPartyName || !loanData.contactName || !loanData.contactEmail) {
        throw new Error('Todos os campos obrigatórios devem ser preenchidos')
      }

      // Simular chamada à API
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const newThirdParty = {
        id: Date.now(),
        name: loanData.thirdPartyName,
        type: loanData.thirdPartyType,
        document: loanData.thirdPartyDocument || '',
        contactName: loanData.contactName,
        contactEmail: loanData.contactEmail,
        contactPhone: loanData.contactPhone || '',
        address: ''
      }

      const newLoan = {
        id: Date.now() + 1,
        code: `TER${String(loans.value.length + 1).padStart(3, '0')}`,
        thirdParty: newThirdParty,
        asset,
        loanDate: loanData.loanDate,
        expectedReturnDate: loanData.expectedReturnDate,
        returnDate: null,
        status: 'Ativo',
        purpose: loanData.purpose || '',
        notes: loanData.notes || '',
        condition: null,
        returnNotes: null,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }

      loans.value.push(newLoan)
      
      // Atualizar status do ativo
      const assetIndex = availableAssets.value.findIndex(a => a.id === loanData.assetId)
      if (assetIndex !== -1) {
        availableAssets.value[assetIndex].status = 'Emprestado'
      }
      
      loading.value = false
      return newLoan
      
    } catch (err) {
      error.value = err.message
      loading.value = false
      throw err
    }
  }

  const returnLoan = async (loanId, returnData) => {
    loading.value = true
    error.value = null

    try {
      // Simular chamada à API
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const loanIndex = loans.value.findIndex(loan => loan.id === loanId)
      if (loanIndex === -1) {
        throw new Error('Empréstimo não encontrado')
      }

      const loan = loans.value[loanIndex]
      if (loan.status !== 'Ativo' && loan.status !== 'Em Atraso') {
        throw new Error('Este empréstimo não está ativo')
      }

      // Validar data de devolução
      const returnDate = new Date(returnData.returnDate)
      const loanDate = new Date(loan.loanDate)
      
      if (returnDate < loanDate) {
        throw new Error('A data de devolução não pode ser anterior à data do empréstimo')
      }

      // Atualizar empréstimo
      loans.value[loanIndex] = {
        ...loan,
        returnDate: returnData.returnDate,
        status: 'Devolvido',
        condition: returnData.condition,
        returnNotes: returnData.returnNotes || '',
        updatedAt: new Date().toISOString()
      }

      // Atualizar status do ativo
      const assetIndex = availableAssets.value.findIndex(a => a.id === loan.asset.id)
      if (assetIndex !== -1) {
        availableAssets.value[assetIndex].status = 'Disponível'
      }
      
      loading.value = false
      return loans.value[loanIndex]
      
    } catch (err) {
      error.value = err.message
      loading.value = false
      throw err
    }
  }

  const updateLoan = async (loanId, loanData) => {
    loading.value = true
    error.value = null

    try {
      // Simular chamada à API
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const loanIndex = loans.value.findIndex(loan => loan.id === loanId)
      if (loanIndex === -1) {
        throw new Error('Empréstimo não encontrado')
      }

      loans.value[loanIndex] = {
        ...loans.value[loanIndex],
        ...loanData,
        updatedAt: new Date().toISOString()
      }
      
      loading.value = false
      return loans.value[loanIndex]
      
    } catch (err) {
      error.value = err.message
      loading.value = false
      throw err
    }
  }

  const cancelLoan = async (loanId, reason) => {
    loading.value = true
    error.value = null

    try {
      // Simular chamada à API
      await new Promise(resolve => setTimeout(resolve, 500))
      
      const loanIndex = loans.value.findIndex(loan => loan.id === loanId)
      if (loanIndex === -1) {
        throw new Error('Empréstimo não encontrado')
      }

      const loan = loans.value[loanIndex]
      if (loan.status !== 'Ativo' && loan.status !== 'Em Atraso') {
        throw new Error('Apenas empréstimos ativos podem ser cancelados')
      }

      // Atualizar empréstimo
      loans.value[loanIndex] = {
        ...loan,
        status: 'Cancelado',
        returnNotes: reason,
        updatedAt: new Date().toISOString()
      }

      // Atualizar status do ativo
      const assetIndex = availableAssets.value.findIndex(a => a.id === loan.asset.id)
      if (assetIndex !== -1) {
        availableAssets.value[assetIndex].status = 'Disponível'
      }
      
      loading.value = false
      return loans.value[loanIndex]
      
    } catch (err) {
      error.value = err.message
      loading.value = false
      throw err
    }
  }

  const getLoanById = (id) => {
    return loans.value.find(loan => loan.id === id)
  }

  const getLoansByThirdParty = (thirdPartyId) => {
    return loans.value.filter(loan => loan.thirdParty.id === thirdPartyId)
  }

  const getLoansByAsset = (assetId) => {
    return loans.value.filter(loan => loan.asset.id === assetId)
  }

  const searchLoans = (query) => {
    if (!query) return loans.value
    
    const searchTerm = query.toLowerCase()
    return loans.value.filter(loan =>
      loan.code.toLowerCase().includes(searchTerm) ||
      loan.thirdParty.name.toLowerCase().includes(searchTerm) ||
      loan.thirdParty.contactName.toLowerCase().includes(searchTerm) ||
      loan.thirdParty.contactEmail.toLowerCase().includes(searchTerm) ||
      loan.asset.name.toLowerCase().includes(searchTerm) ||
      loan.asset.code.toLowerCase().includes(searchTerm) ||
      loan.purpose.toLowerCase().includes(searchTerm) ||
      loan.notes.toLowerCase().includes(searchTerm)
    )
  }

  const filterLoansByStatus = (status) => {
    if (!status) return loans.value
    return loans.value.filter(loan => loan.status === status)
  }

  const filterLoansByType = (type) => {
    if (!type) return loans.value
    return loans.value.filter(loan => loan.thirdParty.type === type)
  }

  const filterLoansByDateRange = (startDate, endDate) => {
    if (!startDate && !endDate) return loans.value
    
    return loans.value.filter(loan => {
      const loanDate = new Date(loan.loanDate)
      const start = startDate ? new Date(startDate) : new Date('1900-01-01')
      const end = endDate ? new Date(endDate) : new Date('2100-12-31')
      
      return loanDate >= start && loanDate <= end
    })
  }

  const getOverdueLoans = () => {
    const today = new Date()
    return loans.value.filter(loan => {
      if (loan.status !== 'Ativo') return false
      const expectedDate = new Date(loan.expectedReturnDate)
      return expectedDate < today
    })
  }

  const updateOverdueStatus = () => {
    const today = new Date()
    loans.value.forEach(loan => {
      if (loan.status === 'Ativo') {
        const expectedDate = new Date(loan.expectedReturnDate)
        if (expectedDate < today) {
          loan.status = 'Em Atraso'
          loan.updatedAt = new Date().toISOString()
        }
      }
    })
  }

  const getThirdPartyHistory = (thirdPartyId) => {
    return loans.value.filter(loan => loan.thirdParty.id === thirdPartyId)
      .sort((a, b) => new Date(b.loanDate) - new Date(a.loanDate))
  }

  const getAssetHistory = (assetId) => {
    return loans.value.filter(loan => loan.asset.id === assetId)
      .sort((a, b) => new Date(b.loanDate) - new Date(a.loanDate))
  }

  const getTopThirdParties = (limit = 5) => {
    const thirdPartyLoans = {}
    
    loans.value.forEach(loan => {
      const id = loan.thirdParty.id
      if (!thirdPartyLoans[id]) {
        thirdPartyLoans[id] = {
          thirdParty: loan.thirdParty,
          count: 0
        }
      }
      thirdPartyLoans[id].count++
    })
    
    return Object.values(thirdPartyLoans)
      .sort((a, b) => b.count - a.count)
      .slice(0, limit)
  }

  const exportLoans = async (format = 'csv', filters = {}) => {
    try {
      loading.value = true
      
      // Aplicar filtros se fornecidos
      let loansToExport = loans.value
      
      if (filters.status) {
        loansToExport = loansToExport.filter(loan => loan.status === filters.status)
      }
      
      if (filters.type) {
        loansToExport = loansToExport.filter(loan => loan.thirdParty.type === filters.type)
      }
      
      if (filters.startDate || filters.endDate) {
        loansToExport = filterLoansByDateRange(filters.startDate, filters.endDate)
      }

      // Simular exportação
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      if (format === 'csv') {
        const csvContent = generateCSV(loansToExport)
        downloadFile(csvContent, 'emprestimos-terceiros.csv', 'text/csv')
      } else if (format === 'excel') {
        // Implementar exportação para Excel
        logger.debug('Exportação para Excel não implementada ainda')
      }
      
      loading.value = false
      return true
      
    } catch (err) {
      error.value = err.message
      loading.value = false
      throw err
    }
  }

  const generateCSV = (loansData) => {
    const headers = [
      'Código', 'Terceiro', 'Tipo', 'Documento', 'Contato', 'Email', 'Telefone',
      'Ativo', 'Código Ativo', 'Data Empréstimo', 'Data Prevista', 'Data Devolução',
      'Status', 'Finalidade', 'Condição', 'Observações'
    ]
    
    const rows = loansData.map(loan => [
      loan.code,
      loan.thirdParty.name,
      loan.thirdParty.type,
      loan.thirdParty.document,
      loan.thirdParty.contactName,
      loan.thirdParty.contactEmail,
      loan.thirdParty.contactPhone,
      loan.asset.name,
      loan.asset.code,
      loan.loanDate,
      loan.expectedReturnDate,
      loan.returnDate || '',
      loan.status,
      loan.purpose,
      loan.condition || '',
      loan.notes
    ])

    const csvContent = [headers, ...rows]
      .map(row => row.map(field => `"${field}"`).join(','))
      .join('\n')

    return csvContent
  }

  const downloadFile = (content, filename, contentType) => {
    const blob = new Blob([content], { type: contentType })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // Estado
    loans,
    availableAssets,
    loading,
    error,
    
    // Getters
    totalLoans,
    activeLoans,
    overdueLoans,
    returnedLoans,
    loansByType,
    loansByStatus,
    assetsOnLoan,
    availableAssetsForLoan,
    loansByMonth,
    
    // Actions
    fetchLoans,
    createLoan,
    returnLoan,
    updateLoan,
    cancelLoan,
    getLoanById,
    getLoansByThirdParty,
    getLoansByAsset,
    searchLoans,
    filterLoansByStatus,
    filterLoansByType,
    filterLoansByDateRange,
    getOverdueLoans,
    updateOverdueStatus,
    getThirdPartyHistory,
    getAssetHistory,
    getTopThirdParties,
    exportLoans,
    clearError
  }
})