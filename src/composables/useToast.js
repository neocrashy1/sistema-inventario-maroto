import { ref, reactive } from 'vue'

/**
 * Sistema global de notificações toast
 */

// Estado global das notificações
const toasts = ref([])
let toastIdCounter = 0

// Tipos de notificação
export const TOAST_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
}

// Configurações padrão
const DEFAULT_CONFIG = {
  duration: 5000, // 5 segundos
  position: 'top-right',
  showCloseButton: true,
  pauseOnHover: true,
  maxToasts: 5
}

// Estrutura para deduplicação e rate limit de toasts
const recentToastHashes = new Map() // hash -> lastShownTimestamp
const TOAST_DEDUP_WINDOW_MS = 5000 // evita toasts idênticos em 5s
const TOAST_RATE_LIMIT_MS = 800 // evita tempestade de toasts sequenciais
let lastToastTimestamp = 0

function makeToastHash(message, type, options) {
  try {
    // Se houver dedupeKey, utilizar como base para deduplicação
    const base = options?.dedupeKey
      ? { key: String(options.dedupeKey), type }
      : { message, type }
    const key = JSON.stringify(base)
    return key
  } catch (_) {
    return `${type}:${message}`
  }
}

/**
 * Composable para gerenciar notificações toast
 */
export function useToast() {
  
  /**
   * Adiciona uma nova notificação com deduplicação e rate limit
   */
  function addToast(message, type = TOAST_TYPES.INFO, options = {}) {
    const now = Date.now()

    // Rate limit simples
    if (now - lastToastTimestamp < TOAST_RATE_LIMIT_MS) {
      return null
    }

    const config = { ...DEFAULT_CONFIG, ...options }
    const hash = makeToastHash(message, type, options)

    // Deduplicação por janela
    const lastShown = recentToastHashes.get(hash)
    if (lastShown && (now - lastShown) < TOAST_DEDUP_WINDOW_MS) {
      return null
    }
    recentToastHashes.set(hash, now)

    const toast = {
      id: ++toastIdCounter,
      message,
      type,
      ...config,
      createdAt: now,
      isVisible: true,
      isPaused: false,
      timeoutId: null
    }
    
    // Limitar número máximo de toasts
    if (toasts.value.length >= config.maxToasts) {
      removeToast(toasts.value[0].id)
    }
    
    toasts.value.push(toast)
    lastToastTimestamp = now
    
    // Auto-remover após duração especificada
    if (config.duration > 0) {
      toast.timeoutId = setTimeout(() => {
        removeToast(toast.id)
      }, config.duration)
    }
    
    return toast.id
  }
  
  /**
   * Remove uma notificação
   */
  function removeToast(id) {
    const index = toasts.value.findIndex(toast => toast.id === id)
    if (index > -1) {
      const toast = toasts.value[index]
      
      // Limpar timeout se existir
      if (toast.timeoutId) {
        clearTimeout(toast.timeoutId)
      }
      
      // Animação de saída
      toast.isVisible = false
      
      // Remover após animação
      setTimeout(() => {
        const currentIndex = toasts.value.findIndex(t => t.id === id)
        if (currentIndex > -1) {
          toasts.value.splice(currentIndex, 1)
        }
      }, 300) // Tempo da animação CSS
    }
  }
  
  /**
   * Pausa o timer de auto-remoção
   */
  function pauseToast(id) {
    const toast = toasts.value.find(t => t.id === id)
    if (toast && toast.timeoutId) {
      clearTimeout(toast.timeoutId)
      toast.isPaused = true
      toast.pausedAt = Date.now()
    }
  }
  
  /**
   * Resume o timer de auto-remoção
   */
  function resumeToast(id) {
    const toast = toasts.value.find(t => t.id === id)
    if (toast && toast.isPaused) {
      const remainingTime = toast.duration - (toast.pausedAt - toast.createdAt)
      
      if (remainingTime > 0) {
        toast.timeoutId = setTimeout(() => {
          removeToast(toast.id)
        }, remainingTime)
      } else {
        removeToast(toast.id)
      }
      
      toast.isPaused = false
      delete toast.pausedAt
    }
  }
  
  /**
   * Remove todas as notificações
   */
  function clearAllToasts() {
    toasts.value.forEach(toast => {
      if (toast.timeoutId) {
        clearTimeout(toast.timeoutId)
      }
    })
    toasts.value = []
  }
  
  /**
   * Métodos de conveniência para diferentes tipos
   */
  function success(message, options = {}) {
    return addToast(message, TOAST_TYPES.SUCCESS, {
      duration: 4000,
      ...options
    })
  }
  
  function error(message, options = {}) {
    return addToast(message, TOAST_TYPES.ERROR, {
      duration: 8000, // Erros ficam mais tempo
      ...options
    })
  }
  
  function warning(message, options = {}) {
    return addToast(message, TOAST_TYPES.WARNING, {
      duration: 6000,
      ...options
    })
  }
  
  function info(message, options = {}) {
    return addToast(message, TOAST_TYPES.INFO, {
      duration: 5000,
      ...options
    })
  }
  
  /**
   * Aliases de compatibilidade com código existente
   */
  function showSuccess(message, options = {}) {
    return success(message, options)
  }
  
  function showError(message, options = {}) {
    return error(message, options)
  }
  
  function showWarning(message, options = {}) {
    return warning(message, options)
  }
  
  function showInfo(message, options = {}) {
    return info(message, options)
  }
  
  /**
   * Método genérico showToast para compatibilidade
   */
  function showToast(message, type = TOAST_TYPES.INFO, options = {}) {
    switch (type) {
      case TOAST_TYPES.SUCCESS:
      case 'success':
        return success(message, options)
      case TOAST_TYPES.ERROR:
      case 'error':
        return error(message, options)
      case TOAST_TYPES.WARNING:
      case 'warning':
        return warning(message, options)
      case TOAST_TYPES.INFO:
      case 'info':
      default:
        return info(message, options)
    }
  }
  
  /**
   * Método para tratar erros de API
   */
  function handleApiError(error, customMessage = null) {
    let message = customMessage || 'Ocorreu um erro inesperado'
    
    if (error.response) {
      // Erro de resposta HTTP
      const status = error.response.status
      const data = error.response.data
      
      switch (status) {
        case 400:
          message = data.message || 'Dados inválidos enviados'
          break
        case 401:
          message = 'Sessão expirada. Faça login novamente'
          break
        case 403:
          message = 'Você não tem permissão para esta ação'
          break
        case 404:
          message = 'Recurso não encontrado'
          break
        case 422:
          message = data.message || 'Dados de entrada inválidos'
          break
        case 429:
          message = 'Muitas tentativas. Tente novamente em alguns minutos'
          break
        case 500:
          message = 'Erro interno do servidor. Tente novamente mais tarde'
          break
        case 503:
          message = 'Serviço temporariamente indisponível'
          break
        default:
          message = data.message || `Erro ${status}: ${error.response.statusText}`
      }
    } else if (error.request) {
      // Erro de rede
      message = 'Erro de conexão. Verifique sua internet'
    } else {
      // Erro de configuração
      message = error.message || 'Erro na configuração da requisição'
    }
    
    return error(message)
  }
  
  /**
   * Método para tratar erros de validação
   */
  function handleValidationErrors(errors) {
    if (Array.isArray(errors)) {
      errors.forEach(err => error(err))
    } else if (typeof errors === 'object') {
      Object.values(errors).forEach(err => {
        if (Array.isArray(err)) {
          err.forEach(e => error(e))
        } else {
          error(err)
        }
      })
    } else {
      error(errors)
    }
  }
  
  return {
    // Estado
    toasts, // retornar como ref para manter reatividade no container
    
    // Métodos principais
    addToast,
    removeToast,
    pauseToast,
    resumeToast,
    clearAllToasts,
    
    // Métodos de conveniência
    success,
    error,
    warning,
    info,
    
    // Aliases para compatibilidade
    showSuccess,
    showError,
    showWarning,
    showInfo,
    showToast,
    
    // Métodos especializados
    handleApiError,
    handleValidationErrors,
    
    // Constantes
    TOAST_TYPES
  }
}