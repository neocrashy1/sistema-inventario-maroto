import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useNetworkDevicesStore = defineStore('networkDevices', () => {
  // Estado
  const discoveredDevices = ref([])
  const registeredDevices = ref([])
  const scanHistory = ref([])
  const ubiquitiDevices = ref([])
  const isScanning = ref(false)
  const lastScanDate = ref(null)

  // Getters
  const totalDiscovered = computed(() => discoveredDevices.value.length)
  const totalRegistered = computed(() => registeredDevices.value.length)
  const unregisteredDevices = computed(() => {
    return discoveredDevices.value.filter(device => !isDeviceRegistered(device))
  })
  const duplicateDevices = computed(() => {
    return discoveredDevices.value.filter(device => isDeviceRegistered(device))
  })

  // Verifica se um dispositivo já está cadastrado
  const isDeviceRegistered = (device) => {
    return registeredDevices.value.some(registered => 
      registered.mac === device.mac || 
      registered.serviceTag === device.serviceTag ||
      registered.ip === device.ip
    )
  }

  // Busca dispositivo registrado por critério
  const findRegisteredDevice = (device) => {
    return registeredDevices.value.find(registered => 
      registered.mac === device.mac || 
      registered.serviceTag === device.serviceTag ||
      registered.ip === device.ip
    )
  }

  // Adiciona dispositivos descobertos
  const addDiscoveredDevices = (devices) => {
    // Merge com dispositivos existentes, evitando duplicatas
    devices.forEach(newDevice => {
      const existingIndex = discoveredDevices.value.findIndex(existing => 
        existing.mac === newDevice.mac || existing.ip === newDevice.ip
      )
      
      if (existingIndex >= 0) {
        // Atualiza dispositivo existente
        discoveredDevices.value[existingIndex] = {
          ...discoveredDevices.value[existingIndex],
          ...newDevice,
          lastSeen: new Date().toISOString()
        }
      } else {
        // Adiciona novo dispositivo com informações detalhadas
        discoveredDevices.value.push({
          ...newDevice,
          discoveredAt: new Date().toISOString(),
          lastSeen: new Date().toISOString(),
          // Informações de hardware
          hardwareInfo: newDevice.hardwareInfo || {
            processor: newDevice.processor || 'N/A',
            memory: newDevice.memory || 'N/A',
            storage: newDevice.storage || 'N/A',
            graphics: newDevice.graphics || 'N/A',
            motherboard: newDevice.motherboard || 'N/A'
          },
          // Informações do usuário
          userInfo: newDevice.userInfo || {
            currentUser: newDevice.currentUser || 'N/A',
            lastLoggedUser: newDevice.lastLoggedUser || 'N/A',
            domain: newDevice.domain || 'N/A',
            userProfile: newDevice.userProfile || 'N/A'
          },
          // Identificação do sistema
          systemInfo: newDevice.systemInfo || {
            serialNumber: newDevice.serialNumber || newDevice.serviceTag || 'N/A',
            serviceTag: newDevice.serviceTag || newDevice.serialNumber || 'N/A',
            assetTag: newDevice.assetTag || 'N/A',
            biosVersion: newDevice.biosVersion || 'N/A',
            systemModel: newDevice.systemModel || newDevice.model || 'N/A',
            systemManufacturer: newDevice.systemManufacturer || newDevice.vendor || 'N/A'
          }
        })
      }
    })
    
    lastScanDate.value = new Date().toISOString()
  }

  // Registra um dispositivo
  const registerDevice = (device, assetInfo) => {
    const registeredDevice = {
      ...device,
      ...assetInfo,
      registeredAt: new Date().toISOString(),
      status: 'registered'
    }
    
    registeredDevices.value.push(registeredDevice)
    
    // Atualiza o dispositivo descoberto
    const discoveredIndex = discoveredDevices.value.findIndex(d => 
      d.mac === device.mac || d.ip === device.ip
    )
    
    if (discoveredIndex >= 0) {
      discoveredDevices.value[discoveredIndex].isRegistered = true
      discoveredDevices.value[discoveredIndex].assetId = assetInfo.id
    }
  }

  // Remove dispositivo registrado
  const unregisterDevice = (deviceId) => {
    const index = registeredDevices.value.findIndex(d => d.id === deviceId)
    if (index >= 0) {
      const device = registeredDevices.value[index]
      registeredDevices.value.splice(index, 1)
      
      // Atualiza dispositivo descoberto
      const discoveredIndex = discoveredDevices.value.findIndex(d => 
        d.mac === device.mac || d.ip === device.ip
      )
      
      if (discoveredIndex >= 0) {
        discoveredDevices.value[discoveredIndex].isRegistered = false
        delete discoveredDevices.value[discoveredIndex].assetId
      }
    }
  }

  // Adiciona dispositivos do Ubiquiti
  const addUbiquitiDevices = (devices) => {
    ubiquitiDevices.value = devices.map(device => ({
      ...device,
      source: 'ubiquiti',
      discoveredAt: new Date().toISOString()
    }))
  }

  // Adiciona entrada ao histórico de scan
  const addScanHistory = (scanInfo) => {
    scanHistory.value.unshift({
      ...scanInfo,
      timestamp: new Date().toISOString()
    })
    
    // Mantém apenas os últimos 50 scans
    if (scanHistory.value.length > 50) {
      scanHistory.value = scanHistory.value.slice(0, 50)
    }
  }

  // Limpa dispositivos descobertos
  const clearDiscoveredDevices = () => {
    discoveredDevices.value = []
  }

  // Limpa histórico
  const clearScanHistory = () => {
    scanHistory.value = []
  }

  // Atualiza status de scan
  const setScanningStatus = (status) => {
    isScanning.value = status
  }

  // Busca dispositivos por critério
  const searchDevices = (query) => {
    const searchTerm = query.toLowerCase()
    return discoveredDevices.value.filter(device => 
      device.hostname?.toLowerCase().includes(searchTerm) ||
      device.ip?.includes(searchTerm) ||
      device.mac?.toLowerCase().includes(searchTerm) ||
      device.manufacturer?.toLowerCase().includes(searchTerm) ||
      device.model?.toLowerCase().includes(searchTerm) ||
      device.serviceTag?.toLowerCase().includes(searchTerm)
    )
  }

  // Removido: filtro por tipo de dispositivo (não utilizado)

  // Filtra dispositivos por status de registro
  const filterDevicesByRegistrationStatus = (isRegistered) => {
    return discoveredDevices.value.filter(device => 
      isDeviceRegistered(device) === isRegistered
    )
  }

  // Estatísticas de rede
  const getNetworkStats = computed(() => {
    const stats = {
      totalDevices: discoveredDevices.value.length,
      registeredDevices: duplicateDevices.value.length,
      unregisteredDevices: unregisteredDevices.value.length,
      manufacturers: {},
      lastScan: lastScanDate.value
    }
    
    // Conta por fabricante
    discoveredDevices.value.forEach(device => {
      const manufacturer = device.manufacturer || 'Unknown'
      stats.manufacturers[manufacturer] = (stats.manufacturers[manufacturer] || 0) + 1
    })
    
    return stats
  })

  // Sincroniza com store de assets
  const syncWithAssets = (assets) => {
    registeredDevices.value = assets
      .filter(asset => asset.networkInfo)
      .map(asset => ({
        id: asset.id,
        name: asset.name,
        ip: asset.networkInfo.ip,
        mac: asset.networkInfo.mac,
        hostname: asset.networkInfo.hostname,
        serviceTag: asset.specifications?.serviceTag,
        manufacturer: asset.specifications?.manufacturer,
        model: asset.specifications?.model,
        registeredAt: asset.networkInfo.registeredAt || asset.createdAt,
        assetId: asset.id
      }))
  }

  // Detecta mudanças na rede
  const detectNetworkChanges = () => {
    const changes = {
      newDevices: [],
      offlineDevices: [],
      changedDevices: []
    }
    
    const now = new Date()
    const offlineThreshold = 24 * 60 * 60 * 1000 // 24 horas
    
    // Dispositivos offline
    discoveredDevices.value.forEach(device => {
      const lastSeen = new Date(device.lastSeen)
      if (now - lastSeen > offlineThreshold) {
        changes.offlineDevices.push(device)
      }
    })
    
    // Novos dispositivos (descobertos nas últimas 24h)
    discoveredDevices.value.forEach(device => {
      const discoveredAt = new Date(device.discoveredAt)
      if (now - discoveredAt < offlineThreshold && !isDeviceRegistered(device)) {
        changes.newDevices.push(device)
      }
    })
    
    return changes
  }

  return {
    // Estado
    discoveredDevices,
    registeredDevices,
    scanHistory,
    ubiquitiDevices,
    isScanning,
    lastScanDate,
    
    // Getters
    totalDiscovered,
    totalRegistered,
    unregisteredDevices,
    duplicateDevices,
    getNetworkStats,
    
    // Actions
    isDeviceRegistered,
    findRegisteredDevice,
    addDiscoveredDevices,
    registerDevice,
    unregisterDevice,
    addUbiquitiDevices,
    addScanHistory,
    clearDiscoveredDevices,
    clearScanHistory,
    setScanningStatus,
    searchDevices,
    filterDevicesByRegistrationStatus,
    syncWithAssets,
    detectNetworkChanges
  }
})