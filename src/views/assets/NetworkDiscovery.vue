<template>
  <div class="network-discovery">
    <!-- Cabeçalho -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">
            <i class="fas fa-network-wired"></i>
            Descoberta de Rede
          </h1>
          <p class="page-description">
            Detecte e cadastre dispositivos na sua rede automaticamente
          </p>
        </div>
        <div class="header-actions">
          <button 
            @click="startNetworkScan" 
            :disabled="isScanning"
            class="btn btn-primary"
          >
            <i class="fas fa-search" v-if="!isScanning"></i>
            <i class="fas fa-spinner fa-spin" v-else></i>
            {{ scanButtonText }}
          </button>
          <button 
            @click="startUbiquitiScan" 
            :disabled="isUbiquitiScanning"
            class="btn btn-secondary"
          >
            <i class="fas fa-wifi" v-if="!isUbiquitiScanning"></i>
            <i class="fas fa-spinner fa-spin" v-else></i>
            {{ ubiquitiButtonText }}
          </button>
          <button 
            @click="showUbiquitiConfig = true" 
            class="btn btn-outline"
          >
            <i class="fas fa-cog"></i>
            Config Ubiquiti
          </button>
          <button 
            @click="clearResults" 
            class="btn btn-secondary"
            :disabled="networkStore.discoveredDevices.length === 0"
          >
            <i class="fas fa-trash"></i>
            Limpar
          </button>
        </div>
      </div>
    </div>

    <!-- Estatísticas -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-network-wired"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ networkStats.totalDevices }}</div>
          <div class="stat-label">Total Descobertos</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon registered">
          <i class="fas fa-check-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ networkStore.totalRegistered }}</div>
          <div class="stat-label">Já Cadastrados</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon unregistered">
          <i class="fas fa-plus-circle"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ networkStore.unregisteredDevices.length }}</div>
          <div class="stat-label">Não Cadastrados</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-clock"></i>
        </div>
        <div class="stat-content">
          <div class="stat-number">{{ networkStats.lastScan ? formatDate(networkStats.lastScan) : 'Nunca' }}</div>
          <div class="stat-label">Último Scan</div>
        </div>
      </div>
    </div>

    <!-- Mensagens -->
    <div v-if="successMessage" class="alert alert-success">
      <i class="fas fa-check-circle"></i>
      {{ successMessage }}
    </div>
    
    <div v-if="errorMessage" class="alert alert-error">
      <i class="fas fa-exclamation-triangle"></i>
      {{ errorMessage }}
    </div>

    <!-- Status do Scan -->
    <div v-if="isScanning" class="scan-status">
      <div class="scan-progress">
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: scanProgress + '%' }"></div>
        </div>
        <p class="scan-text">
          <i class="fas fa-spinner fa-spin"></i>
          Escaneando rede local... {{ scanProgress }}%
        </p>
      </div>
    </div>

    <!-- Filtros -->
    <div v-if="networkStore.discoveredDevices.length > 0" class="filters-section">
      <div class="filters-grid">
        <div class="filter-group">
          <label class="filter-label">Buscar:</label>
          <input 
            v-model="filters.search"
            type="text" 
            placeholder="IP, MAC, hostname, fabricante..."
            class="filter-input"
          >
        </div>
        <div class="filter-group">
          <label class="filter-label">Tipo:</label>
          <select v-model="filters.deviceType" class="filter-select">
            <option value="">Todos os tipos</option>
            <option v-for="type in deviceTypes" :key="type" :value="type">
              {{ type }}
            </option>
          </select>
        </div>
        <div class="filter-group">
          <label class="filter-label">Status:</label>
          <select v-model="filters.registrationStatus" class="filter-select">
            <option value="all">Todos</option>
            <option value="registered">Já cadastrados</option>
            <option value="unregistered">Não cadastrados</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Lista de Dispositivos -->
    <div v-if="filteredDevices.length > 0" class="devices-section">
      <div class="section-header">
        <h2 class="section-title">
          <i class="fas fa-list"></i>
          Dispositivos Encontrados ({{ filteredDevices.length }})
        </h2>
      </div>

      <div class="devices-grid">
        <div 
          v-for="device in filteredDevices" 
          :key="device.id"
          class="device-card"
          :class="{ 'registered': isDeviceRegistered(device) }"
        >
          <div class="device-header">
            <div class="device-icon">
              <i :class="getDeviceIcon(device.deviceType)"></i>
            </div>
            <div class="device-info">
              <h3 class="device-name">{{ device.hostname }}</h3>
              <p class="device-type">{{ device.manufacturer }} {{ device.model }}</p>
            </div>
            <div class="device-status">
              <span 
                class="status-badge" 
                :class="getDeviceStatusClass(device)"
              >
                <i class="fas fa-circle"></i>
                {{ getDeviceStatusText(device) }}
              </span>
            </div>
          </div>

          <div class="device-details">
            <div class="detail-row">
              <span class="detail-label">IP:</span>
              <span class="detail-value">{{ device.ip }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">MAC:</span>
              <span class="detail-value">{{ device.mac }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">Fabricante:</span>
              <span class="detail-value">{{ device.manufacturer }}</span>
            </div>
            <div class="detail-row" v-if="device.serviceTag">
              <span class="detail-label">Service Tag:</span>
              <span class="detail-value">{{ device.serviceTag }}</span>
            </div>
            <div class="detail-row" v-if="device.os">
              <span class="detail-label">SO:</span>
              <span class="detail-value">{{ device.os }}</span>
            </div>
            <div class="detail-row" v-if="device.source">
              <span class="detail-label">Fonte:</span>
              <span class="detail-value">{{ device.source }}</span>
            </div>
          </div>

          <!-- Aviso se já cadastrado -->
          <div v-if="isDeviceRegistered(device)" class="device-warning">
            <i class="fas fa-info-circle"></i>
            <span>Este dispositivo já está cadastrado no sistema</span>
          </div>

          <div class="device-actions">
            <button 
              @click="fetchDeviceDetails(device)"
              class="btn btn-outline btn-sm"
            >
              <i class="fas fa-info-circle"></i>
              Detalhes
            </button>
            <button 
              v-if="!isDeviceRegistered(device)"
              @click="openRegistrationModal(device)"
              class="btn btn-primary btn-sm"
            >
              <i class="fas fa-question-circle"></i>
              Verificar/Cadastrar
            </button>
            <button 
              v-else
              @click="fetchDeviceDetails(getRegisteredDevice(device))"
              class="btn btn-success btn-sm"
              disabled
            >
              <i class="fas fa-check"></i>
              Cadastrado
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Estado Vazio -->
    <div v-else-if="!isScanning && !isUbiquitiScanning && networkStore.discoveredDevices.length === 0" class="empty-state">
      <div class="empty-icon">
        <i class="fas fa-network-wired"></i>
      </div>
      <h3 class="empty-title">Nenhum dispositivo encontrado</h3>
      <p class="empty-description">
        Clique em "Escanear Rede Local" ou "Escanear Ubiquiti" para descobrir dispositivos conectados à sua rede
      </p>
      <div class="empty-actions">
        <button 
          @click="startNetworkScan"
          class="btn btn-primary"
        >
          <i class="fas fa-search"></i>
          Scan Local
        </button>
        <button 
          @click="startUbiquitiScan"
          class="btn btn-secondary"
        >
          <i class="fas fa-wifi"></i>
          Scan Ubiquiti
        </button>
      </div>
    </div>

    <!-- Estado de filtros sem resultados -->
    <div v-else-if="filteredDevices.length === 0 && networkStore.discoveredDevices.length > 0" class="empty-state">
      <div class="empty-icon">
        <i class="fas fa-filter"></i>
      </div>
      <h3 class="empty-title">Nenhum dispositivo encontrado</h3>
      <p class="empty-description">
        Nenhum dispositivo corresponde aos filtros aplicados
      </p>
      <button 
        @click="filters.search = ''; filters.deviceType = ''; filters.registrationStatus = 'all'"
        class="btn btn-outline"
      >
        <i class="fas fa-times"></i>
        Limpar Filtros
      </button>
    </div>

    <!-- Device Details Modal -->
    <div v-if="selectedDevice" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Detalhes do Dispositivo</h2>
          <button class="close-btn" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <div class="device-details-full">
            <div class="detail-section">
              <h3>Informações Básicas</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Hostname:</label>
                  <span>{{ selectedDevice.hostname }}</span>
                </div>
                <div class="detail-item">
                  <label>Modelo:</label>
                  <span>{{ selectedDevice.model }}</span>
                </div>
                <div class="detail-item">
                  <label>Service Tag:</label>
                  <span>{{ selectedDevice.serviceTag }}</span>
                </div>
                <div class="detail-item">
                  <label>IP:</label>
                  <span>{{ selectedDevice.ip }}</span>
                </div>
              </div>
            </div>

            <div v-if="selectedDevice.specifications" class="detail-section">
              <h3>Especificações</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Processador:</label>
                  <span>{{ selectedDevice.specifications.cpu }}</span>
                </div>
                <div class="detail-item">
                  <label>Memória:</label>
                  <span>{{ selectedDevice.specifications.ram }}</span>
                </div>
                <div class="detail-item">
                  <label>Armazenamento:</label>
                  <span>{{ selectedDevice.specifications.storage }}</span>
                </div>
                <div class="detail-item">
                  <label>Rede:</label>
                  <span>{{ selectedDevice.specifications.network }}</span>
                </div>
              </div>
            </div>

            <div v-if="selectedDevice.warranty" class="detail-section">
              <h3>Garantia</h3>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>Status:</label>
                  <span class="warranty-status" :class="selectedDevice.warranty.status.toLowerCase()">
                    {{ selectedDevice.warranty.status }}
                  </span>
                </div>
                <div class="detail-item">
                  <label>Tipo:</label>
                  <span>{{ selectedDevice.warranty.type }}</span>
                </div>
                <div class="detail-item">
                  <label>Início:</label>
                  <span>{{ formatDate(selectedDevice.warranty.startDate) }}</span>
                </div>
                <div class="detail-item">
                  <label>Fim:</label>
                  <span>{{ formatDate(selectedDevice.warranty.endDate) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">
            Fechar
          </button>
          <button class="btn btn-primary" @click="registerAsset(selectedDevice)">
            <i class="fas fa-plus"></i>
            Cadastrar como Ativo
          </button>
        </div>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="successMessage" class="success-message">
      <i class="fas fa-check-circle"></i>
      {{ successMessage }}
    </div>

    <!-- Error Message -->
    <div v-if="errorMessage" class="error-message">
      <i class="fas fa-exclamation-triangle"></i>
      {{ errorMessage }}
    </div>

      <!-- Modal de Configuração Ubiquiti -->
      <div v-if="showUbiquitiConfig" class="modal-overlay" @click="showUbiquitiConfig = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              <i class="fas fa-wifi"></i>
              Configuração Ubiquiti UniFi
            </h3>
            <button @click="showUbiquitiConfig = false" class="modal-close">
              <i class="fas fa-times"></i>
            </button>
          </div>

          <div class="modal-body">
            <form @submit.prevent="saveUbiquitiConfig">
              <div class="form-group">
                <label class="form-label">
                  <i class="fas fa-toggle-on"></i>
                  Habilitar Integração Ubiquiti
                </label>
                <div class="form-control">
                  <label class="switch">
                    <input 
                      type="checkbox" 
                      v-model="ubiquitiConfig.enabled"
                    >
                    <span class="slider"></span>
                  </label>
                </div>
              </div>

              <div v-if="ubiquitiConfig.enabled">
                <div class="form-group">
                  <label class="form-label">
                    <i class="fas fa-server"></i>
                    URL do Controller
                  </label>
                  <input 
                    type="url" 
                    v-model="ubiquitiConfig.baseUrl"
                    placeholder="https://192.168.1.1:8443"
                    class="form-input"
                    required
                  >
                  <small class="form-help">
                    URL completa do UniFi Controller (incluindo porta)
                  </small>
                </div>

                <div class="form-group">
                  <label class="form-label">
                    <i class="fas fa-user"></i>
                    Usuário
                  </label>
                  <input 
                    type="text" 
                    v-model="ubiquitiConfig.username"
                    placeholder="admin"
                    class="form-input"
                    required
                  >
                </div>

                <div class="form-group">
                  <label class="form-label">
                    <i class="fas fa-lock"></i>
                    Senha
                  </label>
                  <input 
                    type="password" 
                    v-model="ubiquitiConfig.password"
                    placeholder="••••••••"
                    class="form-input"
                    required
                  >
                </div>

                <div class="form-group">
                  <label class="form-label">
                    <i class="fas fa-sitemap"></i>
                    Site
                  </label>
                  <input 
                    type="text" 
                    v-model="ubiquitiConfig.site"
                    placeholder="default"
                    class="form-input"
                  >
                  <small class="form-help">
                    Nome do site no UniFi Controller (geralmente "default")
                  </small>
                </div>

                <div class="form-actions">
                  <button 
                    type="button"
                    @click="testUbiquitiConnection"
                    class="btn btn-outline"
                  >
                    <i class="fas fa-plug"></i>
                    Testar Conexão
                  </button>
                </div>
              </div>

              <div class="modal-footer">
                <button 
                  type="button"
                  @click="showUbiquitiConfig = false"
                  class="btn btn-secondary"
                >
                  Cancelar
                </button>
                <button 
                  type="submit"
                  class="btn btn-primary"
                >
                  <i class="fas fa-save"></i>
                  Salvar Configuração
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Modal de Confirmação de Cadastro -->
      <div v-if="showRegistrationModal" class="modal-overlay" @click="closeRegistrationModal">
        <div class="modal-content registration-modal" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">
              <i class="fas fa-question-circle"></i>
              Confirmar Cadastro de Dispositivo
            </h3>
            <button @click="closeRegistrationModal" class="modal-close">
              <i class="fas fa-times"></i>
            </button>
          </div>

          <div class="modal-body">
            <div v-if="deviceToRegister" class="device-registration-info">
              <!-- Status de Cadastro -->
              <div class="registration-status">
                <div v-if="deviceToRegister.isAlreadyRegistered" class="status-card already-registered">
                  <div class="status-icon">
                    <i class="fas fa-check-circle"></i>
                  </div>
                  <div class="status-content">
                    <h4>Dispositivo Já Cadastrado</h4>
                    <p>Este dispositivo já está registrado no sistema.</p>
                    <div class="existing-info">
                      <span><strong>ID:</strong> {{ deviceToRegister.existingAsset?.id }}</span>
                      <span><strong>Cadastrado em:</strong> {{ formatDate(deviceToRegister.existingAsset?.registrationDate) }}</span>
                    </div>
                  </div>
                </div>
                
                <div v-else class="status-card new-device">
                  <div class="status-icon">
                    <i class="fas fa-plus-circle"></i>
                  </div>
                  <div class="status-content">
                    <h4>Novo Dispositivo Encontrado</h4>
                    <p>Deseja cadastrar este dispositivo no sistema?</p>
                  </div>
                </div>
              </div>

              <!-- Informações Básicas -->
              <div class="device-basic-info">
                <h5><i class="fas fa-info-circle"></i> Informações Básicas</h5>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="label">IP:</span>
                    <span class="value">{{ deviceToRegister.ip }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">MAC:</span>
                    <span class="value">{{ deviceToRegister.macAddress }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Fabricante:</span>
                    <span class="value">{{ deviceToRegister.vendor }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Tipo:</span>
                    <span class="value">{{ deviceToRegister.deviceType }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Hostname:</span>
                    <span class="value">{{ deviceToRegister.hostname || 'N/A' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">SO:</span>
                    <span class="value">{{ deviceToRegister.operatingSystem || 'N/A' }}</span>
                  </div>
                </div>
              </div>

              <!-- Informações Detalhadas -->
              <div v-if="deviceToRegister.detailedInfo" class="device-detailed-info">
                <h5><i class="fas fa-cogs"></i> Informações Detalhadas</h5>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="label">Número de Série:</span>
                    <span class="value">{{ deviceToRegister.detailedInfo.serialNumber }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Modelo:</span>
                    <span class="value">{{ deviceToRegister.detailedInfo.model }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Valor Estimado:</span>
                    <span class="value">{{ formatCurrency(deviceToRegister.detailedInfo.estimatedValue) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="label">Categoria:</span>
                    <span class="value">{{ deviceToRegister.detailedInfo.category }}</span>
                  </div>
                </div>

                <!-- Especificações Técnicas -->
                <div v-if="deviceToRegister.detailedInfo.specifications" class="specifications">
                  <h6><i class="fas fa-microchip"></i> Especificações</h6>
                  <div class="spec-grid">
                    <div class="spec-item">
                      <span class="label">CPU:</span>
                      <span class="value">{{ deviceToRegister.detailedInfo.specifications.cpu }}</span>
                    </div>
                    <div class="spec-item">
                      <span class="label">RAM:</span>
                      <span class="value">{{ deviceToRegister.detailedInfo.specifications.ram }}</span>
                    </div>
                    <div class="spec-item">
                      <span class="label">Storage:</span>
                      <span class="value">{{ deviceToRegister.detailedInfo.specifications.storage }}</span>
                    </div>
                  </div>
                </div>

                <!-- Informações Específicas da Dell -->
                <div v-if="deviceToRegister.detailedInfo.dellSpecific" class="dell-specific">
                  <h6><i class="fab fa-dell"></i> Informações Dell</h6>
                  <div class="dell-grid">
                    <div class="dell-item">
                      <span class="label">Service Tag:</span>
                      <span class="value">{{ deviceToRegister.detailedInfo.dellSpecific.serviceTag }}</span>
                    </div>
                    <div class="dell-item">
                      <span class="label">Express Service Code:</span>
                      <span class="value">{{ deviceToRegister.detailedInfo.dellSpecific.expressServiceCode }}</span>
                    </div>
                    <div class="dell-item">
                      <span class="label">Status da Garantia:</span>
                      <span class="value warranty-active">{{ deviceToRegister.detailedInfo.dellSpecific.warrantyStatus }}</span>
                    </div>
                    <div class="dell-item">
                      <span class="label">Suporte:</span>
                      <span class="value">{{ deviceToRegister.detailedInfo.dellSpecific.supportLevel }}</span>
                    </div>
                  </div>
                </div>

                <!-- Informações de Garantia -->
                <div v-if="deviceToRegister.detailedInfo.warranty" class="warranty-info">
                  <h6><i class="fas fa-shield-alt"></i> Garantia</h6>
                  <div class="warranty-grid">
                    <div class="warranty-item">
                      <span class="label">Período:</span>
                      <span class="value">{{ deviceToRegister.detailedInfo.warranty.period }}</span>
                    </div>
                    <div class="warranty-item">
                      <span class="label">Tipo:</span>
                      <span class="value">{{ deviceToRegister.detailedInfo.warranty.type }}</span>
                    </div>
                    <div v-if="deviceToRegister.detailedInfo.warranty.expires" class="warranty-item">
                      <span class="label">Expira em:</span>
                      <span class="value">{{ formatDate(deviceToRegister.detailedInfo.warranty.expires) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer">
            <button 
              type="button"
              @click="closeRegistrationModal"
              class="btn btn-secondary"
            >
              <i class="fas fa-times"></i>
              Cancelar
            </button>
            
            <button 
              v-if="!deviceToRegister?.isAlreadyRegistered"
              type="button"
              @click="confirmDeviceRegistration"
              class="btn btn-primary"
              :disabled="isRegistering"
            >
              <i class="fas fa-spinner fa-spin" v-if="isRegistering"></i>
              <i class="fas fa-plus" v-else></i>
              {{ isRegistering ? 'Cadastrando...' : 'Cadastrar Dispositivo' }}
            </button>

            <button 
              v-else
              type="button"
              @click="viewExistingAsset"
              class="btn btn-info"
            >
              <i class="fas fa-eye"></i>
              Ver Ativo Existente
            </button>
          </div>
        </div>
      </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import logger from '@/utils/logger'
import { useAssetsStore } from '@/stores/assets'
import { useNetworkDevicesStore } from '@/stores/networkDevices'
import ubiquitiService from '@/services/ubiquitiService'
import { format } from 'date-fns'
import { ptBR } from 'date-fns/locale'

const assetsStore = useAssetsStore()
const networkStore = useNetworkDevicesStore()

// Estado reativo
const isScanning = ref(false)
const isUbiquitiScanning = ref(false)
const selectedDevice = ref(null)
const scanStatus = ref(null)
const loadingDetails = reactive({})
const registering = reactive({})
const successMessage = ref('')
const errorMessage = ref('')
const showUbiquitiConfig = ref(false)
const activeTab = ref('discovered')

// Modal de confirmação de cadastro
const showRegistrationModal = ref(false)
const deviceToRegister = ref(null)
const isRegistering = ref(false)

// Configuração Ubiquiti
const ubiquitiConfig = ref({
  baseUrl: 'https://192.168.1.1:8443',
  username: '',
  password: '',
  site: 'default',
  enabled: false
})

// Filtros
const filters = ref({
  search: '',
  deviceType: '',
  registrationStatus: 'all' // all, registered, unregistered
})

// Computed
const discoveredDevices = computed(() => {
  let devices = networkStore.discoveredDevices

  // Filtro por busca
  if (filters.value.search) {
    devices = networkStore.searchDevices(filters.value.search)
  }

  // Filtro por tipo
  if (filters.value.deviceType) {
    devices = devices.filter(device => device.deviceType === filters.value.deviceType)
  }

  // Filtro por status de registro
  if (filters.value.registrationStatus === 'registered') {
    devices = devices.filter(device => networkStore.isDeviceRegistered(device))
  } else if (filters.value.registrationStatus === 'unregistered') {
    devices = devices.filter(device => !networkStore.isDeviceRegistered(device))
  }

  return devices
})

const deviceTypes = computed(() => {
  const types = [...new Set(networkStore.discoveredDevices.map(d => d.deviceType))]
  return types.filter(Boolean).sort()
})

const networkStats = computed(() => networkStore.getNetworkStats)

// Inicia scan da rede
const startNetworkScan = async () => {
  try {
    isScanning.value = true
    errorMessage.value = ''
    
    const devices = await networkDiscovery.scanNetwork()
    discoveredDevices.value = devices
    scanStatus.value = networkDiscovery.getScanStatus()
    
    // Destaca o PC Dell específico se encontrado
    const dellPC = devices.find(d => d.serviceTag === 'GPSM954')
    if (dellPC) {
      successMessage.value = `PC Dell OptiPlex encontrado! Service Tag: ${dellPC.serviceTag}`
      setTimeout(() => successMessage.value = '', 5000)
    }
    
  } catch (error) {
    errorMessage.value = 'Erro ao escanear a rede: ' + error.message
    setTimeout(() => errorMessage.value = '', 5000)
  } finally {
    isScanning.value = false
  }
}

// Busca detalhes de um dispositivo
const getDeviceDetails = async (device) => {
  try {
    loadingDetails[device.ip] = true
    const details = await networkDiscovery.getDeviceDetails(device.ip)
    selectedDevice.value = details
  } catch (error) {
    errorMessage.value = 'Erro ao buscar detalhes: ' + error.message
    setTimeout(() => errorMessage.value = '', 5000)
  } finally {
    loadingDetails[device.ip] = false
  }
}

// Cadastra dispositivo como ativo
const registerAsset = async (device) => {
  try {
    registering[device.ip] = true
    
    // Busca detalhes completos se necessário
    let fullDevice = device
    if (!device.specifications) {
      fullDevice = await networkDiscovery.getDeviceDetails(device.ip)
    }
    
    // Cria objeto do ativo
    const newAsset = {
      id: Date.now().toString(),
      name: fullDevice.hostname,
      code: fullDevice.serviceTag || `AUTO-${Date.now()}`,
      category: getAssetCategory(fullDevice.deviceType),
      status: 'Ativo',
      location: 'Descoberto via Rede',
      responsible: 'Sistema Automático',
      value: getEstimatedValue(fullDevice),
      purchaseDate: fullDevice.purchaseInfo?.purchaseDate || new Date().toISOString().split('T')[0],
      description: `${fullDevice.manufacturer} ${fullDevice.model}`,
      specifications: {
        manufacturer: fullDevice.manufacturer,
        model: fullDevice.model,
        serviceTag: fullDevice.serviceTag,
        ip: fullDevice.ip,
        mac: fullDevice.mac,
        os: fullDevice.os,
        processor: fullDevice.specifications?.cpu || fullDevice.processor,
        memory: fullDevice.specifications?.ram || fullDevice.memory,
        storage: fullDevice.specifications?.storage || fullDevice.storage,
        network: fullDevice.specifications?.network,
        warranty: fullDevice.warranty
      },
      networkInfo: {
        ip: fullDevice.ip,
        mac: fullDevice.mac,
        hostname: fullDevice.hostname,
        lastSeen: fullDevice.lastSeen,
        discoveryDate: new Date().toISOString()
      }
    }
    
    // Adiciona ao store
    await assetsStore.addAsset(newAsset)
    
    successMessage.value = `Ativo ${fullDevice.hostname} cadastrado com sucesso!`
    setTimeout(() => successMessage.value = '', 5000)
    
    // Fecha modal se estiver aberto
    if (selectedDevice.value?.ip === device.ip) {
      closeModal()
    }
    
  } catch (error) {
    errorMessage.value = 'Erro ao cadastrar ativo: ' + error.message
    setTimeout(() => errorMessage.value = '', 5000)
  } finally {
    registering[device.ip] = false
  }
}

// Utilitários
const getDeviceIcon = (deviceType) => {
  const icons = {
    'Computer': 'fas fa-desktop',
    'Laptop': 'fas fa-laptop',
    'Printer': 'fas fa-print',
    'Server': 'fas fa-server',
    'Switch': 'fas fa-network-wired',
    'Router': 'fas fa-wifi'
  }
  return icons[deviceType] || 'fas fa-question-circle'
}

const getAssetCategory = (deviceType) => {
  const categories = {
    'Computer': 'Computadores',
    'Laptop': 'Notebooks',
    'Printer': 'Impressoras',
    'Server': 'Servidores',
    'Switch': 'Equipamentos de Rede',
    'Router': 'Equipamentos de Rede'
  }
  return categories[deviceType] || 'Outros'
}

const getEstimatedValue = (device) => {
  // Valores estimados baseados no tipo e modelo
  if (device.model?.includes('OptiPlex')) return 3850.00
  if (device.model?.includes('Latitude')) return 5200.00
  if (device.model?.includes('LaserJet')) return 1200.00
  return 1000.00
}

const clearResults = () => {
  discoveredDevices.value = []
  scanStatus.value = null
  networkDiscovery.clearCache()
}

const closeModal = () => {
  selectedDevice.value = null
}

const formatDateTime = (dateString) => {
  return format(new Date(dateString), 'dd/MM/yyyy HH:mm', { locale: ptBR })
}

const formatDate = (dateString) => {
  return format(new Date(dateString), 'dd/MM/yyyy', { locale: ptBR })
}

const formatCurrency = (value) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value)
}

// Métodos do modal de confirmação de cadastro
const openRegistrationModal = async (device) => {
  try {
    deviceToRegister.value = { ...device }
    
    // Verifica se o dispositivo já está cadastrado usando o store
    const isRegistered = networkStore.isDeviceRegistered(device)
    const existingDevice = networkStore.findRegisteredDevice(device)
    
    deviceToRegister.value.isAlreadyRegistered = isRegistered
    deviceToRegister.value.existingAsset = existingDevice ? {
      id: existingDevice.assetId || existingDevice.id,
      name: existingDevice.name || `${device.vendor} ${device.deviceType}`,
      serialNumber: existingDevice.serviceTag || device.serviceTag,
      registrationDate: existingDevice.registeredAt,
      lastUpdate: new Date().toISOString(),
      status: 'ativo',
      ipAddress: existingDevice.ip,
      macAddress: existingDevice.mac
    } : null
    
    // Obtém informações detalhadas do dispositivo
    const detailedInfo = await networkDiscovery.getDetailedDeviceInfo(device)
    deviceToRegister.value.detailedInfo = detailedInfo
    
    showRegistrationModal.value = true
  } catch (error) {
    logger.error('Erro ao verificar status de cadastro', { error })
    errorMessage.value = 'Erro ao verificar status do dispositivo'
  }
}

const closeRegistrationModal = () => {
  showRegistrationModal.value = false
  deviceToRegister.value = null
  isRegistering.value = false
}

const confirmDeviceRegistration = async () => {
  if (!deviceToRegister.value) return
  
  try {
    isRegistering.value = true
    
    // Cria um novo ativo baseado nas informações do dispositivo
    const newAsset = {
      name: `${deviceToRegister.value.vendor || 'Dispositivo'} ${deviceToRegister.value.deviceType || 'Desconhecido'}`,
      category: deviceToRegister.value.deviceType || 'Network Device',
      manufacturer: deviceToRegister.value.vendor,
      model: deviceToRegister.value.model,
      serialNumber: deviceToRegister.value.serviceTag || deviceToRegister.value.detailedInfo?.serialNumber,
      location: 'Rede Local',
      status: 'Ativo',
      acquisitionDate: new Date().toISOString().split('T')[0],
      value: deviceToRegister.value.detailedInfo?.estimatedValue || 0,
      networkInfo: {
        ip: deviceToRegister.value.ip,
        mac: deviceToRegister.value.mac,
        hostname: deviceToRegister.value.hostname,
        registeredAt: new Date().toISOString()
      },
      specifications: {
        manufacturer: deviceToRegister.value.vendor,
        model: deviceToRegister.value.model,
        serviceTag: deviceToRegister.value.serviceTag,
        ...deviceToRegister.value.detailedInfo?.specifications
      }
    }
    
    // Adiciona o ativo usando o store de assets
    const createdAsset = await assetsStore.addAsset(newAsset)
    
    // Registra o dispositivo no store de rede
    networkStore.registerDevice(deviceToRegister.value, createdAsset)
    
    successMessage.value = `Dispositivo ${deviceToRegister.value.ip} cadastrado com sucesso!`
    
    closeRegistrationModal()
    
    // Limpa mensagem após 5 segundos
    setTimeout(() => {
      successMessage.value = ''
    }, 5000)
  } catch (error) {
    logger.error('Erro ao cadastrar dispositivo', { error })
    errorMessage.value = 'Erro ao cadastrar dispositivo'
  } finally {
    isRegistering.value = false
  }
}

const viewExistingAsset = () => {
  if (deviceToRegister.value?.existingAsset) {
    // Redireciona para a página de detalhes do ativo
    // Aqui você pode implementar a navegação para a página de assets
    logger.userAction('visualizar_ativo', { asset: deviceToRegister.value.existingAsset })
    closeRegistrationModal()
  }
}

// Auto-start scan quando componente é montado
onMounted(() => {
  // Adiciona alguns dispositivos de exemplo ao store para demonstração
  const exampleRegisteredDevices = [
    {
      id: 1,
      name: 'Dell OptiPlex 7090',
      ip: '192.168.1.100',
      mac: '00:1A:2B:3C:4D:5E',
      hostname: 'DESKTOP-001',
      serviceTag: 'ABCD123',
      manufacturer: 'Dell',
      model: 'OptiPlex 7090',
      registeredAt: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
      assetId: 1001
    },
    {
      id: 2,
      name: 'HP ProBook 450',
      ip: '192.168.1.150',
      mac: '00:2B:3C:4D:5E:6F',
      hostname: 'LAPTOP-002',
      serviceTag: 'EFGH456',
      manufacturer: 'HP',
      model: 'ProBook 450',
      registeredAt: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      assetId: 1002
    }
  ]
  
  // Adiciona os dispositivos registrados ao store
  exampleRegisteredDevices.forEach(device => {
    networkStore.registeredDevices.push(device)
  })
  
  // Inicia scan automaticamente para demonstração
  setTimeout(() => {
    startNetworkScan()
  }, 1000)
})
</script>

<style scoped>
.network-discovery {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.header-info {
  flex: 1;
}

.page-title {
  font-size: 2rem;
  font-weight: 700;
  color: #111827;
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-description {
  color: #6b7280;
  margin: 0;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Estatísticas */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.stat-icon.registered {
  background: linear-gradient(135deg, #10b981, #059669);
}

.stat-icon.unregistered {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 0.875rem;
  color: #6b7280;
  font-weight: 500;
}

/* Filtros */
.filters-section {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
}

.filter-input,
.filter-select {
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.filter-input:focus,
.filter-select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Botões */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background: #e5e7eb;
  border-color: #9ca3af;
}

.btn-outline {
  background: transparent;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.btn-sm {
  padding: 8px 12px;
  font-size: 0.875rem;
}

/* Alertas */
.alert {
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.alert-success {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.alert-error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

/* Status do Scan */
.scan-status {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border: 1px solid #0ea5e9;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 32px;
}

.scan-progress {
  text-align: center;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e0f2fe;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 16px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #0ea5e9, #0284c7);
  transition: width 0.3s ease;
}

.scan-text {
  color: #0369a1;
  font-weight: 500;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

/* Seção de dispositivos */
.devices-section {
  margin-bottom: 32px;
}

.section-header {
  margin-bottom: 24px;
}

.section-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}

.devices-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
}

.device-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
  position: relative;
}

.device-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border-color: #3b82f6;
}

.device-card.registered {
  border-left: 4px solid #10b981;
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
}

.device-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.device-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.25rem;
  flex-shrink: 0;
}

.device-info {
  flex: 1;
}

.device-name {
  margin: 0 0 4px 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
}

.device-type {
  color: #6b7280;
  margin: 0;
  font-size: 0.875rem;
}

.device-status {
  display: flex;
  align-items: center;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-badge.online {
  background: #dcfce7;
  color: #166534;
}

.status-badge.offline {
  background: #fee2e2;
  color: #991b1b;
}

.status-badge.registered {
  background: #dcfce7;
  color: #166534;
}

.device-details {
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.detail-value {
  color: #111827;
  font-size: 0.875rem;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.device-warning {
  background: #fef3c7;
  border: 1px solid #f59e0b;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: #92400e;
}

.device-actions {
  display: flex;
  gap: 12px;
}

/* Estado vazio */
.empty-state {
  text-align: center;
  padding: 48px 24px;
  background: #f9fafb;
  border-radius: 12px;
  margin-bottom: 32px;
}

.empty-icon {
  font-size: 3rem;
  color: #9ca3af;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 8px 0;
}

.empty-description {
  color: #6b7280;
  margin: 0 0 24px 0;
}

.empty-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
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
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 24px 0 24px;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 24px;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #6b7280;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: #f3f4f6;
  color: #374151;
}

.modal-body {
  padding: 0 24px 24px 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid #e5e7eb;
}

/* Formulário */
.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-help {
  display: block;
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 4px;
}

.form-control {
  display: flex;
  align-items: center;
}

.form-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

/* Switch */
.switch {
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 18px;
  width: 18px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #3b82f6;
}

input:checked + .slider:before {
  transform: translateX(24px);
}

/* Responsive Design */
@media (max-width: 768px) {
  .network-discovery {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: stretch;
  }
  
  .header-actions .btn {
    flex: 1;
    justify-content: center;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .filters-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .devices-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .device-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .device-actions {
    flex-direction: column;
  }
  
  .device-actions .btn {
    justify-content: center;
  }

  .empty-actions {
    flex-direction: column;
    align-items: center;
  }

  .empty-actions .btn {
    width: 200px;
  }
  
  .modal-content {
    margin: 10px;
    max-width: calc(100vw - 20px);
  }
}

/* Estilos do Modal de Confirmação de Cadastro */
.registration-modal {
  max-width: 800px;
}

.device-registration-info {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.registration-status {
  margin-bottom: 20px;
}

.status-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 12px;
  border: 2px solid;
}

.status-card.already-registered {
  background: #f0f9ff;
  border-color: #0ea5e9;
  color: #0c4a6e;
}

.status-card.new-device {
  background: #f0fdf4;
  border-color: #22c55e;
  color: #14532d;
}

.status-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.status-content h4 {
  margin: 0 0 8px 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.status-content p {
  margin: 0;
  opacity: 0.8;
}

.existing-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 12px;
  font-size: 0.875rem;
}

.device-basic-info,
.device-detailed-info {
  background: #f9fafb;
  border-radius: 8px;
  padding: 20px;
}

.device-basic-info h5,
.device-detailed-info h5 {
  margin: 0 0 16px 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
}

.info-item .label {
  font-weight: 500;
  color: #6b7280;
  font-size: 0.875rem;
}

.info-item .value {
  color: #111827;
  font-size: 0.875rem;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.specifications,
.dell-specific,
.warranty-info {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e5e7eb;
}

.specifications h6,
.dell-specific h6,
.warranty-info h6 {
  margin: 0 0 12px 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 6px;
}

.spec-grid,
.dell-grid,
.warranty-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
}

.spec-item,
.dell-item,
.warranty-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: white;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
  font-size: 0.8rem;
}

.spec-item .label,
.dell-item .label,
.warranty-item .label {
  font-weight: 500;
  color: #6b7280;
}

.spec-item .value,
.dell-item .value,
.warranty-item .value {
  color: #111827;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.warranty-active {
  color: #059669 !important;
  font-weight: 600;
}

.dell-specific {
  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
}

.dell-specific h6 {
  color: #0369a1;
}

@media (max-width: 768px) {
  .registration-modal {
    max-width: 95vw;
    margin: 10px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .spec-grid,
  .dell-grid,
  .warranty-grid {
    grid-template-columns: 1fr;
  }
  
  .status-card {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .page-title {
    font-size: 1.5rem;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
    font-size: 1rem;
  }

  .stat-number {
    font-size: 1.25rem;
  }
}
</style>