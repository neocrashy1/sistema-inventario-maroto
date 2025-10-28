<template>
  <v-card class="cpu-metrics-card" elevation="2">
    <v-card-title class="d-flex align-center">
      <v-icon icon="mdi-cpu-64-bit" color="primary" class="mr-2"></v-icon>
      <span>CPU</span>
      <v-spacer></v-spacer>
      <v-chip 
        :color="getStatusColor(cpuData.usage_percent)" 
        size="small"
        variant="flat"
      >
        {{ cpuData.usage_percent }}%
      </v-chip>
    </v-card-title>

    <v-card-text>
      <div class="metrics-content">
        <!-- Gauge de uso da CPU -->
        <div class="cpu-gauge-container">
          <v-progress-circular
            :model-value="cpuData.usage_percent"
            :color="getStatusColor(cpuData.usage_percent)"
            :size="120"
            :width="12"
            class="cpu-gauge"
          >
            <div class="gauge-content">
              <div class="usage-percent">{{ cpuData.usage_percent }}%</div>
              <div class="usage-label">CPU</div>
            </div>
          </v-progress-circular>
        </div>

        <!-- Informações detalhadas -->
        <div class="cpu-details">
          <v-row dense>
            <v-col cols="6">
              <div class="detail-item">
                <v-icon icon="mdi-chip" size="small" class="mr-1"></v-icon>
                <span class="detail-label">Cores Físicos:</span>
                <span class="detail-value">{{ cpuData.cores_physical || 'N/A' }}</span>
              </div>
            </v-col>
            <v-col cols="6">
              <div class="detail-item">
                <v-icon icon="mdi-memory" size="small" class="mr-1"></v-icon>
                <span class="detail-label">Cores Lógicos:</span>
                <span class="detail-value">{{ cpuData.cores_logical || 'N/A' }}</span>
              </div>
            </v-col>
            <v-col cols="6">
              <div class="detail-item">
                <v-icon icon="mdi-speedometer" size="small" class="mr-1"></v-icon>
                <span class="detail-label">Frequência:</span>
                <span class="detail-value">{{ formatFrequency(cpuData.frequency_mhz) }}</span>
              </div>
            </v-col>
            <v-col cols="6">
              <div class="detail-item">
                <v-icon icon="mdi-speedometer-medium" size="small" class="mr-1"></v-icon>
                <span class="detail-label">Freq. Máx:</span>
                <span class="detail-value">{{ formatFrequency(cpuData.frequency_max_mhz) }}</span>
              </div>
            </v-col>
          </v-row>
        </div>

        <!-- Status e alertas -->
        <div class="cpu-status mt-3">
          <v-alert
            v-if="cpuData.usage_percent > 90"
            type="error"
            variant="tonal"
            density="compact"
            class="mb-2"
          >
            <template #prepend>
              <v-icon icon="mdi-alert"></v-icon>
            </template>
            CPU com uso crítico (>90%)
          </v-alert>
          
          <v-alert
            v-else-if="cpuData.usage_percent > 75"
            type="warning"
            variant="tonal"
            density="compact"
            class="mb-2"
          >
            <template #prepend>
              <v-icon icon="mdi-alert-outline"></v-icon>
            </template>
            CPU com uso alto (>75%)
          </v-alert>

          <div class="timestamp">
            <v-icon icon="mdi-clock-outline" size="small" class="mr-1"></v-icon>
            <span class="text-caption">
              Atualizado: {{ formatTimestamp(cpuData.timestamp) }}
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
  cpuData: {
    type: Object,
    default: () => ({
      usage_percent: 0,
      cores_physical: null,
      cores_logical: null,
      frequency_mhz: null,
      frequency_max_mhz: null,
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
  if (usage > 75) return 'warning'
  if (usage > 50) return 'info'
  return 'success'
}

const formatFrequency = (mhz) => {
  if (!mhz) return 'N/A'
  if (mhz >= 1000) {
    return `${(mhz / 1000).toFixed(1)} GHz`
  }
  return `${Math.round(mhz)} MHz`
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
.cpu-metrics-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.metrics-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.cpu-gauge-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px 0;
}

.cpu-gauge {
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

.cpu-details {
  background: rgba(var(--v-theme-surface-variant), 0.3);
  border-radius: 8px;
  padding: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 8px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-size: 0.75rem;
  opacity: 0.8;
  min-width: 60px;
}

.detail-value {
  font-size: 0.75rem;
  font-weight: 500;
}

.cpu-status {
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
  .cpu-gauge-container {
    padding: 8px 0;
  }
  
  .cpu-gauge {
    width: 100px !important;
    height: 100px !important;
  }
  
  .usage-percent {
    font-size: 1.2rem;
  }
  
  .detail-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }
  
  .detail-label {
    min-width: auto;
  }
}

/* Animações */
.cpu-gauge {
  transition: all 0.3s ease;
}

.detail-value {
  transition: color 0.3s ease;
}

/* Tema escuro */
.v-theme--dark .cpu-details {
  background: rgba(var(--v-theme-surface-variant), 0.2);
}
</style>