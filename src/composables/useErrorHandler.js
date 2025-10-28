import { useToast } from './useToast'
import logger from '@/utils/logger'

/**
 * Composable para tratamento global de erros
 */
export function useErrorHandler() {
  const { showError, showWarning } = useToast()

  // Evita toasts duplicados marcando o erro como já tratado
  function isAlreadyHandled(error) {
    return Boolean(error && error.__toastHandled)
  }

  function markHandled(error) {
    if (error) {
      try { error.__toastHandled = true } catch (_) { /* no-op */ }
    }
  }

  /**
   * Mapear códigos de status HTTP para mensagens amigáveis
   */
  const statusMessages = {
    400: 'Dados inválidos enviados',
    401: 'Sessão expirada. Faça login novamente',
    403: 'Você não tem permissão para esta ação',
    404: 'Recurso não encontrado',
    409: 'Conflito de dados. Verifique as informações',
    422: 'Dados inválidos. Verifique os campos',
    429: 'Muitas tentativas. Tente novamente em alguns minutos',
    500: 'Erro interno do servidor',
    502: 'Servidor temporariamente indisponível',
    503: 'Serviço temporariamente indisponível',
    504: 'Tempo limite de conexão excedido'
  }

  /**
   * Obter mensagem amigável baseada no erro
   */
  function getErrorMessage(error) {
    // Se o erro tem uma mensagem customizada
    if (error?.response?.data?.message) {
      return error.response.data.message
    }

    // Se o erro tem uma mensagem de validação
    if (error?.response?.data?.errors) {
      const errors = error.response.data.errors
      if (Array.isArray(errors)) {
        return errors.join(', ')
      }
      if (typeof errors === 'object') {
        return Object.values(errors).flat().join(', ')
      }
    }

    // Mensagem baseada no status HTTP
    const status = error?.response?.status
    if (status && statusMessages[status]) {
      return statusMessages[status]
    }

    // Erro de rede
    if (error?.code === 'NETWORK_ERROR' || !error?.response) {
      return 'Erro de conexão. Verifique sua internet'
    }

    // Timeout
    if (error?.code === 'ECONNABORTED') {
      return 'Tempo limite de conexão excedido'
    }

    // Mensagem genérica
    return error?.message || 'Ocorreu um erro inesperado'
  }

  // Normaliza mensagem para dedupeKey
  function normalizeMessage(message) {
    try {
      return String(message)
        .toLowerCase()
        .replace(/\s+/g, ' ')
        .replace(/horário: [^|]+/gi, '')
        .trim()
    } catch (_) {
      return 'unknown'
    }
  }

  // Gera dedupeKey consistente
  function getDedupeKey(error, message) {
    const status = error?.response?.status
    const baseMsg = normalizeMessage(message)
    if (status) return `status:${status}:${baseMsg}`
    if (error?.code === 'NETWORK_ERROR') return `net:${baseMsg}`
    return `generic:${baseMsg}`
  }

  /**
   * Obter detalhes adicionais do erro
   */
  function getErrorDetails(error) {
    const details = []

    // Adicionar código de status se disponível
    if (error?.response?.status) {
      details.push(`Código: ${error.response.status}`)
    }

    // Adicionar timestamp
    details.push(`Horário: ${new Date().toLocaleTimeString()}`)

    // Adicionar ID da requisição se disponível
    if (error?.response?.headers?.['x-request-id']) {
      details.push(`ID: ${error.response.headers['x-request-id']}`)
    }

    return details.length > 0 ? details.join(' | ') : null
  }

  /**
   * Determinar se o erro deve ser mostrado como warning
   */
  function isWarningError(error) {
    const status = error?.response?.status
    return status === 400 || status === 422 || status === 409
  }

  /**
   * Tratar erro de API
   */
  function handleApiError(error, context = '') {
    // Evitar toasts duplicados
    if (isAlreadyHandled(error)) {
      return {
        message: getErrorMessage(error),
        details: getErrorDetails(error),
        status: error?.response?.status,
        code: error?.code
      }
    }
    logger.apiError(error.config?.url || 'unknown', error, {
        method: error.config?.method,
        data: error.config?.data
      })

    const message = getErrorMessage(error)
    const details = getErrorDetails(error)
    const fullMessage = context ? `${context}: ${message}` : message

    const status = error?.response?.status
    const dedupeKey = getDedupeKey(error, message)

    if (isWarningError(error)) {
      showWarning(fullMessage, { details, dedupeKey })
    } else {
      // Para 403, evitar detalhes para não poluir a UI
      const opts = status === 403 ? { dedupeKey } : { details, dedupeKey }
      showError(fullMessage, opts)
    }

    markHandled(error)

    // Retornar informações do erro para uso posterior
    return {
      message,
      details,
      status: error?.response?.status,
      code: error?.code
    }
  }

  /**
   * Tratar erro de validação
   */
  function handleValidationError(errors, context = 'Erro de validação') {
    let message = context

    if (typeof errors === 'string') {
      message = errors
    } else if (Array.isArray(errors)) {
      message = errors.join(', ')
    } else if (typeof errors === 'object') {
      const errorMessages = Object.values(errors).flat()
      message = errorMessages.join(', ')
    }

    showWarning(message)
    return { message }
  }

  /**
   * Tratar erro de rede e erros relacionados a requisições
   */
  const getHttpStatusCategory = (status) => {
    if (!status) return 'unknown'
    if (status >= 500) return 'server'
    if (status >= 400) return 'client'
    return 'other'
  }

  function handleNetworkError(error, context = 'Erro de rede') {
    if (isAlreadyHandled(error)) {
      return { type: 'network', context, message: getErrorMessage(error), details: getErrorDetails(error), status: error?.response?.status }
    }
    const message = getErrorMessage(error)
    const status = error?.response?.status
    const category = getHttpStatusCategory(status)

    const details = getErrorDetails(error)

    if (category === 'server') {
      logger.error(`[${context}] ${message}`, { status, error })
    } else if (category === 'client') {
      logger.warn(`[${context}] ${message}`, { status, error })
    } else {
      logger.info(`[${context}] ${message}`, { status, error })
    }

    const dedupeKey = getDedupeKey(error, message)
    showError(message, { details, dedupeKey })
    markHandled(error)
    return { type: 'network', context, message, details, status }
  }

  /**
   * Tratar erro genérico
   */
  function handleGenericError(error, context = 'Erro genérico') {
    if (isAlreadyHandled(error)) {
      const message = getErrorMessage(error)
      const details = getErrorDetails(error)
      const fullMessage = context ? `${context}: ${message}` : message
      return { type: 'generic', context, message: fullMessage, details }
    }
    const message = getErrorMessage(error)
    const details = getErrorDetails(error)
    const fullMessage = context ? `${context}: ${message}` : message

    logger.error(fullMessage, { error })

    if (isWarningError(error)) {
      showWarning(fullMessage, { details, dedupeKey: getDedupeKey(error, fullMessage) })
    } else {
      showError(fullMessage, { details, dedupeKey: getDedupeKey(error, fullMessage) })
    }

    markHandled(error)
    return { type: 'generic', context, message: fullMessage, details }
  }

  /**
   * Wrapper para funções assíncronas com tratamento de erro
   */
  async function withErrorHandling(fn, { context = 'Operação', rethrow = false } = {}) {
    try {
      return await fn()
    } catch (error) {
      const result = handleError(error, context)
      if (rethrow) throw error
      return result
    }
  }

  /**
   * Tratar múltiplos erros
   */
  function handleMultipleErrors(errors, context = 'Múltiplos erros encontrados') {
    if (!Array.isArray(errors) || errors.length === 0) {
      return { type: 'multiple', context, messages: [], count: 0 }
    }

    if (errors.length === 1) {
      return handleError(errors[0], context)
    }

    const messages = errors.map(error => getErrorMessage(error))
    const uniqueMessages = [...new Set(messages)]
    showError(`${context} (${errors.length} erros)`, {
      details: uniqueMessages.join(' | ')
    })
    return { type: 'multiple', context, messages: uniqueMessages, count: errors.length }
  }

  /**
   * Roteamento de tratamento baseado no tipo de erro
   */
  function handleError(error, context = 'Erro') {
    if (!error) return { type: 'unknown', context, details: null }

    // Erro de API (axios)
    if (error?.response) {
      return handleApiError(error, context)
    }

    // Erro de rede
    if (error?.code === 'NETWORK_ERROR' || error?.isAxiosError || error?.config || !error?.response) {
      return handleNetworkError(error, context)
    }

    // Erro genérico
    return handleGenericError(error, context)
  }

  return {
    handleError,
    withErrorHandling,
    handleApiError,
    handleValidationError,
    handleNetworkError,
    handleGenericError,
    handleMultipleErrors,
    getErrorMessage,
    getErrorDetails,
    isWarning: isWarningError,
  }
}