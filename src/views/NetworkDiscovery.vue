<template>
  <div class="network-discovery">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">
            <i class="fas fa-network-wired"></i>
            Descoberta de Rede
          </h1>
          <p class="page-subtitle">
            Descubra e cadastre automaticamente máquinas na rede
          </p>
        </div>
        <div class="header-actions">
          <button 
            class="btn btn-outline" 
            @click="showReports = !showReports"
            :class="{ active: showReports }"
          >
            <i class="fas fa-chart-line"></i>
            {{ showReports ? 'Ocultar Relatórios' : 'Ver Relatórios' }}
          </button>
          <button 
            class="btn btn-secondary"
            @click="clearResults"
            :disabled="isScanning"
          >
            <i class="fas fa-trash"></i>
            Limpar Resultados
          </button>
          <button 
            class="btn btn-primary"
            @click="startScan"
            :disabled="isScanning"
          >
            <i class="fas fa-search"></i>
            {{ isScanning ? 'Escaneando...' : 'Pesquisar Rede' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Reports Section -->
    <div v-if="showReports" class="reports-section">
      <DiscoveryReport @view-details="viewDeviceDetails" />
    </div>

    <!-- Configuration Panel -->
    <div class="config-panel">
      <div class="panel-header">
        <h3>
          <i class="fas fa-cog"></i>
          Configurações do Scan
        </h3>
      </div>
      <div class="panel-content">
        <div class="config-grid">
          <div class="config-item">
            <label for="networkRange">Faixa de Rede</label>
            <input
              id="networkRange"
              v-model="scanConfig.networkRange"
              type="text"
              placeholder="192.168.1.0/24"
              :disabled="isScanning"
            />
          </div>
          <div class="config-item">
            <label for="timeout">Timeout (ms)</label>
            <input
              id="timeout"
              v-model.number="scanConfig.timeout"
              type="number"
              min="1000"
              max="10000"
              :disabled="isScanning"
            />
          </div>
          <div class="config-item">
            <label for="maxConcurrent">Máx. Simultâneos</label>
            <input
              id="maxConcurrent"
              v-model.number="scanConfig.maxConcurrent"
              type="number"
              min="10"
              max="100"
              :disabled="isScanning"
            />
          </div>
          <div class="config-item">
            <label class="checkbox-label">
              <input
                v-model="scanConfig.autoRegister"
                type="checkbox"
                :disabled="isScanning"
              />
              <span class="checkmark"></span>
              Cadastro Automático
            </label>
          </div>
          <div class="config-item">
            <label class="checkbox-label">
              <input
                v-model="scanConfig.updateExisting"
                type="checkbox"
                :disabled="isScanning"
              />
              <span class="checkmark"></span>
              Atualizar Existentes
            </label>
          </div>
          <div class="config-item">
            <label class="checkbox-label">
              <input
                v-model="scanConfig.includeOffline"
                type="checkbox"
                :disabled="isScanning"
              />
              <span class="checkmark"></span>
              Incluir Offline
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- Progress Bar -->
    <div v-if="isScanning || scanProgress > 0" class="progress-panel">
      <div class="progress-header">
        <h3>Progresso do Scan</h3>
        <button 
          v-if="isScanning"
          class="btn btn-danger btn-sm"
          @click="cancelScan"
        >
          <i class="fas fa-stop"></i>
          Cancelar
        </button>
      </div>
      <div class="progress-bar">
        <div 
          class="progress-fill"
          :style="{ width: scanProgress + '%' }"
        ></div>
      </div>
      <div class="progress-info">
        <span>{{ scanProgress }}% - {{ devicesFound }} dispositivos encontrados</span>
      </div>
    </div>

    <!-- Results Summary -->
    <div v-if="discoveryResults" class="results-summary">
      <div class="summary-cards">
        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-desktop text-blue"></i>
          </div>
          <div class="card-content">
            <h4>{{ discoveryResults.scanResult?.devicesFound || 0 }}</h4>
            <p>Dispositivos Encontrados</p>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-plus-circle text-green"></i>
          </div>
          <div class="card-content">
            <h4>{{ discoveryResults.registeredDevices?.length || 0 }}</h4>
            <p>Novos Cadastros</p>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-check-circle text-orange"></i>
          </div>
          <div class="card-content">
            <h4>{{ discoveryResults.existingDevices?.length || 0 }}</h4>
            <p>Já Cadastrados</p>
          </div>
        </div>
        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-exclamation-triangle text-red"></i>
          </div>
          <div class="card-content">
            <h4>{{ discoveryResults.errors?.length || 0 }}</h4>
            <p>Erros</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Devices Table -->
    <div v-if="discoveredDevices.length > 0" class="devices-table-panel">
      <div class="panel-header">
        <h3>
          <i class="fas fa-list"></i>
          Dispositivos Descobertos
        </h3>
        <div class="table-actions">
          <div class="filter-group">
            <select v-model="filterVendor" class="filter-select">
              <option value="">Todos os Fabricantes</option>
              <option v-for="vendor in uniqueVendors" :key="vendor" :value="vendor">
                {{ vendor }}
              </option>
            </select>
            <select v-model="filterType" class="filter-select">
              <option value="">Todos os Tipos</option>
              <option v-for="type in uniqueTypes" :key="type" :value="type">
                {{ type }}
              </option>
            </select>
          </div>
          <button class="btn btn-secondary btn-sm" @click="exportResults">
            <i class="fas fa-download"></i>
            Exportar
          </button>
        </div>
      </div>
      <div class="table-container">
        <table class="devices-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>IP</th>
              <th>Hostname</th>
              <th>Usuário</th>
              <th>Fabricante</th>
              <th>Tipo</th>
              <th>Serial/Service Tag</th>
              <th>MAC Address</th>
              <th>SO</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="device in filteredDevices" :key="device.ip">
              <td>
                <span 
                  class="status-badge"
                  :class="getStatusClass(device)"
                >
                  {{ getStatusText(device) }}
                </span>
              </td>
              <td class="ip-cell">{{ device.ip }}</td>
              <td class="hostname-cell">{{ device.hostname || 'N/A' }}</td>
              <td class="user-cell">
                <div class="user-info">
                  <i class="fas fa-user"></i>
                  {{ device.userInfo?.currentUser || device.currentUser || 'N/A' }}
                </div>
              </td>
              <td class="vendor-cell">
                <div class="vendor-info">
                  <i :class="getVendorIcon(device.vendor)"></i>
                  {{ device.vendor }}
                </div>
              </td>
              <td class="type-cell">{{ device.deviceType }}</td>
              <td class="serial-cell">
                <div class="serial-info">
                  <div class="serial-number">
                    <small>SN:</small> {{ device.systemInfo?.serialNumber || device.serialNumber || 'N/A' }}
                  </div>
                  <div class="service-tag">
                    <small>ST:</small> {{ device.systemInfo?.serviceTag || device.serviceTag || 'N/A' }}
                  </div>
                </div>
              </td>
              <td class="mac-cell">{{ device.macAddress }}</td>
              <td class="os-cell">{{ device.operatingSystem || 'N/A' }}</td>
              <td class="actions-cell">
                <div class="action-buttons">
                  <button 
                    class="btn btn-sm btn-primary"
                    @click="viewDeviceDetails(device)"
                    title="Ver Detalhes"
                  >
                    <i class="fas fa-eye"></i>
                  </button>
                  <button 
                    v-if="!isDeviceRegistered(device)"
                    class="btn btn-sm btn-success"
                    @click="registerDevice(device)"
                    title="Cadastrar"
                  >
                    <i class="fas fa-plus"></i>
                  </button>
                  <button
                    v-else
                    class="btn btn-sm btn-secondary"
                    disabled
                    title="Já Cadastrado"
                  >
                    <i class="fas fa-check"></i>
                    Cadastrado
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Device Details Modal -->
    <div v-if="selectedDevice" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Detalhes do Dispositivo</h3>
          <button class="modal-close" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <div class="device-details">
            <div class="detail-section">
              <h4>Informações Básicas</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>IP:</label>
                  <span>{{ selectedDevice.ip }}</span>
                </div>
                <div class="detail-item">
                  <label>Hostname:</label>
                  <span>{{ selectedDevice.hostname || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>MAC Address:</label>
                  <span>{{ selectedDevice.macAddress }}</span>
                </div>
                <div class="detail-item">
                  <label>Fabricante:</label>
                  <span>{{ selectedDevice.vendor }}</span>
                </div>
                <div class="detail-item">
                  <label>Tipo:</label>
                  <span>{{ selectedDevice.deviceType }}</span>
                </div>
                <div class="detail-item">
                  <label>Sistema Operacional:</label>
                  <span>{{ selectedDevice.operatingSystem || 'N/A' }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4>Identificação do Sistema</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Serial Number:</label>
                  <span>{{ selectedDevice.systemInfo?.serialNumber || selectedDevice.serialNumber || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>Service Tag:</label>
                  <span>{{ selectedDevice.systemInfo?.serviceTag || selectedDevice.serviceTag || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>Asset Tag:</label>
                  <span>{{ selectedDevice.systemInfo?.assetTag || selectedDevice.assetTag || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>Modelo do Sistema:</label>
                  <span>{{ selectedDevice.systemInfo?.systemModel || selectedDevice.model || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>Fabricante do Sistema:</label>
                  <span>{{ selectedDevice.systemInfo?.systemManufacturer || selectedDevice.vendor || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>Versão da BIOS:</label>
                  <span>{{ selectedDevice.systemInfo?.biosVersion || selectedDevice.biosVersion || 'N/A' }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4>Informações do Usuário</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Usuário Atual:</label>
                  <span>{{ selectedDevice.userInfo?.currentUser || selectedDevice.currentUser || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>Último Usuário Logado:</label>
                  <span>{{ selectedDevice.userInfo?.lastLoggedUser || selectedDevice.lastLoggedUser || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>Domínio:</label>
                  <span>{{ selectedDevice.userInfo?.domain || selectedDevice.domain || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>Perfil do Usuário:</label>
                  <span>{{ selectedDevice.userInfo?.userProfile || selectedDevice.userProfile || 'N/A' }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4>Informações de Hardware</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Processador:</label>
                  <span>{{ selectedDevice.hardwareInfo?.processor || selectedDevice.processor || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>Memória:</label>
                  <span>{{ selectedDevice.hardwareInfo?.memory || selectedDevice.memory || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>Armazenamento:</label>
                  <span>{{ selectedDevice.hardwareInfo?.storage || selectedDevice.storage || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>Placa Gráfica:</label>
                  <span>{{ selectedDevice.hardwareInfo?.graphics || selectedDevice.graphics || 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>Placa-Mãe:</label>
                  <span>{{ selectedDevice.hardwareInfo?.motherboard || selectedDevice.motherboard || 'N/A' }}</span>
                </div>
              </div>
            </div>
            
            <div class="detail-section">
              <h4>Conectividade</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Status:</label>
                  <span class="status-badge" :class="getStatusClass(selectedDevice)">
                    {{ getStatusText(selectedDevice) }}
                  </span>
                </div>
                <div class="detail-item">
                  <label>Tempo de Resposta:</label>
                  <span>{{ selectedDevice.responseTime ? selectedDevice.responseTime + 'ms' : 'N/A' }}</span>
                </div>
                <div class="detail-item">
                  <label>Última Visualização:</label>
                  <span>{{ formatDate(selectedDevice.lastSeen) }}</span>
                </div>
              </div>
            </div>

            <div v-if="selectedDevice.ports && selectedDevice.ports.length > 0" class="detail-section">
              <h4>Portas Abertas</h4>
              <div class="ports-list">
                <span 
                  v-for="port in selectedDevice.ports" 
                  :key="port" 
                  class="port-badge"
                >
                  {{ port }}
                </span>
              </div>
            </div>

            <div v-if="selectedDevice.services && selectedDevice.services.length > 0" class="detail-section">
              <h4>Serviços</h4>
              <div class="services-list">
                <span 
                  v-for="service in selectedDevice.services" 
                  :key="service" 
                  class="service-badge"
                >
                  {{ service }}
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">
            Fechar
          </button>
          <button 
            v-if="!isDeviceRegistered(selectedDevice)"
            class="btn btn-primary"
            @click="registerDevice(selectedDevice)"
          >
            <i class="fas fa-plus"></i>
            Cadastrar Dispositivo
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import logger from '@/utils/logger'
import { NetworkDiscoveryService } from '@/services/networkDiscovery'
import DiscoveryReport from '@/components/reports/DiscoveryReport.vue'

export default {
  name: 'NetworkDiscovery',
  components: {
    DiscoveryReport
  },
  data() {
    return {
      discoveryService: null,
      showReports: false,
      isScanning: false,
      scanProgress: 0,
      devicesFound: 0,
      discoveredDevices: [],
      discoveryResults: null,
      selectedDevice: null,
      filterVendor: '',
      filterType: '',
      scanConfig: {
        networkRange: '192.168.1.0/24',
        timeout: 5000,
        maxConcurrent: 50,
        autoRegister: true,
        updateExisting: false,
        includeOffline: false
      }
    }
  },
  created() {
    this.discoveryService = new NetworkDiscoveryService()
  },
  computed: {
    uniqueVendors() {
      const vendors = [...new Set(this.discoveredDevices.map(d => d.vendor))]
      return vendors.filter(v => v && v !== 'Desconhecido').sort()
    },
    uniqueTypes() {
      const types = [...new Set(this.discoveredDevices.map(d => d.deviceType))]
      return types.filter(t => t).sort()
    },
    filteredDevices() {
      return this.discoveredDevices.filter(device => {
        const vendorMatch = !this.filterVendor || device.vendor === this.filterVendor
        const typeMatch = !this.filterType || device.deviceType === this.filterType
        return vendorMatch && typeMatch
      })
    }
  },
  methods: {
    async startScan() {
      try {
        this.isScanning = true
        this.scanProgress = 0
        this.devicesFound = 0
        this.discoveredDevices = []
        this.discoveryResults = null

        // Inicia o scan
        const progressInterval = setInterval(() => {
          const progress = this.discoveryService.getScanProgress()
          this.scanProgress = progress.progress
          this.devicesFound = progress.devicesFound
          this.discoveredDevices = [...progress.currentResults]

          if (!progress.isScanning) {
            clearInterval(progressInterval)
            this.isScanning = false
          }
        }, 500)

        // Executa descoberta completa
        const results = await this.discoveryService.performFullDiscovery(
          this.scanConfig.networkRange,
          {
            timeout: this.scanConfig.timeout,
            maxConcurrent: this.scanConfig.maxConcurrent,
            includeOffline: this.scanConfig.includeOffline,
            autoRegister: this.scanConfig.autoRegister,
            updateExisting: this.scanConfig.updateExisting
          }
        )

        this.discoveryResults = results

        // Marca dispositivos já cadastrados e anexa informações detalhadas quando disponíveis
        const existingByIp = new Set((results.existingDevices || []).map(d => d.ip))
        const detailsByIp = new Map((results.newDevices || []).map(d => [d.ip, d.detailedInfo]))

        this.discoveredDevices = (results.scanResult.devices || []).map(d => {
          const di = detailsByIp.get(d.ip)
          const isReg = existingByIp.has(d.ip)
          const systemInfo = di ? {
            serialNumber: di.serialNumber,
            serviceTag: di.dellSpecific?.serviceTag,
            systemModel: di.model,
            systemManufacturer: d.vendor
          } : d.systemInfo
          return { ...d, isRegistered: isReg, detailedInfo: di, systemInfo }
        })

        // Feedbacks visuais
        const totalFound = results.scanResult?.devicesFound || this.discoveredDevices.length
        this.$toast.success(`Scan concluído! ${totalFound} dispositivos encontrados.`)
        const already = results.existingDevices?.length || 0
        if (already > 0) {
          this.$toast.info(`${already} equipamentos já cadastrados encontrados na rede`)
        }
        const dellCount = this.discoveredDevices.filter(x => (x.vendor || '').toLowerCase().includes('dell')).length
        if (dellCount > 0) {
          this.$toast.success(`${dellCount} dispositivos Dell identificados`)
        }

      } catch (error) {
        logger.error('Erro durante o scan:', error)
        this.$toast.error('Erro durante o scan da rede: ' + error.message)
      } finally {
        this.isScanning = false
      }
    },

    cancelScan() {
      this.discoveryService.cancelScan()
      this.isScanning = false
      this.$toast.info('Scan cancelado pelo usuário')
    },

    clearResults() {
      this.discoveredDevices = []
      this.discoveryResults = null
      this.scanProgress = 0
      this.devicesFound = 0
      this.selectedDevice = null
    },

    async viewDeviceDetails(device) {
      try {
        if (!device.detailedInfo) {
          const details = await this.discoveryService.getDetailedDeviceInfo(device)
          device.detailedInfo = details
          device.systemInfo = device.systemInfo || {}
          device.systemInfo.serialNumber = device.systemInfo.serialNumber || details.serialNumber
          if (details.dellSpecific?.serviceTag) {
            device.systemInfo.serviceTag = details.dellSpecific.serviceTag
          }
        }
        this.selectedDevice = device
      } catch (e) {
        logger.error('Erro ao carregar detalhes:', e)
        this.$toast.error('Não foi possível carregar detalhes do dispositivo.')
      }
    },

    closeModal() {
      this.selectedDevice = null
    },

    async registerDevice(device) {
      try {
        if (this.isDeviceRegistered(device)) {
          this.$toast.warning('Este dispositivo já está cadastrado.')
          return
        }
        const result = await this.discoveryService.autoRegisterDevice(device)
        if (result.success) {
          this.$toast.success(`Dispositivo ${device.hostname || device.ip} cadastrado com sucesso!`)
          device.isRegistered = true
        }
      } catch (error) {
        logger.error('Erro ao cadastrar dispositivo:', error)
        this.$toast.error('Erro ao cadastrar dispositivo: ' + error.message)
      }
    },

    isDeviceRegistered(device) {
      return device.isRegistered || 
             (this.discoveryResults?.existingDevices?.some(d => d.ip === device.ip))
    },

    getStatusClass(device) {
      if (device.status === 'online') return 'status-online'
      if (device.status === 'offline') return 'status-offline'
      return 'status-unknown'
    },

    getStatusText(device) {
      if (device.status === 'online') return 'Online'
      if (device.status === 'offline') return 'Offline'
      return 'Desconhecido'
    },

    getVendorIcon(vendor) {
      if (vendor.includes('Dell')) return 'fas fa-desktop text-blue'
      if (vendor.includes('HP') || vendor.includes('Hewlett')) return 'fas fa-print text-orange'
      if (vendor.includes('Apple')) return 'fab fa-apple text-gray'
      if (vendor.includes('Microsoft')) return 'fab fa-microsoft text-blue'
      if (vendor.includes('VMware')) return 'fas fa-cloud text-purple'
      return 'fas fa-microchip text-gray'
    },

    formatDate(dateString) {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleString('pt-BR')
    },

    exportResults() {
      if (this.discoveredDevices.length === 0) {
        this.$toast.warning('Nenhum dispositivo para exportar')
        return
      }

      const csvContent = this.generateCSV()
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `descoberta_rede_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    },

    generateCSV() {
      const headers = ['IP', 'Hostname', 'Fabricante', 'Tipo', 'MAC Address', 'Sistema Operacional', 'Status', 'Tempo Resposta']
      const rows = this.discoveredDevices.map(device => [
        device.ip,
        device.hostname || '',
        device.vendor,
        device.deviceType,
        device.macAddress,
        device.operatingSystem || '',
        device.status,
        device.responseTime || ''
      ])

      return [headers, ...rows]
        .map(row => row.map(field => `"${field}"`).join(','))
        .join('\n')
    }
  }
}
</script>

<style scoped>
.network-discovery {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* Reports Section */
.reports-section {
  margin-bottom: 24px;
}

/* Header */
.page-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-subtitle {
  color: #666;
  margin: 0;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Configuration Panel */
.config-panel {
  background: white;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.panel-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
}

.panel-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-content {
  padding: 24px;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.config-item label {
  display: block;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.config-item input[type="text"],
.config-item input[type="number"] {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.config-item input[type="text"]:focus,
.config-item input[type="number"]:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin-top: 20px;
}

.checkbox-label input[type="checkbox"] {
  margin: 0;
}

/* Progress Panel */
.progress-panel {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.progress-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #1d4ed8);
  transition: width 0.3s ease;
}

.progress-info {
  text-align: center;
  color: #666;
  font-size: 14px;
}

/* Results Summary */
.results-summary {
  margin-bottom: 24px;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card-icon {
  font-size: 24px;
}

.card-content h4 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
}

.card-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

/* Devices Table */
.devices-table-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.table-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-group {
  display: flex;
  gap: 8px;
}

.filter-select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.table-container {
  overflow-x: auto;
}

.devices-table {
  width: 100%;
  border-collapse: collapse;
}

.devices-table th,
.devices-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.devices-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.devices-table td {
  font-size: 14px;
  color: #1a1a1a;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-online {
  background: #dcfce7;
  color: #166534;
}

.status-offline {
  background: #fee2e2;
  color: #dc2626;
}

.status-unknown {
  background: #f3f4f6;
  color: #6b7280;
}

.vendor-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-buttons {
  display: flex;
  gap: 4px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.modal-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
}

.modal-body {
  padding: 24px;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  font-weight: 500;
  color: #6b7280;
  font-size: 14px;
}

.detail-item span {
  color: #1a1a1a;
  font-size: 14px;
}

.ports-list,
.services-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.port-badge,
.service-badge {
  padding: 4px 8px;
  background: #f3f4f6;
  border-radius: 6px;
  font-size: 12px;
  color: #374151;
}

.modal-footer {
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Utility Classes */
.text-blue { color: #3b82f6; }
.text-green { color: #10b981; }
.text-orange { color: #f59e0b; }
.text-red { color: #ef4444; }
.text-purple { color: #8b5cf6; }
.text-gray { color: #6b7280; }

/* Buttons */
.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  text-decoration: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-outline {
  background: transparent;
  color: #3b82f6;
  border: 1px solid #3b82f6;
}

.btn-outline:hover {
  background: #3b82f6;
  color: white;
}

.btn-outline.active {
  background: #3b82f6;
  color: white;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
}

.btn-success {
  background: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #059669;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #dc2626;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

/* Responsive */
@media (max-width: 768px) {
  .network-discovery {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .config-grid {
    grid-template-columns: 1fr;
  }
  
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .table-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    flex-direction: column;
  }
}
</style>