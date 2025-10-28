<template>
  <v-card class="memory-metrics-card" elevation="2">
    <v-card-title class="d-flex align-center">
      <v-icon icon="mdi-memory" color="secondary" class="mr-2"></v-icon>
      <span>Memória</span>
      <v-spacer></v-spacer>
      <v-chip 
        :color="getStatusColor(memoryData.usage_percent)" 
        size="small"
        variant="flat"
      >
        {{ memoryData.usage_percent }}%
      </v-chip>
    </v-card-title>

    <v-card-text>
      <div class="metrics-content">
        <!-- Gauge de uso da memória -->
        <div class="memory-gauge-container">
          <v-progress-circular
            :model-value="memoryData.usage_percent"
            :color="getStatusColor(memoryData.usage_percent)"
            :size="120"
            :width="12"
            class="memory-gauge"
          >
            <div class="gauge-content">
              <div class="usage-percent">{{ memoryData.usage_percent }}%</div>
              <div class="usage-label">RAM</div>
            </div>
          </v-progress-circular>
        </div>

        <!-- Informações de uso -->
        <div class="memory-usage">
          <div class="usage-bar-container">
            <div class="usage-labels">
              <span class="used-label">Usado: {{ memoryData.used_gb }} GB</span>
              <span class="total-label">Total: {{ memoryData.total_gb }} GB</span>
            </div>
            <v-progress-linear
              :model-value="memoryData.usage_percent"
              :color="getStatusColor(memoryData.usage_percent)"
              height="8"
              rounded
              class="usage-bar"
            ></v-progress-linear>
            <div class="available-info">
              <span class="available-label">Disponível: {{ memoryData.available_gb }} GB</span>
            </div>
          </div>
        </div>

        <!-- Informações de SWAP -->
        <div v-if="memoryData.swap_total_gb > 0" class="swap-info">
          <v-divider class="my-3"></v-divider>
          <div class="swap-header">
            <v-icon icon="mdi-harddisk" size="small" class="mr-1"></v-icon>
            <span class="swap-title">Memória Virtual (SWAP)</span>
          </div>
          
          <div class="swap-details">
            <v-row dense>
              <v-col cols="6">
                <div class="detail-item">
                  <span class="detail-label">Total:</span>
                  <span class="detail-value">{{ memoryData.swap_total_gb }} GB</span>
                </div>
              </v-col>
              <v-col cols="6">
                <div class="detail-item">
                  <span class="detail-label">Usado:</span>
                  <span class="detail-value">{{ memoryData.swap_used_gb }} GB</span>
                </div>
              </v-col>
            </v-row>
            
            <v-progress-linear
              :model-value="memoryData.swap_usage_percent"
              :color="getSwapStatusColor(memoryData.swap_usage_percent)"
              height="6"
              rounded
              class="swap-bar mt-2"
            ></v-progress-linear>
            
            <div class="swap-percentage">
              <span class="text-caption">{{ memoryData.swap_usage_percent }}% utilizado</span>
            </div>
          </div>
        </div>

        <!-- Status e alertas -->
        <div class="memory-status mt-3">
          <v-alert
            v-if="memoryData.usage_percent > 90"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-2"
          >
            <template #prepend>
              <v-icon icon="mdi-alert"></v-icon>
            </template>
            Memória com uso crítico (>90%)
          </v-alert>
          
          <v-alert
            v-else-if="memoryData.usage_percent > 80"
            type="warning"
            variant="tonal"
            density="compact"
            class="mb-2"
          >
            <template #prepend>
              <v-icon icon="mdi-alert-outline"></v-icon>
            </template>
            Memória com uso alto (>80%)
          </v-alert>

          <v-alert
            v-if="memoryData.swap_usage_percent > 50"
            type="warning"
            variant="tonal"
            density="compact"
            class="mb-2"
          >
            <template #prepend>
              <v-icon icon="mdi-information-outline"></v-icon>
            </template>
            Alto uso de memória virtual ({{ memoryData.swap_usage_percent }}%)
          </v-alert>

          <div class="timestamp">
            <v-icon icon="mdi-clock-outline" size="small" class="mr-1"></v-icon>
            <span class="text-caption">
              Atualizado: {{ formatTimestamp(memoryData.timestamp) }}
            </span>
          </div>
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
  memoryData: {
    type: Object,
    default: () => ({
      total_gb: 0,
      available_gb: 0,
      used_gb: 0,
      usage_percent: 0,
      swap_total_gb: 0,
      swap_used_gb: 0,
      swap_usage_percent: 0,
      timestamp: null
    })
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['refresh', 'view-details'])

// Computed
const getStatusColor = (usage) => {
  if (usage > 90) return 'error'
  if (usage > 80) return 'warning'
  if (usage > 60) return 'info'
  return 'success'
}

const getSwapStatusColor = (usage) => {
  if (usage > 70) return 'error'
  if (usage > 50) return 'warning'
  if (usage > 30) return 'info'
  return 'success'
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
.memory-metrics-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.metrics-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.memory-gauge-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px 0;
}

.memory-gauge {
  position: relative;
}

.gauge-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.usage-percent {
  font-size: 1.5rem;
  font-weight: bold;
  line-height: 1;
}

.usage-label {
  font-size: 0.75rem;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.memory-usage {
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 8px;
  padding: 12px;
}

.usage-bar-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.usage-labels {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.used-label,
.total-label,
.available-label {
  font-size: 0.75rem;
  font-weight: 500;
}

.available-info {
  display: flex;
  justify-content: center;
}

.available-label {
  opacity: 0.8;
}

.swap-info {
  background: rgba(var(--v-theme-surface-variant), 0.2);
  border-radius: 8px;
  padding: 12px;
}

.swap-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.swap-title {
  font-size: 0.875rem;
  font-weight: 500;
}

.swap-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 0.75rem;
  opacity: 0.8;
}

.detail-value {
  font-size: 0.75rem;
  font-weight: 500;
}

.swap-percentage {
  display: flex;
  justify-content: center;
  margin-top: 4px;
}

.memory-status {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.timestamp {
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
}

/* Responsividade */
@media (max-width: 600px) {
  .memory-gauge-container {
    padding: 8px 0;
  }
  
  .memory-gauge {
    width: 100px !important;
    height: 100px !important;
  }
  
  .usage-percent {
    font-size: 1.2rem;
  }
  
  .usage-labels {
    flex-direction: column;
    gap: 4px;
    align-items: flex-start;
  }
}

/* Animações */
.memory-gauge,
.usage-bar,
.swap-bar {
  transition: all 0.3s ease;
}

.detail-value {
  transition: color 0.3s ease;
}

/* Tema escuro */
.v-theme--dark .memory-usage {
  background: rgba(var(--v-theme-surface-variant), 0.2);
}

.v-theme--dark .swap-info {
  background: rgba(var(--v-theme-surface-variant), 0.15);
}
</style>