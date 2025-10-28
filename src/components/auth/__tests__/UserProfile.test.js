import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { createVuetify } from 'vuetify'
import UserProfile from '../UserProfile.vue'
import { createMockAuthStore, createMockRouter } from '@/test/utils'

// Mock do store de autenticação
const mockAuthStore = createMockAuthStore({
  user: {
    id: 1,
    name: 'João Silva',
    email: 'joao@example.com',
    role: 'admin'
  },
  isAuthenticated: true,
  permissions: ['system.configure'],
  userName: 'João Silva',
  userRole: 'admin',
  userInitials: 'JS'
})

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

// Mock do composable useAuth
vi.mock('@/composables/useAuth', () => ({
  useAuth: () => ({
    changePassword: vi.fn(),
    logout: vi.fn()
  })
}))

// Mock do ProtectedComponent
vi.mock('../ProtectedComponent.vue', () => ({
  default: {
    name: 'ProtectedComponent',
    template: '<div><slot /></div>',
    props: ['permission', 'showFallback']
  }
}))

describe('UserProfile', () => {
  let vuetify

  beforeEach(() => {
    vuetify = createVuetify()
    vi.clearAllMocks()
  })

  const mountComponent = (options = {}) => {
    return mount(UserProfile, {
      global: {
        plugins: [vuetify],
        mocks: {
          $router: createMockRouter()
        }
      },
      ...options
    })
  }

  it('deve renderizar o componente', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('deve exibir informações do usuário', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('João Silva')
    expect(wrapper.text()).toContain('joao@example.com')
  })

  it('deve ter métodos de navegação', () => {
    const wrapper = mountComponent()
    expect(wrapper.vm.goToProfile).toBeDefined()
    expect(wrapper.vm.openChangePassword).toBeDefined()
    expect(wrapper.vm.handleLogout).toBeDefined()
  })

  it('deve gerenciar estado do modal de alteração de senha', () => {
    const wrapper = mountComponent()
    
    // Estado inicial
    expect(wrapper.vm.showChangePassword).toBe(false)
    
    // Abrir modal
    wrapper.vm.openChangePassword()
    expect(wrapper.vm.showChangePassword).toBe(true)
    
    // Fechar modal
    wrapper.vm.closeChangePassword()
    expect(wrapper.vm.showChangePassword).toBe(false)
  })
})