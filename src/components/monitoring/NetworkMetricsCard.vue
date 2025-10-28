<template>
  <v-card class="network-metrics-card" elevation="2">
    <v-card-title class="d-flex align-center">
      <v-icon icon="mdi-network" color="secondary" class="mr-2"></v-icon>
      <span>Rede</span>
      <v-spacer></v-spacer>
      <v-chip 
        :color="getConnectionStatusColor()" 
        size="small"
        variant="flat"
      >
        {{ getConnectionStatus() }}
      </v-chip>
    </v-card-title>

    <v-card-text>
      <div class="metrics-content">
        <!-- Resumo de tráfego -->
        <div class="traffic-summary">
          <v-row dense>
            <v-col cols="6">
              <div class="traffic-item download">
                <div class="traffic-icon">
                  <v-icon icon="mdi-download" color="success"></v-icon>
                </div>
                <div class="traffic-info">
                  <div class="traffic-value">{{ networkData.download_mbps }} Mbps</div>
                  <div class="traffic-label">Download</div>
                  <div class="traffic-total">{{ networkData.total_received_gb }} GB total</div>
                </div>
              </div>
            </v-col>
            
            <v-col cols="6">
              <div class="traffic-item upload">
                <div class="traffic-icon">
                  <v-icon icon="mdi-upload" color="info"></v-icon>
                </div>
                <div class="traffic-info">
                  <div class="traffic-value">{{ networkData.upload_mbps }} Mbps</div>
                  <div class="traffic-label">Upload</div>
                  <div class="traffic-total">{{ networkData.total_sent_gb }} GB total</div>
                </div>
              </div>
            </v-col>
          </v-row>
        </div>

        <!-- Gráfico de atividade -->
        <div class="activity-chart">
          <div class="chart-header">
            <span class="chart-title">Atividade de Rede</span>
            <span class="chart-subtitle">Últimos minutos</span>
          </div>
          
          <div class="activity-bars">
            <div class="activity-legend">
              <div class="legend-item">
                <div class="legend-color download-color"></div>
                <span class="legend-label">Download</span>
              </div>
              <div class="legend-item">
                <div class="legend-color upload-color"></div>
                <span class="legend-label">Upload</span>
              </div>
            </div>
            
            <div class="bars-container">
              <div 
                v-for="(point, index) in activityData" 
                :key="index"
                class="bar-group"
              >
                <div class="bar-pair">
                  <div 
                    class="activity-bar download-bar"
                    :style="{ height: `${getBarHeight(point.download)}%` }"
                  ></div>
                  <div 
                    class="activity-bar upload-bar"
                    :style="{ height: `${getBarHeight(point.upload)}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <v-divider class="my-3"></v-divider>

        <!-- Interfaces de rede -->
        <div class="network-interfaces">
          <div class="interfaces-header">
            <v-icon icon="mdi-ethernet" size="small" class="mr-1"></v-icon>
            <span class="interfaces-title">Interfaces de Rede</span>
          </div>
          
          <div class="interfaces-list">
            <div 
              v-for="(iface, index) in networkData.interfaces" 
              :key="iface.name || index"
              class="interface-item"
            >
              <div class="interface-header">
                <div class="interface-info">
                  <v-icon 
                    :icon="getInterfaceIcon(iface.type)" 
                    size="small" 
                    class="mr-2"
                  ></v-icon>
                  <span class="interface-name">{{ iface.name }}</span>
                  <v-chip 
                    :color="iface.is_up ? 'success' : 'error'"
                    size="x-small"
                    variant="flat"
                    class="ml-2"
                  >
                    {{ iface.is_up ? 'Ativo' : 'Inativo' }}
                  </v-chip>
                </div>
                
                <div class="interface-speed" v-if="iface.speed_mbps">
                  <span class="text-caption">{{ iface.speed_mbps }} Mbps</span>
                </div>
              </div>

              <div v-if="iface.is_up" class="interface-details">
                <div class="interface-addresses" v-if="iface.addresses && iface.addresses.length > 0">
                  <div 
                    v-for="(addr, addrIndex) in iface.addresses" 
                    :key="addrIndex"
                    class="address-item"
                  >
                    <v-icon 
                      :icon="addr.family === 'IPv4' ? 'mdi-ip' : 'mdi-ipv6'" 
                      size="x-small" 
                      class="mr-1"
                    ></v-icon>
                    <span class="address-value">{{ addr.address }}</span>
                    <v-chip 
                      size="x-small"
                      variant="outlined"
                      class="ml-1"
                    >
                      {{ addr.family }}
                    </v-chip>
                  </div>
                </div>
                
                <div class="interface-stats" v-if="iface.bytes_sent || iface.bytes_recv">
                  <v-row dense>
                    <v-col cols="6">
                      <div class="stat-item">
                        <span class="stat-label">Enviado:</span>
                        <span class="stat-value">{{ formatBytes(iface.bytes_sent) }}</span>
                      </div>
                    </v-col>
                    <v-col cols="6">
                      <div class="stat-item">
                        <span class="stat-label">Recebido:</span>
                        <span class="stat-value">{{ formatBytes(iface.bytes_recv) }}</span>
                      </div>
                    </v-col>
                  </v-row>
                </div>
              </div>

              <v-divider v-if="index < networkData.interfaces.length - 1" class="my-2"></v-divider>
            </div>
          </div>
        </div>

        <!-- Estatísticas de conexão -->
        <div v-if="networkData.connections" class="connection-stats">
          <v-divider class="my-3"></v-divider>
          <div class="connections-header">
            <v-icon icon="mdi-connection" size="small" class="mr-1"></v-icon>
            <span class="connections-title">Conexões Ativas</span>
          </div>
          
          <v-row dense class="mt-2">
            <v-col cols="3">
              <div class="connection-item">
                <div class="connection-value">{{ networkData.connections.established || 0 }}</div>
                <div class="connection-label">Estabelecidas</div>
              </div>
            </v-col>
            <v-col cols="3">
              <div class="connection-item">
                <div class="connection-value">{{ networkData.connections.listening || 0 }}</div>
                <div class="connection-label">Escutando</div>
              </div>
            </v-col>
            <v-col cols="3">
              <div class="connection-item">
                <div class="connection-value">{{ networkData.connections.time_wait || 0 }}</div>
                <div class="connection-label">Time Wait</div>
              </div>
            </v-col>
            <v-col cols="3">
              <div class="connection-item">
                <div class="connection-value">{{ networkData.connections.total || 0 }}</div>
                <div class="connection-label">Total</div>
              </div>
            </v-col>
          </v-row>
        </div>

        <!-- Timestamp -->
        <div class="timestamp mt-3">
          <v-icon icon="mdi-clock-outline" size="small" class="mr-1"></v-icon>
          <span class="text-caption">
            Atualizado: {{ formatTimestamp(networkData.timestamp) }}
          </span>
        </div>
      </div>
    </v-card-text>

    <!-- Ações -->
    <v-card-actions>
      <v-btn
        variant="text"
        size="small"
        @click="$emit('refresh')"
        :loading="loading"
      >
        <v-icon icon="mdi-refresh" class="mr-1"></v-icon>
        Atualizar
      </v-btn>
      
      <v-spacer></v-spacer>
      
      <v-btn
        variant="text"
        size="small"
        @click="$emit('test-connection')"
      >
        <v-icon icon="mdi-network-outline" class="mr-1"></v-icon>
        Testar
      </v-btn>
      
      <v-btn
        variant="text"
        size="small"
        @click="$emit('view-details')"
      >
        <v-icon icon="mdi-chart-line" class="mr-1"></v-icon>
        Detalhes
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup>
import { computed } from 'vue'

// Props
const props = defineProps({
  networkData: {
    type: Object,
    default: () => ({
      download_mbps: 0,
      upload_mbps: 0,
      total_received_gb: 0,
      total_sent_gb: 0,
      interfaces: [],
      connections: null,
      timestamp: null
    })
  },
  activityData: {
    type: Array,
    default: () => Array(20).fill().map(() => ({ download: 0, upload: 0 }))
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['refresh', 'test-connection', 'view-details'])

// Computed
const getConnectionStatus = () => {
  const activeInterfaces = props.networkData.interfaces?.filter(i => i.is_up) || []
  
  if (activeInterfaces.length === 0) return 'Desconectado'
  if (activeInterfaces.some(i => i.type === 'ethernet')) return 'Ethernet'
  if (activeInterfaces.some(i => i.type === 'wireless')) return 'Wi-Fi'
  return 'Conectado'
}

const getConnectionStatusColor = () => {
  const status = getConnectionStatus()
  if (status === 'Desconectado') return 'error'
  if (status === 'Ethernet') return 'success'
  if (status === 'Wi-Fi') return 'info'
  return 'success'
}

const getInterfaceIcon = (type) => {
  if (!type) return 'mdi-ethernet'
  
  const interfaceType = type.toLowerCase()
  if (interfaceType.includes('wireless') || interfaceType.includes('wifi')) return 'mdi-wifi'
  if (interfaceType.includes('ethernet') || interfaceType.includes('wired')) return 'mdi-ethernet'
  if (interfaceType.includes('loopback')) return 'mdi-repeat'
  if (interfaceType.includes('vpn')) return 'mdi-vpn'
  if (interfaceType.includes('bluetooth')) return 'mdi-bluetooth'
  
  return 'mdi-ethernet'
}

const getBarHeight = (value) => {
  const maxValue = Math.max(
    ...props.activityData.map(point => Math.max(point.download, point.upload))
  )
  
  if (maxValue === 0) return 0
  return Math.min((value / maxValue) * 100, 100)
}

const formatBytes = (bytes) => {
  if (!bytes || bytes === 0) return '0 B'
  
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  
  return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`
}

const formatTimestamp = (timestamp) => {
  if (!timestamp) return 'N/A'
  
  try {
    const date = new Date(timestamp)
    return date.toLocaleString('pt-BR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (error) {
    return 'N/A'
  }
}
</script>

<style scoped>
.network-metrics-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.metrics-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.traffic-summary {
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 8px;
  padding: 16px;
}

.traffic-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 6px;
  background: rgba(var(--v-theme-surface-variant), 0.3);
}

.traffic-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(var(--v-theme-surface-variant), 0.5);
}

.traffic-info {
  flex: 1;
}

.traffic-value {
  font-size: 1.1rem;
  font-weight: bold;
  line-height: 1;
}

.traffic-label {
  font-size: 0.75rem;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.traffic-total {
  font-size: 0.7rem;
  opacity: 0.6;
}

.activity-chart {
  background: rgba(var(--v-theme-surface-variant), 0.2);
  border-radius: 8px;
  padding: 16px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-title {
  font-size: 0.875rem;
  font-weight: 500;
}

.chart-subtitle {
  font-size: 0.75rem;
  opacity: 0.7;
}

.activity-legend {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.download-color {
  background: rgb(var(--v-theme-success));
}

.upload-color {
  background: rgb(var(--v-theme-info));
}

.network-interfaces {
  background: rgba(var(--v-theme-surface-variant), 0.2);
  border-radius: 8px;
  padding: 12px;
}

.interfaces-header,
.connections-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.interfaces-title,
.connections-title {
  font-size: 0.875rem;
  font-weight: 500;
}

.interfaces-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.interface-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.interface-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.interface-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.interface-name {
  font-weight: 500;
  font-size: 0.875rem;
}

.interface-details {
  padding-left: 24px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.interface-addresses {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.address-item {
  display: flex;
  align-items: center;
  font-size: 0.75rem;
}

.address-value {
  font-family: monospace;
}

.interface-stats {
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 4px;
  padding: 8px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 0.7rem;
  opacity: 0.8;
}

.stat-value {
  font-size: 0.7rem;
  font-weight: 500;
  font-family: monospace;
}

.connection-stats {
  background: rgba(var(--v-theme-surface-variant), 0.2);
  border-radius: 8px;
  padding: 12px;
}

.connection-item {
  text-align: center;
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 6px;
  padding: 8px;
}

.connection-value {
  font-size: 1rem;
  font-weight: bold;
  line-height: 1;
}

.connection-label {
  font-size: 0.7rem;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.timestamp {
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
}

/* Responsividade */
@media (max-width: 600px) {
  .traffic-item {
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }
  
  .interface-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .activity-legend {
    justify-content: flex-start;
  }
}

/* Animações */
.activity-bar {
  transition: height 0.3s ease, background-color 0.3s ease;
}

.traffic-value,
.connection-value {
  transition: color 0.3s ease;
}

/* Tema escuro */
.v-theme--dark .traffic-summary {
  background: rgba(var(--v-theme-surface-variant), 0.2);
}

.v-theme--dark .traffic-item {
  background: rgba(var(--v-theme-surface-variant), 0.2);
}

.v-theme--dark .activity-chart {
  background: rgba(var(--v-theme-surface-variant), 0.15);
}

.v-theme--dark .network-interfaces {
  background: rgba(var(--v-theme-surface-variant), 0.15);
}

.v-theme--dark .connection-stats {
  background: rgba(var(--v-theme-surface-variant), 0.15);
}

.v-theme--dark .connection-item {
  background: rgba(var(--v-theme-surface-variant), 0.2);
}

.v-theme--dark .interface-stats {
  background: rgba(var(--v-theme-surface-variant), 0.2);
}
</style>