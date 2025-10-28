import logger from '@/utils/logger'
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  // Estado
  const loading = ref(false)
  const error = ref(null)
  
  // Configurações do sistema
  const settings = ref({
    general: {
      companyName: 'Levitiis',
      cnpj: '',
      address: '',
      phone: '',
      email: '',
      timezone: 'America/Sao_Paulo',
      language: 'pt-BR',
      dateFormat: 'DD/MM/YYYY',
      maintenanceMode: false
    },
    network: {
      scanInterval: 60,
      pingTimeout: 1000,
      scanNetworks: ['192.168.1.0/24'],
      autoDiscovery: true,
      ubiquiti: {
        enabled: false,
        controllerUrl: '',
        username: '',
        password: '',
        siteId: 'default'
      }
    },
    security: {
      sessionTimeout: 480,
      maxLoginAttempts: 3,
      lockoutTime: 15,
      requireStrongPassword: true,
      twoFactorAuth: false,
      logLevel: 'info',
      logRetention: 90,
      auditTrail: true
    },
    notifications: {
      email: {
        smtpServer: '',
        smtpPort: 587,
        smtpUser: '',
        smtpPassword: '',
        useSSL: true
      },
      types: {
        deviceDown: { email: true, system: true },
        newDevice: { email: false, system: true },
        systemError: { email: true, system: true },
        backup: { email: false, system: true },
        maintenance: { email: true, system: true }
      }
    },
    backup: {
      autoBackup: true,
      frequency: 'daily',
      time: '02:00',
      retention: 30
    }
  })

  // Histórico de backups
  const backupHistory = ref([
    {
      id: 1,
      date: '2024-01-15T02:00:00Z',
      type: 'Automático',
      status: 'Completo',
      size: '2.5 MB',
      duration: '45s',
      location: 'Local'
    },
    {
      id: 2,
      date: '2024-01-14T02:00:00Z',
      type: 'Automático',
      status: 'Completo',
      size: '2.4 MB',
      duration: '42s',
      location: 'Local'
    },
    {
      id: 3,
      date: '2024-01-13T15:30:00Z',
      type: 'Manual',
      status: 'Completo',
      size: '2.3 MB',
      duration: '38s',
      location: 'Local'
    }
  ])

  // Logs do sistema
  const systemLogs = ref([
    {
      id: 1,
      timestamp: '2024-01-15T10:30:00Z',
      level: 'info',
      category: 'settings',
      message: 'Configurações salvas com sucesso',
      user: 'admin@levitiis.com'
    },
    {
      id: 2,
      timestamp: '2024-01-15T09:15:00Z',
      level: 'warn',
      category: 'network',
      message: 'Timeout na descoberta de rede',
      user: 'system'
    },
    {
      id: 3,
      timestamp: '2024-01-15T08:00:00Z',
      level: 'info',
      category: 'backup',
      message: 'Backup automático executado com sucesso',
      user: 'system'
    }
  ])

  // Getters
  const isMaintenanceMode = computed(() => settings.value.general.maintenanceMode)
  
  const emailConfigured = computed(() => {
    const email = settings.value.notifications.email
    return email.smtpServer && email.smtpUser && email.smtpPassword
  })
  
  const ubiquitiConfigured = computed(() => {
    const ubiquiti = settings.value.network.ubiquiti
    return ubiquiti.enabled && ubiquiti.controllerUrl && ubiquiti.username
  })
  
  const backupStats = computed(() => {
    const total = backupHistory.value.length
    const successful = backupHistory.value.filter(b => b.status === 'Completo').length
    const failed = total - successful
    
    return {
      total,
      successful,
      failed,
      successRate: total > 0 ? Math.round((successful / total) * 100) : 0
    }
  })

  // Actions
  async function loadSettings() {
    loading.value = true
    error.value = null
    
    try {
      // Simular carregamento das configurações
      const savedSettings = localStorage.getItem('levitiis-settings')
      if (savedSettings) {
       const parsed = (() => { try { return JSON.parse(savedSettings) } catch { return null } })()
       if (parsed && typeof parsed === 'object') {
         settings.value = { ...settings.value, ...parsed }
       }
      }
      
      await new Promise(resolve => setTimeout(resolve, 500))
    } catch (err) {
      error.value = 'Erro ao carregar configurações'
      logger.error('Erro ao carregar configurações:', err)
    } finally {
      loading.value = false
    }
  }

  async function saveSettings(newSettings) {
    loading.value = true
    error.value = null
    
    try {
      // Simular salvamento das configurações
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      settings.value = { ...settings.value, ...newSettings }
      localStorage.setItem('levitiis-settings', JSON.stringify(settings.value))
      
      // Adicionar log
      addSystemLog('info', 'settings', 'Configurações salvas com sucesso')
      
      return { success: true, message: 'Configurações salvas com sucesso!' }
    } catch (err) {
      error.value = 'Erro ao salvar configurações'
      logger.error('Erro ao salvar configurações:', err)
      return { success: false, message: 'Erro ao salvar configurações' }
    } finally {
      loading.value = false
    }
  }

  async function testEmailConnection() {
    loading.value = true
    error.value = null
    
    try {
      // Simular teste de conexão de email
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const email = settings.value.notifications.email
      if (!email.smtpServer || !email.smtpUser) {
        throw new Error('Configurações de email incompletas')
      }
      
      addSystemLog('info', 'email', 'Teste de email executado com sucesso')
      return { success: true, message: 'Email de teste enviado com sucesso!' }
    } catch (err) {
      error.value = 'Erro no teste de email'
      addSystemLog('error', 'email', `Erro no teste de email: ${err.message}`)
      return { success: false, message: 'Erro no teste de email' }
    } finally {
      loading.value = false
    }
  }

  async function testUbiquitiConnection() {
    loading.value = true
    error.value = null
    
    try {
      // Simular teste de conexão Ubiquiti
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const ubiquiti = settings.value.network.ubiquiti
      if (!ubiquiti.controllerUrl || !ubiquiti.username) {
        throw new Error('Configurações Ubiquiti incompletas')
      }
      
      addSystemLog('info', 'ubiquiti', 'Teste de conexão Ubiquiti executado com sucesso')
      return { success: true, message: 'Conexão com Ubiquiti estabelecida com sucesso!' }
    } catch (err) {
      error.value = 'Erro no teste Ubiquiti'
      addSystemLog('error', 'ubiquiti', `Erro no teste Ubiquiti: ${err.message}`)
      return { success: false, message: 'Erro no teste de conexão Ubiquiti' }
    } finally {
      loading.value = false
    }
  }

  async function createBackup() {
    loading.value = true
    error.value = null
    
    try {
      // Simular criação de backup
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      const backup = {
        id: Date.now(),
        date: new Date().toISOString(),
        type: 'Manual',
        status: 'Completo',
        size: '2.6 MB',
        duration: '52s',
        location: 'Local'
      }
      
      backupHistory.value.unshift(backup)
      addSystemLog('info', 'backup', 'Backup manual criado com sucesso')
      
      return { success: true, message: 'Backup criado com sucesso!' }
    } catch (err) {
      error.value = 'Erro ao criar backup'
      addSystemLog('error', 'backup', `Erro ao criar backup: ${err.message}`)
      return { success: false, message: 'Erro ao criar backup' }
    } finally {
      loading.value = false
    }
  }

  async function restoreBackup(backupData) {
    loading.value = true
    error.value = null
    
    try {
      // Simular restauração de backup
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      if (backupData.settings) {
        settings.value = { ...settings.value, ...backupData.settings }
        localStorage.setItem('levitiis-settings', JSON.stringify(settings.value))
        
        addSystemLog('info', 'backup', 'Backup restaurado com sucesso')
        return { success: true, message: 'Backup restaurado com sucesso!' }
      } else {
        throw new Error('Arquivo de backup inválido')
      }
    } catch (err) {
      error.value = 'Erro ao restaurar backup'
      addSystemLog('error', 'backup', `Erro ao restaurar backup: ${err.message}`)
      return { success: false, message: 'Erro ao restaurar backup' }
    } finally {
      loading.value = false
    }
  }

  function exportBackup() {
    try {
      const backup = {
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        settings: settings.value,
        metadata: {
          exportedBy: 'admin@levitiis.com',
          systemVersion: '1.0.0'
        }
      }
      
      const dataStr = JSON.stringify(backup, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })
      
      const link = document.createElement('a')
      link.href = URL.createObjectURL(dataBlob)
      link.download = `levitiis-backup-${new Date().toISOString().split('T')[0]}.json`
      link.click()
      
      addSystemLog('info', 'backup', 'Backup exportado com sucesso')
      return { success: true, message: 'Backup exportado com sucesso!' }
    } catch (err) {
      error.value = 'Erro ao exportar backup'
      addSystemLog('error', 'backup', `Erro ao exportar backup: ${err.message}`)
      return { success: false, message: 'Erro ao exportar backup' }
    }
  }

  function addSystemLog(level, category, message, user = 'admin@levitiis.com') {
    const log = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      level,
      category,
      message,
      user
    }
    
    systemLogs.value.unshift(log)
    
    // Manter apenas os últimos 100 logs
    if (systemLogs.value.length > 100) {
      systemLogs.value = systemLogs.value.slice(0, 100)
    }
  }

  function clearSystemLogs() {
    systemLogs.value = []
    addSystemLog('info', 'system', 'Logs do sistema limpos')
  }

  function getSystemLogsByLevel(level) {
    return systemLogs.value.filter(log => log.level === level)
  }

  function getSystemLogsByCategory(category) {
    return systemLogs.value.filter(log => log.category === category)
  }

  return {
    // Estado
    loading,
    error,
    settings,
    backupHistory,
    systemLogs,
    
    // Getters
    isMaintenanceMode,
    emailConfigured,
    ubiquitiConfigured,
    backupStats,
    
    // Actions
    loadSettings,
    saveSettings,
    testEmailConnection,
    testUbiquitiConnection,
    createBackup,
    restoreBackup,
    exportBackup,
    addSystemLog,
    clearSystemLogs,
    getSystemLogsByLevel,
    getSystemLogsByCategory
  }
})
