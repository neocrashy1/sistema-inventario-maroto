import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { machinesAPI, cachedAPI, handleAPIError } from '@/services/api'
import websocketService from '@/services/websocket'
import logger from '@/utils/logger'
import { useAuthStore } from './auth'

export const useMachinesStore = defineStore('machines', () => {
  // Estado reativo
  const machines = ref([])
  const selectedMachine = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const lastUpdate = ref(null)
  
  // Estado de conexão WebSocket
  const wsConnected = ref(false)
  const wsError = ref(null)
  
  // Filtros e configurações
  const filters = ref({
    status: 'all', // all, online, offline, warning, critical
    location: '',
    department: '',
    search: ''
  })
  
  // Configurações de monitoramento
  const monitoringConfig = ref({
    autoRefresh: true,
    refreshRate: 30000, // 30 segundos
    realTimeUpdates: true,
    alertsEnabled: true
  })
  
  // Métricas agregadas
  const metrics = ref({
    totalMachines: 0,
    onlineMachines: 0,
    offlineMachines: 0,
    warningMachines: 0,
    criticalMachines: 0,
    avgCpuUsage: 0,
    avgMemoryUsage: 0,
    avgDiskUsage: 0,
    systemUptime: 0
  })
  
  // Alertas de máquinas
  const alerts = ref([])
  
  // Histórico de performance
  const performanceHistory = ref({})
  
  // Computed properties
  const filteredMachines = computed(() => {
    let filtered = machines.value
    
    // Filtro por status
    if (filters.value.status !== 'all') {
      filtered = filtered.filter(machine => machine.status === filters.value.status)
    }
    
    // Filtro por localização
    if (filters.value.location) {
      filtered = filtered.filter(machine => 
        machine.location?.toLowerCase().includes(filters.value.location.toLowerCase())
      )
    }
    
    // Filtro por departamento
    if (filters.value.department) {
      filtered = filtered.filter(machine => 
        machine.department?.toLowerCase().includes(filters.value.department.toLowerCase())
      )
    }
    
    // Filtro por busca
    if (filters.value.search) {
      const searchTerm = filters.value.search.toLowerCase()
      filtered = filtered.filter(machine => 
        machine.name?.toLowerCase().includes(searchTerm) ||
        machine.hostname?.toLowerCase().includes(searchTerm) ||
        machine.ip?.includes(searchTerm) ||
        machine.user?.toLowerCase().includes(searchTerm)
      )
    }
    
    return filtered
  })
  
  const onlineMachines = computed(() => 
    machines.value.filter(machine => machine.status === 'online')
  )
  
  const offlineMachines = computed(() => 
    machines.value.filter(machine => machine.status === 'offline')
  )
  
  const criticalMachines = computed(() => 
    machines.value.filter(machine => machine.status === 'critical')
  )
  
  const warningMachines = computed(() => 
    machines.value.filter(machine => machine.status === 'warning')
  )
  
  // Actions
  const fetchMachines = async (forceRefresh = false) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await cachedAPI.machines.getAll({
        forceRefresh,
        cacheKey: 'machines:all',
        cacheTTL: 60000 // 1 minuto
      })
      
      machines.value = response.data || []
      updateMetrics()
      lastUpdate.value = new Date()
      
      return { success: true, data: response.data }
    } catch (err) {
      const apiError = handleAPIError(err)
      error.value = 'Erro ao carregar máquinas: ' + apiError.message
      logger.error('Erro ao buscar máquinas:', err)
      
      // Fallback para dados mock em desenvolvimento
      if (process.env.NODE_ENV === 'development') {
        machines.value = generateMockMachines()
        updateMetrics()
        return { success: true, data: machines.value, mock: true }
      }
      
      return { success: false, error: apiError.message }
    } finally {
      loading.value = false
    }
  }
  
  const fetchMachineStatus = async (machineId) => {
    try {
      const response = await cachedAPI.machines.getStatus(machineId, {
        cacheKey: `machines:${machineId}:status`,
        cacheTTL: 10000 // 10 segundos
      })
      
      // Atualizar máquina específica na lista
      const machineIndex = machines.value.findIndex(m => m.id === machineId)
      if (machineIndex !== -1) {
        machines.value[machineIndex] = { ...machines.value[machineIndex], ...response.data }
        updateMetrics()
      }
      
      return { success: true, data: response.data }
    } catch (err) {
      const apiError = handleAPIError(err)
      logger.error(`Erro ao buscar status da máquina ${machineId}:`, err)
      return { success: false, error: apiError.message }
    }
  }
  
  const registerMachine = async (machineData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await machinesAPI.register(machineData)
      
      // Adicionar nova máquina à lista
      machines.value.push(response.data)
      updateMetrics()
      
      return { success: true, data: response.data }
    } catch (err) {
      const apiError = handleAPIError(err)
      error.value = 'Erro ao registrar máquina: ' + apiError.message
      logger.error('Erro ao registrar máquina:', err)
      return { success: false, error: apiError.message }
    } finally {
      loading.value = false
    }
  }
  
  const updateMachineStatus = async (statusData) => {
    try {
      const response = await machinesAPI.updateStatus(statusData)
      
      // Atualizar máquina na lista
      const machineIndex = machines.value.findIndex(m => m.id === statusData.machineId)
      if (machineIndex !== -1) {
        machines.value[machineIndex] = { ...machines.value[machineIndex], ...response.data }
        updateMetrics()
        
        // Adicionar ao histórico de performance
        addPerformanceData(statusData.machineId, response.data)
      }
      
      return { success: true, data: response.data }
    } catch (err) {
      const apiError = handleAPIError(err)
      logger.error('Erro ao atualizar status da máquina:', err)
      return { success: false, error: apiError.message }
    }
  }
  
  const selectMachine = (machine) => {
    selectedMachine.value = machine
  }
  
  const clearSelection = () => {
    selectedMachine.value = null
  }
  
  const setFilters = (newFilters) => {
    filters.value = { ...filters.value, ...newFilters }
  }
  
  const clearFilters = () => {
    filters.value = {
      status: 'all',
      location: '',
      department: '',
      search: ''
    }
  }
  
  const updateMetrics = () => {
    const total = machines.value.length
    const online = machines.value.filter(m => m.status === 'online').length
    const offline = machines.value.filter(m => m.status === 'offline').length
    const warning = machines.value.filter(m => m.status === 'warning').length
    const critical = machines.value.filter(m => m.status === 'critical').length
    
    // Calcular médias de performance
    const onlineMachinesData = machines.value.filter(m => m.status === 'online' && m.performance)
    const avgCpu = onlineMachinesData.length > 0 
      ? onlineMachinesData.reduce((sum, m) => sum + (m.performance?.cpu || 0), 0) / onlineMachinesData.length
      : 0
    const avgMemory = onlineMachinesData.length > 0
      ? onlineMachinesData.reduce((sum, m) => sum + (m.performance?.memory || 0), 0) / onlineMachinesData.length
      : 0
    const avgDisk = onlineMachinesData.length > 0
      ? onlineMachinesData.reduce((sum, m) => sum + (m.performance?.disk || 0), 0) / onlineMachinesData.length
      : 0
    
    metrics.value = {
      totalMachines: total,
      onlineMachines: online,
      offlineMachines: offline,
      warningMachines: warning,
      criticalMachines: critical,
      avgCpuUsage: Math.round(avgCpu * 100) / 100,
      avgMemoryUsage: Math.round(avgMemory * 100) / 100,
      avgDiskUsage: Math.round(avgDisk * 100) / 100,
      systemUptime: total > 0 ? Math.round((online / total) * 100 * 100) / 100 : 0
    }
  }
  
  const addPerformanceData = (machineId, data) => {
    if (!performanceHistory.value[machineId]) {
      performanceHistory.value[machineId] = []
    }
    
    const history = performanceHistory.value[machineId]
    history.push({
      timestamp: new Date(),
      cpu: data.performance?.cpu || 0,
      memory: data.performance?.memory || 0,
      disk: data.performance?.disk || 0,
      network: data.performance?.network || 0
    })
    
    // Manter apenas os últimos 100 pontos
    if (history.length > 100) {
      history.splice(0, history.length - 100)
    }
  }
  
  const generateMockMachines = () => {
    const statuses = ['online', 'offline', 'warning', 'critical']
    const locations = ['Sede', 'Filial 1', 'Filial 2', 'Home Office']
    const departments = ['TI', 'Financeiro', 'RH', 'Vendas', 'Marketing']
    
    return Array.from({ length: 25 }, (_, i) => ({
      id: `machine-${i + 1}`,
      name: `Máquina ${i + 1}`,
      hostname: `PC-${String(i + 1).padStart(3, '0')}`,
      ip: `192.168.1.${i + 10}`,
      status: statuses[Math.floor(Math.random() * statuses.length)],
      location: locations[Math.floor(Math.random() * locations.length)],
      department: departments[Math.floor(Math.random() * departments.length)],
      user: `usuario${i + 1}`,
      os: 'Windows 11 Pro',
      lastSeen: new Date(Date.now() - Math.random() * 3600000),
      performance: {
        cpu: Math.round(Math.random() * 100),
        memory: Math.round(Math.random() * 100),
        disk: Math.round(Math.random() * 100),
        network: Math.round(Math.random() * 100)
      },
      hardware: {
        processor: 'Intel Core i7-12700K',
        memory: '16 GB DDR4',
        storage: '512 GB SSD',
        graphics: 'NVIDIA RTX 3060'
      },
      uptime: Math.floor(Math.random() * 720) // horas
    }))
  }
  
  // Auto-refresh
  let refreshInterval = null
  
  const startAutoRefresh = () => {
    if (monitoringConfig.value.autoRefresh && !refreshInterval) {
      refreshInterval = setInterval(() => {
        fetchMachines()
      }, monitoringConfig.value.refreshRate)
    }
  }
  
  const stopAutoRefresh = () => {
    if (refreshInterval) {
      clearInterval(refreshInterval)
      refreshInterval = null
    }
  }
  
  // WebSocket
  const connectWebSocket = async () => {
    try {
      // Get auth token from auth store
      const authStore = useAuthStore()
      const token = authStore.token
      
      // Build WebSocket URL with token
      const wsUrl = token 
        ? `ws://localhost:8000/api/v1/ws?token=${token}`
        : 'ws://localhost:8000/api/v1/ws'
      
      await websocketService.connect(wsUrl)
      
      // Listeners para eventos WebSocket
      websocketService.on('connected', () => {
        wsConnected.value = true
        logger.info('WebSocket conectado - solicitando dados iniciais')
        websocketService.send('subscribe', { type: 'machines' })
      })

      websocketService.on('disconnected', () => {
        wsConnected.value = false
        logger.warn('WebSocket desconectado')
      })

      websocketService.on('machine_update', ({ data }) => {
        handleMachineUpdate(data)
      })

      websocketService.on('machine_metrics', ({ data }) => {
        handleMachineMetrics(data)
      })

      websocketService.on('machine_alert', ({ data }) => {
        handleMachineAlert(data)
      })

      websocketService.on('machines_list', ({ data }) => {
        handleMachinesList(data)
      })

      websocketService.on('error', ({ error }) => {
        logger.error('Erro no WebSocket:', error)
        wsConnected.value = false
      })

    } catch (error) {
      logger.error('Erro ao conectar WebSocket:', error)
      wsConnected.value = false
    }
  }

  const disconnectWebSocket = () => {
    websocketService.disconnect()
    wsConnected.value = false
  }

  // Handlers para mensagens WebSocket
  const handleMachineUpdate = (data) => {
    const { machineId, updates } = data
    const machineIndex = machines.value.findIndex(m => m.id === machineId)
    
    if (machineIndex !== -1) {
      // Atualiza máquina existente
      machines.value[machineIndex] = {
        ...machines.value[machineIndex],
        ...updates,
        lastUpdate: new Date().toISOString()
      }
      logger.debug(`Máquina ${machineId} atualizada via WebSocket`)
    } else {
      // Adiciona nova máquina
      machines.value.push({
        id: machineId,
        ...updates,
        lastUpdate: new Date().toISOString()
      })
      logger.debug(`Nova máquina ${machineId} adicionada via WebSocket`)
    }
    
    lastUpdate.value = new Date().toISOString()
  }

  const handleMachineMetrics = (data) => {
    const { machineId, metrics } = data
    
    // Atualiza métricas da máquina
    const machine = machines.value.find(m => m.id === machineId)
    if (machine) {
      machine.metrics = {
        ...machine.metrics,
        ...metrics,
        timestamp: new Date().toISOString()
      }
      
      // Adiciona ao histórico de performance
      addPerformanceData(machineId, metrics)
    }
    
    // Atualiza métricas agregadas
    updateAggregatedMetrics()
  }

  const handleMachineAlert = (data) => {
    const { machineId, alert } = data
    
    // Adiciona alerta
    alerts.value.unshift({
      id: Date.now(),
      machineId,
      ...alert,
      timestamp: new Date().toISOString(),
      read: false
    })
    
    // Mantém apenas os últimos 100 alertas
    if (alerts.value.length > 100) {
      alerts.value = alerts.value.slice(0, 100)
    }
    
    logger.info(`Novo alerta para máquina ${machineId}:`, alert)
  }

  const handleMachinesList = (data) => {
    const { machines: machinesList } = data
    
    // Atualiza lista completa de máquinas
    machines.value = machinesList.map(machine => ({
      ...machine,
      lastUpdate: new Date().toISOString()
    }))
    
    lastUpdate.value = new Date().toISOString()
    updateAggregatedMetrics()
    
    logger.info(`Lista de máquinas atualizada via WebSocket: ${machinesList.length} máquinas`)
  }
  
  const updateMonitoringConfig = (newConfig) => {
    monitoringConfig.value = { ...monitoringConfig.value, ...newConfig }
    
    // Reiniciar auto-refresh se necessário
    if (monitoringConfig.value.autoRefresh) {
      stopAutoRefresh()
      startAutoRefresh()
    } else {
      stopAutoRefresh()
    }
  }
  
  // Retorno do store
  return {
    // Estado
    machines,
    selectedMachine,
    loading,
    error,
    lastUpdate,
    wsConnected,
    wsError,
    filters,
    monitoringConfig,
    metrics,
    alerts,
    performanceHistory,
    
    // Computed
    filteredMachines,
    onlineMachines,
    offlineMachines,
    criticalMachines,
    warningMachines,
    
    // Actions
    fetchMachines,
    fetchMachineStatus,
    registerMachine,
    updateMachineStatus,
    selectMachine,
    clearSelection,
    setFilters,
    clearFilters,
    updateMetrics,
    addPerformanceData,
    connectWebSocket,
    disconnectWebSocket,
    startAutoRefresh,
    stopAutoRefresh,
    updateMonitoringConfig,
    
    // WebSocket handlers
    handleMachineUpdate,
    handleMachineMetrics,
    handleMachineAlert,
    handleMachinesList
  }
})