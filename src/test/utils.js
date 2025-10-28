import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createRouter, createWebHistory } from 'vue-router'
import { vi } from 'vitest'

// Mock das rotas para testes
const mockRoutes = [
  { path: '/', name: 'Home', component: { template: '<div>Home</div>' } },
  { path: '/login', name: 'Login', component: { template: '<div>Login</div>' } },
  { path: '/dashboard', name: 'Dashboard', component: { template: '<div>Dashboard</div>' } },
  { path: '/assets', name: 'Assets', component: { template: '<div>Assets</div>' } },
  { path: '/users', name: 'Users', component: { template: '<div>Users</div>' } },
]

/**
 * Cria um router mock para testes
 */
export function createMockRouter(routes = mockRoutes) {
  return createRouter({
    history: createWebHistory(),
    routes,
  })
}

/**
 * Cria uma instância do Pinia para testes
 */
export function createTestPinia() {
  const pinia = createPinia()
  setActivePinia(pinia)
  return pinia
}

/**
 * Monta um componente com todas as dependências necessárias
 */
export function mountComponent(component, options = {}) {
  const pinia = createTestPinia()
  const router = createMockRouter()
  
  const defaultOptions = {
    global: {
      plugins: [pinia, router],
      stubs: {
        'router-link': true,
        'router-view': true,
      },
    },
  }

  return mount(component, {
    ...defaultOptions,
    ...options,
    global: {
      ...defaultOptions.global,
      ...options.global,
    },
  })
}

/**
 * Mock do store de autenticação
 */
export function createMockAuthStore(overrides = {}) {
  return {
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: false,
    permissions: [],
    role: null,
    isBlocked: false,
    blockTimeRemaining: 0,
    userName: 'Usuário Teste',
    userRole: 'user',
    ...overrides,
    
    // Métodos
    login: vi.fn(),
    logout: vi.fn(),
    register: vi.fn(),
    checkAuth: vi.fn(),
    hasPermission: vi.fn(),
    hasRole: vi.fn(),
    canAccessModule: vi.fn(),
    updateProfile: vi.fn(),
    changePassword: vi.fn(),
    forgotPassword: vi.fn(),
    resetPassword: vi.fn(),
    initializeAuth: vi.fn(),
  }
}

/**
 * Mock do store de notificações
 */
export function createMockNotificationsStore(overrides = {}) {
  return {
    notifications: [],
    unreadCount: 0,
    ...overrides,
    
    // Métodos
    addNotification: vi.fn(),
    removeNotification: vi.fn(),
    markAsRead: vi.fn(),
    markAllAsRead: vi.fn(),
    loadNotifications: vi.fn(),
  }
}

/**
 * Mock do store de assets
 */
export function createMockAssetsStore(overrides = {}) {
  return {
    assets: [],
    totalAssets: 0,
    loading: false,
    filters: {},
    ...overrides,
    
    // Métodos
    fetchAssets: vi.fn(),
    createAsset: vi.fn(),
    updateAsset: vi.fn(),
    deleteAsset: vi.fn(),
    setFilters: vi.fn(),
  }
}

/**
 * Utilitário para aguardar próximo tick do Vue
 */
export async function nextTick() {
  return new Promise(resolve => setTimeout(resolve, 0))
}

/**
 * Utilitário para simular delay
 */
export function delay(ms = 100) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * Mock de resposta da API
 */
export function createMockApiResponse(data, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: vi.fn().mockResolvedValue(data),
    text: vi.fn().mockResolvedValue(JSON.stringify(data)),
  }
}

/**
 * Configuração padrão para mocks de fetch
 */
export function setupFetchMock() {
  global.fetch = vi.fn()
  return global.fetch
}