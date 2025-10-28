import logger from '@/utils/logger'
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { assetsAPI, handleAPIError } from '@/services/api'

export const useAssetsStore = defineStore('assets', () => {
  // State
  const assets = ref([])
  const loading = ref(false)
  const error = ref(null)
  const dashboardSummary = ref({
    totalAssets: 0,
    totalValue: 0,
    activeAssets: 0,
    inMaintenance: 0,
    byCategory: [],
    byStatus: [],
    trends: []
  })
  const filters = ref({
    search: '',
    category: '',
    status: '',
    location: '',
    department: '',
    page: 1,
    limit: 20
  })

  // Mock data
  const mockAssets = [
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
      supplier: 'Dell Computadores do Brasil',
      invoice: 'NF-2023-001',
      condition: 'Novo',
      depreciation: {
        method: 'Linear',
        rate: 20,
        currentValue: 2800.00
      },
      maintenance: {
        lastDate: '2023-12-15',
        nextDate: '2024-06-15',
        frequency: 'Semestral'
      },
      specifications: {
        processor: 'Intel Core i7-1165G7',
        memory: '16GB DDR4',
        storage: '512GB SSD',
        screen: '15.6" Full HD'
      },
      description: 'Notebook para desenvolvimento de software'
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
      supplier: 'LG Electronics do Brasil',
      invoice: 'NF-2023-002',
      condition: 'Novo',
      depreciation: {
        method: 'Linear',
        rate: 10,
        currentValue: 720.00
      },
      maintenance: {
        lastDate: '2023-11-10',
        nextDate: '2024-05-10',
        frequency: 'Semestral'
      },
      specifications: {
        size: '24 polegadas',
        resolution: '1920x1080',
        panel: 'IPS',
        connectivity: 'HDMI, VGA'
      },
      description: 'Monitor para estação de trabalho'
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
      supplier: 'HP Computadores do Brasil',
      invoice: 'NF-2022-003',
      condition: 'Usado',
      depreciation: {
        method: 'Linear',
        rate: 20,
        currentValue: 720.00
      },
      maintenance: {
        lastDate: '2024-01-15',
        nextDate: '2024-07-15',
        frequency: 'Semestral'
      },
      specifications: {
        type: 'Laser Monocromática',
        speed: '38 ppm',
        resolution: '1200 x 1200 dpi',
        connectivity: 'Ethernet, USB'
      },
      description: 'Impressora laser para documentos administrativos'
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
      supplier: 'Samsung Eletrônica da Amazônia',
      invoice: 'NF-2023-004',
      condition: 'Novo',
      depreciation: {
        method: 'Linear',
        rate: 25,
        currentValue: 1350.00
      },
      maintenance: {
        lastDate: null,
        nextDate: '2024-06-15',
        frequency: 'Anual'
      },
      specifications: {
        storage: '256GB',
        memory: '8GB RAM',
        screen: '6.4" Super AMOLED',
        camera: '50MP + 12MP + 5MP'
      },
      description: 'Smartphone corporativo para equipe de vendas'
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
      supplier: 'Móveis Office Ltda',
      invoice: 'NF-2023-005',
      condition: 'Novo',
      depreciation: {
        method: 'Linear',
        rate: 10,
        currentValue: 2250.00
      },
      maintenance: {
        lastDate: null,
        nextDate: '2025-03-10',
        frequency: 'Bianual'
      },
      specifications: {
        material: 'MDF com acabamento em laminado',
        dimensions: '160cm x 80cm x 75cm',
        color: 'Mogno',
        drawers: '3 gavetas com fechadura'
      },
      description: 'Mesa executiva para diretoria'
    }
  ]

  // Getters
  const filteredAssets = computed(() => {
    let result = assets.value

    if (filters.value.search) {
      const search = filters.value.search.toLowerCase()
      result = result.filter(asset => 
        asset.name.toLowerCase().includes(search) ||
        asset.tag.toLowerCase().includes(search) ||
        asset.responsible.toLowerCase().includes(search)
      )
    }

    if (filters.value.category) {
      result = result.filter(asset => asset.category === filters.value.category)
    }

    if (filters.value.status) {
      result = result.filter(asset => asset.status === filters.value.status)
    }

    if (filters.value.location) {
      result = result.filter(asset => asset.location.includes(filters.value.location))
    }

    if (filters.value.department) {
      result = result.filter(asset => asset.department === filters.value.department)
    }

    return result
  })

  const totalAssets = computed(() => assets.value.length)
  const totalValue = computed(() => 
    assets.value.reduce((sum, asset) => sum + asset.value, 0)
  )

  const assetsByStatus = computed(() => {
    const statusCount = {}
    assets.value.forEach(asset => {
      statusCount[asset.status] = (statusCount[asset.status] || 0) + 1
    })
    return statusCount
  })

  const assetsByCategory = computed(() => {
    const categoryCount = {}
    assets.value.forEach(asset => {
      categoryCount[asset.category] = (categoryCount[asset.category] || 0) + 1
    })
    return categoryCount
  })

  const assetsByWarrantyStatus = computed(() => {
    const warrantyCount = { 'Ativa': 0, 'Expirada': 0, 'Próxima ao Vencimento': 0 }
    const today = new Date()
    const thirtyDaysFromNow = new Date(today.getTime() + (30 * 24 * 60 * 60 * 1000))

    assets.value.forEach(asset => {
      if (asset.warranty && asset.warranty.endDate) {
        const endDate = new Date(asset.warranty.endDate)
        if (endDate < today) {
          warrantyCount['Expirada']++
        } else if (endDate <= thirtyDaysFromNow) {
          warrantyCount['Próxima ao Vencimento']++
        } else {
          warrantyCount['Ativa']++
        }
      }
    })
    return warrantyCount
  })

  const assetsByDepartment = computed(() => {
    const departmentCount = {}
    assets.value.forEach(asset => {
      departmentCount[asset.department] = (departmentCount[asset.department] || 0) + 1
    })
    return departmentCount
  })

  const totalDepreciatedValue = computed(() => 
    assets.value.reduce((sum, asset) => sum + (asset.depreciation?.currentValue || asset.value), 0)
  )

  const assetsNearingMaintenance = computed(() => {
    const today = new Date()
    const thirtyDaysFromNow = new Date(today.getTime() + (30 * 24 * 60 * 60 * 1000))
    
    return assets.value.filter(asset => {
      if (asset.maintenance?.nextDate) {
        const nextDate = new Date(asset.maintenance.nextDate)
        return nextDate <= thirtyDaysFromNow && nextDate >= today
      }
      return false
    })
  })

  const expiredWarranties = computed(() => {
    const today = new Date()
    return assets.value.filter(asset => {
      if (asset.warranty?.endDate) {
        const endDate = new Date(asset.warranty.endDate)
        return endDate < today
      }
      return false
    })
  })

  // Computed properties adicionais para o Dashboard
  const activeAssets = computed(() => 
    assets.value.filter(asset => asset.status === 'Ativo').length
  )

  const maintenanceAssets = computed(() => 
    assets.value.filter(asset => asset.status === 'Manutenção').length
  )

  const categories = computed(() => {
    const uniqueCategories = [...new Set(assets.value.map(asset => asset.category))]
    return uniqueCategories.map(category => ({
      name: category,
      count: assets.value.filter(asset => asset.category === category).length
    }))
  })

  // Actions
  const fetchAssets = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await assetsAPI.getAll(filters.value)
      assets.value = response.data.items || response.data
      return { success: true, data: response.data }
    } catch (err) {
      const apiError = handleAPIError(err)
      error.value = apiError.message
      
      // Fallback to mock data if API fails
      logger.warn('API failed, using mock data:', apiError.message)
      assets.value = [...mockAssets]
      
      return { success: false, error: apiError.message }
    } finally {
      loading.value = false
    }
  }

  const fetchDashboardSummary = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await assetsAPI.getDashboardSummary()
      dashboardSummary.value = response.data
      return { success: true, data: response.data }
    } catch (err) {
      const apiError = handleAPIError(err)
      error.value = apiError.message
      
      // Fallback to calculated values from mock data
      dashboardSummary.value = {
        totalAssets: mockAssets.length,
        totalValue: mockAssets.reduce((sum, asset) => sum + asset.value, 0),
        activeAssets: mockAssets.filter(a => a.status === 'Ativo').length,
        inMaintenance: mockAssets.filter(a => a.status === 'Manutenção').length,
        byCategory: [],
        byStatus: [],
        trends: []
      }
      
      return { success: false, error: apiError.message }
    } finally {
      loading.value = false
    }
  }

  const addAsset = async (assetData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await assetsAPI.create(assetData)
      const newAsset = response.data
      assets.value.push(newAsset)
      return { success: true, data: newAsset }
    } catch (err) {
      const apiError = handleAPIError(err)
      error.value = apiError.message
      // Fallback local (dev): adiciona ao estado mesmo sem API
      const localAsset = {
        id: assetData?.id || Date.now(),
        ...assetData,
        createdAt: assetData?.createdAt || new Date(),
        updatedAt: assetData?.updatedAt || new Date()
      }
      assets.value.push(localAsset)
      return { success: true, data: localAsset, error: apiError.message }
    } finally {
      loading.value = false
    }
  }

  const updateAsset = async (id, assetData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await assetsAPI.update(id, assetData)
      const updatedAsset = response.data
      
      const index = assets.value.findIndex(asset => asset.id === id)
      if (index !== -1) {
        assets.value[index] = updatedAsset
      }
      
      return { success: true, data: updatedAsset }
    } catch (err) {
      const apiError = handleAPIError(err)
      error.value = apiError.message
      // Fallback local (dev): atualiza no estado mesmo sem API
      const index = assets.value.findIndex(asset => asset.id === id)
      if (index !== -1) {
        assets.value[index] = { ...assets.value[index], ...assetData, id }
        return { success: true, data: assets.value[index], error: apiError.message }
      }
      return { success: false, error: apiError.message, errors: apiError.errors }
    } finally {
      loading.value = false
    }
  }

  const deleteAsset = async (id) => {
    loading.value = true
    error.value = null
    
    try {
      await assetsAPI.delete(id)
      
      const index = assets.value.findIndex(asset => asset.id === id)
      if (index !== -1) {
        const deletedAsset = assets.value.splice(index, 1)[0]
        return { success: true, data: deletedAsset }
      }
      
      return { success: true }
    } catch (err) {
      const apiError = handleAPIError(err)
      error.value = apiError.message
      // Fallback local (dev): remove do estado mesmo sem API
      const index = assets.value.findIndex(asset => asset.id === id)
      if (index !== -1) {
        const deletedAsset = assets.value.splice(index, 1)[0]
        return { success: true, data: deletedAsset, error: apiError.message }
      }
      return { success: false, error: apiError.message }
    } finally {
      loading.value = false
    }
  }

  const setFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  const clearFilters = () => {
    filters.value = {
      search: '',
      category: '',
      status: '',
      location: '',
      department: ''
    }
  }

  const getAssetById = (id) => {
    return assets.value.find(asset => asset.id === id)
  }

  const loadMoreAssets = async (page = 1, limit = 50) => {
    if (loading.value) return { success: false, message: 'Already loading' }
    
    loading.value = true
    error.value = null
    
    try {
      const response = await assetsAPI.getAll({ 
        page, 
        limit,
        ...filters.value 
      })
      
      if (page === 1) {
        assets.value = response.data.assets || response.data || []
      } else {
        assets.value.push(...(response.data.assets || response.data || []))
      }
      
      return { 
        success: true, 
        data: response.data,
        hasMore: response.data.hasMore || false,
        total: response.data.total || assets.value.length
      }
    } catch (err) {
      const apiError = handleAPIError(err)
      error.value = apiError.message
      
      // Fallback to mock data for development
      if (page === 1) {
        assets.value = mockAssets
      }
      
      return { 
        success: false, 
        error: apiError.message,
        hasMore: false,
        total: assets.value.length
      }
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    assets,
    loading,
    error,
    filters,
    dashboardSummary,
    // Getters
    filteredAssets,
    totalAssets,
    totalValue,
    assetsByStatus,
    assetsByCategory,
    assetsByWarrantyStatus,
    assetsByDepartment,
    totalDepreciatedValue,
    assetsNearingMaintenance,
    expiredWarranties,
    activeAssets,
    // Actions
    fetchAssets,
    fetchDashboardSummary,
    addAsset,
    updateAsset,
    deleteAsset,
    setFilters,
    clearFilters,
    getAssetById,
    loadMoreAssets
  }
})
