import { ref, reactive, computed, watch } from 'vue'
import { validateField, validateObject } from '@/utils/formValidations'

/**
 * Composable para gerenciar validações de formulários com feedback visual em tempo real
 */
export function useFormValidation(initialData = {}, validationRules = {}) {
  // Estado do formulário
  const formData = reactive({ ...initialData })
  
  // Estado das validações
  const errors = reactive({})
  const touched = reactive({})
  const isValidating = ref(false)
  
  // Computed para verificar se o formulário é válido
  const isValid = computed(() => {
    return Object.keys(errors).length === 0
  })
  
  // Computed para verificar se há campos tocados
  const hasBeenTouched = computed(() => {
    return Object.keys(touched).some(key => touched[key])
  })
  
  // Computed para verificar se pode submeter
  const canSubmit = computed(() => {
    return isValid.value && hasBeenTouched.value && !isValidating.value
  })
  
  // Função para validar um campo específico
  const validateSingleField = (fieldName, value = formData[fieldName]) => {
    const rules = validationRules[fieldName]
    if (!rules) return true
    
    const result = validateField(value, rules)
    
    if (result === true) {
      delete errors[fieldName]
    } else {
      errors[fieldName] = result
    }
    
    return result === true
  }
  
  // Função para validar todos os campos
  const validateAllFields = () => {
    isValidating.value = true
    
    const result = validateObject(formData, validationRules)
    
    // Limpar erros anteriores
    Object.keys(errors).forEach(key => delete errors[key])
    
    // Adicionar novos erros
    Object.assign(errors, result.errors)
    
    // Marcar todos os campos como tocados
    Object.keys(validationRules).forEach(field => {
      touched[field] = true
    })
    
    isValidating.value = false
    
    return result.isValid
  }
  
  // Função para marcar um campo como tocado
  const touchField = (fieldName) => {
    touched[fieldName] = true
  }
  
  // Função para limpar erro de um campo
  const clearFieldError = (fieldName) => {
    delete errors[fieldName]
  }
  
  // Função para limpar todos os erros
  const clearAllErrors = () => {
    Object.keys(errors).forEach(key => delete errors[key])
  }
  
  // Função para resetar o formulário
  const resetForm = (newData = initialData) => {
    // Resetar dados
    Object.keys(formData).forEach(key => delete formData[key])
    Object.assign(formData, { ...newData })
    
    // Resetar validações
    Object.keys(errors).forEach(key => delete errors[key])
    Object.keys(touched).forEach(key => delete touched[key])
    
    isValidating.value = false
  }
  
  // Função para atualizar dados do formulário
  const updateFormData = (newData) => {
    Object.assign(formData, newData)
  }
  
  // Função para obter classe CSS baseada no estado do campo
  const getFieldClass = (fieldName) => {
    const classes = ['form-input']
    
    if (touched[fieldName]) {
      if (errors[fieldName]) {
        classes.push('form-input--error')
      } else {
        classes.push('form-input--success')
      }
    }
    
    return classes.join(' ')
  }
  
  // Função para obter mensagem de erro de um campo
  const getFieldError = (fieldName) => {
    return touched[fieldName] ? errors[fieldName] : null
  }
  
  // Função para verificar se um campo tem erro
  const hasFieldError = (fieldName) => {
    return touched[fieldName] && !!errors[fieldName]
  }
  
  // Função para verificar se um campo é válido
  const isFieldValid = (fieldName) => {
    return touched[fieldName] && !errors[fieldName]
  }
  
  // Watcher para validação em tempo real
  const setupRealtimeValidation = (fieldName, immediate = false) => {
    return watch(
      () => formData[fieldName],
      (newValue) => {
        if (touched[fieldName] || immediate) {
          validateSingleField(fieldName, newValue)
        }
      },
      { immediate }
    )
  }
  
  // Função para configurar validação em tempo real para todos os campos
  const setupAllRealtimeValidation = (immediate = false) => {
    const watchers = []
    
    Object.keys(validationRules).forEach(fieldName => {
      const watcher = setupRealtimeValidation(fieldName, immediate)
      watchers.push(watcher)
    })
    
    return watchers
  }
  
  // Função para lidar com blur de campo
  const handleFieldBlur = (fieldName) => {
    touchField(fieldName)
    validateSingleField(fieldName)
  }
  
  // Função para lidar com input de campo
  const handleFieldInput = (fieldName, value) => {
    formData[fieldName] = value
    
    // Se o campo já foi tocado, validar em tempo real
    if (touched[fieldName]) {
      validateSingleField(fieldName, value)
    }
  }
  
  // Função para submeter formulário
  const submitForm = async (submitCallback) => {
    if (!validateAllFields()) {
      return { success: false, errors }
    }
    
    try {
      isValidating.value = true
      const result = await submitCallback(formData)
      return { success: true, data: result }
    } catch (error) {
      return { success: false, error: error.message }
    } finally {
      isValidating.value = false
    }
  }
  
  return {
    // Estado
    formData,
    errors,
    touched,
    isValidating,
    
    // Computed
    isValid,
    hasBeenTouched,
    canSubmit,
    
    // Métodos de validação
    validateSingleField,
    validateAllFields,
    
    // Métodos de controle
    touchField,
    clearFieldError,
    clearAllErrors,
    resetForm,
    updateFormData,
    
    // Métodos de UI
    getFieldClass,
    getFieldError,
    hasFieldError,
    isFieldValid,
    
    // Métodos de eventos
    handleFieldBlur,
    handleFieldInput,
    
    // Validação em tempo real
    setupRealtimeValidation,
    setupAllRealtimeValidation,
    
    // Submissão
    submitForm
  }
}