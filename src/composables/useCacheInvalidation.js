/**
 * Composable para gerenciar invalidação de cache
 * Automatiza a limpeza de cache quando dados são modificados
 */

import { useApiCache } from './useApiCache'
import logger from '@/utils/logger'

export function useCacheInvalidation() {
  const { invalidateCache, invalidatePattern, clearCache } = useApiCache()

  /**
   * Invalida cache relacionado a usuários
   */
  const invalidateUsersCache = () => {
    logger.info('Invalidating users cache')
    invalidatePattern('users:')
    invalidateCache('dashboard:stats') // Dashboard pode mostrar contadores de usuários
  }

  /**
   * Invalida cache relacionado a localizações
   */
  const invalidateLocationsCache = () => {
    logger.info('Invalidating locations cache')
    invalidatePattern('locations:')
    invalidateCache('dashboard:stats')
  }

  /**
   * Invalida cache relacionado a máquinas
   */
  const invalidateMachinesCache = () => {
    logger.info('Invalidating machines cache')
    invalidatePattern('machines:')
    invalidateCache('dashboard:stats')
    invalidateCache('dashboard:metrics')
  }

  /**
   * Invalida cache relacionado a tickets
   */
  const invalidateTicketsCache = () => {
    logger.info('Invalidating tickets cache')
    invalidatePattern('tickets:')
    invalidateCache('dashboard:alerts')
    invalidateCache('dashboard:stats')
  }

  /**
   * Invalida cache relacionado a alertas
   */
  const invalidateAlertsCache = () => {
    logger.info('Invalidating alerts cache')
    invalidatePattern('alerts:')
    invalidateCache('dashboard:alerts')
  }

  /**
   * Invalida todo o cache do dashboard
   */
  const invalidateDashboardCache = () => {
    logger.info('Invalidating dashboard cache')
    invalidatePattern('dashboard:')
  }

  /**
   * Invalida cache baseado no tipo de operação
   */
  const invalidateByOperation = (operation, entityType, entityId = null) => {
    logger.info('Cache invalidation triggered', { operation, entityType, entityId })

    switch (entityType) {
      case 'user':
        invalidateUsersCache()
        if (entityId) {
          invalidateCache(`users:${entityId}`)
        }
        break

      case 'location':
        invalidateLocationsCache()
        if (entityId) {
          invalidateCache(`locations:${entityId}`)
        }
        break

      case 'machine':
        invalidateMachinesCache()
        if (entityId) {
          invalidateCache(`machines:${entityId}:status`)
        }
        break

      case 'ticket':
        invalidateTicketsCache()
        if (entityId) {
          invalidateCache(`tickets:${entityId}`)
        }
        break

      case 'alert':
        invalidateAlertsCache()
        if (entityId) {
          invalidateCache(`alerts:${entityId}`)
        }
        break

      default:
        logger.warn('Unknown entity type for cache invalidation', { entityType })
    }

    // Operações que sempre afetam o dashboard
    if (['create', 'update', 'delete'].includes(operation)) {
      invalidateCache('dashboard:stats')
    }
  }

  /**
   * Invalida cache após operações CRUD
   */
  const invalidateAfterCreate = (entityType, entityData = null) => {
    invalidateByOperation('create', entityType, entityData?.id)
  }

  const invalidateAfterUpdate = (entityType, entityId) => {
    invalidateByOperation('update', entityType, entityId)
  }

  const invalidateAfterDelete = (entityType, entityId) => {
    invalidateByOperation('delete', entityType, entityId)
  }

  /**
   * Limpa todo o cache (usar com cuidado)
   */
  const clearAllCache = () => {
    logger.warn('Clearing all cache')
    clearCache()
  }

  /**
   * Invalida cache relacionado a relatórios
   */
  const invalidateReportsCache = () => {
    logger.info('Invalidating reports cache')
    invalidatePattern('reports:')
    invalidatePattern('analytics:')
  }

  /**
   * Invalida cache quando configurações são alteradas
   */
  const invalidateSettingsCache = () => {
    logger.info('Invalidating settings cache')
    invalidatePattern('settings:')
    // Configurações podem afetar todo o sistema
    clearAllCache()
  }

  return {
    // Invalidação por entidade
    invalidateUsersCache,
    invalidateLocationsCache,
    invalidateMachinesCache,
    invalidateTicketsCache,
    invalidateAlertsCache,
    invalidateDashboardCache,
    invalidateReportsCache,
    invalidateSettingsCache,

    // Invalidação por operação
    invalidateByOperation,
    invalidateAfterCreate,
    invalidateAfterUpdate,
    invalidateAfterDelete,

    // Limpeza geral
    clearAllCache,

    // Acesso direto às funções do cache
    invalidateCache,
    invalidatePattern,
    clearCache
  }
}