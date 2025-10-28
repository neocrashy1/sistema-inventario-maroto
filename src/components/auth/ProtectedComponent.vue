<template>
  <div v-if="hasAccess" class="protected-component">
    <slot />
  </div>
  <div v-else-if="showFallback" class="access-denied">
    <slot name="fallback">
      <div class="access-denied-content">
        <v-icon size="48" color="warning">mdi-lock</v-icon>
        <h3>Acesso Restrito</h3>
        <p>{{ fallbackMessage }}</p>
      </div>
    </slot>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  // Permissão específica requerida
  permission: {
    type: String,
    default: null
  },
  
  // Role requerida
  role: {
    type: String,
    default: null
  },
  
  // Módulo requerido
  module: {
    type: String,
    default: null
  },
  
  // Múltiplas permissões (todas devem ser atendidas)
  permissions: {
    type: Array,
    default: () => []
  },
  
  // Múltiplas roles (pelo menos uma deve ser atendida)
  roles: {
    type: Array,
    default: () => []
  },
  
  // Se deve mostrar fallback quando não tem acesso
  showFallback: {
    type: Boolean,
    default: false
  },
  
  // Mensagem personalizada para fallback
  fallbackMessage: {
    type: String,
    default: 'Você não tem permissão para acessar este conteúdo.'
  }
})

const authStore = useAuthStore()

const hasAccess = computed(() => {
  // Se não está autenticado, não tem acesso
  if (!authStore.isAuthenticated) {
    return false
  }
  
  // Verificar permissão específica
  if (props.permission && !authStore.hasPermission(props.permission)) {
    return false
  }
  
  // Verificar role específica
  if (props.role && !authStore.hasRole(props.role)) {
    return false
  }
  
  // Verificar módulo específico
  if (props.module && !authStore.canAccessModule(props.module)) {
    return false
  }
  
  // Verificar múltiplas permissões (todas devem ser atendidas)
  if (props.permissions.length > 0) {
    const hasAllPermissions = props.permissions.every(permission => 
      authStore.checkPermission(permission)
    )
    if (!hasAllPermissions) {
      return false
    }
  }
  
  // Verificar múltiplas roles (pelo menos uma deve ser atendida)
  if (props.roles.length > 0) {
    const hasAnyRole = props.roles.some(role => 
      authStore.hasRole(role)
    )
    if (!hasAnyRole) {
      return false
    }
  }
  
  return true
})
</script>

<style scoped>
.protected-component {
  width: 100%;
}

.access-denied {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
}

.access-denied-content {
  text-align: center;
  color: var(--text-muted);
}

.access-denied-content h3 {
  margin: var(--spacing-md) 0 var(--spacing-sm) 0;
  color: var(--text-secondary);
}

.access-denied-content p {
  margin: 0;
  font-size: 0.875rem;
}
</style>