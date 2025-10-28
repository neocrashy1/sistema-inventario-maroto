<template>
  <aside 
    class="sidebar" 
    :class="{ collapsed: isCollapsed, 'mobile-open': mobileOpen }"
    role="navigation"
    :aria-label="isCollapsed ? 'Menu principal (recolhido)' : 'Menu principal'"
    :aria-expanded="!isCollapsed"
  >
    <header class="sidebar-header">
      <router-link 
        to="/" 
        class="logo" 
        @click="closeMobileMenu"
        aria-label="Ir para página inicial - Levitiis AMS"
        @keydown.enter="closeMobileMenu"
        @keydown.space.prevent="closeMobileMenu"
      >
        <i class="fas fa-cube" aria-hidden="true"></i>
        <span v-show="!isCollapsed">Sistema Inventario Levitiis</span>
      </router-link>
      
      <!-- Mobile close button -->
      <button 
        class="mobile-close-btn"
        @click="$emit('close-mobile')"
        aria-label="Fechar menu de navegação"
        title="Fechar menu (Escape)"
        @keydown.enter="$emit('close-mobile')"
        @keydown.space.prevent="$emit('close-mobile')"
      >
        <i class="fas fa-times" aria-hidden="true"></i>
        <span class="sr-only">Fechar</span>
      </button>
    </header>
    
    <nav class="sidebar-nav" role="menubar" aria-orientation="vertical">
      <!-- Principal -->
      <section class="nav-section" role="group" aria-labelledby="principal-section">
        <h2 
          id="principal-section" 
          v-show="!isCollapsed" 
          class="nav-section-title"
        >
          Principal
        </h2>
        <router-link 
          to="/" 
          class="nav-item"
          :class="{ active: $route.name === 'Dashboard' }"
          @click="closeMobileMenu"
          role="menuitem"
          :aria-current="$route.name === 'Dashboard' ? 'page' : null"
          aria-label="Dashboard - Visão geral do sistema"
          @keydown.enter="closeMobileMenu"
          @keydown.space.prevent="closeMobileMenu"
        >
          <i class="fas fa-tachometer-alt" aria-hidden="true"></i>
          <span v-show="!isCollapsed">Dashboard</span>
        </router-link>
        
        <router-link 
          to="/assets" 
          class="nav-item"
          :class="{ active: $route.name === 'Assets' }"
          @click="closeMobileMenu"
          role="menuitem"
          :aria-current="$route.name === 'Assets' ? 'page' : null"
          aria-label="Ativos - Gerenciar equipamentos e recursos"
          @keydown.enter="closeMobileMenu"
          @keydown.space.prevent="closeMobileMenu"
        >
          <i class="fas fa-boxes" aria-hidden="true"></i>
          <span v-show="!isCollapsed">Ativos</span>
        </router-link>
        
        <router-link 
          to="/assets/network-discovery" 
          class="nav-item"
          :class="{ active: $route.name === 'NetworkDiscovery' }"
          @click="closeMobileMenu"
          role="menuitem"
          :aria-current="$route.name === 'NetworkDiscovery' ? 'page' : null"
          aria-label="Descoberta de Rede - Detectar dispositivos na rede"
          @keydown.enter="closeMobileMenu"
          @keydown.space.prevent="closeMobileMenu"
        >
          <i class="fas fa-network-wired" aria-hidden="true"></i>
          <span v-show="!isCollapsed">Descoberta de Rede</span>
        </router-link>
        
        <!-- Ocultado: Monitoramento (fora do escopo de inventário) -->
        <!--
        <router-link 
          to="/monitoring" 
          class="nav-item"
          :class="{ active: $route.name === 'Monitoring' }"
          @click="closeMobileMenu"
          role="menuitem"
          :aria-current="$route.name === 'Monitoring' ? 'page' : null"
          aria-label="Monitoramento - Monitorar máquinas Windows em tempo real"
          @keydown.enter="closeMobileMenu"
          @keydown.space.prevent="closeMobileMenu"
        >
          <i class="fas fa-desktop" aria-hidden="true"></i>
          <span v-show="!isCollapsed">Monitoramento</span>
        </router-link>
        -->
        
        <router-link 
          to="/movements" 
          class="nav-item"
          :class="{ active: $route.name === 'Movements' }"
          @click="closeMobileMenu"
          role="menuitem"
          :aria-current="$route.name === 'Movements' ? 'page' : null"
          aria-label="Movimentações - Histórico de transferências de ativos"
          @keydown.enter="closeMobileMenu"
          @keydown.space.prevent="closeMobileMenu"
        >
          <i class="fas fa-exchange-alt" aria-hidden="true"></i>
          <span v-show="!isCollapsed">Movimentações</span>
        </router-link>
        
        <router-link 
          to="/locations" 
          class="nav-item"
          :class="{ active: $route.name === 'Locations' }"
          @click="closeMobileMenu"
          role="menuitem"
          :aria-current="$route.name === 'Locations' ? 'page' : null"
          aria-label="Localizações - Gerenciar locais e departamentos"
          @keydown.enter="closeMobileMenu"
          @keydown.space.prevent="closeMobileMenu"
        >
          <i class="fas fa-map-marker-alt" aria-hidden="true"></i>
          <span v-show="!isCollapsed">Localizações</span>
        </router-link>
        
        <router-link 
          to="/analytics" 
          class="nav-item" 
          :class="{ active: $route.name === 'Analytics' }"
          @click="closeMobileMenu"
          role="menuitem"
          :aria-current="$route.name === 'Analytics' ? 'page' : null"
          aria-label="Analytics - Análises e métricas do sistema"
          @keydown.enter="closeMobileMenu"
          @keydown.space.prevent="closeMobileMenu"
        >
          <i class="fas fa-chart-bar" aria-hidden="true"></i>
          <span v-if="!isCollapsed">Analytics</span>
        </router-link>

        <router-link 
          to="/test" 
          class="nav-item" 
          :class="{ active: $route.name === 'TestFunctionalities' }"
          @click="closeMobileMenu"
          role="menuitem"
          :aria-current="$route.name === 'TestFunctionalities' ? 'page' : null"
          aria-label="Teste - Funcionalidades de teste do sistema"
          @keydown.enter="closeMobileMenu"
          @keydown.space.prevent="closeMobileMenu"
        >
          <i class="fas fa-flask" aria-hidden="true"></i>
          <span v-if="!isCollapsed">Teste</span>
        </router-link>
      </section>
      
      <!-- Empréstimos -->
      <section class="nav-section" role="group" aria-labelledby="loans-section">
        <h2 
          id="loans-section" 
          v-show="!isCollapsed" 
          class="nav-section-title"
        >
          Empréstimos
        </h2>
        <router-link 
          to="/employees" 
          class="nav-item"
          :class="{ active: $route.name === 'Employees' }"
          @click="closeMobileMenu"
          role="menuitem"
          :aria-current="$route.name === 'Employees' ? 'page' : null"
          aria-label="Funcionários - Gerenciar cadastro de funcionários"
          @keydown.enter="closeMobileMenu"
          @keydown.space.prevent="closeMobileMenu"
        >
          <i class="fas fa-users" aria-hidden="true"></i>
          <span v-show="!isCollapsed">Funcionários</span>
        </router-link>
        
        <router-link 
          to="/third-parties" 
          class="nav-item"
          :class="{ active: $route.name === 'ThirdParties' }"
          @click="closeMobileMenu"
          role="menuitem"
          :aria-current="$route.name === 'ThirdParties' ? 'page' : null"
          aria-label="Terceiros - Gerenciar cadastro de terceiros"
          @keydown.enter="closeMobileMenu"
          @keydown.space.prevent="closeMobileMenu"
        >
          <i class="fas fa-handshake" aria-hidden="true"></i>
          <span v-show="!isCollapsed">Terceiros</span>
        </router-link>
        
        <router-link 
          to="/loans/employees" 
          class="nav-item"
          :class="{ active: $route.name === 'EmployeeLoans' }"
          @click="closeMobileMenu"
          role="menuitem"
          :aria-current="$route.name === 'EmployeeLoans' ? 'page' : null"
          aria-label="Empréstimos - Gerenciar empréstimos para funcionários"
          @keydown.enter="closeMobileMenu"
          @keydown.space.prevent="closeMobileMenu"
        >
          <i class="fas fa-user-tie" aria-hidden="true"></i>
          <span v-show="!isCollapsed">Empréstimos</span>
        </router-link>
        
        <router-link 
          to="/loans/third-party" 
          class="nav-item"
          :class="{ active: $route.name === 'ThirdPartyLoans' }"
          @click="closeMobileMenu"
          role="menuitem"
          :aria-current="$route.name === 'ThirdPartyLoans' ? 'page' : null"
          aria-label="Empréstimos Terceiros - Gerenciar empréstimos para terceiros"
          @keydown.enter="closeMobileMenu"
          @keydown.space.prevent="closeMobileMenu"
        >
          <i class="fas fa-clipboard-list" aria-hidden="true"></i>
          <span v-show="!isCollapsed">Empréstimos Terceiros</span>
        </router-link>
      </section>
      
      <!-- Auditoria -->
      <div class="nav-section">
        <div v-show="!isCollapsed" class="nav-section-title">Auditoria</div>
        <router-link 
          to="/audits" 
          class="nav-item"
          :class="{ active: $route.name === 'Audits' }"
          @click="closeMobileMenu"
        >
          <i class="fas fa-search"></i>
          <span v-show="!isCollapsed">Auditorias</span>
        </router-link>
        
        <router-link 
          to="/audits/physical-inventory" 
          class="nav-item"
          :class="{ active: $route.name === 'PhysicalInventory' }"
          @click="closeMobileMenu"
        >
          <i class="fas fa-clipboard-list"></i>
          <span v-show="!isCollapsed">Inventário Físico</span>
        </router-link>
      </div>
      
      <!-- Manutenção -->
      <div class="nav-section">
        <div v-show="!isCollapsed" class="nav-section-title">Manutenção</div>
        <router-link 
          to="/maintenance/service-orders" 
          class="nav-item"
          :class="{ active: $route.name === 'ServiceOrders' }"
          @click="closeMobileMenu"
        >
          <i class="fas fa-tools"></i>
          <span v-show="!isCollapsed">Ordens de Serviço</span>
        </router-link>
        
        <router-link 
          to="/maintenance/schedules" 
          class="nav-item"
          :class="{ active: $route.name === 'Schedules' }"
          @click="closeMobileMenu"
        >
          <i class="fas fa-calendar-alt"></i>
          <span v-show="!isCollapsed">Agendamentos</span>
        </router-link>
        
        <router-link 
          to="/maintenance/sla-contracts" 
          class="nav-item"
          :class="{ active: $route.name === 'SLAContracts' }"
          @click="closeMobileMenu"
        >
          <i class="fas fa-file-contract"></i>
          <span v-show="!isCollapsed">SLA & Contratos</span>
        </router-link>
        
        <router-link 
          to="/purchases" 
          class="nav-item"
          :class="{ active: $route.name === 'Purchases' }"
          @click="closeMobileMenu"
          role="menuitem"
          :aria-current="$route.name === 'Purchases' ? 'page' : null"
          aria-label="Compras - Gerenciar orçamentos e pedidos"
          @keydown.enter="closeMobileMenu"
          @keydown.space.prevent="closeMobileMenu"
        >
          <i class="fas fa-shopping-cart" aria-hidden="true"></i>
          <span v-show="!isCollapsed">Compras</span>
        </router-link>
      </div>
      
      <!-- Relatórios -->
      <div class="nav-section">
        <div v-show="!isCollapsed" class="nav-section-title">Relatórios</div>
        <router-link 
          to="/reports" 
          class="nav-item"
          :class="{ active: $route.name === 'Reports' }"
          @click="closeMobileMenu"
        >
          <i class="fas fa-chart-bar"></i>
          <span v-show="!isCollapsed">Relatórios</span>
        </router-link>
        
        <router-link 
          to="/reports/analytics" 
          class="nav-item"
          :class="{ active: $route.name === 'ReportsAnalytics' }"
          @click="closeMobileMenu"
        >
          <i class="fas fa-chart-line"></i>
          <span v-show="!isCollapsed">Analytics</span>
        </router-link>
      </div>
      
      <!-- Administração -->
      <div v-if="authStore.canAccessModule('admin')" class="nav-section">
        <div v-show="!isCollapsed" class="nav-section-title">Administração</div>
        <router-link 
          to="/admin/users" 
          class="nav-item"
          :class="{ active: $route.name === 'Users' }"
          @click="closeMobileMenu"
        >
          <i class="fas fa-users"></i>
          <span v-show="!isCollapsed">Usuários</span>
        </router-link>
        
        <router-link 
          to="/admin/settings" 
          class="nav-item"
          :class="{ active: $route.name === 'Settings' }"
          @click="closeMobileMenu"
        >
          <i class="fas fa-cog"></i>
          <span v-show="!isCollapsed">Configurações</span>
        </router-link>
      </div>
    </nav>
  </aside>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useAccessibility } from '@/composables/useAccessibility'

defineProps({
  isCollapsed: {
    type: Boolean,
    default: false
  },
  mobileOpen: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['toggle', 'close-mobile'])

const authStore = useAuthStore()
const { announce } = useAccessibility()

// Method to close mobile menu
const closeMobileMenu = () => {
  emit('close-mobile')
}

// Keyboard navigation
const handleKeydown = (e) => {
  const sidebar = document.querySelector('.sidebar')
  if (!sidebar) return

  const menuItems = Array.from(sidebar.querySelectorAll('.nav-item'))
  const currentFocus = document.activeElement
  const currentIndex = menuItems.indexOf(currentFocus)

  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault()
      if (currentIndex < menuItems.length - 1) {
        menuItems[currentIndex + 1].focus()
      } else {
        menuItems[0].focus() // Loop to first
      }
      break

    case 'ArrowUp':
      e.preventDefault()
      if (currentIndex > 0) {
        menuItems[currentIndex - 1].focus()
      } else {
        menuItems[menuItems.length - 1].focus() // Loop to last
      }
      break

    case 'Home':
      e.preventDefault()
      if (menuItems.length > 0) {
        menuItems[0].focus()
      }
      break

    case 'End':
      e.preventDefault()
      if (menuItems.length > 0) {
        menuItems[menuItems.length - 1].focus()
      }
      break

    case 'Escape':
      e.preventDefault()
      if (document.querySelector('.sidebar.mobile-open')) {
        closeMobileMenu()
        announce('Menu fechado')
      }
      break
  }
}

// Focus management
const focusFirstMenuItem = () => {
  nextTick(() => {
    const firstMenuItem = document.querySelector('.sidebar .nav-item')
    if (firstMenuItem) {
      firstMenuItem.focus()
    }
  })
}

// Skip link functionality
const skipToContent = () => {
  const mainContent = document.querySelector('main') || document.querySelector('[role="main"]')
  if (mainContent) {
    mainContent.focus()
    mainContent.scrollIntoView({ behavior: 'smooth' })
    announce('Navegou para o conteúdo principal')
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
  
  // Add skip link if not exists
  if (!document.querySelector('.skip-link')) {
    const skipLink = document.createElement('a')
    skipLink.href = '#main-content'
    skipLink.className = 'skip-link'
    skipLink.textContent = 'Pular para o conteúdo principal'
    skipLink.addEventListener('click', (e) => {
      e.preventDefault()
      skipToContent()
    })
    document.body.insertBefore(skipLink, document.body.firstChild)
  }
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})

// Expose methods for parent components
defineExpose({
  focusFirstMenuItem,
  skipToContent
})
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 280px;
  background-color: var(--bg-dark);
  color: white;
  transition: width 0.3s ease;
  z-index: 1000;
  overflow-y: auto;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  padding: var(--spacing-lg);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  color: white;
  text-decoration: none;
  font-size: 1.25rem;
  font-weight: 700;
}

.logo i {
  font-size: 1.5rem;
  color: var(--primary-color);
}

.sidebar-nav {
  padding: var(--spacing-lg) 0;
}

.nav-section {
  margin-bottom: var(--spacing-xl);
}

.nav-section-title {
  padding: 0 var(--spacing-lg);
  margin-bottom: var(--spacing-md);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: rgba(255, 255, 255, 0.6);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  color: rgba(255, 255, 255, 0.8);
  text-decoration: none;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-item.active {
  background-color: rgba(59, 130, 246, 0.2);
  color: white;
  border-left-color: var(--primary-color);
}

.nav-item i {
  width: 20px;
  text-align: center;
  font-size: 1rem;
}

.collapsed .nav-item {
  justify-content: center;
  padding: var(--spacing-md);
}

.collapsed .nav-item span {
  display: none;
}

/* Scrollbar */
.sidebar::-webkit-scrollbar {
  width: 4px;
}

.sidebar::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
}

.sidebar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

/* Accessibility Improvements */
.nav-section-title {
  /* Screen reader only when collapsed */
}

.collapsed .nav-section-title {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.nav-item {
  position: relative;
}

.nav-item:focus {
  outline: 3px solid rgba(59, 130, 246, 0.6);
  outline-offset: -3px;
  background-color: rgba(255, 255, 255, 0.15);
}

.nav-item:focus-visible {
  outline: 3px solid var(--primary-color);
  outline-offset: -3px;
}

/* Mobile close button accessibility */
.mobile-close-btn {
  display: none;
  position: absolute;
  top: 50%;
  right: var(--spacing-lg);
  transform: translateY(-50%);
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mobile-close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.mobile-close-btn:focus {
  outline: 2px solid var(--primary-color);
  outline-offset: 2px;
  background: rgba(255, 255, 255, 0.2);
}

/* Skip link styles */
.skip-link {
  position: absolute;
  top: -40px;
  left: 6px;
  background: var(--primary-color);
  color: white;
  padding: 8px 16px;
  text-decoration: none;
  border-radius: 4px;
  z-index: 10001;
  font-weight: 600;
  transition: top 0.3s ease;
}

.skip-link:focus {
  top: 6px;
}

/* High contrast mode */
.high-contrast .sidebar {
  background-color: #000000;
  border-right: 2px solid #ffffff;
}

.high-contrast .nav-item {
  border-left: 3px solid transparent;
}

.high-contrast .nav-item:hover {
  background-color: #333333;
  color: #ffffff;
}

.high-contrast .nav-item.active {
  background-color: #0066cc;
  border-left-color: #00ffff;
}

.high-contrast .nav-item:focus {
  outline: 3px solid #00ffff;
  background-color: #333333;
}

/* Reduced motion */
.reduced-motion .nav-item,
.reduced-motion .sidebar {
  transition: none;
}

/* Mobile responsive */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  
  .sidebar.mobile-open {
    transform: translateX(0);
  }
  
  .mobile-close-btn {
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .sidebar-header {
    position: relative;
  }
}

/* Touch targets for mobile */
@media (max-width: 768px) {
  .nav-item {
    min-height: 48px;
    padding: var(--spacing-lg);
  }
  
  .mobile-close-btn {
    min-width: 44px;
    min-height: 44px;
  }
}

/* Print styles */
@media print {
  .sidebar {
    display: none;
  }
}
</style>