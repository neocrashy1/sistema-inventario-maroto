// Serviço para integração com Ubiquiti UniFi Controller
import logger from '@/utils/logger'
class UbiquitiService {
  constructor() {
    this.baseUrl = ''
    this.username = ''
    this.password = ''
    this.site = 'default'
    this.sessionCookie = null
    this.isAuthenticated = false
  }

  // Configura credenciais do UniFi Controller
  configure(config) {
    this.baseUrl = config.baseUrl?.replace(/\/$/, '') // Remove trailing slash
    this.username = config.username
    this.password = config.password
    this.site = config.site || 'default'
  }

  // Autentica no UniFi Controller
  async authenticate() {
    try {
      const response = await fetch(`${this.baseUrl}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: this.username,
          password: this.password,
          remember: false
        }),
        credentials: 'include'
      })

      if (response.ok) {
        const data = await response.json()
        this.isAuthenticated = true
        
        // Extrai cookie de sessão
        const cookies = response.headers.get('set-cookie')
        if (cookies) {
          this.sessionCookie = cookies
        }
        
        return { success: true, data }
      } else {
        throw new Error(`Falha na autenticação: ${response.status}`)
      }
    } catch (error) {
      logger.error('Erro na autenticação Ubiquiti:', error)
      this.isAuthenticated = false
      return { success: false, error: error.message }
    }
  }

  // Faz logout do UniFi Controller
  async logout() {
    try {
      await fetch(`${this.baseUrl}/api/logout`, {
        method: 'POST',
        credentials: 'include'
      })
      
      this.isAuthenticated = false
      this.sessionCookie = null
    } catch (error) {
      logger.error('Erro no logout:', error)
    }
  }

  // Busca todos os clientes conectados
  async getClients() {
    if (!this.isAuthenticated) {
      const authResult = await this.authenticate()
      if (!authResult.success) {
        return { success: false, error: 'Falha na autenticação' }
      }
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/s/${this.site}/stat/sta`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        const clients = this.parseClients(data.data || [])
        return { success: true, data: clients }
      } else {
        throw new Error(`Erro ao buscar clientes: ${response.status}`)
      }
    } catch (error) {
      logger.error('Erro ao buscar clientes Ubiquiti:', error)
      return { success: false, error: error.message }
    }
  }

  // Busca dispositivos UniFi (APs, Switches, etc.)
  async getDevices() {
    if (!this.isAuthenticated) {
      const authResult = await this.authenticate()
      if (!authResult.success) {
        return { success: false, error: 'Falha na autenticação' }
      }
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/s/${this.site}/stat/device`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      })

      if (response.ok) {
        const data = await response.json()
        const devices = this.parseDevices(data.data || [])
        return { success: true, data: devices }
      } else {
        throw new Error(`Erro ao buscar dispositivos: ${response.status}`)
      }
    } catch (error) {
      logger.error('Erro ao buscar dispositivos Ubiquiti:', error)
      return { success: false, error: error.message }
    }
  }

  // Busca informações de rede
  async getNetworkInfo() {
    if (!this.isAuthenticated) {
      const authResult = await this.authenticate()
      if (!authResult.success) {
        return { success: false, error: 'Falha na autenticação' }
      }
    }

    try {
      const [clientsResult, devicesResult] = await Promise.all([
        this.getClients(),
        this.getDevices()
      ])

      const networkInfo = {
        clients: clientsResult.success ? clientsResult.data : [],
        devices: devicesResult.success ? devicesResult.data : [],
        totalDevices: 0,
        onlineDevices: 0,
        offlineDevices: 0
      }

      // Combina clientes e dispositivos
      const allDevices = [...networkInfo.clients, ...networkInfo.devices]
      networkInfo.totalDevices = allDevices.length
      networkInfo.onlineDevices = allDevices.filter(d => d.isOnline).length
      networkInfo.offlineDevices = allDevices.filter(d => !d.isOnline).length

      return { success: true, data: networkInfo }
    } catch (error) {
      logger.error('Erro ao buscar informações de rede:', error)
      return { success: false, error: error.message }
    }
  }

  // Testa conectividade com o controller
  async testConnection() {
    try {
      const response = await fetch(`${this.baseUrl}/api/self`, {
        method: 'GET',
        timeout: 5000
      })

      return {
        success: response.ok,
        status: response.status,
        message: response.ok ? 'Conexão bem-sucedida' : 'Falha na conexão'
      }
    } catch (error) {
      return {
        success: false,
        status: 0,
        message: `Erro de conexão: ${error.message}`
      }
    }
  }

  // Converte dados de clientes para formato padrão
  parseClients(clients) {
    return clients.map(client => ({
      id: client._id,
      hostname: client.hostname || client.name || 'Unknown',
      ip: client.ip,
      mac: client.mac,
      manufacturer: this.getManufacturerFromOUI(client.oui) || 'Unknown',
      model: client.model || 'Unknown',
      deviceType: this.detectDeviceType(client),
      isOnline: client.is_online || false,
      lastSeen: client.last_seen ? new Date(client.last_seen * 1000).toISOString() : null,
      signalStrength: client.rssi || null,
      connectionType: client.is_wired ? 'Wired' : 'Wireless',
      network: client.network || 'Unknown',
      apMac: client.ap_mac || null,
      userAgent: client.os_name || null,
      source: 'ubiquiti-client',
      ubiquitiData: {
        userId: client.user_id,
        siteId: client.site_id,
        experience: client.satisfaction,
        bytesReceived: client.rx_bytes,
        bytesTransmitted: client.tx_bytes,
        packetsReceived: client.rx_packets,
        packetsTransmitted: client.tx_packets
      }
    }))
  }

  // Converte dados de dispositivos para formato padrão
  parseDevices(devices) {
    return devices.map(device => ({
      id: device._id,
      hostname: device.name || device.hostname || 'Unknown',
      ip: device.ip,
      mac: device.mac,
      manufacturer: 'Ubiquiti Inc.',
      model: device.model || 'Unknown',
      deviceType: this.getUbiquitiDeviceType(device.type),
      isOnline: device.state === 1,
      lastSeen: device.last_seen ? new Date(device.last_seen * 1000).toISOString() : null,
      firmwareVersion: device.version || null,
      serialNumber: device.serial || null,
      connectionType: 'Wired',
      source: 'ubiquiti-device',
      ubiquitiData: {
        type: device.type,
        adopted: device.adopted,
        cfgVersion: device.cfgversion,
        configNetwork: device.config_network,
        connectRequestIp: device.connect_request_ip,
        connectRequestPort: device.connect_request_port,
        deviceId: device.device_id,
        knownCfgVersion: device.known_cfgversion,
        locating: device.locating,
        provisionedAt: device.provisioned_at,
        requiredVersion: device.required_version,
        rollupgrade: device.rollupgrade,
        setupId: device.setup_id,
        startConnectedMillis: device.start_connected_millis,
        startDisconnectedMillis: device.start_disconnected_millis,
        startupTimestamp: device.startup_timestamp,
        state: device.state,
        twoPhaseAdopt: device.two_phase_adopt,
        upgradable: device.upgradable,
        upgradeToFirmware: device.upgrade_to_firmware,
        uplink: device.uplink,
        uptime: device.uptime,
        version: device.version
      }
    }))
  }

  // Detecta tipo de dispositivo baseado nos dados do cliente
  detectDeviceType(client) {
    const hostname = (client.hostname || '').toLowerCase()
    const name = (client.name || '').toLowerCase()
    const osName = (client.os_name || '').toLowerCase()

    // Detecta por sistema operacional
    if (osName.includes('windows')) return 'Computer'
    if (osName.includes('macos') || osName.includes('mac os')) return 'Computer'
    if (osName.includes('linux')) return 'Computer'
    if (osName.includes('android')) return 'Mobile'
    if (osName.includes('ios')) return 'Mobile'

    // Detecta por hostname/nome
    if (hostname.includes('printer') || name.includes('printer')) return 'Printer'
    if (hostname.includes('camera') || name.includes('camera')) return 'Camera'
    if (hostname.includes('phone') || name.includes('phone')) return 'Phone'
    if (hostname.includes('tablet') || name.includes('tablet')) return 'Tablet'
    if (hostname.includes('tv') || name.includes('tv')) return 'TV'
    if (hostname.includes('chromecast') || name.includes('chromecast')) return 'Media Device'

    // Detecta por tipo de conexão
    if (client.is_wired) return 'Computer'

    return 'Unknown'
  }

  // Converte tipo de dispositivo Ubiquiti
  getUbiquitiDeviceType(type) {
    const typeMap = {
      'uap': 'Access Point',
      'usw': 'Switch',
      'ugw': 'Gateway',
      'usg': 'Security Gateway',
      'uck': 'Cloud Key',
      'udm': 'Dream Machine',
      'unvr': 'NVR',
      'uap-ac': 'Access Point',
      'uap-hd': 'Access Point',
      'uap-pro': 'Access Point'
    }

    return typeMap[type] || 'Network Device'
  }

  // Obtém fabricante a partir do OUI (simplificado)
  getManufacturerFromOUI(oui) {
    if (!oui) return null

    const ouiMap = {
      '00:50:56': 'VMware',
      '08:00:27': 'Oracle VirtualBox',
      '00:0C:29': 'VMware',
      '00:1B:21': 'Intel',
      '00:15:5D': 'Microsoft',
      '52:54:00': 'QEMU',
      '00:16:3E': 'Xen',
      'F4:8E:38': 'Ubiquiti',
      '24:5A:4C': 'Ubiquiti',
      '04:18:D6': 'Ubiquiti',
      '68:D7:9A': 'Ubiquiti',
      'B4:FB:E4': 'Ubiquiti',
      '78:8A:20': 'Ubiquiti',
      '80:2A:A8': 'Ubiquiti'
    }

    return ouiMap[oui.toUpperCase()] || null
  }

  // Simula dados para desenvolvimento/teste
  async getMockData() {
    // Simula delay de rede
    await new Promise(resolve => setTimeout(resolve, 1000))

    return {
      success: true,
      data: {
        clients: [
          {
            id: 'mock-client-1',
            hostname: 'DESKTOP-ABC123',
            ip: '192.168.1.100',
            mac: '00:11:22:33:44:55',
            manufacturer: 'Intel',
            model: 'Unknown',
            deviceType: 'Computer',
            isOnline: true,
            lastSeen: new Date().toISOString(),
            connectionType: 'Wireless',
            source: 'ubiquiti-client'
          },
          {
            id: 'mock-client-2',
            hostname: 'iPhone-John',
            ip: '192.168.1.101',
            mac: '00:11:22:33:44:56',
            manufacturer: 'Apple',
            model: 'iPhone',
            deviceType: 'Mobile',
            isOnline: true,
            lastSeen: new Date().toISOString(),
            connectionType: 'Wireless',
            source: 'ubiquiti-client'
          }
        ],
        devices: [
          {
            id: 'mock-device-1',
            hostname: 'UniFi-AP-Living',
            ip: '192.168.1.10',
            mac: 'F4:8E:38:11:22:33',
            manufacturer: 'Ubiquiti Inc.',
            model: 'UAP-AC-PRO',
            deviceType: 'Access Point',
            isOnline: true,
            lastSeen: new Date().toISOString(),
            connectionType: 'Wired',
            source: 'ubiquiti-device'
          }
        ],
        totalDevices: 3,
        onlineDevices: 3,
        offlineDevices: 0
      }
    }
  }
}

export default new UbiquitiService()