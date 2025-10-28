import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { useToast } from '@/composables/useToast'
import { useCacheInvalidation } from '@/composables/useCacheInvalidation'
import { cachedAPI, usersAPI } from '@/services/api'

export const useUsersStore = defineStore('users', () => {
  // Composables
  const { handleError } = useErrorHandler()
  const { showSuccess, showError } = useToast()
  const { 
    invalidateAfterCreate, 
    invalidateAfterUpdate, 
    invalidateAfterDelete,
    invalidateUsersCache 
  } = useCacheInvalidation()

  // Estado
  const users = ref([
    {
      id: 1,
      name: 'Administrador',
      email: 'admin@levitiis.com',
      username: 'admin',
      role: 'admin',
      department: 'TI',
      status: 'active',
      avatar: null,
      permissions: ['all'],
      createdAt: new Date('2024-01-01'),
      lastLogin: new Date(),
      phone: '(11) 99999-9999'
    },
    {
      id: 2,
      name: 'João Silva',
      email: 'joao.silva@levitiis.com',
      username: 'joao.silva',
      role: 'manager',
      department: 'Patrimônio',
      status: 'active',
      avatar: null,
      permissions: ['assets.read', 'assets.write', 'reports.read', 'inventory.read', 'inventory.write'],
      createdAt: new Date('2024-01-15'),
      lastLogin: new Date('2024-01-20'),
      phone: '(11) 98888-8888'
    },
    {
      id: 3,
      name: 'Maria Santos',
      email: 'maria.santos@levitiis.com',
      username: 'maria.santos',
      role: 'user',
      department: 'Financeiro',
      status: 'active',
      avatar: null,
      permissions: ['assets.read', 'reports.read'],
      createdAt: new Date('2024-01-20'),
      lastLogin: new Date('2024-01-19'),
      phone: '(11) 97777-7777'
    },
    {
      id: 4,
      name: 'Pedro Costa',
      email: 'pedro.costa@levitiis.com',
      username: 'pedro.costa',
      role: 'user',
      department: 'RH',
      status: 'inactive',
      avatar: null,
      permissions: ['assets.read'],
      createdAt: new Date('2024-01-10'),
      lastLogin: new Date('2024-01-15'),
      phone: '(11) 96666-6666'
    }
  ])

  const roles = ref([
    {
      id: 'admin',
      name: 'Administrador',
      description: 'Acesso total ao sistema',
      permissions: ['all'],
      color: '#dc2626'
    },
    {
      id: 'manager',
      name: 'Gerente',
      description: 'Acesso de gerenciamento',
      permissions: [
        'assets.read', 'assets.write', 'assets.delete',
        'inventory.read', 'inventory.write',
        'reports.read', 'reports.write',
        'audits.read', 'audits.write',
        'users.read'
      ],
      color: '#ea580c'
    },
    {
      id: 'user',
      name: 'Usuário',
      description: 'Acesso básico de leitura',
      permissions: ['assets.read', 'reports.read', 'inventory.read'],
      color: '#2563eb'
    },
    {
      id: 'auditor',
      name: 'Auditor',
      description: 'Acesso para auditoria',
      permissions: [
        'assets.read', 'inventory.read', 'inventory.write',
        'audits.read', 'audits.write', 'reports.read'
      ],
      color: '#7c3aed'
    }
  ])

  const departments = ref([
    'TI', 'Patrimônio', 'Financeiro', 'RH', 'Operações', 'Auditoria', 'Compras'
  ])

  const permissions = ref([
    { id: 'assets.read', name: 'Visualizar Ativos', category: 'Ativos' },
    { id: 'assets.write', name: 'Editar Ativos', category: 'Ativos' },
    { id: 'assets.delete', name: 'Excluir Ativos', category: 'Ativos' },
    { id: 'inventory.read', name: 'Visualizar Inventário', category: 'Inventário' },
    { id: 'inventory.write', name: 'Editar Inventário', category: 'Inventário' },
    { id: 'reports.read', name: 'Visualizar Relatórios', category: 'Relatórios' },
    { id: 'reports.write', name: 'Criar Relatórios', category: 'Relatórios' },
    { id: 'audits.read', name: 'Visualizar Auditorias', category: 'Auditorias' },
    { id: 'audits.write', name: 'Realizar Auditorias', category: 'Auditorias' },
    { id: 'users.read', name: 'Visualizar Usuários', category: 'Usuários' },
    { id: 'users.write', name: 'Gerenciar Usuários', category: 'Usuários' },
    { id: 'settings.read', name: 'Visualizar Configurações', category: 'Sistema' },
    { id: 'settings.write', name: 'Alterar Configurações', category: 'Sistema' },
    { id: 'all', name: 'Acesso Total', category: 'Sistema' }
  ])

  // Getters
  const activeUsers = computed(() => users.value.filter(user => user.status === 'active'))
  const inactiveUsers = computed(() => users.value.filter(user => user.status === 'inactive'))
  const usersByRole = computed(() => {
    const grouped = {}
    roles.value.forEach(role => {
      grouped[role.id] = users.value.filter(user => user.role === role.id)
    })
    return grouped
  })

  // Actions
  async function fetchUsers(params = {}, useCache = true) {
    try {
      if (useCache) {
        const response = await cachedAPI.users.getAll(params)
        users.value = response.data.items || response.data
      } else {
        const response = await usersAPI.getAll(params)
        users.value = response.data.items || response.data
      }
      return users.value
    } catch (error) {
      handleError(error, 'Erro ao carregar usuários')
      throw error
    }
  }

  async function fetchUserById(userId, useCache = true) {
    try {
      if (useCache) {
        const response = await cachedAPI.users.getById(userId)
        return response.data
      } else {
        const response = await usersAPI.getById(userId)
        return response.data
      }
    } catch (error) {
      handleError(error, 'Erro ao carregar usuário')
      throw error
    }
  }

  async function addUser(userData) {
    try {
      const response = await usersAPI.create(userData)
      const newUser = response.data
      
      // Atualizar estado local
      users.value.push(newUser)
      
      // Invalidar cache
      invalidateAfterCreate('user', newUser)
      
      showSuccess(`Usuário ${newUser.name} criado com sucesso`)
      return newUser
    } catch (error) {
      handleError(error, 'Erro ao criar usuário')
      throw error
    }
  }

  async function updateUser(userId, userData) {
    try {
      const response = await usersAPI.update(userId, userData)
      const updatedUser = response.data
      
      // Atualizar estado local
      const index = users.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        users.value[index] = { ...users.value[index], ...updatedUser }
      }
      
      // Invalidar cache
      invalidateAfterUpdate('user', userId)
      
      showSuccess(`Usuário ${updatedUser.name} atualizado com sucesso`)
      return updatedUser
    } catch (error) {
      handleError(error, 'Erro ao atualizar usuário')
      throw error
    }
  }

  async function deleteUser(userId) {
    try {
      const userToDelete = users.value.find(user => user.id === userId)
      if (!userToDelete) {
        showError('Usuário não encontrado')
        return false
      }
      
      await usersAPI.delete(userId)
      
      // Atualizar estado local
      const index = users.value.findIndex(user => user.id === userId)
      if (index !== -1) {
        users.value.splice(index, 1)
      }
      
      // Invalidar cache
      invalidateAfterDelete('user', userId)
      
      showSuccess(`Usuário ${userToDelete.name} removido com sucesso`)
      return true
    } catch (error) {
      handleError(error, 'Erro ao remover usuário')
      throw error
    }
  }

  function getUserById(userId) {
    return users.value.find(user => user.id === userId)
  }

  function getUsersByDepartment(department) {
    return users.value.filter(user => user.department === department)
  }

  function toggleUserStatus(userId) {
    const user = getUserById(userId)
    if (user) {
      user.status = user.status === 'active' ? 'inactive' : 'active'
      return user
    }
    return null
  }

  function getRoleById(roleId) {
    return roles.value.find(role => role.id === roleId)
  }

  function updateUserLastLogin(userId) {
    const user = getUserById(userId)
    if (user) {
      user.lastLogin = new Date()
    }
  }

  function hasPermission(userId, permission) {
    const user = getUserById(userId)
    if (!user) return false
    
    if (user.permissions.includes('all')) return true
    return user.permissions.includes(permission)
  }

  function getUserPermissions(userId) {
    const user = getUserById(userId)
    if (!user) return []
    
    if (user.permissions.includes('all')) {
      return permissions.value.map(p => p.id)
    }
    
    return user.permissions
  }

  function resetUserPassword(userId, newPassword) {
    const user = getUserById(userId)
    if (user) {
      // Em um sistema real, isso seria enviado para o backend
      // Aqui apenas simulamos a atualização
      user.passwordResetAt = new Date()
      user.temporaryPassword = true
      return true
    }
    return false
  }

  return {
    // Estado
    users,
    roles,
    departments,
    permissions,
    
    // Getters
    activeUsers,
    inactiveUsers,
    usersByRole,
    
    // Actions
    addUser,
    updateUser,
    deleteUser,
    getUserById,
    getUsersByDepartment,
    toggleUserStatus,
    getRoleById,
    updateUserLastLogin,
    hasPermission,
    getUserPermissions,
    resetUserPassword
  }
})