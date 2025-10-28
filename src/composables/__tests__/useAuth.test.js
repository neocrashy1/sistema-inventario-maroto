import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuth } from '../useAuth'
import { createMockAuthStore, createMockRouter } from '@/test/utils'

describe('useAuth', () => {
  let mockAuthStore
  let mockRouter

  beforeEach(() => {
    mockAuthStore = createMockAuthStore()
    mockRouter = createMockRouter()
    
    // Mock dos stores
    vi.doMock('@/stores/auth', () => ({
      useAuthStore: () => mockAuthStore
    }))
    
    vi.doMock('vue-router', () => ({
      useRouter: () => mockRouter
    }))
  })

  it('deve retornar as propriedades básicas', () => {
    const auth = useAuth()
    
    expect(auth).toBeDefined()
    expect(typeof auth.login).toBe('function')
    expect(typeof auth.logout).toBe('function')
    expect(typeof auth.register).toBe('function')
  })

  it('deve fazer login', async () => {
    mockAuthStore.login.mockResolvedValue({ success: true })
    
    const { login } = useAuth()
    const credentials = { email: 'test@example.com', password: 'password' }
    
    const result = await login(credentials)
    
    expect(mockAuthStore.login).toHaveBeenCalledWith(credentials)
    expect(result.success).toBe(true)
  })

  it('deve fazer logout', async () => {
    mockAuthStore.logout.mockResolvedValue()
    
    const { logout } = useAuth()
    
    await logout()
    
    expect(mockAuthStore.logout).toHaveBeenCalled()
  })

  it('deve verificar permissões', () => {
    mockAuthStore.hasPermission.mockReturnValue(true)
    
    const { hasPermission } = useAuth()
    
    expect(hasPermission('users.manage')).toBe(true)
    expect(mockAuthStore.hasPermission).toHaveBeenCalledWith('users.manage')
  })

  it('deve verificar roles', () => {
    mockAuthStore.hasRole.mockReturnValue(true)
    
    const { hasRole } = useAuth()
    
    expect(hasRole('admin')).toBe(true)
    expect(mockAuthStore.hasRole).toHaveBeenCalledWith('admin')
  })
})