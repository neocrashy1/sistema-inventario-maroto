import { ref, computed } from 'vue'

/**
 * Composable para gerenciar estados de loading de forma consistente
 * @param {Object} options - Opções de configuração
 * @param {boolean} options.initialState - Estado inicial do loading
 * @param {number} options.minDuration - Duração mínima do loading em ms
 */
export function useLoading(options = {}) {
  const {
    initialState = false,
    minDuration = 300 // Mínimo de 300ms para evitar flicker
  } = options

  // Estados
  const isLoading = ref(initialState)
  const loadingStates = ref(new Map())
  const startTime = ref(null)

  // Computed
  const hasAnyLoading = computed(() => {
    return isLoading.value || Array.from(loadingStates.value.values()).some(state => state)
  })

  // Métodos principais
  const startLoading = async (key = 'default') => {
    if (key === 'default') {
      isLoading.value = true
      startTime.value = Date.now()
    } else {
      loadingStates.value.set(key, true)
    }
  }

  const stopLoading = async (key = 'default') => {
    const ensureMinDuration = async () => {
      if (startTime.value && minDuration > 0) {
        const elapsed = Date.now() - startTime.value
        if (elapsed < minDuration) {
          await new Promise(resolve => setTimeout(resolve, minDuration - elapsed))
        }
      }
    }

    if (key === 'default') {
      await ensureMinDuration()
      isLoading.value = false
      startTime.value = null
    } else {
      loadingStates.value.set(key, false)
    }
  }

  // Wrapper para executar função com loading
  const withLoading = async (fn, key = 'default') => {
    try {
      await startLoading(key)
      const result = await fn()
      return result
    } finally {
      await stopLoading(key)
    }
  }

  // Verificar estado específico
  const isLoadingKey = (key) => {
    return loadingStates.value.get(key) || false
  }

  // Limpar todos os estados
  const clearAll = () => {
    isLoading.value = false
    loadingStates.value.clear()
    startTime.value = null
  }

  // Estados específicos para operações comuns
  const loadingStates_common = {
    fetching: computed(() => isLoadingKey('fetching')),
    saving: computed(() => isLoadingKey('saving')),
    deleting: computed(() => isLoadingKey('deleting')),
    creating: computed(() => isLoadingKey('creating')),
    updating: computed(() => isLoadingKey('updating'))
  }

  // Métodos de conveniência
  const startFetching = () => startLoading('fetching')
  const stopFetching = () => stopLoading('fetching')
  const startSaving = () => startLoading('saving')
  const stopSaving = () => stopLoading('saving')
  const startDeleting = () => startLoading('deleting')
  const stopDeleting = () => stopLoading('deleting')
  const startCreating = () => startLoading('creating')
  const stopCreating = () => stopLoading('creating')
  const startUpdating = () => startLoading('updating')
  const stopUpdating = () => stopLoading('updating')

  // Wrappers específicos
  const withFetching = (fn) => withLoading(fn, 'fetching')
  const withSaving = (fn) => withLoading(fn, 'saving')
  const withDeleting = (fn) => withLoading(fn, 'deleting')
  const withCreating = (fn) => withLoading(fn, 'creating')
  const withUpdating = (fn) => withLoading(fn, 'updating')

  return {
    // Estados principais
    isLoading,
    hasAnyLoading,
    
    // Estados específicos
    ...loadingStates_common,
    
    // Métodos principais
    startLoading,
    stopLoading,
    withLoading,
    isLoadingKey,
    clearAll,
    
    // Métodos de conveniência
    startFetching,
    stopFetching,
    startSaving,
    stopSaving,
    startDeleting,
    stopDeleting,
    startCreating,
    stopCreating,
    startUpdating,
    stopUpdating,
    
    // Wrappers específicos
    withFetching,
    withSaving,
    withDeleting,
    withCreating,
    withUpdating
  }
}

// Hook para loading de página inteira
export function usePageLoading() {
  const loading = useLoading({ minDuration: 500 })
  
  return {
    ...loading,
    // Método específico para carregamento de página
    loadPage: async (loadFn) => {
      return loading.withLoading(loadFn)
    }
  }
}

// Hook para loading de formulários
export function useFormLoading() {
  const loading = useLoading({ minDuration: 200 })
  
  return {
    ...loading,
    // Método específico para submissão de formulário
    submitForm: async (submitFn) => {
      return loading.withSaving(submitFn)
    }
  }
}