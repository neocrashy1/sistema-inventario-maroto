import { useErrorHandler } from '@/composables/useErrorHandler'
import logger from '@/utils/logger'

/**
 * Plugin para tratamento global de erros do Vue
 */
export default {
  install(app) {
    const { handleError } = useErrorHandler()

    // Capturar erros não tratados do Vue
    app.config.errorHandler = (error, instance, info) => {
      logger.error('Vue Error', { error, instance, info })
      
      // Determinar contexto baseado na informação do erro
      let context = 'Erro na aplicação'
      
      if (info) {
        if (info.includes('render')) {
          context = 'Erro de renderização'
        } else if (info.includes('event handler')) {
          context = 'Erro em manipulador de evento'
        } else if (info.includes('component')) {
          context = 'Erro no componente'
        } else if (info.includes('watcher')) {
          context = 'Erro no watcher'
        }
      }

      // Usar o tratamento global de erros
      handleError(error, context)
    }

    // Capturar erros de promises não tratadas
    window.addEventListener('unhandledrejection', (event) => {
      logger.error('Unhandled Promise Rejection', { reason: event.reason })
      
      // Prevenir o log padrão do browser
      event.preventDefault()
      
      // Tratar o erro
      handleError(event.reason, 'Promise rejeitada')
    })

    // Capturar erros JavaScript globais
    window.addEventListener('error', (event) => {
      logger.error('Global JavaScript Error', { error: event.error })
      
      // Tratar o erro
      handleError(event.error, 'Erro JavaScript')
    })

    // Disponibilizar o tratamento de erros globalmente
    app.config.globalProperties.$handleError = handleError
    app.provide('errorHandler', { handleError })
  }
}