<template>
  <div class="monitoring-view">
    <!-- Header da página -->
    <div class="page-header">
      <div class="header-content">
        <div class="breadcrumb-section">
          <v-breadcrumbs
            :items="breadcrumbItems"
            density="compact"
          >
            <template #prepend>
              <v-icon icon="mdi-home" size="small"></v-icon>
            </template>
          </v-breadcrumbs>
        </div>
        
        <div class="page-title-section">
          <h1 class="page-title">
            <v-icon icon="mdi-monitor-dashboard" class="mr-3"></v-icon>
            Sistema de Monitoramento
          </h1>
          <p class="page-description">
            Monitoramento em tempo real de máquinas Windows da rede
          </p>
        </div>
      </div>
    </div>

    <!-- Conteúdo principal -->
    <div class="page-content">
      <MonitoringDashboard />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import MonitoringDashboard from '@/components/monitoring/MonitoringDashboard.vue'

// Computed properties
const breadcrumbItems = computed(() => [
  {
    title: 'Início',
    disabled: false,
    href: '/'
  },
  {
    title: 'Monitoramento',
    disabled: true
  }
])
</script>

<style scoped>
.monitoring-view {
  min-height: 100vh;
  background: rgb(var(--v-theme-background));
  display: flex;
  flex-direction: column;
}

.page-header {
  background: rgb(var(--v-theme-surface));
  border-bottom: 1px solid rgba(var(--v-theme-outline), 0.12);
  padding: 16px 24px;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.breadcrumb-section {
  opacity: 0.8;
}

.page-title-section {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.page-title {
  display: flex;
  align-items: center;
  font-size: 1.75rem;
  font-weight: 600;
  margin: 0;
  color: rgb(var(--v-theme-on-surface));
}

.page-description {
  color: rgb(var(--v-theme-on-surface-variant));
  margin: 0;
  font-size: 0.875rem;
}

.page-content {
  flex: 1;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  padding: 0;
}

/* Responsividade */
@media (max-width: 960px) {
  .page-header {
    padding: 12px 16px;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
}

@media (max-width: 600px) {
  .page-header {
    padding: 8px 12px;
  }
  
  .page-title {
    font-size: 1.25rem;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}

/* Tema escuro */
.v-theme--dark .page-header {
  background: rgb(var(--v-theme-surface));
  border-bottom-color: rgba(var(--v-theme-outline), 0.12);
}
</style>