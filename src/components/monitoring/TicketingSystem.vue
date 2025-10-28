<template>
  <div class="ticketing-system">
    <!-- Header do Sistema de Chamados -->
    <div class="ticketing-header">
      <div class="header-content">
        <div class="header-info">
          <h3 class="ticketing-title">
            <v-icon icon="mdi-ticket-confirmation" class="mr-2"></v-icon>
            Sistema de Chamados
          </h3>
          <p class="ticketing-subtitle">
            {{ tickets.length }} {{ tickets.length === 1 ? 'chamado registrado' : 'chamados registrados' }}
          </p>
        </div>
        
        <div class="header-actions">
          <v-btn
            variant="flat"
            color="primary"
            size="small"
            @click="openCreateTicketDialog"
            class="mr-2"
          >
            <v-icon icon="mdi-plus" class="mr-1"></v-icon>
            Novo Chamado
          </v-btn>
          
          <v-btn
            variant="outlined"
            size="small"
            @click="refreshTickets"
            :loading="isRefreshing"
            class="mr-2"
          >
            <v-icon icon="mdi-refresh" class="mr-1"></v-icon>
            Atualizar
          </v-btn>
          
          <v-btn
            variant="outlined"
            size="small"
            @click="exportTickets"
            :disabled="tickets.length === 0"
          >
            <v-icon icon="mdi-download" class="mr-1"></v-icon>
            Exportar
          </v-btn>
        </div>
      </div>
    </div>

    <!-- Estatísticas dos Chamados -->
    <div class="ticketing-stats">
      <v-row dense>
        <v-col cols="12" sm="6" md="3">
          <v-card variant="tonal" color="info">
            <v-card-text class="text-center">
              <v-icon icon="mdi-ticket-outline" size="large" class="mb-2"></v-icon>
              <div class="stat-value">{{ totalTickets }}</div>
              <div class="stat-label">Total de Chamados</div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-card variant="tonal" color="warning">
            <v-card-text class="text-center">
              <v-icon icon="mdi-clock-outline" size="large" class="mb-2"></v-icon>
              <div class="stat-value">{{ openTickets }}</div>
              <div class="stat-label">Abertos</div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-card variant="tonal" color="primary">
            <v-card-text class="text-center">
              <v-icon icon="mdi-progress-clock" size="large" class="mb-2"></v-icon>
              <div class="stat-value">{{ inProgressTickets }}</div>
              <div class="stat-label">Em Andamento</div>
            </v-card-text>
          </v-card>
        </v-col>
        
        <v-col cols="12" sm="6" md="3">
          <v-card variant="tonal" color="success">
            <v-card-text class="text-center">
              <v-icon icon="mdi-check-circle" size="large" class="mb-2"></v-icon>
              <div class="stat-value">{{ resolvedTickets }}</div>
              <div class="stat-label">Resolvidos</div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </div>

    <!-- Filtros e Busca -->
    <div class="ticketing-filters">
      <v-card>
        <v-card-text>
          <v-row align="center">
            <v-col cols="12" md="3">
              <v-text-field
                v-model="searchQuery"
                label="Buscar chamados"
                variant="outlined"
                density="compact"
                clearable
                @input="filterTickets"
              >
                <template #prepend-inner>
                  <v-icon icon="mdi-magnify"></v-icon>
                </template>
              </v-text-field>
            </v-col>
            
            <v-col cols="12" md="2">
              <v-select
                v-model="statusFilter"
                :items="statusOptions"
                label="Status"
                variant="outlined"
                density="compact"
                clearable
                @update:model-value="filterTickets"
              >
                <template #prepend-inner>
                  <v-icon icon="mdi-filter"></v-icon>
                </template>
              </v-select>
            </v-col>
            
            <v-col cols="12" md="2">
              <v-select
                v-model="priorityFilter"
                :items="priorityOptions"
                label="Prioridade"
                variant="outlined"
                density="compact"
                clearable
                @update:model-value="filterTickets"
              >
                <template #prepend-inner>
                  <v-icon icon="mdi-flag"></v-icon>
                </template>
              </v-select>
            </v-col>
            
            <v-col cols="12" md="2">
              <v-select
                v-model="categoryFilter"
                :items="categoryOptions"
                label="Categoria"
                variant="outlined"
                density="compact"
                clearable
                @update:model-value="filterTickets"
              >
                <template #prepend-inner>
                  <v-icon icon="mdi-tag"></v-icon>
                </template>
              </v-select>
            </v-col>
            
            <v-col cols="12" md="2">
              <v-select
                v-model="assigneeFilter"
                :items="assigneeOptions"
                label="Responsável"
                variant="outlined"
                density="compact"
                clearable
                @update:model-value="filterTickets"
              >
                <template #prepend-inner>
                  <v-icon icon="mdi-account"></v-icon>
                </template>
              </v-select>
            </v-col>
            
            <v-col cols="12" md="1">
              <v-btn
                variant="outlined"
                block
                @click="clearFilters"
                :disabled="!hasActiveFilters"
              >
                <v-icon icon="mdi-filter-remove"></v-icon>
              </v-btn>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </div>

    <!-- Lista de Chamados -->
    <div class="ticketing-list">
      <v-card>
        <v-card-title>
          <div class="d-flex justify-space-between align-center w-100">
            <span>Lista de Chamados</span>
            <v-chip
              color="primary"
              size="small"
              variant="flat"
            >
              {{ filteredTickets.length }} {{ filteredTickets.length === 1 ? 'chamado' : 'chamados' }}
            </v-chip>
          </div>
        </v-card-title>
        
        <v-card-text v-if="filteredTickets.length === 0" class="text-center py-8">
          <v-icon icon="mdi-ticket-outline" size="64" color="surface-variant" class="mb-4"></v-icon>
          <h4 class="text-h6 mb-2">Nenhum chamado encontrado</h4>
          <p class="text-body-2 text-medium-emphasis">
            {{ tickets.length === 0 ? 'Crie um novo chamado para começar.' : 'Ajuste os filtros para encontrar chamados específicos.' }}
          </p>
        </v-card-text>
        
        <div v-else>
          <v-data-table
            :headers="tableHeaders"
            :items="filteredTickets"
            :loading="isRefreshing"
            item-value="id"
            class="ticketing-table"
            @click:row="viewTicketDetails"
          >
            <!-- ID Column -->
            <template #item.id="{ item }">
              <div class="ticket-id">
                #{{ String(item.id).padStart(4, '0') }}
              </div>
            </template>
            
            <!-- Priority Column -->
            <template #item.priority="{ item }">
              <v-chip
                :color="getPriorityColor(item.priority)"
                size="small"
                variant="flat"
              >
                <v-icon :icon="getPriorityIcon(item.priority)" size="small" class="mr-1"></v-icon>
                {{ item.priority }}
              </v-chip>
            </template>
            
            <!-- Status Column -->
            <template #item.status="{ item }">
              <v-chip
                :color="getStatusColor(item.status)"
                size="small"
                variant="flat"
              >
                <v-icon :icon="getStatusIcon(item.status)" size="small" class="mr-1"></v-icon>
                {{ getStatusLabel(item.status) }}
              </v-chip>
            </template>
            
            <!-- Machine Column -->
            <template #item.machine="{ item }">
              <div class="machine-info">
                <div class="machine-name">{{ item.machine_hostname }}</div>
                <div class="machine-ip text-caption text-medium-emphasis">{{ item.machine_ip }}</div>
              </div>
            </template>
            
            <!-- Category Column -->
            <template #item.category="{ item }">
              <v-chip
                size="small"
                variant="outlined"
                :color="getCategoryColor(item.category)"
              >
                <v-icon :icon="getCategoryIcon(item.category)" size="small" class="mr-1"></v-icon>
                {{ item.category }}
              </v-chip>
            </template>
            
            <!-- Assignee Column -->
            <template #item.assignee="{ item }">
              <div class="assignee-info" v-if="item.assignee">
                <v-avatar size="24" class="mr-2">
                  <v-icon icon="mdi-account"></v-icon>
                </v-avatar>
                {{ item.assignee }}
              </div>
              <span v-else class="text-medium-emphasis">Não atribuído</span>
            </template>
            
            <!-- Created Date Column -->
            <template #item.created_at="{ item }">
              <div class="date-info">
                <div class="date-value">{{ formatDate(item.created_at) }}</div>
                <div class="date-relative text-caption text-medium-emphasis">{{ formatRelativeDate(item.created_at) }}</div>
              </div>
            </template>
            
            <!-- Actions Column -->
            <template #item.actions="{ item }">
              <div class="action-buttons">
                <v-btn
                  icon="mdi-eye"
                  size="small"
                  variant="text"
                  @click.stop="viewTicketDetails(item)"
                  class="mr-1"
                ></v-btn>
                
                <v-btn
                  icon="mdi-pencil"
                  size="small"
                  variant="text"
                  color="primary"
                  @click.stop="editTicket(item)"
                  class="mr-1"
                ></v-btn>
                
                <v-btn
                  icon="mdi-account-plus"
                  size="small"
                  variant="text"
                  color="info"
                  @click.stop="assignTicket(item)"
                  :disabled="item.status === 'resolved'"
                  class="mr-1"
                ></v-btn>
                
                <v-btn
                  icon="mdi-check"
                  size="small"
                  variant="text"
                  color="success"
                  @click.stop="resolveTicket(item)"
                  :disabled="item.status === 'resolved'"
                ></v-btn>
              </div>
            </template>
          </v-data-table>
        </div>
      </v-card>
    </div>

    <!-- Dialog de Criação/Edição de Chamado -->
    <v-dialog v-model="showCreateDialog" max-width="800">
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-ticket-plus" class="mr-3"></v-icon>
          {{ editingTicket ? 'Editar Chamado' : 'Novo Chamado' }}
        </v-card-title>
        
        <v-card-text>
          <v-form ref="ticketForm" v-model="formValid">
            <v-row>
              <v-col cols="12" md="6">
                <v-text-field
                  v-model="ticketForm.title"
                  label="Título do Chamado"
                  variant="outlined"
                  :rules="[v => !!v || 'Título é obrigatório']"
                  required
                ></v-text-field>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="ticketForm.priority"
                  :items="priorityOptions"
                  label="Prioridade"
                  variant="outlined"
                  :rules="[v => !!v || 'Prioridade é obrigatória']"
                  required
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="ticketForm.category"
                  :items="categoryOptions"
                  label="Categoria"
                  variant="outlined"
                  :rules="[v => !!v || 'Categoria é obrigatória']"
                  required
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="ticketForm.machine_id"
                  :items="machineOptions"
                  label="Máquina Relacionada"
                  variant="outlined"
                  clearable
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="ticketForm.assignee"
                  :items="assigneeOptions"
                  label="Responsável"
                  variant="outlined"
                  clearable
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="ticketForm.status"
                  :items="statusOptions"
                  label="Status"
                  variant="outlined"
                  :rules="[v => !!v || 'Status é obrigatório']"
                  required
                ></v-select>
              </v-col>
              
              <v-col cols="12">
                <v-textarea
                  v-model="ticketForm.description"
                  label="Descrição do Problema"
                  variant="outlined"
                  rows="4"
                  :rules="[v => !!v || 'Descrição é obrigatória']"
                  required
                ></v-textarea>
              </v-col>
              
              <v-col cols="12" v-if="editingTicket">
                <v-textarea
                  v-model="ticketForm.resolution"
                  label="Resolução (opcional)"
                  variant="outlined"
                  rows="3"
                ></v-textarea>
              </v-col>
            </v-row>
          </v-form>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="closeCreateDialog"
          >
            Cancelar
          </v-btn>
          <v-btn
            color="primary"
            variant="flat"
            @click="saveTicket"
            :disabled="!formValid"
            :loading="isSaving"
          >
            {{ editingTicket ? 'Atualizar' : 'Criar' }} Chamado
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Dialog de Detalhes do Chamado -->
    <v-dialog v-model="showDetailsDialog" max-width="900">
      <v-card v-if="selectedTicket">
        <v-card-title class="d-flex align-center">
          <v-icon icon="mdi-ticket-confirmation" class="mr-3"></v-icon>
          Chamado #{{ String(selectedTicket.id).padStart(4, '0') }}
          <v-spacer></v-spacer>
          <v-chip
            :color="getStatusColor(selectedTicket.status)"
            size="small"
            variant="flat"
          >
            {{ getStatusLabel(selectedTicket.status) }}
          </v-chip>
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <v-col cols="12" md="8">
              <h4 class="text-subtitle-1 mb-3">{{ selectedTicket.title }}</h4>
              <p class="text-body-1 mb-4">{{ selectedTicket.description }}</p>
              
              <div v-if="selectedTicket.resolution" class="resolution-section">
                <h4 class="text-subtitle-1 mb-2">Resolução</h4>
                <p class="text-body-2">{{ selectedTicket.resolution }}</p>
              </div>
            </v-col>
            
            <v-col cols="12" md="4">
              <div class="ticket-metadata">
                <div class="metadata-item mb-3">
                  <span class="metadata-label">Prioridade:</span>
                  <v-chip
                    :color="getPriorityColor(selectedTicket.priority)"
                    size="small"
                    variant="flat"
                    class="ml-2"
                  >
                    {{ selectedTicket.priority }}
                  </v-chip>
                </div>
                
                <div class="metadata-item mb-3">
                  <span class="metadata-label">Categoria:</span>
                  <v-chip
                    size="small"
                    variant="outlined"
                    :color="getCategoryColor(selectedTicket.category)"
                    class="ml-2"
                  >
                    {{ selectedTicket.category }}
                  </v-chip>
                </div>
                
                <div class="metadata-item mb-3" v-if="selectedTicket.machine_hostname">
                  <span class="metadata-label">Máquina:</span>
                  <div class="ml-2">
                    <div class="font-weight-medium">{{ selectedTicket.machine_hostname }}</div>
                    <div class="text-caption text-medium-emphasis">{{ selectedTicket.machine_ip }}</div>
                  </div>
                </div>
                
                <div class="metadata-item mb-3">
                  <span class="metadata-label">Responsável:</span>
                  <span class="ml-2">{{ selectedTicket.assignee || 'Não atribuído' }}</span>
                </div>
                
                <div class="metadata-item mb-3">
                  <span class="metadata-label">Criado em:</span>
                  <span class="ml-2">{{ formatDate(selectedTicket.created_at) }}</span>
                </div>
                
                <div class="metadata-item mb-3" v-if="selectedTicket.updated_at">
                  <span class="metadata-label">Atualizado em:</span>
                  <span class="ml-2">{{ formatDate(selectedTicket.updated_at) }}</span>
                </div>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-btn
            variant="outlined"
            @click="editTicket(selectedTicket)"
          >
            <v-icon icon="mdi-pencil" class="mr-1"></v-icon>
            Editar
          </v-btn>
          
          <v-btn
            variant="outlined"
            color="info"
            @click="assignTicket(selectedTicket)"
            :disabled="selectedTicket.status === 'resolved'"
          >
            <v-icon icon="mdi-account-plus" class="mr-1"></v-icon>
            Atribuir
          </v-btn>
          
          <v-btn
            variant="outlined"
            color="success"
            @click="resolveTicket(selectedTicket)"
            :disabled="selectedTicket.status === 'resolved'"
          >
            <v-icon icon="mdi-check" class="mr-1"></v-icon>
            Resolver
          </v-btn>
          
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="showDetailsDialog = false"
          >
            Fechar
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
import { ticketsAPI, machineMonitoringAPI } from '@/services/api'

// Reactive data
const tickets = ref([])
const filteredTickets = ref([])
const machines = ref([])
const searchQuery = ref('')
const statusFilter = ref(null)
const priorityFilter = ref(null)
const categoryFilter = ref(null)
const assigneeFilter = ref(null)
const isRefreshing = ref(false)
const isSaving = ref(false)
const showCreateDialog = ref(false)
const showDetailsDialog = ref(false)
const selectedTicket = ref(null)
const editingTicket = ref(false)
const formValid = ref(false)

// Form data
const ticketForm = ref({
  title: '',
  description: '',
  priority: '',
  category: '',
  status: 'open',
  machine_id: null,
  assignee: '',
  resolution: ''
})

// Notification system
const showNotification = ref(false)
const notificationMessage = ref('')
const notificationColor = ref('success')

// Table configuration
const tableHeaders = [
  { title: 'ID', key: 'id', sortable: true, width: '80px' },
  { title: 'Título', key: 'title', sortable: true },
  { title: 'Prioridade', key: 'priority', sortable: true },
  { title: 'Status', key: 'status', sortable: true },
  { title: 'Máquina', key: 'machine', sortable: false },
  { title: 'Categoria', key: 'category', sortable: true },
  { title: 'Responsável', key: 'assignee', sortable: true },
  { title: 'Criado em', key: 'created_at', sortable: true },
  { title: 'Ações', key: 'actions', sortable: false }
]

// Filter options
const statusOptions = [
  { title: 'Aberto', value: 'open' },
  { title: 'Em Andamento', value: 'in_progress' },
  { title: 'Aguardando', value: 'waiting' },
  { title: 'Resolvido', value: 'resolved' },
  { title: 'Fechado', value: 'closed' }
]

const priorityOptions = [
  { title: 'Baixa', value: 'low' },
  { title: 'Média', value: 'medium' },
  { title: 'Alta', value: 'high' },
  { title: 'Crítica', value: 'critical' }
]

const categoryOptions = [
  { title: 'Hardware', value: 'hardware' },
  { title: 'Software', value: 'software' },
  { title: 'Rede', value: 'network' },
  { title: 'Performance', value: 'performance' },
  { title: 'Segurança', value: 'security' },
  { title: 'Backup', value: 'backup' },
  { title: 'Outro', value: 'other' }
]

const assigneeOptions = [
  { title: 'João Silva', value: 'joao.silva' },
  { title: 'Maria Santos', value: 'maria.santos' },
  { title: 'Pedro Costa', value: 'pedro.costa' },
  { title: 'Ana Oliveira', value: 'ana.oliveira' }
]

// Computed properties
const totalTickets = computed(() => tickets.value.length)

const openTickets = computed(() => {
  return tickets.value.filter(t => t.status === 'open').length
})

const inProgressTickets = computed(() => {
  return tickets.value.filter(t => t.status === 'in_progress').length
})

const resolvedTickets = computed(() => {
  return tickets.value.filter(t => t.status === 'resolved').length
})

const hasActiveFilters = computed(() => {
  return searchQuery.value || statusFilter.value || priorityFilter.value || 
         categoryFilter.value || assigneeFilter.value
})

const machineOptions = computed(() => {
  return machines.value.map(machine => ({
    title: `${machine.hostname} (${machine.ip_address})`,
    value: machine.id
  }))
})

// Métodos
const transformMachinesFromBackend = (list = []) => list.map(m => ({
  id: m.id ?? m.machine_id ?? m.uuid ?? m._id ?? m.identifier ?? m.name,
  hostname: m.hostname ?? m.name ?? m.machine_id ?? `machine-${m.id ?? m.machine_id ?? Math.random().toString(36).slice(2, 8)}`,
  ip_address: m.ip_address ?? m.ip ?? m.last_known_ip ?? m.address ?? '0.0.0.0',
}))

const loadTickets = async () => {
  try {
    const response = await ticketsAPI.getAll()
    tickets.value = response.data
  } catch (error) {
    logger.error('Error loading tickets:', error)
    // Dados simulados para demonstração
    tickets.value = generateMockTickets()
  }
  filterTickets()
}

const loadMachines = async () => {
  try {
    const response = await machineMonitoringAPI.getMachines()
    const backendMachines = Array.isArray(response.data?.machines)
      ? response.data.machines
      : Array.isArray(response.data)
        ? response.data
        : []
    machines.value = transformMachinesFromBackend(backendMachines)
  } catch (error) {
    logger.error('Error loading machines:', error)
    // Dados simulados para demonstração
    machines.value = generateMockMachines()
  }
}

const generateMockTickets = () => {
  return [
    {
      id: 1,
      title: 'Alto uso de CPU na máquina DESKTOP-001',
      description: 'A máquina DESKTOP-001 está apresentando uso de CPU acima de 90% por mais de 30 minutos. Processo "chrome.exe" consumindo recursos excessivos.',
      priority: 'high',
      status: 'open',
      category: 'performance',
      machine_id: 1,
      machine_hostname: 'DESKTOP-001',
      machine_ip: '192.168.1.100',
      assignee: 'joao.silva',
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(),
      resolution: null
    },
    {
      id: 2,
      title: 'Disco com pouco espaço no servidor',
      description: 'O servidor SERVER-001 está com apenas 5% de espaço livre no disco C:. Necessário limpeza ou expansão.',
      priority: 'critical',
      status: 'in_progress',
      category: 'hardware',
      machine_id: 3,
      machine_hostname: 'SERVER-001',
      machine_ip: '192.168.1.10',
      assignee: 'maria.santos',
      created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
      resolution: null
    },
    {
      id: 3,
      title: 'Falha na conexão de rede',
      description: 'DESKTOP-002 perdeu conectividade com a rede. Cabo de rede pode estar danificado.',
      priority: 'medium',
      status: 'resolved',
      category: 'network',
      machine_id: 2,
      machine_hostname: 'DESKTOP-002',
      machine_ip: '192.168.1.101',
      assignee: 'pedro.costa',
      created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
      resolution: 'Cabo de rede substituído. Conectividade restaurada.'
    },
    {
      id: 4,
      title: 'Atualização de software pendente',
      description: 'Múltiplas atualizações de segurança pendentes no LAPTOP-001. Sistema pode estar vulnerável.',
      priority: 'medium',
      status: 'waiting',
      category: 'security',
      machine_id: 4,
      machine_hostname: 'LAPTOP-001',
      machine_ip: '192.168.1.150',
      assignee: 'ana.oliveira',
      created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
      resolution: null
    }
  ]
}

const generateMockMachines = () => {
  return [
    { id: 1, hostname: 'DESKTOP-001', ip_address: '192.168.1.100' },
    { id: 2, hostname: 'DESKTOP-002', ip_address: '192.168.1.101' },
    { id: 3, hostname: 'SERVER-001', ip_address: '192.168.1.10' },
    { id: 4, hostname: 'LAPTOP-001', ip_address: '192.168.1.150' }
  ]
}

const refreshTickets = async () => {
  isRefreshing.value = true
  try {
    await loadTickets()
    showSuccess('Chamados atualizados com sucesso')
  } catch (error) {
    showError('Erro ao atualizar chamados')
  } finally {
    isRefreshing.value = false
  }
}

const exportTickets = () => {
  const csvContent = generateCSV()
  downloadCSV(csvContent, 'chamados.csv')
  showSuccess('Chamados exportados com sucesso')
}

const generateCSV = () => {
  const headers = ['ID', 'Título', 'Prioridade', 'Status', 'Categoria', 'Máquina', 'Responsável', 'Criado em']
  const rows = tickets.value.map(ticket => [
    ticket.id,
    ticket.title,
    ticket.priority,
    getStatusLabel(ticket.status),
    ticket.category,
    ticket.machine_hostname || 'N/A',
    ticket.assignee || 'Não atribuído',
    formatDate(ticket.created_at)
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

const filterTickets = () => {
  let filtered = [...tickets.value]
  
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(ticket => 
      ticket.title.toLowerCase().includes(query) ||
      ticket.description.toLowerCase().includes(query) ||
      ticket.machine_hostname?.toLowerCase().includes(query)
    )
  }
  
  if (statusFilter.value) {
    filtered = filtered.filter(ticket => ticket.status === statusFilter.value)
  }
  
  if (priorityFilter.value) {
    filtered = filtered.filter(ticket => ticket.priority === priorityFilter.value)
  }
  
  if (categoryFilter.value) {
    filtered = filtered.filter(ticket => ticket.category === categoryFilter.value)
  }
  
  if (assigneeFilter.value) {
    filtered = filtered.filter(ticket => ticket.assignee === assigneeFilter.value)
  }
  
  filteredTickets.value = filtered
}

const clearFilters = () => {
  searchQuery.value = ''
  statusFilter.value = null
  priorityFilter.value = null
  categoryFilter.value = null
  assigneeFilter.value = null
  filterTickets()
}

const openCreateTicketDialog = () => {
  editingTicket.value = false
  resetTicketForm()
  showCreateDialog.value = true
}

const editTicket = (ticket) => {
  editingTicket.value = true
  ticketForm.value = { ...ticket }
  showDetailsDialog.value = false
  showCreateDialog.value = true
}

const closeCreateDialog = () => {
  showCreateDialog.value = false
  resetTicketForm()
}

const resetTicketForm = () => {
  ticketForm.value = {
    title: '',
    description: '',
    priority: '',
    category: '',
    status: 'open',
    machine_id: null,
    assignee: '',
    resolution: ''
  }
}

const saveTicket = async () => {
  isSaving.value = true
  try {
    if (editingTicket.value) {
      // Atualizar chamado existente
      const index = tickets.value.findIndex(t => t.id === ticketForm.value.id)
      if (index !== -1) {
        tickets.value[index] = {
          ...ticketForm.value,
          updated_at: new Date().toISOString()
        }
        showSuccess('Chamado atualizado com sucesso')
      }
    } else {
      // Criar novo chamado
      const newTicket = {
        ...ticketForm.value,
        id: Math.max(...tickets.value.map(t => t.id), 0) + 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
      
      // Adicionar informações da máquina se selecionada
      if (newTicket.machine_id) {
        const machine = machines.value.find(m => m.id === newTicket.machine_id)
        if (machine) {
          newTicket.machine_hostname = machine.hostname
          newTicket.machine_ip = machine.ip_address
        }
      }
      
      tickets.value.unshift(newTicket)
      showSuccess('Chamado criado com sucesso')
    }
    
    filterTickets()
    closeCreateDialog()
  } catch (error) {
    showError('Erro ao salvar chamado')
  } finally {
    isSaving.value = false
  }
}

const viewTicketDetails = (ticket) => {
  selectedTicket.value = ticket
  showDetailsDialog.value = true
}

const assignTicket = (ticket) => {
  // Implementar lógica de atribuição
  showInfo(`Funcionalidade de atribuição para chamado #${ticket.id} em desenvolvimento`)
}

const resolveTicket = (ticket) => {
  const index = tickets.value.findIndex(t => t.id === ticket.id)
  if (index !== -1) {
    tickets.value[index].status = 'resolved'
    tickets.value[index].updated_at = new Date().toISOString()
    filterTickets()
    showSuccess(`Chamado #${ticket.id} marcado como resolvido`)
  }
}

// Utility functions
const getStatusColor = (status) => {
  switch (status) {
    case 'open': return 'warning'
    case 'in_progress': return 'primary'
    case 'waiting': return 'info'
    case 'resolved': return 'success'
    case 'closed': return 'surface-variant'
    default: return 'surface-variant'
  }
}

const getStatusIcon = (status) => {
  switch (status) {
    case 'open': return 'mdi-clock-outline'
    case 'in_progress': return 'mdi-progress-clock'
    case 'waiting': return 'mdi-pause-circle'
    case 'resolved': return 'mdi-check-circle'
    case 'closed': return 'mdi-close-circle'
    default: return 'mdi-help-circle'
  }
}

const getStatusLabel = (status) => {
  switch (status) {
    case 'open': return 'Aberto'
    case 'in_progress': return 'Em Andamento'
    case 'waiting': return 'Aguardando'
    case 'resolved': return 'Resolvido'
    case 'closed': return 'Fechado'
    default: return status
  }
}

const getPriorityColor = (priority) => {
  switch (priority) {
    case 'low': return 'success'
    case 'medium': return 'warning'
    case 'high': return 'error'
    case 'critical': return 'purple'
    default: return 'surface-variant'
  }
}

const getPriorityIcon = (priority) => {
  switch (priority) {
    case 'low': return 'mdi-flag-outline'
    case 'medium': return 'mdi-flag'
    case 'high': return 'mdi-flag'
    case 'critical': return 'mdi-flag-variant'
    default: return 'mdi-flag-outline'
  }
}

const getCategoryColor = (category) => {
  switch (category) {
    case 'hardware': return 'blue'
    case 'software': return 'green'
    case 'network': return 'orange'
    case 'performance': return 'red'
    case 'security': return 'purple'
    case 'backup': return 'teal'
    default: return 'grey'
  }
}

const getCategoryIcon = (category) => {
  switch (category) {
    case 'hardware': return 'mdi-memory'
    case 'software': return 'mdi-application'
    case 'network': return 'mdi-network'
    case 'performance': return 'mdi-speedometer'
    case 'security': return 'mdi-shield'
    case 'backup': return 'mdi-backup-restore'
    default: return 'mdi-tag'
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const formatRelativeDate = (dateString) => {
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
  return `${diffDays} dias atrás`
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
  loadTickets()
  loadMachines()
})
</script>

<style scoped>
.ticketing-system {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.ticketing-header {
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

.ticketing-title {
  display: flex;
  align-items: center;
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 4px;
  color: rgb(var(--v-theme-on-background));
}

.ticketing-subtitle {
  color: rgb(var(--v-theme-on-background-variant));
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.ticketing-stats {
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

.ticket-id {
  font-family: monospace;
  font-weight: bold;
  color: rgb(var(--v-theme-primary));
}

.machine-info {
  display: flex;
  flex-direction: column;
}

.machine-name {
  font-weight: 500;
}

.machine-ip {
  font-size: 0.75rem;
  opacity: 0.7;
}

.assignee-info {
  display: flex;
  align-items: center;
}

.date-info {
  display: flex;
  flex-direction: column;
}

.date-value {
  font-size: 0.875rem;
}

.date-relative {
  font-size: 0.75rem;
  opacity: 0.7;
}

.action-buttons {
  display: flex;
  align-items: center;
}

.ticket-metadata {
  background: rgb(var(--v-theme-surface-variant));
  border-radius: 8px;
  padding: 16px;
}

.metadata-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.metadata-label {
  font-weight: 500;
  min-width: 100px;
  flex-shrink: 0;
}

.resolution-section {
  background: rgb(var(--v-theme-surface-variant));
  border-radius: 8px;
  padding: 16px;
  margin-top: 16px;
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
  
  .metadata-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .metadata-label {
    min-width: auto;
  }
}

/* Animações */
.ticketing-table {
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

/* Hover effects */
.ticketing-table :deep(.v-data-table__tr) {
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.ticketing-table :deep(.v-data-table__tr:hover) {
  background-color: rgb(var(--v-theme-surface-variant)) !important;
}
</style>