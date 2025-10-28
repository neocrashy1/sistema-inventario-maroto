<template>
  <v-card class="disk-metrics-card" elevation="2">
    <v-card-title class="d-flex align-center">
      <v-icon icon="mdi-harddisk" color="secondary" class="mr-2"></v-icon>
      <span>Armazenamento</span>
      <v-spacer></v-spacer>
      <v-chip 
        :color="getOverallStatusColor()" 
        size="small"
        variant="flat"
      >
        {{ diskData.length }} {{ diskData.length === 1 ? 'Disco' : 'Discos' }}
      </v-chip>
    </v-card-title>

    <v-card-text>
      <div class="metrics-content">
        <!-- Resumo geral -->
        <div v-if="totalStats" class="total-stats">
          <v-row dense>
            <v-col cols="4">
              <div class="stat-item">
                <div class="stat-value">{{ totalStats.total_gb }} GB</div>
                <div class="stat-label">Total</div>
              </div>
            </v-col>
            <v-col cols="4">
              <div class="stat-item">
                <div class="stat-value">{{ totalStats.used_gb }} GB</div>
                <div class="stat-label">Usado</div>
              </div>
            </v-col>
            <v-col cols="4">
              <div class="stat-item">
                <div class="stat-value">{{ totalStats.free_gb }} GB</div>
                <div class="stat-label">Livre</div>
              </div>
            </v-col>
          </v-row>
          
          <v-progress-linear
            :model-value="totalStats.usage_percent"
            :color="getStatusColor(totalStats.usage_percent)"
            height="8"
            rounded
            class="total-usage-bar mt-2"
          ></v-progress-linear>
          
          <div class="total-percentage">
            <span class="text-caption">{{ totalStats.usage_percent }}% do espaço total utilizado</span>
          </div>
        </div>

        <v-divider v-if="diskData.length > 0" class="my-3"></v-divider>

        <!-- Lista de discos -->
        <div class="disks-list">
          <div 
            v-for="(disk, index) in diskData" 
            :key="disk.device || index"
            class="disk-item"
          >
            <div class="disk-header">
              <div class="disk-info">
                <v-icon 
                  :icon="getDiskIcon(disk.fstype)" 
                  size="small" 
                  class="mr-2"
                ></v-icon>
                <span class="disk-name">{{ disk.device || `Disco ${index + 1}` }}</span>
                <v-chip 
                  v-if="disk.fstype"
                  size="x-small"
                  variant="outlined"
                  class="ml-2"
                >
                  {{ disk.fstype }}
                </v-chip>
              </div>
              
              <div class="disk-usage">
                <v-chip 
                  :color="getStatusColor(disk.usage_percent)" 
                  size="small"
                  variant="flat"
                >
                  {{ disk.usage_percent }}%
                </v-chip>
              </div>
            </div>

            <div class="disk-details">
              <div class="disk-path" v-if="disk.mountpoint">
                <v-icon icon="mdi-folder" size="x-small" class="mr-1"></v-icon>
                <span class="text-caption">{{ disk.mountpoint }}</span>
              </div>
              
              <div class="disk-space">
                <div class="space-info">
                  <span class="space-used">{{ disk.used_gb }} GB usado</span>
                  <span class="space-total">de {{ disk.total_gb }} GB</span>
                </div>
                
                <v-progress-linear
                  :model-value="disk.usage_percent"
                  :color="getStatusColor(disk.usage_percent)"
                  height="6"
                  rounded
                  class="disk-bar"
                ></v-progress-linear>
                
                <div class="space-free">
                  <span class="text-caption">{{ disk.free_gb }} GB disponível</span>
                </div>
              </div>

              <!-- Alertas por disco -->
              <div v-if="disk.usage_percent > 90" class="disk-alert">
                <v-alert
                  type="error"
                  variant="tonal"
                  density="compact"
                  class="mt-2"
                >
                  <template #prepend>
                    <v-icon icon="mdi-alert" size="small"></v-icon>
                  </template>
                  Espaço crítico ({{ disk.free_gb }} GB restante)
                </v-alert>
              </div>
              
              <div v-else-if="disk.usage_percent > 80" class="disk-alert">
                <v-alert
                  type="warning"
                  variant="tonal"
                  density="compact"
                  class="mt-2"
                >
                  <template #prepend>
                    <v-icon icon="mdi-alert-outline" size="small"></v-icon>
                  </template>
                  Pouco espaço disponível
                </v-alert>
              </div>
            </div>

            <v-divider v-if="index < diskData.length - 1" class="my-3"></v-divider>
          </div>
        </div>

        <!-- Informações de I/O se disponível -->
        <div v-if="ioStats" class="io-stats">
          <v-divider class="my-3"></v-divider>
          <div class="io-header">
            <v-icon icon="mdi-swap-horizontal" size="small" class="mr-1"></v-icon>
            <span class="io-title">Atividade de I/O</span>
          </div>
          
          <v-row dense class="mt-2">
            <v-col cols="6">
              <div class="io-item">
                <div class="io-value">{{ ioStats.read_mb_s }} MB/s</div>
                <div class="io-label">Leitura</div>
              </div>
            </v-col>
            <v-col cols="6">
              <div class="io-item">
                <div class="io-value">{{ ioStats.write_mb_s }} MB/s</div>
                <div class="io-label">Escrita</div>
              </div>
            </v-col>
          </v-row>
        </div>

        <!-- Timestamp -->
        <div class="timestamp mt-3">
          <v-icon icon="mdi-clock-outline" size="small" class="mr-1"></v-icon>
          <span class="text-caption">
            Atualizado: {{ formatTimestamp(lastUpdate) }}
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
        @click="$emit('cleanup')"
      >
        <v-icon icon="mdi-broom" class="mr-1"></v-icon>
        Limpeza
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
  diskData: {
    type: Array,
    default: () => []
  },
  ioStats: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['refresh', 'cleanup', 'view-details'])

// Computed
const totalStats = computed(() => {
  if (!props.diskData || props.diskData.length === 0) return null
  
  const total = props.diskData.reduce((acc, disk) => {
    acc.total_gb += disk.total_gb || 0
    acc.used_gb += disk.used_gb || 0
    acc.free_gb += disk.free_gb || 0
    return acc
  }, { total_gb: 0, used_gb: 0, free_gb: 0 })
  
  total.usage_percent = total.total_gb > 0 
    ? Math.round((total.used_gb / total.total_gb) * 100) 
    : 0
  
  return total
})

const lastUpdate = computed(() => {
  if (!props.diskData || props.diskData.length === 0) return null
  
  // Pega o timestamp mais recente
  const timestamps = props.diskData
    .map(disk => disk.timestamp)
    .filter(Boolean)
    .sort((a, b) => new Date(b) - new Date(a))
  
  return timestamps[0] || null
})

const getStatusColor = (usage) => {
  if (usage > 90) return 'error'
  if (usage > 80) return 'warning'
  if (usage > 70) return 'info'
  return 'success'
}

const getOverallStatusColor = () => {
  if (!totalStats.value) return 'surface-variant'
  
  const criticalDisks = props.diskData.filter(disk => disk.usage_percent > 90).length
  const warningDisks = props.diskData.filter(disk => disk.usage_percent > 80).length
  
  if (criticalDisks > 0) return 'error'
  if (warningDisks > 0) return 'warning'
  return 'success'
}

const getDiskIcon = (fstype) => {
  if (!fstype) return 'mdi-harddisk'
  
  const type = fstype.toLowerCase()
  if (type.includes('ntfs') || type.includes('fat')) return 'mdi-microsoft-windows'
  if (type.includes('ext') || type.includes('xfs') || type.includes('btrfs')) return 'mdi-linux'
  if (type.includes('hfs') || type.includes('apfs')) return 'mdi-apple'
  if (type.includes('cd') || type.includes('dvd')) return 'mdi-disc'
  if (type.includes('usb') || type.includes('removable')) return 'mdi-usb'
  
  return 'mdi-harddisk'
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
.disk-metrics-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.metrics-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.total-stats {
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 8px;
  padding: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: bold;
  line-height: 1;
}

.stat-label {
  font-size: 0.75rem;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.total-percentage {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}

.disks-list {
  display: flex;
  flex-direction: column;
}

.disk-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.disk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.disk-info {
  display: flex;
  align-items: center;
  flex: 1;
}

.disk-name {
  font-weight: 500;
  font-size: 0.875rem;
}

.disk-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-left: 24px;
}

.disk-path {
  display: flex;
  align-items: center;
  opacity: 0.8;
}

.disk-space {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.space-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.space-used,
.space-total {
  font-size: 0.75rem;
}

.space-used {
  font-weight: 500;
}

.space-total {
  opacity: 0.8;
}

.space-free {
  display: flex;
  justify-content: center;
}

.io-stats {
  background: rgba(var(--v-theme-surface-variant), 0.2);
  border-radius: 8px;
  padding: 12px;
}

.io-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
}

.io-title {
  font-size: 0.875rem;
  font-weight: 500;
}

.io-item {
  text-align: center;
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 6px;
  padding: 8px;
}

.io-value {
  font-size: 0.875rem;
  font-weight: bold;
  line-height: 1;
}

.io-label {
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
  .disk-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .disk-info {
    width: 100%;
  }
  
  .space-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }
  
  .stat-value {
    font-size: 1rem;
  }
}

/* Animações */
.disk-bar,
.total-usage-bar {
  transition: all 0.3s ease;
}

.stat-value,
.io-value {
  transition: color 0.3s ease;
}

/* Tema escuro */
.v-theme--dark .total-stats {
  background: rgba(var(--v-theme-surface-variant), 0.2);
}

.v-theme--dark .io-stats {
  background: rgba(var(--v-theme-surface-variant), 0.15);
}

.v-theme--dark .io-item {
  background: rgba(var(--v-theme-surface-variant), 0.2);
}
</style>