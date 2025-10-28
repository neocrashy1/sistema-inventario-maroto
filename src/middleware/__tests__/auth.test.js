import { describe, it, expect, beforeEach, vi } from 'vitest'
import { authMiddleware } from '../auth'
import { createMockAuthStore } from '@/test/utils'

// Mock do store de autenticação
const mockAuthStore = createMockAuthStore()

vi.mock('@/stores/auth', () => ({
  useAuthStore: () => mockAuthStore
}))

describe('Auth Middleware', () => {
  let mockTo
  let mockFrom
  let mockNext

  beforeEach(() => {
    vi.clearAllMocks()

    mockTo = {
      path: '/dashboard',
      meta: {}
    }

    mockFrom = {
      path: '/'
    }

    mockNext = vi.fn()
  })

  it('deve permitir acesso a rotas públicas', () => {
    const to = { path: '/login', meta: { requiresAuth: false } }
    const from = { path: '/' }
    
    authMiddleware(to, from, mockNext)
    
    expect(mockNext).toHaveBeenCalledWith()
  })

  it('deve redirecionar usuários não autenticados', () => {
    mockAuthStore.isAuthenticated = false
    
    const to = { path: '/dashboard', meta: { requiresAuth: true } }
    const from = { path: '/' }
    
    authMiddleware(to, from, mockNext)
    
    expect(mockNext).toHaveBeenCalledWith('/login')
  })

  it('deve permitir acesso a usuários autenticados', () => {
    mockAuthStore.isAuthenticated = true
    
    const to = { path: '/dashboard', meta: { requiresAuth: true } }
    const from = { path: '/login' }
    
    authMiddleware(to, from, mockNext)
    
    expect(mockNext).toHaveBeenCalledWith()
  })

  it('deve verificar permissões quando necessário', () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.hasPermission.mockReturnValue(true)
    
    const to = { 
      path: '/users', 
      meta: { 
        requiresAuth: true,
        requiresPermission: 'users.manage'
      } 
    }
    const from = { path: '/dashboard' }
    
    authMiddleware(to, from, mockNext)
    
    expect(mockAuthStore.hasPermission).toHaveBeenCalledWith('users.manage')
    expect(mockNext).toHaveBeenCalledWith()
  })

  it('deve verificar roles quando necessário', () => {
    mockAuthStore.isAuthenticated = true
    mockAuthStore.hasRole.mockReturnValue(true)
    
    const to = { 
      path: '/admin', 
      meta: { 
        requiresAuth: true,
        requiresRole: 'admin'
      } 
    }
    const from = { path: '/dashboard' }
    
    authMiddleware(to, from, mockNext)
    
    expect(mockAuthStore.hasRole).toHaveBeenCalledWith('admin')
    expect(mockNext).toHaveBeenCalledWith()
  })
})