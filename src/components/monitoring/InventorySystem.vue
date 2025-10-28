<template>
  <div class="inventory-system">
    <!-- Header do Sistema de Inventário -->
    <div class="inventory-header">
      <div class="header-content">
        <div class="header-info">
          <h3 class="inventory-title">
            <v-icon icon="mdi-server-network" class="mr-2"></v-icon>
            Sistema de Inventário
          </h3>
          <p class="inventory-subtitle">
            {{ machines.length }} {{ machines.length === 1 ? 'máquina catalogada' : 'máquinas catalogadas' }}
          </p>
        </div>
        
        <div class="header-actions">
          <v-btn
            variant="outlined"
            size="small"
            @click="scanNetwork"
            :loading="isScanning"
            class="mr-2"
          >
            <v-icon icon="mdi-radar" class="mr-1"></v-icon>
            Escanear Rede
          </v-btn>
          
          <v-btn
            variant="outlined"
            size="small"
            @click="refreshInventory"
            :loading="isRefreshing"
            class="mr-2"
          >
            <v-icon icon="mdi-refresh" class="mr-1"></v-icon>
            Atualizar
          </v-btn>
          
          <v-btn
            variant="outlined"
            size="small"
            @click="exportInventory"
            :disabled="machines.length === 0"
          >
            <v-icon icon="mdi-download" class="mr-1"></v-icon>
            Exportar
          </v-btn>
        </div>
      </div>
    </div>

    <!-- Estatísticas do Inventário -->
    <div class="inventory-stats">
      <v-row dense>
        <v-col cols="12" sm="6" md="3">
          <v-card variant="tonal" color="primary">
            <v-card-text class="text-center">
              <v-icon icon="mdi-desktop-classic" size="large" class="mb-2"></v-icon>
              <div class="stat-value">{{ totalMachines }}</div>
              <div class="stat-label">Total de Máquinas</div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-card variant="tonal" color="success">
            <v-card-text class="text-center">
              <v-icon icon="mdi-check-circle" size="large" class="mb-2"></v-icon>
              <div class="stat-value">{{ onlineMachines }}</div>
              <div class="stat-label">Online</div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-card variant="tonal" color="error">
            <v-card-text class="text-center">
              <v-icon icon="mdi-server-off" size="large" class="mb-2"></v-icon>
              <div class="stat-value">{{ offlineMachines }}</div>
              <div class="stat-label">Offline</div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-card variant="tonal" color="info">
            <v-card-text class="text-center">
              <v-icon icon="mdi-microsoft-windows" size="large" class="mb-2"></v-icon>
              <div class="stat-value">{{ windowsMachines }}</div>
              <div class="stat-label">Windows</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- Filtros e Busca -->
    <div class="inventory-filters">
      <v-card>
        <v-card-text>
          <v-row align="center">
            <v-col cols="12" md="4">
              <v-text-field
                v-model="searchQuery"
                label="Buscar máquinas"
                variant="outlined"
                density="compact"
                clearable
                @input="filterMachines"
              >
                <template #prepend-inner>
                  <v-icon icon="mdi-magnify"></v-icon>
                </template>
              </v-text-field>
            </v-col>
            
            <v-col cols="12" md="3">
              <v-select
                v-model="statusFilter"
                :items="statusOptions"
                label="Status"
                variant="outlined"
                density="compact"
                clearable
                @update:model-value="filterMachines"
              >
                <template #prepend-inner>
                  <v-icon icon="mdi-filter"></v-icon>
                </template>
              </v-select>
            </v-col>
            
            <v-col cols="12" md="3">
              <v-select
                v-model="osFilter"
                :items="osOptions"
                label="Sistema Operacional"
                variant="outlined"
                density="compact"
                clearable
                @update:model-value="filterMachines"
              >
                <template #prepend-inner>
                  <v-icon icon="mdi-microsoft-windows"></v-icon>
                </template>
              </v-select>
            </v-col>
            
            <v-col cols="12" md="2">
              <v-btn
                variant="outlined"
                block
                @click="clearFilters"
                :disabled="!hasActiveFilters"
              >
                <v-icon icon="mdi-filter-remove" class="mr-1"></v-icon>
                Limpar
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </div>

    <!-- Lista de Máquinas -->
    <div class="inventory-list">
      <v-card>
        <v-card-title>
          <div class="d-flex justify-space-between align-center w-100">
            <span>Inventário de Máquinas</span>
            <v-chip
              color="primary"
              size="small"
              variant="flat"
            >
              {{ filteredMachines.length }} {{ filteredMachines.length === 1 ? 'máquina' : 'máquinas' }}
            </v-chip>
          </div>
        </v-card-title>
        
        <v-card-text v-if="filteredMachines.length === 0" class="text-center py-8">
          <v-icon icon="mdi-server-network-off" size="64" color="surface-variant" class="mb-4"></v-icon>
          <h4 class="text-h6 mb-2">Nenhuma máquina encontrada</h4>
          <p class="text-body-2 text-medium-emphasis">
            {{ machines.length === 0 ? 'Execute um escaneamento de rede para descobrir máquinas.' : 'Ajuste os filtros para encontrar máquinas específicas.' }}
          </p>
        </v-card-text>
        
        <div v-else>
          <v-data-table
            :headers="tableHeaders"
            :items="filteredMachines"
            :loading="isRefreshing"
            item-value="id"
            class="inventory-table"
          >
            <!-- Status Column -->
            <template #item.status="{ item }">
              <v-chip
                :color="getStatusColor(item.status)"
                size="small"
                variant="flat"
              >
                <v-icon :icon="getStatusIcon(item.status)" size="small" class="mr-1"></v-icon>
                {{ item.status }}
              </v-chip>
            </template>
            
            <!-- OS Column -->
            <template #item.os_name="{ item }">
              <div class="d-flex align-center">
                <v-icon :icon="getOSIcon(item.os_name)" class="mr-2"></v-icon>
                <div>
                  <div class="font-weight-medium">{{ item.os_name }}</div>
                  <div class="text-caption text-medium-emphasis">{{ item.os_version }}</div>
                </div>
              </div>
            </template>
            
            <!-- Hardware Column -->
            <template #item.hardware="{ item }">
              <div class="hardware-info">
                <div class="text-caption">
                  <v-icon icon="mdi-memory" size="small" class="mr-1"></v-icon>
                  {{ formatMemory(item.total_memory) }}
                </div>
                <div class="text-caption">
                  <v-icon icon="mdi-cpu-64-bit" size="small" class="mr-1"></v-icon>
                  {{ item.cpu_cores }} cores
                </div>
                <div class="text-caption">
                  <v-icon icon="mdi-harddisk" size="small" class="mr-1"></v-icon>
                  {{ formatStorage(item.total_storage) }}
                </div>
              </div>
            </template>
            
            <!-- Last Seen Column -->
            <template #item.last_seen="{ item }">
              <div class="text-caption">
                {{ formatLastSeen(item.last_seen) }}
              </div>
            </template>
            
            <!-- Actions Column -->
            <template #item.actions="{ item }">
              <div class="action-buttons">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  variant="text"
                  @click="viewMachineDetails(item)"
                  class="mr-1"
                ></v-btn>
                
                <v-btn
                  icon="mdi-monitor-dashboard"
                  size="small"
                  variant="text"
                  color="primary"
                  @click="openMonitoring(item)"
                  :disabled="item.status === 'offline'"
                  class="mr-1"
                ></v-btn>
                
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  variant="text"
                  @click="editMachine(item)"
                  class="mr-1"
                ></v-btn>
                
                <v-btn
                  icon="mdi-delete"
                  size="small"
                  variant="text"
                  color="error"
                  @click="deleteMachine(item)"
                ></v-btn>
              </div>
            </template>
          </v-data-table>
        </div>
      </v-card>
    </div>

    <!-- Dialog de Detalhes da Máquina -->
    <v-dialog v-model="showDetailsDialog" max-width="800">
      <v-card v-if="selectedMachine">
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-desktop-classic" class="mr-3"></v-icon>
          {{ selectedMachine.hostname }}
          <v-spacer></v-spacer>
          <v-chip
            :color="getStatusColor(selectedMachine.status)"
            size="small"
            variant="flat"
          >
            {{ selectedMachine.status }}
          </v-chip>
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <h4 class="text-subtitle-1 mb-3">Informações Básicas</h4>
              <div class="detail-item mb-2">
                <span class="detail-label">Nome:</span>
                <span class="detail-value">{{ selectedMachine.hostname }}</span>
              </div>
              <div class="detail-item mb-2">
                <span class="detail-label">Endereço IP:</span>
                <span class="detail-value">{{ selectedMachine.ip_address }}</span>
              </div>
              <div class="detail-item mb-2">
                <span class="detail-label">Endereço MAC:</span>
                <span class="detail-value">{{ selectedMachine.mac_address || 'N/A' }}</span>
              </div>
              <div class="detail-item mb-2">
                <span class="detail-label">Domínio:</span>
                <span class="detail-value">{{ selectedMachine.domain || 'N/A' }}</span>
              </div>
            </v-col>
            
            <v-col cols="12" md="6">
              <h4 class="text-subtitle-1 mb-3">Sistema Operacional</h4>
              <div class="detail-item mb-2">
                <span class="detail-label">SO:</span>
                <span class="detail-value">{{ selectedMachine.os_name }}</span>
              </div>
              <div class="detail-item mb-2">
                <span class="detail-label">Versão:</span>
                <span class="detail-value">{{ selectedMachine.os_version }}</span>
              </div>
              <div class="detail-item mb-2">
                <span class="detail-label">Arquitetura:</span>
                <span class="detail-value">{{ selectedMachine.architecture || 'N/A' }}</span>
              </div>
              <div class="detail-item mb-2">
                <span class="detail-label">Última atualização:</span>
                <span class="detail-value">{{ selectedMachine.last_update || 'N/A' }}</span>
              </div>
            </v-col>
          </v-row>
          
          <v-divider class="my-4"></v-divider>
          
          <v-row>
            <v-col cols="12" md="6">
              <h4 class="text-subtitle-1 mb-3">Hardware</h4>
              <div class="detail-item mb-2">
                <span class="detail-label">Processador:</span>
                <span class="detail-value">{{ selectedMachine.cpu_model || 'N/A' }}</span>
              </div>
              <div class="detail-item mb-2">
                <span class="detail-label">Cores:</span>
                <span class="detail-value">{{ selectedMachine.cpu_cores }}</span>
              </div>
              <div class="detail-item mb-2">
                <span class="detail-label">Memória RAM:</span>
                <span class="detail-value">{{ formatMemory(selectedMachine.total_memory) }}</span>
              </div>
              <div class="detail-item mb-2">
                <span class="detail-label">Armazenamento:</span>
                <span class="detail-value">{{ formatStorage(selectedMachine.total_storage) }}</span>
              </div>
            </v-col>
            
            <v-col cols="12" md="6">
              <h4 class="text-subtitle-1 mb-3">Rede</h4>
              <div class="detail-item mb-2">
                <span class="detail-label">Interfaces:</span>
                <span class="detail-value">{{ selectedMachine.network_interfaces || 'N/A' }}</span>
              </div>
              <div class="detail-item mb-2">
                <span class="detail-label">Gateway:</span>
                <span class="detail-value">{{ selectedMachine.gateway || 'N/A' }}</span>
              </div>
              <div class="detail-item mb-2">
                <span class="detail-label">DNS:</span>
                <span class="detail-value">{{ selectedMachine.dns_servers || 'N/A' }}</span>
              </div>
              <div class="detail-item mb-2">
                <span class="detail-label">Última conexão:</span>
                <span class="detail-value">{{ formatLastSeen(selectedMachine.last_seen) }}</span>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="showDetailsDialog = false"
          >
            Fechar
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            @click="openMonitoring(selectedMachine)"
            :disabled="selectedMachine.status === 'offline'"
          >
            Monitorar
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar para notificações -->
    <v-snackbar
      v-model="showNotification"
      :color="notificationColor"
      :timeout="3000"
      location="top right"
    >
      {{ notificationMessage }}
      <template #actions>
        <v-btn
          variant="text"
          @click="showNotification = false"
        >
          Fechar
        </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup>
import logger from '@/utils/logger'
import { ref, computed, onMounted } from 'vue'
import { machineMonitoringAPI } from '@/services/api'

// Reactive data
const machines = ref([])
const filteredMachines = ref([])
const searchQuery = ref('')
const statusFilter = ref(null)
const osFilter = ref(null)
const isScanning = ref(false)
const isRefreshing = ref(false)
const showDetailsDialog = ref(false)
const selectedMachine = ref(null)

// Notification system
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationColor = ref('success')

// Table configuration
const tableHeaders = [
  { title: 'Nome', key: 'hostname', sortable: true },
  { title: 'IP', key: 'ip_address', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Sistema Operacional', key: 'os_name', sortable: true },
  { title: 'Hardware', key: 'hardware', sortable: false },
  { title: 'Última Conexão', key: 'last_seen', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false }
]

// Filter options
const statusOptions = [
  { title: 'Online', value: 'online' },
  { title: 'Offline', value: 'offline' },
  { title: 'Desconhecido', value: 'unknown' }
]

const osOptions = [
  { title: 'Windows 11', value: 'Windows 11' },
  { title: 'Windows 10', value: 'Windows 10' },
  { title: 'Windows Server 2022', value: 'Windows Server 2022' },
  { title: 'Windows Server 2019', value: 'Windows Server 2019' }
]

// Computed properties
const totalMachines = computed(() => machines.value.length)

const onlineMachines = computed(() => {
  return machines.value.filter(m => m.status === 'online').length
})

const offlineMachines = computed(() => {
  return machines.value.filter(m => m.status === 'offline').length
})

const windowsMachines = computed(() => {
  return machines.value.filter(m => m.os_name.includes('Windows')).length
})

const hasActiveFilters = computed(() => {
  return searchQuery.value || statusFilter.value || osFilter.value
})

// Methods
const loadInventory = async () => {
  try {
    const response = await machineMonitoringAPI.getMachines()
    // Backend retorna objeto com { machines: [...], total_count, limit, offset }
    const backendMachines = Array.isArray(response.data?.machines)
      ? response.data.machines
      : Array.isArray(response.data)
        ? response.data
        : []
    machines.value = transformMachinesFromBackend(backendMachines)
  } catch (error) {
    logger.error('Error loading inventory:', error)
    // Dados simulados para demonstração
    machines.value = generateMockInventory()
  }
  filterMachines()
}

const generateMockInventory = () => {
  return [
    {
      id: 1,
      hostname: 'DESKTOP-001',
      ip_address: '192.168.1.100',
      mac_address: '00:1B:44:11:3A:B7',
      status: 'online',
      os_name: 'Windows 11',
      os_version: '22H2',
      architecture: 'x64',
      cpu_model: 'Intel Core i7-12700K',
      cpu_cores: 12,
      total_memory: 16777216, // 16GB em KB
      total_storage: 1073741824, // 1TB em KB
      domain: 'EMPRESA.LOCAL',
      last_seen: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
      last_update: '2024-01-15',
      network_interfaces: '2',
      gateway: '192.168.1.1',
      dns_servers: '192.168.1.1, 8.8.8.8'
    },
    {
      id: 2,
      hostname: 'DESKTOP-002',
      ip_address: '192.168.1.101',
      mac_address: '00:1B:44:11:3A:B8',
      status: 'online',
      os_name: 'Windows 10',
      os_version: '22H2',
      architecture: 'x64',
      cpu_model: 'AMD Ryzen 5 5600X',
      cpu_cores: 6,
      total_memory: 8388608, // 8GB em KB
      total_storage: 536870912, // 512GB em KB
      domain: 'EMPRESA.LOCAL',
      last_seen: new Date(Date.now() - 10 * 60 * 1000).toISOString(),
      last_update: '2024-01-10',
      network_interfaces: '1',
      gateway: '192.168.1.1',
      dns_servers: '192.168.1.1'
    },
    {
      id: 3,
      hostname: 'SERVER-001',
      ip_address: '192.168.1.10',
      mac_address: '00:1B:44:11:3A:B9',
      status: 'online',
      os_name: 'Windows Server 2022',
      os_version: 'Standard',
      architecture: 'x64',
      cpu_model: 'Intel Xeon E5-2690',
      cpu_cores: 16,
      total_memory: 67108864, // 64GB em KB
      total_storage: 2147483648, // 2TB em KB
      domain: 'EMPRESA.LOCAL',
      last_seen: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
      last_update: '2024-01-20',
      network_interfaces: '4',
      gateway: '192.168.1.1',
      dns_servers: '127.0.0.1, 192.168.1.1'
    },
    {
      id: 4,
      hostname: 'LAPTOP-001',
      ip_address: '192.168.1.150',
      mac_address: '00:1B:44:11:3A:C0',
      status: 'offline',
      os_name: 'Windows 11',
      os_version: '23H2',
      architecture: 'x64',
      cpu_model: 'Intel Core i5-1235U',
      cpu_cores: 10,
      total_memory: 16777216, // 16GB em KB
      total_storage: 536870912, // 512GB em KB
      domain: 'EMPRESA.LOCAL',
      last_seen: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      last_update: '2024-01-12',
      network_interfaces: '2',
      gateway: '192.168.1.1',
      dns_servers: '192.168.1.1, 8.8.8.8'
    }
  ]
}

const scanNetwork = async () => {
  isScanning.value = true
  try {
    // Simula escaneamento de rede
    await new Promise(resolve => setTimeout(resolve, 3000))
    await loadInventory()
    showSuccess('Escaneamento de rede concluído')
  } catch (error) {
    showError('Erro durante o escaneamento de rede')
  } finally {
    isScanning.value = false
  }
}

const refreshInventory = async () => {
  isRefreshing.value = true
  try {
    await loadInventory()
    showSuccess('Inventário atualizado com sucesso')
  } catch (error) {
    showError('Erro ao atualizar inventário')
  } finally {
    isRefreshing.value = false
  }
}

const exportInventory = () => {
  const csvContent = generateCSV()
  downloadCSV(csvContent, 'inventario-maquinas.csv')
  showSuccess('Inventário exportado com sucesso')
}

const generateCSV = () => {
  const headers = ['Nome', 'IP', 'Status', 'SO', 'Versão', 'CPU', 'Memória', 'Armazenamento', 'Última Conexão']
  const rows = machines.value.map(machine => [
    machine.hostname,
    machine.ip_address,
    machine.status,
    machine.os_name,
    machine.os_version,
    machine.cpu_model,
    formatMemory(machine.total_memory),
    formatStorage(machine.total_storage),
    formatLastSeen(machine.last_seen)
  ])
  
  return [headers, ...rows].map(row => row.join(',')).join('\n')
}

const downloadCSV = (content, filename) => {
  const blob = new Blob([content], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', filename)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const filterMachines = () => {
  let filtered = [...machines.value]
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(machine => 
      machine.hostname.toLowerCase().includes(query) ||
      machine.ip_address.includes(query) ||
      machine.os_name.toLowerCase().includes(query)
    )
  }
  
  if (statusFilter.value) {
    filtered = filtered.filter(machine => machine.status === statusFilter.value)
  }
  
  if (osFilter.value) {
    filtered = filtered.filter(machine => machine.os_name === osFilter.value)
  }
  
  filteredMachines.value = filtered
}

const clearFilters = () => {
  searchQuery.value = ''
  statusFilter.value = null
  osFilter.value = null
  filterMachines()
}

const viewMachineDetails = (machine) => {
  selectedMachine.value = machine
  showDetailsDialog.value = true
}

const openMonitoring = (machine) => {
  // Implementar navegação para o dashboard de monitoramento
  showInfo(`Abrindo monitoramento para ${machine.hostname}`)
}

const editMachine = (machine) => {
  showInfo(`Funcionalidade de edição para ${machine.hostname} em desenvolvimento`)
}

const deleteMachine = (machine) => {
  const index = machines.value.findIndex(m => m.id === machine.id)
  if (index !== -1) {
    machines.value.splice(index, 1)
    filterMachines()
    showSuccess(`Máquina ${machine.hostname} removida do inventário`)
  }
}

// Utility functions
const getStatusColor = (status) => {
  switch (status) {
    case 'online': return 'success'
    case 'offline': return 'error'
    case 'unknown': return 'warning'
    default: return 'surface-variant'
  }
}

const getStatusIcon = (status) => {
  switch (status) {
    case 'online': return 'mdi-check-circle'
    case 'offline': return 'mdi-close-circle'
    case 'unknown': return 'mdi-help-circle'
    default: return 'mdi-help-circle'
  }
}

const getOSIcon = (osName) => {
  if (osName.includes('Windows')) return 'mdi-microsoft-windows'
  if (osName.includes('Linux')) return 'mdi-linux'
  if (osName.includes('macOS')) return 'mdi-apple'
  return 'mdi-desktop-classic'
}

const formatMemory = (memoryKB) => {
  if (!memoryKB) return 'N/A'
  const memoryGB = memoryKB / 1024 / 1024
  return `${memoryGB.toFixed(0)} GB`
}

const formatStorage = (storageKB) => {
  if (!storageKB) return 'N/A'
  const storageGB = storageKB / 1024 / 1024
  if (storageGB >= 1024) {
    return `${(storageGB / 1024).toFixed(1)} TB`
  }
  return `${storageGB.toFixed(0)} GB`
}

const formatLastSeen = (dateString) => {
  if (!dateString) return 'N/A'
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = now - date
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)
  
  if (diffMins < 1) return 'Agora'
  if (diffMins < 60) return `${diffMins}min atrás`
  if (diffHours < 24) return `${diffHours}h atrás`
  if (diffDays < 7) return `${diffDays}d atrás`
  return date.toLocaleDateString('pt-BR')
}

// Notification helpers
const showSuccess = (message) => {
  notificationMessage.value = message
  notificationColor.value = 'success'
  showNotification.value = true
}

const showError = (message) => {
  notificationMessage.value = message
  notificationColor.value = 'error'
  showNotification.value = true
}

const showInfo = (message) => {
  notificationMessage.value = message
  notificationColor.value = 'info'
  showNotification.value = true
}

// Lifecycle hooks
onMounted(() => {
  loadInventory()
})

// Normaliza e mapeia o formato das máquinas do backend para o formato esperado pelo Inventário
const transformMachinesFromBackend = (backendMachines = []) => {
  const toKB = (gb) => {
    if (gb === null || gb === undefined) return undefined
    return Math.round(Number(gb) * 1024 * 1024)
  }
  const normalizeOSName = (os) => {
    if (!os) return 'Desconhecido'
    const s = String(os)
    if (s.toLowerCase() === 'windows') return 'Windows'
    if (s.toLowerCase() === 'linux') return 'Linux'
    if (s.toLowerCase() === 'macos') return 'macOS'
    return s
  }
  return backendMachines.map(m => {
    const osName = normalizeOSName(m.operating_system)
    const hardwareParts = []
    if (m.cpu_model) hardwareParts.push(m.cpu_model)
    if (m.cpu_cores) hardwareParts.push(`${m.cpu_cores} cores`)
    if (m.architecture) hardwareParts.push(m.architecture)
    if (typeof m.ram_total_gb === 'number') hardwareParts.push(`${m.ram_total_gb.toFixed(1)} GB RAM`)
    if (typeof m.disk_total_gb === 'number') hardwareParts.push(`${m.disk_total_gb.toFixed(1)} GB Disco`)
    const hardware = hardwareParts.join(' | ')

    return {
      id: m.id,
      hostname: m.hostname || m.name || m.machine_id || `machine-${m.id}`,
      ip_address: m.ip_address,
      mac_address: m.mac_address,
      status: m.status || 'unknown',
      os_name: osName,
      os_version: m.os_version,
      architecture: m.architecture,
      cpu_model: m.cpu_model,
      cpu_cores: m.cpu_cores,
      total_memory: toKB(m.ram_total_gb),
      total_storage: toKB(m.disk_total_gb),
      domain: m.domain,
      last_seen: m.agent_last_seen,
      last_update: m.updated_at,
      network_interfaces: m.custom_metadata?.network_interfaces,
      gateway: m.custom_metadata?.gateway,
      dns_servers: m.custom_metadata?.dns_servers,
      hardware
    }
  })
}
</script>

<style scoped>
.inventory-system {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.inventory-header {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.header-info {
  flex: 1;
}

.inventory-title {
  display: flex;
  align-items: center;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 4px;
  color: rgb(var(--v-theme-on-background));
}

.inventory-subtitle {
  color: rgb(var(--v-theme-on-background-variant));
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.inventory-stats {
  margin-top: 16px;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  line-height: 1;
}

.stat-label {
  font-size: 0.75rem;
  opacity: 0.8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.hardware-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.action-buttons {
  display: flex;
  align-items: center;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.detail-label {
  font-weight: 500;
  min-width: 120px;
}

.detail-value {
  flex: 1;
}

/* Responsividade */
@media (max-width: 960px) {
  .header-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 600px) {
  .header-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 4px;
  }
}

/* Animações */
.inventory-table {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>