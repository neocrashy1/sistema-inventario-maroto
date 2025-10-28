/**
 * API Service for Levitiis Asset Management System
 * Integrates with FastAPI backend
 */

import axios from 'axios'
import { useErrorHandler } from '@/composables/useErrorHandler'
import { useApiCache, CACHE_STRATEGIES } from '@/composables/useApiCache'
import logger from '@/utils/logger'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
// Normalize API version and combine safely
const API_VERSION = import.meta.env.VITE_API_VERSION || '/api/v1'
const API_BASE_FINAL = (() => {
  if (!API_VERSION) return API_BASE_URL
  // Avoid double prefix if base already contains version (e.g., '/api/v1' or 'http://.../api/v1')
  if (API_BASE_URL.endsWith('/api/v1')) return API_BASE_URL
  const versionNormalized = API_VERSION.startsWith('/') ? API_VERSION : `/${API_VERSION}`
  return `${API_BASE_URL}${versionNormalized}`
})()

// Create axios instances
const apiClient = axios.create({
  baseURL: API_BASE_FINAL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

const analyticsApiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL_ANALYTICS || 'http://localhost:8001',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Shared Request interceptor for authentication
const attachInterceptors = (client) => {
  client.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      // Add Agent API Key if available to access endpoints that allow API Key
      const agentApiKey = localStorage.getItem('agent_api_key') || import.meta.env.VITE_AGENT_API_KEY
      if (agentApiKey) {
        config.headers['X-API-Key'] = agentApiKey
      }

      // Log request (debug only)
      logger.debug('API Request', { url: config.url, method: config.method, baseURL: config.baseURL })

      return config
    },
    (error) => {
      // Uniformizar código de erro de rede
      if (error.code === 'ERR_NETWORK') {
        error.code = 'NETWORK_ERROR'
      }
      logger.error('API Request Error', { message: error.message })
      return Promise.reject(error)
    }
  )

  // Response interceptor for error handling
  client.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config
      const { handleError } = useErrorHandler()

      // Uniformizar código de erro de rede
      if (error.code === 'ERR_NETWORK') {
        error.code = 'NETWORK_ERROR'
      }

      // Handle 401 errors (authentication)
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true
        
        try {
          const refreshToken = localStorage.getItem('refresh_token')
          if (refreshToken) {
            // Always refresh via core API client
            const response = await apiClient.post('/auth/refresh', {
              refresh_token: refreshToken
            })
            
            const { access_token, refresh_token: newRefreshToken } = response.data
            localStorage.setItem('access_token', access_token)
            if (newRefreshToken) {
              localStorage.setItem('refresh_token', newRefreshToken)
            }
            // Ensure retried request uses the new token
            originalRequest.headers = originalRequest.headers || {}
            originalRequest.headers.Authorization = `Bearer ${access_token}`
            
            logger.info('Access token refreshed successfully')
            return client(originalRequest)
          }
        } catch (refreshError) {
          // Refresh failed, não redirecionar para login temporariamente
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          logger.error('Token refresh failed', { error: refreshError.message })
          handleError(refreshError, 'Sessão expirada')
          // window.location.href = '/auth/login'
          return Promise.reject(refreshError)
        }
      }

      // Log API Error com contexto
      logger.apiError(error.config?.url || 'unknown', error, {
        method: error.config?.method,
        status: error.response?.status,
        data: error.config?.data
      })

      // Handle other errors globally (only if not explicitly handled)
      if (!originalRequest?._skipGlobalErrorHandler) {
        handleError(error)
      }
      
      return Promise.reject(error)
    }
  )
}

attachInterceptors(apiClient)
attachInterceptors(analyticsApiClient)

// API Services
export const authAPI = {
  login: (credentials) => apiClient.post('/auth/login', credentials),
  register: (userData, config = {}) => apiClient.post('/auth/register', userData, { ...config }),
  logout: () => apiClient.post('/auth/logout'),
  refreshToken: (refreshToken) => apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
  getCurrentUser: () => apiClient.get('/auth/me'),
  changePassword: (passwordData) => apiClient.post('/auth/change-password', passwordData),
  // Added endpoints to unify auth flows and avoid hardcoded URLs
  forgotPassword: (email) => apiClient.post('/auth/forgot-password', { email }),
  resetPassword: (token, password) => apiClient.post('/auth/reset-password', { token, password }),
  updateProfile: (profileData) => apiClient.put('/auth/profile', profileData)
}

export const assetsAPI = {
  getAll: (params = {}) => apiClient.get('/assets', { params, _skipGlobalErrorHandler: true }),
  getById: (id) => apiClient.get(`/assets/${id}`),
  create: (assetData) => apiClient.post('/assets', assetData),
  update: (id, assetData) => apiClient.put(`/assets/${id}`, assetData),
  delete: (id) => apiClient.delete(`/assets/${id}`),
  move: (id, movementData) => apiClient.post(`/assets/${id}/move`, movementData),
  getHistory: (id) => apiClient.get(`/assets/${id}/history`),
 getDashboardSummary: () => apiClient.get('/assets/dashboard/summary', { _skipGlobalErrorHandler: true })
}

export const machinesAPI = {
  register: (machineData) => apiClient.post('/machines/register', machineData),
  updateStatus: (statusData) => apiClient.post('/machines/status', statusData),
  getStatus: (machineId) => apiClient.get(`/machines/${machineId}/status`),
  getAll: (params = {}) => apiClient.get('/machines', { params })
}

export const ticketsAPI = {
  create: (ticketData) => apiClient.post('/tickets/create', ticketData),
  getById: (id) => apiClient.get(`/tickets/${id}`),
  update: (id, updateData) => apiClient.put(`/tickets/${id}`, updateData),
  addComment: (id, commentData) => apiClient.post(`/tickets/${id}/comments`, commentData),
  getAll: (params = {}) => apiClient.get('/tickets', { params })
}

export const alertsAPI = {
  send: (alertData) => apiClient.post('/alerts/send', alertData),
  getAll: (params = {}) => apiClient.get('/alerts', { params }),
  getById: (id) => apiClient.get(`/alerts/${id}`),
  acknowledge: (id, ackData = {}) => apiClient.put(`/alerts/${id}`, { status: 'acknowledged', ...ackData }),
  resolve: (id, resolutionData = {}) => apiClient.put(`/alerts/${id}`, { status: 'resolved', ...resolutionData })
}

export const analyticsAPI = {
  getOverview: (params = {}) => analyticsApiClient.get('/analytics/overview', { params, _skipGlobalErrorHandler: true }),
  getTopCpu: (params = {}) => analyticsApiClient.get('/analytics/machines/top_cpu', { params, _skipGlobalErrorHandler: true }),
  getMachineTimeseries: (machineId, params = {}) => analyticsApiClient.get(`/analytics/machine/${machineId}/timeseries`, { params, _skipGlobalErrorHandler: true })
}

export const usersAPI = {
  getAll: (params = {}) => apiClient.get('/users', { params }),
  getById: (id) => apiClient.get(`/users/${id}`),
  create: (userData) => apiClient.post('/users', userData),
  update: (id, userData) => apiClient.put(`/users/${id}`, userData),
  delete: (id) => apiClient.delete(`/users/${id}`),
  resetPassword: (id) => apiClient.post(`/users/${id}/reset-password`),
 getDashboardSummary: () => apiClient.get('/users/dashboard/summary', { _skipGlobalErrorHandler: true })
}

export const locationsAPI = {
  getAll: (params = {}) => apiClient.get('/locations', { params }),
  getById: (id) => apiClient.get(`/locations/${id}`),
  create: (locationData) => apiClient.post('/locations', locationData),
  update: (id, locationData) => apiClient.put(`/locations/${id}`, locationData),
  delete: (id) => apiClient.delete(`/locations/${id}`)
}

// Dashboard API
export const dashboardAPI = {
  getOverview: () => apiClient.get('/dashboard/stats', { _skipGlobalErrorHandler: true }),
  getStats: () => apiClient.get('/dashboard/stats', { _skipGlobalErrorHandler: true }),
  getMetrics: () => apiClient.get('/dashboard/metrics', { _skipGlobalErrorHandler: true }),
  getAlerts: () => apiClient.get('/dashboard/alerts', { _skipGlobalErrorHandler: true }),
  getRecentActivity: () => apiClient.get('/dashboard/recent-activity', { _skipGlobalErrorHandler: true }),
  getHealthCheck: () => apiClient.get('/dashboard/health-check', { _skipGlobalErrorHandler: true })
}

// Cached API Services
const { cachedRequest } = useApiCache()

export const cachedAPI = {
  // Dashboard com cache inteligente
  dashboard: {
    getStats: (options = {}) => cachedRequest(
      () => apiClient.get('/dashboard/stats', { _skipGlobalErrorHandler: true }),
      {
        cacheKey: 'dashboard:stats',
        strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE,
        ttl: 2 * 60 * 1000, // 2 minutos
        ...options
      }
    ),
    
    getMetrics: (options = {}) => cachedRequest(
      () => apiClient.get('/dashboard/metrics', { _skipGlobalErrorHandler: true }),
      {
        cacheKey: 'dashboard:metrics',
        strategy: CACHE_STRATEGIES.CACHE_FIRST,
        ttl: 5 * 60 * 1000, // 5 minutos
        ...options
      }
    ),
    
    getAlerts: (options = {}) => cachedRequest(
      () => apiClient.get('/dashboard/alerts', { _skipGlobalErrorHandler: true }),
      {
        cacheKey: 'dashboard:alerts',
        strategy: CACHE_STRATEGIES.NETWORK_FIRST,
        ttl: 1 * 60 * 1000, // 1 minuto
        ...options
      }
    )
  },

  // Usuários com cache
  users: {
    getAll: (params = {}, options = {}) => cachedRequest(
      (p) => apiClient.get('/users', { params: p }),
      {
        cacheKey: `users:all:${JSON.stringify(params)}`,
        strategy: CACHE_STRATEGIES.CACHE_FIRST,
        ttl: 10 * 60 * 1000, // 10 minutos
        params,
        ...options
      }
    ),
    
    getById: (id, options = {}) => cachedRequest(
      () => apiClient.get(`/users/${id}`),
      {
        cacheKey: `users:${id}`,
        strategy: CACHE_STRATEGIES.CACHE_FIRST,
        ttl: 15 * 60 * 1000, // 15 minutos
        ...options
      }
    )
  },

  // Localizações com cache
  locations: {
    getAll: (params = {}, options = {}) => cachedRequest(
      (p) => apiClient.get('/locations', { params: p }),
      {
        cacheKey: `locations:all:${JSON.stringify(params)}`,
        strategy: CACHE_STRATEGIES.CACHE_FIRST,
        ttl: 30 * 60 * 1000, // 30 minutos (dados mais estáticos)
        params,
        ...options
      }
    ),
    
    getById: (id, options = {}) => cachedRequest(
      () => apiClient.get(`/locations/${id}`),
      {
        cacheKey: `locations:${id}`,
        strategy: CACHE_STRATEGIES.CACHE_FIRST,
        ttl: 30 * 60 * 1000,
        ...options
      }
    )
  },

  // Máquinas com cache
  machines: {
    getAll: (params = {}, options = {}) => cachedRequest(
      (p) => apiClient.get('/machines', { params: p }),
      {
        cacheKey: `machines:all:${JSON.stringify(params)}`,
        strategy: CACHE_STRATEGIES.CACHE_FIRST,
        ttl: 5 * 60 * 1000, // 5 minutos
        params,
        ...options
      }
    ),
    
    getStatus: (machineId, options = {}) => cachedRequest(
      () => apiClient.get(`/machines/${machineId}/status`),
      {
        cacheKey: `machines:${machineId}:status`,
        strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE,
        ttl: 30 * 1000, // 30 segundos (dados dinâmicos)
        ...options
      }
    )
  },

  // Analytics com cache
  analytics: {
    getOverview: (options = {}) => cachedRequest(
      () => analyticsApiClient.get('/analytics/overview', { _skipGlobalErrorHandler: true }),
      {
        cacheKey: 'analytics:overview',
        strategy: CACHE_STRATEGIES.STALE_WHILE_REVALIDATE,
        ttl: 60 * 1000,
        ...options
      }
    ),

    getTopCpu: (params = {}, options = {}) => cachedRequest(
      (p) => analyticsApiClient.get('/analytics/machines/top_cpu', { params: p, _skipGlobalErrorHandler: true }),
      {
        cacheKey: `analytics:top_cpu:${JSON.stringify(params)}`,
        strategy: CACHE_STRATEGIES.NETWORK_FIRST,
        ttl: 30 * 1000,
        params,
        ...options
      }
    ),

    getMachineTimeseries: (machineId, params = {}, options = {}) => cachedRequest(
      (p) => analyticsApiClient.get(`/analytics/machine/${machineId}/timeseries`, { params: p, _skipGlobalErrorHandler: true }),
      {
        cacheKey: `analytics:machine:${machineId}:timeseries:${JSON.stringify(params)}`,
        strategy: CACHE_STRATEGIES.NETWORK_FIRST,
        ttl: 30 * 1000,
        params,
        ...options
      }
    ),
  },

  // Tickets com cache seletivo
  tickets: {
    getAll: (params = {}, options = {}) => cachedRequest(
      (p) => apiClient.get('/tickets', { params: p }),
      {
        cacheKey: `tickets:all:${JSON.stringify(params)}`,
        strategy: CACHE_STRATEGIES.NETWORK_FIRST, // Dados críticos, priorizar rede
        ttl: 2 * 60 * 1000, // 2 minutos
        params,
        ...options
      }
    ),
    
    getById: (id, options = {}) => cachedRequest(
      () => apiClient.get(`/tickets/${id}`),
      {
        cacheKey: `tickets:${id}`,
        strategy: CACHE_STRATEGIES.CACHE_FIRST,
        ttl: 5 * 60 * 1000,
        ...options
      }
    )
  }
}

// Utility functions
export const handleAPIError = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response
    return {
      status,
      message: data.detail || data.message || 'Erro no servidor',
      errors: data.errors || []
    }
  } else if (error.request) {
    // Request was made but no response received
    return {
      status: 0,
      message: 'Erro de conexão com o servidor',
      errors: []
    }
  } else {
    // Something else happened
    return {
      status: 0,
      message: error.message || 'Erro desconhecido',
      errors: []
    }
  }
}

export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem('access_token', token)
  } else {
    localStorage.removeItem('access_token')
  }
}

export const getAuthToken = () => {
  return localStorage.getItem('access_token')
}

export const clearAuth = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export default apiClient

export const machineMonitoringAPI = {
  getMachines: (params = {}) => apiClient.get('/machines/list', { params }),
  getMetrics: (machineId) => apiClient.get(`/machines/${machineId}/metrics`)
}

export const auditorsAPI = {
  getAll: (params = {}) => apiClient.get('/auditorias', { params }),
  getById: (id) => apiClient.get(`/auditorias/${id}`),
  create: (auditoriaData) => apiClient.post('/auditorias', auditoriaData),
  start: (id) => apiClient.put(`/auditorias/${id}/iniciar`),
  getCountList: (id, params = {}) => apiClient.get(`/auditorias/${id}/lista-contagem`, { params }),
  registerCollection: (id, coletaData) => apiClient.post(`/auditorias/${id}/coletas`, coletaData),
  reconcile: (id, data = {}) => apiClient.put(`/auditorias/${id}/reconciliar`, data),
  getReconciliationReport: (id, params = {}) => apiClient.get(`/auditorias/${id}/relatorio-reconciliacao`, { params })
}

export { apiClient }
