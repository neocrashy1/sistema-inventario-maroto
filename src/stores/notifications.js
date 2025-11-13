import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useNotificationsStore = defineStore('notifications', () => {
  // State
  const notifications = ref([])
  const isConnected = ref(false)
  const lastUpdate = ref(null)

  // Computed
  const unreadCount = computed(() => {
    if (!Array.isArray(notifications.value)) return 0
    return notifications.value.filter(n => !n.read).length
  })

  const recentNotifications = computed(() => {
    if (!Array.isArray(notifications.value)) return []
    return notifications.value
      .sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
      .slice(0, 10)
  })

  // Actions
  const addNotification = (notification) => {
    const newNotification = {
      id: Date.now() + Math.random(),
      ...notification,
      read: false,
      createdAt: new Date().toISOString()
    }
    
    notifications.value.unshift(newNotification)
    
    // Limita a 100 notificações para evitar problemas de performance
    if (notifications.value.length > 100) {
      notifications.value = notifications.value.slice(0, 100)
    }
    
    // Mostra notificação do browser se permitido
    showBrowserNotification(newNotification)
  }

  const markAsRead = (notificationId) => {
    const notification = notifications.value.find(n => n.id === notificationId)
    if (notification) {
      notification.read = true
    }
  }

  const markAllAsRead = () => {
    notifications.value.forEach(n => n.read = true)
  }

  const removeNotification = (notificationId) => {
    const index = notifications.value.findIndex(n => n.id === notificationId)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearAll = () => {
    notifications.value = []
  }

  // Simula conexão WebSocket para notificações em tempo real
  const connectToNotifications = () => {
    if (isConnected.value) return

    isConnected.value = true
    lastUpdate.value = new Date().toISOString()

    // Simula recebimento de notificações periódicas
    const simulateNotifications = () => {
      const notificationTypes = [
        {
          type: 'asset_maintenance',
          title: 'Ativo em manutenção',
          icon: 'fas fa-tools',
          color: 'warning'
        },
        {
          type: 'loan_overdue',
          title: 'Empréstimo vencido',
          icon: 'fas fa-exclamation-triangle',
          color: 'danger'
        },
        {
          type: 'new_asset',
          title: 'Novo ativo cadastrado',
          icon: 'fas fa-plus-circle',
          color: 'success'
        },
        {
          type: 'audit_required',
          title: 'Auditoria necessária',
          icon: 'fas fa-clipboard-check',
          color: 'info'
        },
        {
          type: 'system_update',
          title: 'Atualização do sistema',
          icon: 'fas fa-sync-alt',
          color: 'primary'
        }
      ]

      // Simula notificação aleatória a cada 30-60 segundos
      const randomDelay = Math.random() * 30000 + 30000 // 30-60 segundos
      
      setTimeout(() => {
        if (isConnected.value) {
          const randomType = notificationTypes[Math.floor(Math.random() * notificationTypes.length)]
          const assetCodes = ['LVT-001', 'LVT-002', 'LVT-003', 'LVT-004', 'LVT-005']
          const userNames = ['João Silva', 'Maria Santos', 'Pedro Oliveira', 'Ana Costa']
          
          let message = ''
          switch (randomType.type) {
            case 'asset_maintenance':
              message = `${assetCodes[Math.floor(Math.random() * assetCodes.length)]} foi enviado para manutenção`
              break
            case 'loan_overdue':
              message = `Empréstimo para ${userNames[Math.floor(Math.random() * userNames.length)]} está vencido`
              break
            case 'new_asset':
              message = `Novo ativo ${assetCodes[Math.floor(Math.random() * assetCodes.length)]} foi cadastrado`
              break
            case 'audit_required':
              message = `Auditoria necessária para o setor de TI`
              break
            case 'system_update':
              message = `Nova versão do sistema disponível`
              break
          }

          addNotification({
            type: randomType.type,
            title: randomType.title,
            message,
            icon: randomType.icon,
            color: randomType.color,
            priority: Math.random() > 0.7 ? 'high' : 'normal'
          })

          simulateNotifications() // Agenda próxima notificação
        }
      }, randomDelay)
    }

    simulateNotifications()
  }

  const disconnectFromNotifications = () => {
    isConnected.value = false
  }

  // Notificações do browser
  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission()
      return permission === 'granted'
    }
    return false
  }

  const showBrowserNotification = (notification) => {
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification(notification.title, {
        body: notification.message,
        icon: '/favicon.ico',
        tag: notification.id
      })
    }
  }

  // Carrega notificações iniciais (simuladas)
  const loadInitialNotifications = () => {
    const initialNotifications = [
      {
        type: 'asset_maintenance',
        title: 'Ativo em manutenção',
        message: 'Notebook LVT-001 foi enviado para manutenção',
        icon: 'fas fa-tools',
        color: 'warning',
        priority: 'normal',
        read: false,
        createdAt: new Date(Date.now() - 1000 * 60 * 30).toISOString() // 30 min ago
      },
      {
        type: 'loan_overdue',
        title: 'Empréstimo vencido',
        message: 'Monitor LVT-002 emprestado para João Silva está vencido',
        icon: 'fas fa-exclamation-triangle',
        color: 'danger',
        priority: 'high',
        read: false,
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString() // 2 hours ago
      },
      {
        type: 'new_asset',
        title: 'Novo ativo cadastrado',
        message: 'Impressora HP LaserJet foi adicionada ao sistema',
        icon: 'fas fa-plus-circle',
        color: 'success',
        priority: 'normal',
        read: true,
        createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString() // 1 day ago
      }
    ]

    notifications.value = initialNotifications.map(n => ({
      id: Date.now() + Math.random(),
      ...n
    }))
  }

  return {
    // State
    notifications,
    isConnected,
    lastUpdate,
    
    // Computed
    unreadCount,
    recentNotifications,
    
    // Actions
    addNotification,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
    connectToNotifications,
    disconnectFromNotifications,
    requestNotificationPermission,
    loadInitialNotifications
  }
})