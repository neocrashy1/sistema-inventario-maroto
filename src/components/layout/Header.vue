<template>
  <header class="header">
    <div class="header-left">
      <!-- Mobile menu toggle -->
      <button 
        class="mobile-menu-toggle"
        @click="$emit('toggle-mobile-menu')"
      >
        <i class="fas fa-bars"></i>
      </button>
      
      <!-- Desktop sidebar toggle -->
      <button 
        class="sidebar-toggle"
        @click="$emit('toggle-sidebar')"
      >
        <i class="fas fa-bars"></i>
      </button>
      
      <h1 class="page-title">{{ $route.meta.title || 'Dashboard' }}</h1>
    </div>
    
    <div class="header-right">
      <!-- Search -->
      <div class="search-box">
        <i class="fas fa-search"></i>
        <input 
          type="text" 
          placeholder="Buscar ativos, funcionários..."
          v-model="searchQuery"
          @keyup.enter="performSearch"
        >
      </div>
      
      <!-- Notifications -->
      <NotificationCenter />
      
      <!-- User Profile -->
      <UserProfile />
    </div>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationsStore } from '@/stores/notifications'
import NotificationCenter from '@/components/common/NotificationCenter.vue'
import UserProfile from '@/components/auth/UserProfile.vue'

defineProps({
  sidebarCollapsed: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle-sidebar', 'toggle-mobile-menu'])

const router = useRouter()
const authStore = useAuthStore()
const notificationsStore = useNotificationsStore()

// State
const searchQuery = ref('')

// Methods
const performSearch = () => {
  if (searchQuery.value.trim()) {
    // Determina a página de destino baseada no termo de busca
    const query = searchQuery.value.toLowerCase().trim()
    
    // Se contém palavras relacionadas a usuários
    if (query.includes('usuário') || query.includes('usuario') || query.includes('user') || 
        query.includes('funcionário') || query.includes('funcionario') || query.includes('employee')) {
      router.push({
        name: 'Users',
        query: { search: searchQuery.value }
      })
    }
    // Se contém palavras relacionadas a empréstimos
    else if (query.includes('empréstimo') || query.includes('emprestimo') || query.includes('loan') ||
             query.includes('terceiro') || query.includes('terceiros')) {
      router.push({
        name: 'EmployeeLoans',
        query: { search: searchQuery.value }
      })
    }
    // Se contém palavras relacionadas a auditoria
    else if (query.includes('auditoria') || query.includes('audit') || query.includes('inventário') || 
             query.includes('inventario') || query.includes('inventory')) {
      router.push({
        name: 'Audits',
        query: { search: searchQuery.value }
      })
    }
    // Por padrão, busca em ativos
    else {
      router.push({
        name: 'Assets',
        query: { search: searchQuery.value }
      })
    }
    
    // Limpa o campo de busca após a pesquisa
    searchQuery.value = ''
  }
}

const markAllAsRead = () => {
  notificationsStore.markAllAsRead()
}

const formatTime = (time) => {
  const date = typeof time === 'string' ? new Date(time) : time
  return formatDistanceToNow(date, { 
    addSuffix: true, 
    locale: ptBR 
  })
}

const closeDropdowns = (event) => {
  if (!event.target.closest('.notification-dropdown')) {
    showNotifications.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', closeDropdowns)
  
  // Inicializa o sistema de notificações
  notificationsStore.loadInitialNotifications()
  notificationsStore.connectToNotifications()
  notificationsStore.requestNotificationPermission()
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdowns)
  notificationsStore.disconnectFromNotifications()
})
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-lg);
  height: 64px;
  background-color: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.mobile-menu-toggle {
  display: none;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.mobile-menu-toggle:hover {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
}

.sidebar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.sidebar-toggle:hover {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
}

.page-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-box i {
  position: absolute;
  left: var(--spacing-md);
  color: var(--text-muted);
}

.search-box input {
  width: 300px;
  padding: var(--spacing-sm) var(--spacing-md) var(--spacing-sm) 2.5rem;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  background-color: var(--bg-secondary);
  transition: all 0.2s ease;
}

.search-box input:focus {
  outline: none;
  border-color: var(--primary-color);
  background-color: var(--bg-primary);
}

.notification-dropdown,
.user-dropdown {
  position: relative;
}

.notification-btn,
.user-btn {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm);
  border: none;
  background: none;
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all 0.2s ease;
}

.notification-btn:hover,
.user-btn:hover {
  background-color: var(--bg-tertiary);
}

.notification-btn {
  position: relative;
  width: 40px;
  height: 40px;
  justify-content: center;
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: var(--danger-color);
  color: white;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}



.notification-panel {
  position: absolute;
  top: 100%;
  right: 0;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  min-width: 300px;
}

.notification-panel {
  width: 400px;
}

.notification-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-color);
}

.notification-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
}

.mark-all-read {
  background: none;
  border: none;
  color: var(--primary-color);
  font-size: 0.875rem;
  cursor: pointer;
}

.notification-list {
  max-height: 400px;
  overflow-y: auto;
}

.notification-item {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--border-light);
  transition: background-color 0.2s ease;
}

.notification-item:hover {
  background-color: var(--bg-secondary);
}

.notification-item.unread {
  background-color: rgba(59, 130, 246, 0.05);
}

.notification-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: var(--bg-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.notification-content {
  flex: 1;
}

.notification-title {
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
  font-size: 0.875rem;
}

.notification-message {
  color: var(--text-secondary);
  margin: 0 0 var(--spacing-xs) 0;
  font-size: 0.875rem;
}

.notification-time {
  color: var(--text-muted);
  font-size: 0.75rem;
}



@media (max-width: 992px) {
  .mobile-menu-toggle {
    display: flex;
  }
  
  .sidebar-toggle {
    display: none;
  }
}

@media (max-width: 768px) {
  .search-box {
    display: none;
  }
  
  .header {
    padding: 0 var(--spacing-md);
  }
  
  .page-title {
    font-size: 1.25rem;
  }
  
  .header-right {
    gap: var(--spacing-sm);
  }
  
  .notification-panel {
    width: 320px;
    right: -20px;
  }
}
</style>