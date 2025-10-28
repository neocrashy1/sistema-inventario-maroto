import { defineStore } from 'pinia'
import { auditorsAPI, handleAPIError } from '@/services/api'

export const usePhysicalInventoryStore = defineStore('physicalInventory', {
  state: () => ({
    inventories: [
      {
        id: 1,
        code: 'INV-2024-001',
        description: 'Inventário Anual - Sede Principal',
        location: { id: 1, name: 'Sede Principal', code: 'SEDE' },
        responsible: { id: 1, name: 'João Silva', email: 'joao.silva@empresa.com' },
        startDate: '2024-01-15',
        endDate: '2024-01-30',
        status: 'completed',
        totalAssets: 150,
        countedAssets: 150,
        discrepancies: 3,
        progress: 100,
        createdAt: '2024-01-10T08:00:00Z',
        updatedAt: '2024-01-30T17:30:00Z',
        notes: 'Inventário concluído com sucesso. Pequenas discrepâncias identificadas e corrigidas.',
        assets: [
          {
            id: 1,
            assetCode: 'NB-001',
            assetName: 'Notebook Dell Latitude',
            expectedLocation: 'Sala 101',
            actualLocation: 'Sala 101',
            status: 'found',
            condition: 'good',
            notes: 'Ativo encontrado em bom estado'
          },
          {
            id: 2,
            assetCode: 'MON-015',
            assetName: 'Monitor Samsung 24"',
            expectedLocation: 'Sala 102',
            actualLocation: 'Sala 103',
            status: 'moved',
            condition: 'good',
            notes: 'Ativo encontrado em localização diferente'
          }
        ]
      },
      {
        id: 2,
        code: 'INV-2024-002',
        description: 'Inventário Trimestral - Filial Norte',
        location: { id: 2, name: 'Filial Norte', code: 'FIL-N' },
        responsible: { id: 2, name: 'Maria Santos', email: 'maria.santos@empresa.com' },
        startDate: '2024-02-01',
        endDate: '2024-02-15',
        status: 'in_progress',
        totalAssets: 85,
        countedAssets: 62,
        discrepancies: 1,
        progress: 73,
        createdAt: '2024-01-25T09:00:00Z',
        updatedAt: '2024-02-10T14:20:00Z',
        notes: 'Inventário em andamento. Progresso dentro do cronograma.',
        assets: [
          {
            id: 3,
            assetCode: 'CPU-025',
            assetName: 'Desktop HP ProDesk',
            expectedLocation: 'Sala 201',
            actualLocation: 'Sala 201',
            status: 'found',
            condition: 'good',
            notes: 'Ativo encontrado conforme esperado'
          }
        ]
      },
      {
        id: 3,
        code: 'INV-2024-003',
        description: 'Inventário Especial - Equipamentos TI',
        location: { id: 4, name: 'Data Center', code: 'DC' },
        responsible: { id: 3, name: 'Carlos Oliveira', email: 'carlos.oliveira@empresa.com' },
        startDate: '2024-03-01',
        endDate: '2024-03-10',
        status: 'planned',
        totalAssets: 45,
        countedAssets: 0,
        discrepancies: 0,
        progress: 0,
        createdAt: '2024-02-20T10:00:00Z',
        updatedAt: '2024-02-20T10:00:00Z',
        notes: 'Inventário planejado para equipamentos críticos do data center.',
        assets: []
      }
    ],
    locations: [
      { id: 1, name: 'Sede Principal', code: 'SEDE' },
      { id: 2, name: 'Filial Norte', code: 'FIL-N' },
      { id: 3, name: 'Filial Sul', code: 'FIL-S' },
      { id: 4, name: 'Data Center', code: 'DC' },
      { id: 5, name: 'Almoxarifado', code: 'ALM' }
    ],
    responsibles: [
      { id: 1, name: 'João Silva', department: 'TI' },
      { id: 2, name: 'Maria Santos', department: 'Administração' },
      { id: 3, name: 'Carlos Oliveira', department: 'TI' },
      { id: 4, name: 'Ana Costa', department: 'Patrimônio' }
    ],
    availableAssets: [
      {
        id: 1,
        tag: 'LVT-001',
        name: 'Notebook Dell Latitude 5520',
        brand: 'Dell',
        model: 'Latitude 5520',
        serialNumber: 'DL5520-2023-001',
        category: 'Informática',
        subcategory: 'Notebooks',
        status: 'Ativo',
        location: 'TI - Sala 101',
        department: 'Tecnologia da Informação',
        value: 3500.00,
        acquisitionDate: '2023-01-15',
        entryDate: '2023-01-20',
        warranty: {
          startDate: '2023-01-15',
          endDate: '2025-01-15',
          provider: 'Dell Brasil',
          type: 'Garantia do Fabricante',
          status: 'Ativa'
        },
        responsible: 'João Silva',
        condition: 'Novo',
        lastInventoryDate: '2023-12-01',
        inventoryStatus: 'Contado',
        specifications: {
          processor: 'Intel Core i7-1165G7',
          memory: '16GB DDR4',
          storage: '512GB SSD',
          screen: '15.6" Full HD'
        }
      },
      {
        id: 2,
        tag: 'LVT-002',
        name: 'Monitor LG 24"',
        brand: 'LG',
        model: '24MK430H-B',
        serialNumber: 'LG24-2023-002',
        category: 'Informática',
        subcategory: 'Monitores',
        status: 'Ativo',
        location: 'TI - Sala 101',
        department: 'Tecnologia da Informação',
        value: 800.00,
        acquisitionDate: '2023-02-10',
        entryDate: '2023-02-12',
        warranty: {
          startDate: '2023-02-10',
          endDate: '2026-02-10',
          provider: 'LG Electronics',
          type: 'Garantia Estendida',
          status: 'Ativa'
        },
        responsible: 'Maria Santos',
        condition: 'Novo',
        lastInventoryDate: '2023-12-01',
        inventoryStatus: 'Contado',
        specifications: {
          size: '24 polegadas',
          resolution: '1920x1080',
          panel: 'IPS',
          connectivity: 'HDMI, VGA'
        }
      },
      {
        id: 3,
        tag: 'LVT-003',
        name: 'Impressora HP LaserJet Pro M404dn',
        brand: 'HP',
        model: 'LaserJet Pro M404dn',
        serialNumber: 'HP404-2022-003',
        category: 'Equipamentos',
        subcategory: 'Impressoras',
        status: 'Manutenção',
        location: 'Administrativo',
        department: 'Administrativo',
        value: 1200.00,
        acquisitionDate: '2022-08-20',
        entryDate: '2022-08-25',
        warranty: {
          startDate: '2022-08-20',
          endDate: '2024-08-20',
          provider: 'HP Brasil',
          type: 'Garantia do Fabricante',
          status: 'Expirada'
        },
        responsible: 'Carlos Oliveira',
        condition: 'Usado',
        lastInventoryDate: '2023-11-15',
        inventoryStatus: 'Discrepância',
        specifications: {
          type: 'Laser Monocromática',
          speed: '38 ppm',
          resolution: '1200 x 1200 dpi',
          connectivity: 'Ethernet, USB'
        }
      },
      {
        id: 4,
        tag: 'LVT-004',
        name: 'Smartphone Samsung Galaxy A54',
        brand: 'Samsung',
        model: 'Galaxy A54 5G',
        serialNumber: 'SM-A546B-2023-004',
        category: 'Telefonia',
        subcategory: 'Smartphones',
        status: 'Ativo',
        location: 'Vendas - Sala 201',
        department: 'Comercial',
        value: 1800.00,
        acquisitionDate: '2023-06-15',
        entryDate: '2023-06-18',
        warranty: {
          startDate: '2023-06-15',
          endDate: '2024-06-15',
          provider: 'Samsung Brasil',
          type: 'Garantia do Fabricante',
          status: 'Ativa'
        },
        responsible: 'Ana Costa',
        condition: 'Novo',
        lastInventoryDate: null,
        inventoryStatus: 'Não Contado',
        specifications: {
          storage: '256GB',
          memory: '8GB RAM',
          screen: '6.4" Super AMOLED',
          camera: '50MP + 12MP + 5MP'
        }
      },
      {
        id: 5,
        tag: 'LVT-005',
        name: 'Mesa de Escritório Executive',
        brand: 'Móveis Office',
        model: 'Executive 160x80',
        serialNumber: 'MO-EX-160-005',
        category: 'Mobiliário',
        subcategory: 'Mesas',
        status: 'Ativo',
        location: 'Diretoria - Sala 301',
        department: 'Diretoria',
        value: 2500.00,
        acquisitionDate: '2023-03-10',
        entryDate: '2023-03-15',
        warranty: {
          startDate: '2023-03-10',
          endDate: '2028-03-10',
          provider: 'Móveis Office Ltda',
          type: 'Garantia do Fabricante',
          status: 'Ativa'
        },
        responsible: 'Roberto Silva',
        condition: 'Novo',
        lastInventoryDate: '2023-12-01',
        inventoryStatus: 'Contado',
        specifications: {
          material: 'MDF com acabamento em laminado',
          dimensions: '160cm x 80cm x 75cm',
          color: 'Mogno',
          drawers: '3 gavetas com fechadura'
        }
      }
    ],
    loading: false,
    error: null,
    searchTerm: '',
    filters: {
      status: '',
      location: '',
      responsible: '',
      dateRange: { start: '', end: '' }
    }
  }),

  getters: {
    // Estatísticas gerais
    totalInventories: (state) => state.inventories.length,
    
    inventoriesInProgress: (state) => 
      state.inventories.filter(inv => inv.status === 'in_progress').length,
    
    totalAssetsCount: (state) => 
      state.inventories.reduce((total, inv) => total + inv.countedAssets, 0),
    
    totalDiscrepancies: (state) => 
      state.inventories.reduce((total, inv) => total + inv.discrepancies, 0),

    // Inventários por status
    inventoriesByStatus: (state) => {
      return state.inventories.reduce((acc, inventory) => {
        acc[inventory.status] = (acc[inventory.status] || 0) + 1
        return acc
      }, {})
    },

    // Inventários por localização
    inventoriesByLocation: (state) => {
      return state.inventories.reduce((acc, inventory) => {
        acc[inventory.location] = (acc[inventory.location] || 0) + 1
        return acc
      }, {})
    },

    // Inventários por responsável
    inventoriesByResponsible: (state) => {
      return state.inventories.reduce((acc, inventory) => {
        acc[inventory.responsible] = (acc[inventory.responsible] || 0) + 1
        return acc
      }, {})
    },

    // Progresso médio dos inventários
    averageProgress: (state) => {
      const activeInventories = state.inventories.filter(inv => 
        inv.status === 'in_progress' || inv.status === 'completed'
      )
      if (activeInventories.length === 0) return 0
      
      const totalProgress = activeInventories.reduce((sum, inv) => sum + inv.progress, 0)
      return Math.round(totalProgress / activeInventories.length)
    },

    // Inventários filtrados
    filteredInventories: (state) => {
      let filtered = [...state.inventories]

      // Filtro por termo de busca
      if (state.searchTerm) {
        const term = state.searchTerm.toLowerCase()
        filtered = filtered.filter(inventory =>
          inventory.code.toLowerCase().includes(term) ||
          inventory.description.toLowerCase().includes(term) ||
          inventory.responsible.toLowerCase().includes(term) ||
          inventory.location.toLowerCase().includes(term)
        )
      }

      // Filtro por status
      if (state.filters.status) {
        filtered = filtered.filter(inventory => inventory.status === state.filters.status)
      }

      // Filtro por localização
      if (state.filters.location) {
        filtered = filtered.filter(inventory => inventory.location === state.filters.location)
      }

      // Filtro por responsável
      if (state.filters.responsible) {
        filtered = filtered.filter(inventory => inventory.responsible === state.filters.responsible)
      }

      // Filtro por período
      if (state.filters.dateRange.start && state.filters.dateRange.end) {
        filtered = filtered.filter(inventory => {
          const startDate = new Date(inventory.startDate)
          const filterStart = new Date(state.filters.dateRange.start)
          const filterEnd = new Date(state.filters.dateRange.end)
          return startDate >= filterStart && startDate <= filterEnd
        })
      }

      return filtered
    },

    // Estatísticas dos ativos disponíveis
    totalAvailableAssets: (state) => state.availableAssets.length,

    // Ativos por status de inventário
    assetsByInventoryStatus: (state) => {
      return state.availableAssets.reduce((acc, asset) => {
        const status = asset.inventoryStatus || 'Não Contado'
        acc[status] = (acc[status] || 0) + 1
        return acc
      }, {})
    },

    // Ativos por status de garantia
    assetsByWarrantyStatus: (state) => {
      const now = new Date()
      const thirtyDaysFromNow = new Date(now.getTime() + (30 * 24 * 60 * 60 * 1000))
      
      return state.availableAssets.reduce((acc, asset) => {
        if (!asset.warranty) {
          acc['Sem Garantia'] = (acc['Sem Garantia'] || 0) + 1
          return acc
        }

        const endDate = new Date(asset.warranty.endDate)
        
        if (endDate < now) {
          acc['Expirada'] = (acc['Expirada'] || 0) + 1
        } else if (endDate <= thirtyDaysFromNow) {
          acc['Expirando'] = (acc['Expirando'] || 0) + 1
        } else {
          acc['Ativa'] = (acc['Ativa'] || 0) + 1
        }
        
        return acc
      }, {})
    },

    // Ativos por categoria
    assetsByCategory: (state) => {
      return state.availableAssets.reduce((acc, asset) => {
        acc[asset.category] = (acc[asset.category] || 0) + 1
        return acc
      }, {})
    },

    // Ativos por departamento
    assetsByDepartment: (state) => {
      return state.availableAssets.reduce((acc, asset) => {
        acc[asset.department] = (acc[asset.department] || 0) + 1
        return acc
      }, {})
    },

    // Valor total dos ativos disponíveis
    totalAssetsValue: (state) => {
      return state.availableAssets.reduce((total, asset) => total + (asset.value || 0), 0)
    },

    // Ativos com garantia expirada
    expiredWarrantyAssets: (state) => {
      const now = new Date()
      return state.availableAssets.filter(asset => {
        if (!asset.warranty) return false
        const endDate = new Date(asset.warranty.endDate)
        return endDate < now
      })
    },

    // Ativos com garantia expirando em 30 dias
    expiringWarrantyAssets: (state) => {
      const now = new Date()
      const thirtyDaysFromNow = new Date(now.getTime() + (30 * 24 * 60 * 60 * 1000))
      
      return state.availableAssets.filter(asset => {
        if (!asset.warranty) return false
        const endDate = new Date(asset.warranty.endDate)
        return endDate >= now && endDate <= thirtyDaysFromNow
      })
    },

    // Ativos não contados no último inventário
    uncountedAssets: (state) => {
      return state.availableAssets.filter(asset => 
        !asset.inventoryStatus || asset.inventoryStatus === 'Não Contado'
      )
    },

    // Ativos com discrepâncias
    discrepancyAssets: (state) => {
      return state.availableAssets.filter(asset => 
        asset.inventoryStatus === 'Discrepância'
      )
    },

    // Ativos por condição
    assetsByCondition: (state) => {
      return state.availableAssets.reduce((acc, asset) => {
        const condition = asset.condition || 'Não Informado'
        acc[condition] = (acc[condition] || 0) + 1
        return acc
      }, {})
    }
  },

  actions: {
    // Buscar inventários
    async fetchInventories() {
      this.loading = true
      this.error = null

      try {
        const { data } = await auditorsAPI.getAll({ skip: 0, limit: 100 })
        const items = Array.isArray(data?.items) ? data.items : (Array.isArray(data) ? data : [])
        this.inventories = items.map((a) => this.mapAuditoriaToInventory(a))
        this.loading = false
      } catch (error) {
        const err = handleAPIError(error)
        this.error = err.message || 'Erro ao carregar inventários'
        this.loading = false
        throw error
      }
    },

    // Iniciar inventário
    async startInventory(id) {
      this.loading = true
      this.error = null

      try {
        await auditorsAPI.start(id)
        await this.updateInventory(id, { 
          status: 'in_progress',
          startDate: new Date().toISOString().split('T')[0]
        })
        this.loading = false
      } catch (error) {
        const err = handleAPIError(error)
        this.error = err.message || 'Erro ao iniciar inventário'
        this.loading = false
        throw error
      }
    },

    // Registrar contagem de ativo
    async recordAssetCount(inventoryId, assetData) {
      this.loading = true
      this.error = null

      try {
        const coletaPayload = Array.isArray(assetData) ? assetData.map(a => ({
          item_id: a.itemId || a.id,
          codigo_lido: a.assetCode || a.codigo_lido || a.tag,
          local_encontrado_id: a.local_encontrado_id || a.actualLocationId || null,
          estado_encontrado: a.condition || a.estado_encontrado || null,
          observacoes: a.notes || a.observacoes || '',
          foto_url: a.foto_url || a.photoUrl || null
        })) : [{
          item_id: assetData.itemId || assetData.id,
          codigo_lido: assetData.assetCode || assetData.codigo_lido || assetData.tag,
          local_encontrado_id: assetData.local_encontrado_id || assetData.actualLocationId || null,
          estado_encontrado: assetData.condition || assetData.estado_encontrado || null,
          observacoes: assetData.notes || assetData.observacoes || '',
          foto_url: assetData.foto_url || assetData.photoUrl || null
        }]

        await auditorsAPI.registerCollection(inventoryId, coletaPayload)

        const inventory = this.inventories.find(inv => inv.id === inventoryId)
        if (inventory) {
          const normalize = (a) => ({
            id: a.item_id || a.id || Date.now(),
            assetCode: a.codigo_lido || a.assetCode || a.tag || '',
            assetName: a.assetName || a.descricao || '',
            expectedLocation: a.expectedLocation || '',
            actualLocation: a.actualLocation || '',
            status: this.mapCountStatusToAssetStatus(a.countStatus || 'found'),
            condition: a.estado_encontrado || a.condition || 'good',
            notes: a.observacoes || a.notes || ''
          })

          const payloadAssets = Array.isArray(assetData) ? assetData.map(normalize) : [normalize(assetData)]
          payloadAssets.forEach(asset => {
            const existingAssetIndex = inventory.assets.findIndex(a => a.assetCode === asset.assetCode)
            if (existingAssetIndex !== -1) {
              inventory.assets[existingAssetIndex] = { ...inventory.assets[existingAssetIndex], ...asset }
            } else {
              inventory.assets.push({ id: Date.now(), ...asset })
            }
          })

          inventory.countedAssets = inventory.assets.length
          inventory.discrepancies = inventory.assets.filter(asset => 
            asset.status === 'moved' || asset.status === 'missing' || asset.status === 'damaged'
          ).length
          inventory.progress = inventory.totalAssets > 0
            ? Math.round((inventory.countedAssets / inventory.totalAssets) * 100)
            : 0
          inventory.updatedAt = new Date().toISOString()
        }

        this.loading = false
      } catch (error) {
        const err = handleAPIError(error)
        this.error = err.message || 'Erro ao registrar contagem'
        this.loading = false
        throw error
      }
    },

    // Buscar ativos para inventário
    async getInventoryAssets(inventoryId) {
      this.loading = true
      this.error = null

      try {
        const { data } = await auditorsAPI.getCountList(inventoryId)
        const items = Array.isArray(data?.itens) ? data.itens : []
        const assets = items.map((item) => this.mapAPIItemToAsset(item))
        this.loading = false
        return assets
      } catch (error) {
        const err = handleAPIError(error)
        this.error = err.message || 'Erro ao buscar ativos para inventário'
        this.loading = false
        throw error
      }
    },

    // Utilitário: mapear Auditoria (API) -> Inventory (Store)
    mapAuditoriaToInventory(a) {
      const totalAssets = a.total_itens ?? a.total_itens_esperados ?? 0
      const countedAssets = (a.itens_conformes || 0) + (a.itens_divergentes || 0) + (a.itens_nao_encontrados || 0) + (a.itens_extras || 0)
      const progress = totalAssets > 0 ? Math.round((countedAssets / totalAssets) * 100) : 0
      const statusMap = {
        'PLANEJADA': 'planned',
        'EM_ANDAMENTO': 'in_progress',
        'RECONCILIACAO': 'in_progress',
        'FINALIZADA': 'completed',
        'CANCELADA': 'cancelled'
      }

      return {
        id: a.id,
        code: a.nome || `AUD-${a.id}`,
        description: a.descricao || '',
        location: a.escopo_locais || '',
        responsible: '',
        startDate: a.data_inicio ? String(a.data_inicio).split('T')[0] : '',
        endDate: a.data_fim ? String(a.data_fim).split('T')[0] : '',
        status: statusMap[a.status] || a.status || 'planned',
        totalAssets,
        countedAssets,
        discrepancies: (a.itens_divergentes || 0) + (a.itens_nao_encontrados || 0) + (a.itens_extras || 0),
        progress,
        createdAt: a.criado_em || '',
        updatedAt: a.atualizado_em || '',
        notes: a.observacoes_finais || '',
        assets: []
      }
    },

    // Utilitário: mapear item da API -> asset da store
    mapAPIItemToAsset(item) {
      return {
        id: item.id || item.item_id || Date.now(),
        assetCode: item.codigo || item.patrimonio || item.tag || '',
        assetName: item.descricao || item.nome || '',
        expectedLocation: item.local_esperado || item.local_esperado_nome || '',
        actualLocation: item.local_encontrado || item.local_encontrado_nome || item.expectedLocation || '',
        status: this.mapCountStatusToAssetStatus(item.countStatus || (item.resultado === 'conforme' ? 'found' : 'not_counted')),
        condition: item.estado_encontrado || 'good',
        notes: item.observacoes || ''
      }
    }
  },

  // Atualizar inventário (utilizado por startInventory)
  async updateInventory(id, updates) {
    this.loading = true
    this.error = null
  
    try {
      // Simular chamada à API
      await new Promise(resolve => setTimeout(resolve, 500))
  
      const index = this.inventories.findIndex(inv => inv.id === id)
      if (index !== -1) {
        this.inventories[index] = {
          ...this.inventories[index],
          ...updates,
          updatedAt: new Date().toISOString()
        }
      }
  
      this.loading = false
    } catch (error) {
      this.error = 'Erro ao atualizar inventário'
      this.loading = false
      throw error
    }
  },

  // Mapear status de contagem para status de ativo
  mapCountStatusToAssetStatus(countStatus) {
    const statusMap = {
      found: 'found',
      not_found: 'missing',
      damaged: 'damaged',
      wrong_location: 'moved',
      not_counted: 'pending'
    }
    return statusMap[countStatus] || 'pending'
  },

  // Criar novo inventário (mock local)
  async createInventory(inventoryData) {
    this.loading = true
    this.error = null
  
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
  
      const newInventory = {
        id: Date.now(),
        code: `INV-${new Date().getFullYear()}-${String(this.inventories.length + 1).padStart(3, '0')}`,
        ...inventoryData,
        status: 'planned',
        totalAssets: 0,
        countedAssets: 0,
        discrepancies: 0,
        progress: 0,
        assets: [],
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
  
      this.inventories.unshift(newInventory)
      this.loading = false
      return newInventory
    } catch (error) {
      this.error = 'Erro ao criar inventário'
      this.loading = false
      throw error
    }
  },

  // Finalizar inventário (mock local)
  async completeInventory(id) {
    await this.updateInventory(id, {
      status: 'completed',
      endDate: new Date().toISOString().split('T')[0],
      progress: 100
    })
  },

  // Cancelar inventário (mock local)
  async cancelInventory(id) {
    await this.updateInventory(id, { status: 'cancelled' })
  },

  // Atualizar contagem do inventário (mock local)
  async updateInventoryCounting(inventoryId, countingAssets) {
    this.loading = true
    this.error = null
  
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
  
      const inventory = this.inventories.find(inv => inv.id === inventoryId)
      if (inventory) {
        inventory.assets = countingAssets.map(asset => ({
          id: asset.id,
          assetCode: asset.tag,
          assetName: asset.name,
          expectedLocation: asset.location,
          actualLocation: asset.actualLocation || asset.location,
          status: this.mapCountStatusToAssetStatus(asset.countStatus),
          condition: asset.condition || 'good',
          notes: asset.countNotes || '',
          counted: asset.counted || false,
          hasDiscrepancy: asset.hasDiscrepancy || false
        }))
  
        inventory.countedAssets = countingAssets.filter(asset => asset.counted).length
        inventory.discrepancies = countingAssets.filter(asset => asset.hasDiscrepancy).length
        inventory.totalAssets = countingAssets.length
  
        inventory.progress = inventory.totalAssets > 0
          ? Math.round((inventory.countedAssets / inventory.totalAssets) * 100)
          : 0
  
        if (inventory.progress === 100) {
          inventory.status = 'completed'
          inventory.endDate = new Date().toISOString().split('T')[0]
        } else if (inventory.progress > 0 && inventory.status === 'planned') {
          inventory.status = 'in_progress'
        }
  
        inventory.updatedAt = new Date().toISOString()
      }
  
      this.loading = false
    } catch (error) {
      this.error = 'Erro ao atualizar contagem do inventário'
      this.loading = false
      throw error
    }
  },

  // Reconciliação de leituras offline de QR
  async reconcileScans(scansQueue) {
    if (!Array.isArray(scansQueue) || scansQueue.length === 0) {
      return { processed: 0, failed: 0 }
    }

    this.loading = true
    this.error = null

    const grouped = scansQueue.reduce((acc, item) => {
      const invId = item.inventoryId
      if (!invId) return acc
      if (!acc[invId]) acc[invId] = []
      acc[invId].push(item)
      return acc
    }, {})

    let processed = 0
    let failed = 0

    for (const [inventoryId, items] of Object.entries(grouped)) {
      const payload = items.map(it => ({
        itemId: it.assetId || it.itemId || null,
        assetCode: it.code || it.assetCode || '',
        condition: it.condition || 'good',
        notes: (it.notes || '') + (it.notes ? ' ' : '') + '[Reconciliação Offline]',
        countStatus: it.status || 'found'
      }))

      if (!payload.length) continue

      try {
        await this.recordAssetCount(parseInt(inventoryId, 10), payload)
        processed += items.length
      } catch (error) {
        failed += items.length
        const err = handleAPIError ? handleAPIError(error) : null
        this.error = (err && err.message) || 'Erro ao reconciliar leituras offline'
      }
    }

    this.loading = false
    return { processed, failed }
  },
  // Limpar erro
  clearError() {
    this.error = null
  },

  // Deletar inventário (mock local)
  async deleteInventory(id) {
    this.loading = true
    this.error = null
  
    try {
      await new Promise(resolve => setTimeout(resolve, 500))
  
      const index = this.inventories.findIndex(inv => inv.id === id)
      if (index !== -1) {
        this.inventories.splice(index, 1)
      }
  
      this.loading = false
    } catch (error) {
      this.error = 'Erro ao deletar inventário'
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
      location: '',
      responsible: '',
      dateRange: { start: '', end: '' }
    }
    this.searchTerm = ''
  },

  // Exportar dados
  async exportInventories(format = 'csv') {
    try {
      const inventories = this.filteredInventories
  
      if (format === 'csv') {
        const csvContent = this.generateCSV(inventories)
        this.downloadFile(csvContent, `inventarios_${new Date().toISOString().split('T')[0]}.csv`, 'text/csv')
      }
  
      return true
    } catch (error) {
      this.error = 'Erro ao exportar dados'
      throw error
    }
  },

  // Gerar CSV
  generateCSV(inventories) {
    const headers = [
      'Código',
      'Descrição',
      'Localização',
      'Responsável',
      'Status',
      'Data Início',
      'Data Fim',
      'Total Ativos',
      'Ativos Contados',
      'Discrepâncias',
      'Progresso (%)',
      'Observações'
    ]
  
    const rows = inventories.map(inventory => [
      inventory.code,
      inventory.description,
      inventory.location,
      inventory.responsible,
      this.getStatusLabel(inventory.status),
      inventory.startDate,
      inventory.endDate || '',
      inventory.totalAssets,
      inventory.countedAssets,
      inventory.discrepancies,
      inventory.progress,
      inventory.notes || ''
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
      planned: 'Planejado',
      in_progress: 'Em Andamento',
      completed: 'Concluído',
      cancelled: 'Cancelado'
    }
    return statusLabels[status] || status
  },

  // Obter cor do status
  getStatusColor(status) {
    const statusColors = {
      planned: 'blue',
      in_progress: 'orange',
      completed: 'green',
      cancelled: 'red'
    }
    return statusColors[status] || 'gray'
  }
})