<template>
  <div class="design-system-demo">
    <!-- Header com gradiente da Levitiis -->
    <div class="demo-header levitiis-gradient-primary">
      <h1 class="demo-title">Design System Levitiis</h1>
      <p class="demo-subtitle">Demonstração do Vuetify com cores da marca</p>
    </div>

    <div class="demo-content">
      <!-- Seção Vuetify - Para Sistemas -->
      <section class="demo-section">
        <h2 class="section-title">
          <v-icon icon="mdi-cog" class="mr-2"></v-icon>
          Vuetify - Componentes de Sistema
        </h2>
        <p class="section-description">
          Ideal para dashboards, formulários e interfaces administrativas
        </p>

        <div class="demo-grid">
          <!-- Cards de métricas -->
          <v-card class="metric-card" elevation="2">
            <v-card-text>
              <div class="metric-header">
                <v-icon icon="mdi-server" color="primary" size="large"></v-icon>
                <v-chip color="success" size="small">Online</v-chip>
              </div>
              <h3 class="metric-value">127</h3>
              <p class="metric-label">Máquinas Ativas</p>
            </v-card-text>
          </v-card>

          <v-card class="metric-card" elevation="2">
            <v-card-text>
              <div class="metric-header">
                <v-icon icon="mdi-memory" color="warning" size="large"></v-icon>
                <v-chip color="warning" size="small">Atenção</v-chip>
              </div>
              <h3 class="metric-value">78%</h3>
              <p class="metric-label">Uso de RAM</p>
            </v-card-text>
          </v-card>

          <v-card class="metric-card" elevation="2">
            <v-card-text>
              <div class="metric-header">
                <v-icon icon="mdi-harddisk" color="error" size="large"></v-icon>
                <v-chip color="error" size="small">Crítico</v-chip>
              </div>
              <h3 class="metric-value">92%</h3>
              <p class="metric-label">Uso de Disco</p>
            </v-card-text>
          </v-card>
        </div>

        <!-- Formulário com Vuetify -->
        <v-card class="mt-6" elevation="2">
          <v-card-title>Configurações do Sistema</v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  label="Nome do Servidor"
                  variant="outlined"
                  prepend-inner-icon="mdi-server"
                  color="primary"
                ></v-text-field>
              </v-col>
              <v-col cols="12" md="6">
                <v-select
                  label="Tipo de Monitoramento"
                  :items="['Básico', 'Avançado', 'Completo']"
                  variant="outlined"
                  color="primary"
                ></v-select>
              </v-col>
              <v-col cols="12">
                <v-switch
                  label="Alertas em tempo real"
                  color="primary"
                  inset
                ></v-switch>
              </v-col>
            </v-row>
            <v-btn color="primary" size="large" class="mt-4">
              <v-icon icon="mdi-content-save" class="mr-2"></v-icon>
              Salvar Configurações
            </v-btn>
          </v-card-text>
        </v-card>
      </section>

      <!-- Seção de Timeline com Vuetify -->
      <section class="demo-section">
        <h2 class="section-title">
          <v-icon icon="mdi-timeline" class="mr-2"></v-icon>
          Timeline de Atividades
        </h2>
        <p class="section-description">
          Histórico de eventos e atividades do sistema
        </p>

        <v-card class="timeline-card" elevation="2">
          <v-card-title>Atividades Recentes</v-card-title>
          <v-card-text>
            <v-timeline align="start" side="end">
              <v-timeline-item
                v-for="event in timelineEvents"
                :key="event.title"
                :dot-color="event.color"
                size="small"
              >
                <template #icon>
                  <v-icon :icon="event.icon" size="small"></v-icon>
                </template>
                <template #opposite>
                  <span class="text-caption">{{ event.date }}</span>
                </template>
                <v-card class="timeline-event-card" elevation="1">
                  <v-card-title class="text-h6">{{ event.title }}</v-card-title>
                  <v-card-text>
                    <p>{{ event.description }}</p>
                    <v-chip :color="event.severity" size="small">{{ event.status }}</v-chip>
                  </v-card-text>
                </v-card>
              </v-timeline-item>
            </v-timeline>
          </v-card-text>
        </v-card>
      </section>

      <!-- Seção de Recursos do Vuetify -->
      <section class="demo-section">
        <h2 class="section-title">Recursos do Vuetify com Tema Levitiis</h2>
        
        <v-card class="features-card" elevation="2">
          <v-card-title>
            <v-icon icon="mdi-cog" class="mr-2"></v-icon>
            Vuetify - Framework Principal
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <h4>Ideal para:</h4>
                <v-list>
                  <v-list-item>
                    <template #prepend>
                      <v-icon icon="mdi-check" color="success"></v-icon>
                    </template>
                    <v-list-item-title>Dashboards administrativos</v-list-item-title>
                  </v-list-item>
                  <v-list-item>
                    <template #prepend>
                      <v-icon icon="mdi-check" color="success"></v-icon>
                    </template>
                    <v-list-item-title>Sistemas internos</v-list-item-title>
                  </v-list-item>
                  <v-list-item>
                    <template #prepend>
                      <v-icon icon="mdi-check" color="success"></v-icon>
                    </template>
                    <v-list-item-title>Formulários complexos</v-list-item-title>
                  </v-list-item>
                  <v-list-item>
                    <template #prepend>
                      <v-icon icon="mdi-check" color="success"></v-icon>
                    </template>
                    <v-list-item-title>Interfaces de dados</v-list-item-title>
                  </v-list-item>
                  <v-list-item>
                    <template #prepend>
                      <v-icon icon="mdi-check" color="success"></v-icon>
                    </template>
                    <v-list-item-title>Aplicações corporativas</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-col>
              <v-col cols="12" md="6">
                <h4>Características:</h4>
                <div class="framework-features">
                  <v-chip color="primary" size="small" class="ma-1">Material Design</v-chip>
                  <v-chip color="secondary" size="small" class="ma-1">Componentes Robustos</v-chip>
                  <v-chip color="accent" size="small" class="ma-1">Grid System</v-chip>
                  <v-chip color="success" size="small" class="ma-1">Tema Personalizado</v-chip>
                  <v-chip color="info" size="small" class="ma-1">Responsivo</v-chip>
                  <v-chip color="warning" size="small" class="ma-1">Acessibilidade</v-chip>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Dados para timeline
const timelineEvents = ref([
  {
    title: 'Sistema Iniciado',
    date: '15:30',
    description: 'Todos os serviços foram iniciados com sucesso',
    status: 'Concluído',
    severity: 'success',
    icon: 'pi pi-check',
    color: 'success'
  },
  {
    title: 'Backup Realizado',
    date: '14:15',
    description: 'Backup automático dos dados críticos',
    status: 'Sucesso',
    severity: 'info',
    icon: 'pi pi-download',
    color: 'info'
  },
  {
    title: 'Alerta de Memória',
    date: '13:45',
    description: 'Uso de memória acima de 80% detectado',
    status: 'Atenção',
    severity: 'warn',
    icon: 'pi pi-exclamation-triangle',
    color: 'warning'
  },
  {
    title: 'Manutenção Programada',
    date: '12:00',
    description: 'Manutenção preventiva agendada para hoje',
    status: 'Pendente',
    severity: 'info',
    icon: 'pi pi-calendar',
    color: 'primary'
  }
])

// Dados para formulário
const monitoringTypes = ref([
  { name: 'Básico', code: 'basic' },
  { name: 'Avançado', code: 'advanced' },
  { name: 'Completo', code: 'complete' },
  { name: 'Personalizado', code: 'custom' }
])

const alertFrequency = ref(15)
const notifications = ref({
  email: true,
  sms: false,
  push: true
})
</script>

<style scoped lang="scss">
.design-system-demo {
  min-height: 100vh;
  background: var(--levitiis-background);
}

.demo-header {
  padding: 4rem 2rem;
  text-align: center;
  color: white;
  
  .demo-title {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 1rem;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  .demo-subtitle {
    font-size: 1.25rem;
    opacity: 0.9;
    max-width: 600px;
    margin: 0 auto;
  }
}

.demo-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.demo-section {
  margin-bottom: 4rem;
  
  .section-title {
    font-size: 2rem;
    font-weight: 600;
    color: var(--levitiis-gray-800);
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
  }
  
  .section-description {
    color: var(--levitiis-gray-600);
    font-size: 1.1rem;
    margin-bottom: 2rem;
  }
}

.demo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.metric-card {
  .metric-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
  
  .metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--levitiis-primary);
    margin-bottom: 0.5rem;
  }
  
  .metric-label {
    color: var(--levitiis-gray-600);
    font-size: 0.9rem;
    margin: 0;
  }
}

.timeline-card {
  .card-title-with-icon {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.5rem;
    font-weight: 600;
  }
}

.timeline-marker {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  
  &.success { background: var(--levitiis-success); }
  &.info { background: var(--levitiis-info); }
  &.warning { background: var(--levitiis-warning); }
  &.primary { background: var(--levitiis-primary); }
}

.timeline-event-card {
  margin: 1rem 0;
  box-shadow: var(--levitiis-shadow);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border-radius: var(--levitiis-radius-lg);
  background: var(--levitiis-surface);
  box-shadow: var(--levitiis-shadow-sm);
  
  .stat-icon {
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 1.25rem;
    
    &.success { background: var(--levitiis-success); }
    &.info { background: var(--levitiis-info); }
    &.warning { background: var(--levitiis-warning); }
    &.primary { background: var(--levitiis-primary); }
  }
  
  .stat-content {
    h4 {
      font-size: 1.5rem;
      font-weight: 700;
      margin: 0 0 0.25rem 0;
      color: var(--levitiis-gray-800);
    }
    
    p {
      margin: 0;
      color: var(--levitiis-gray-600);
      font-size: 0.9rem;
    }
  }
}

.form-grid {
  display: grid;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-group {
  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 600;
    color: var(--levitiis-gray-700);
  }
  
  small {
    color: var(--levitiis-gray-500);
    font-size: 0.875rem;
  }
}

.notification-options {
  display: flex;
  gap: 1.5rem;
  margin-top: 0.5rem;
}

.notification-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
}

.comparison-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.comparison-card {
  padding: 2rem;
  border-radius: var(--levitiis-radius-lg);
  box-shadow: var(--levitiis-shadow-lg);
  background: var(--levitiis-surface);
  
  h3 {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
  }
  
  h4 {
    color: var(--levitiis-gray-700);
    margin-bottom: 1rem;
  }
  
  ul {
    list-style: none;
    padding: 0;
    margin-bottom: 1.5rem;
    
    li {
      padding: 0.5rem 0;
      color: var(--levitiis-gray-600);
      position: relative;
      padding-left: 1.5rem;
      
      &::before {
        content: '✓';
        position: absolute;
        left: 0;
        color: var(--levitiis-success);
        font-weight: bold;
      }
    }
  }
  
  .framework-features {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
}

.vuetify-card {
  border-left: 4px solid var(--levitiis-primary);
}

.primevue-card {
  border-left: 4px solid var(--levitiis-secondary);
}

@media (max-width: 768px) {
  .demo-header {
    padding: 2rem 1rem;
    
    .demo-title {
      font-size: 2rem;
    }
  }
  
  .demo-content {
    padding: 1rem;
  }
  
  .comparison-grid {
    grid-template-columns: 1fr;
  }
  
  .notification-options {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>