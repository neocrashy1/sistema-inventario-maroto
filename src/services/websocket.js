import logger from '@/utils/logger'

class WebSocketService {
  constructor() {
    this.ws = null
    this.url = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 3000
    this.isConnecting = false
    this.isManualClose = false
    this.listeners = new Map()
    this.heartbeatInterval = null
    this.heartbeatTimeout = null
    this.lastHeartbeat = null
    
    // Configurações
    this.config = {
      heartbeatInterval: 30000, // 30 segundos
      heartbeatTimeout: 5000,   // 5 segundos para resposta
      reconnectDelay: 3000,     // 3 segundos entre tentativas
      maxReconnectAttempts: 5
    }
  }

  /**
   * Conecta ao WebSocket
   * @param {string} url - URL do WebSocket
   * @param {Object} options - Opções de conexão
   */
  connect(url = 'ws://localhost:8000/api/v1/ws', options = {}) {
    if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
      logger.warn('WebSocket já está conectando')
      return Promise.resolve()
    }

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      logger.warn('WebSocket já está conectado')
      return Promise.resolve()
    }

    this.url = url
    this.isConnecting = true
    this.isManualClose = false

    return new Promise((resolve, reject) => {
      try {
        logger.info(`Conectando ao WebSocket: ${url}`)
        this.ws = new WebSocket(url)

        // Timeout para conexão
        const connectionTimeout = setTimeout(() => {
          if (this.ws.readyState === WebSocket.CONNECTING) {
            this.ws.close()
            reject(new Error('Timeout na conexão WebSocket'))
          }
        }, options.timeout || 10000)

        this.ws.onopen = (event) => {
          clearTimeout(connectionTimeout)
          this.isConnecting = false
          this.reconnectAttempts = 0
          
          logger.info('WebSocket conectado com sucesso')
          this.emit('connected', { event })
          this.startHeartbeat()
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data)
            this.handleMessage(data)
          } catch (error) {
            logger.error('Erro ao processar mensagem WebSocket:', error)
            this.emit('error', { error, rawData: event.data })
          }
        }

        this.ws.onclose = (event) => {
          clearTimeout(connectionTimeout)
          this.isConnecting = false
          this.stopHeartbeat()
          
          logger.info(`WebSocket desconectado. Code: ${event.code}, Reason: ${event.reason}`)
          this.emit('disconnected', { event })

          if (!this.isManualClose && this.shouldReconnect()) {
            this.scheduleReconnect()
          }
        }

        this.ws.onerror = (error) => {
          clearTimeout(connectionTimeout)
          this.isConnecting = false
          
          logger.error('Erro no WebSocket:', error)
          this.emit('error', { error })
          
          if (this.ws.readyState === WebSocket.CONNECTING) {
            reject(error)
          }
        }

      } catch (error) {
        this.isConnecting = false
        logger.error('Erro ao criar WebSocket:', error)
        reject(error)
      }
    })
  }

  /**
   * Desconecta do WebSocket
   */
  disconnect() {
    this.isManualClose = true
    this.stopHeartbeat()
    
    if (this.ws) {
      if (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING) {
        this.ws.close(1000, 'Desconexão manual')
      }
      this.ws = null
    }
    
    logger.info('WebSocket desconectado manualmente')
  }

  /**
   * Envia mensagem via WebSocket
   * @param {string} type - Tipo da mensagem
   * @param {Object} data - Dados da mensagem
   */
  send(type, data = {}) {
    if (!this.isConnected()) {
      logger.warn('WebSocket não está conectado. Mensagem não enviada:', { type, data })
      return false
    }

    try {
      const message = {
        type,
        data,
        timestamp: Date.now()
      }
      
      this.ws.send(JSON.stringify(message))
      logger.debug('Mensagem enviada via WebSocket:', message)
      return true
    } catch (error) {
      logger.error('Erro ao enviar mensagem WebSocket:', error)
      this.emit('error', { error })
      return false
    }
  }

  /**
   * Verifica se está conectado
   */
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }

  /**
   * Adiciona listener para eventos
   * @param {string} event - Nome do evento
   * @param {Function} callback - Função callback
   */
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event).add(callback)
  }

  /**
   * Remove listener de evento
   * @param {string} event - Nome do evento
   * @param {Function} callback - Função callback
   */
  off(event, callback) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).delete(callback)
    }
  }

  /**
   * Emite evento para listeners
   * @param {string} event - Nome do evento
   * @param {Object} data - Dados do evento
   */
  emit(event, data = {}) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          logger.error(`Erro no listener do evento ${event}:`, error)
        }
      })
    }
  }

  /**
   * Processa mensagens recebidas
   * @param {Object} data - Dados da mensagem
   */
  handleMessage(data) {
    const { type, data: messageData, timestamp } = data

    // Resposta ao heartbeat
    if (type === 'pong') {
      this.handleHeartbeatResponse()
      return
    }

    // Log da mensagem recebida
    logger.debug('Mensagem recebida via WebSocket:', data)

    // Emite evento específico do tipo
    this.emit(type, { data: messageData, timestamp })
    
    // Emite evento genérico de mensagem
    this.emit('message', data)
  }

  /**
   * Inicia heartbeat
   */
  startHeartbeat() {
    this.stopHeartbeat()
    
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected()) {
        this.lastHeartbeat = Date.now()
        this.send('ping')
        
        // Timeout para resposta do heartbeat
        this.heartbeatTimeout = setTimeout(() => {
          logger.warn('Heartbeat timeout - reconectando...')
          this.ws.close(1006, 'Heartbeat timeout')
        }, this.config.heartbeatTimeout)
      }
    }, this.config.heartbeatInterval)
  }

  /**
   * Para heartbeat
   */
  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
    
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout)
      this.heartbeatTimeout = null
    }
  }

  /**
   * Processa resposta do heartbeat
   */
  handleHeartbeatResponse() {
    if (this.heartbeatTimeout) {
      clearTimeout(this.heartbeatTimeout)
      this.heartbeatTimeout = null
    }
    
    const latency = Date.now() - this.lastHeartbeat
    this.emit('heartbeat', { latency })
  }

  /**
   * Verifica se deve reconectar
   */
  shouldReconnect() {
    return this.reconnectAttempts < this.config.maxReconnectAttempts
  }

  /**
   * Agenda reconexão
   */
  scheduleReconnect() {
    if (!this.shouldReconnect()) {
      logger.error('Máximo de tentativas de reconexão atingido')
      this.emit('maxReconnectAttemptsReached')
      return
    }

    this.reconnectAttempts++
    const delay = this.config.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1) // Backoff exponencial
    
    logger.info(`Tentativa de reconexão ${this.reconnectAttempts}/${this.config.maxReconnectAttempts} em ${delay}ms`)
    
    setTimeout(() => {
      if (!this.isManualClose) {
        this.connect(this.url).catch(error => {
          logger.error('Erro na tentativa de reconexão:', error)
        })
      }
    }, delay)
  }

  /**
   * Obtém estatísticas da conexão
   */
  getStats() {
    return {
      isConnected: this.isConnected(),
      reconnectAttempts: this.reconnectAttempts,
      lastHeartbeat: this.lastHeartbeat,
      url: this.url,
      readyState: this.ws ? this.ws.readyState : null,
      listeners: Array.from(this.listeners.keys())
    }
  }
}

// Instância singleton
const websocketService = new WebSocketService()

export default websocketService