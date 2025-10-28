<template>
  <div class="notification-center">
    <!-- Notification Bell -->
    <div class="notification-trigger" @click="toggleNotifications">
      <i class="fas fa-bell"></i>
      <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
    </div>

    <!-- Notifications Dropdown -->
    <transition name="slide-down">
      <div v-if="showNotifications" class="notifications-dropdown" @click.stop>
        <div class="notifications-header">
          <h3>Notificações</h3>
          <div class="header-actions">
            <button @click="markAllAsRead" class="mark-all-read">
              Marcar todas como lidas
            </button>
            <button @click="toggleNotifications" class="close-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
        </div>

        <div class="notifications-content">
          <div v-if="notifications.length === 0" class="no-notifications">
            <i class="fas fa-bell-slash"></i>
            <p>Nenhuma notificação</p>
          </div>

          <div v-else class="notifications-list">
            <div
              v-for="notification in notifications"
              :key="notification.id"
              :class="[
                'notification-item',
                { 'unread': !notification.read },
                `notification-${notification.type}`
              ]"
              @click="markAsRead(notification.id)"
            >
              <div class="notification-icon">
                <i :class="getNotificationIcon(notification.type)"></i>
              </div>
              
              <div class="notification-content">
                <h4>{{ notification.title }}</h4>
                <p>{{ notification.message }}</p>
                <span class="notification-time">
                  {{ formatTime(notification.timestamp) }}
                </span>
              </div>

              <div class="notification-actions">
                <button 
                  @click.stop="dismissNotification(notification.id)"
                  class="dismiss-btn"
                  title="Dispensar"
                >
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="notifications-footer">
          <router-link to="/alerts" class="view-all-link">
            Ver todos os alertas
          </router-link>
        </div>
      </div>
    </transition>

    <!-- Overlay -->
    <div 
      v-if="showNotifications" 
      class="notification-overlay" 
      @click="toggleNotifications"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'

const dashboardStore = useDashboardStore()

// Local state
const showNotifications = ref(false)

// Computed properties
const notifications = computed(() => dashboardStore.alerts)
const unreadCount = computed(() => 
  notifications.value.filter(n => !n.read).length
)

// Methods
const toggleNotifications = () => {
  showNotifications.value = !showNotifications.value
}

const markAsRead = (notificationId) => {
  dashboardStore.markAlertAsRead(notificationId)
}

const markAllAsRead = () => {
  notifications.value.forEach(notification => {
    if (!notification.read) {
      dashboardStore.markAlertAsRead(notification.id)
    }
  })
}

const dismissNotification = (notificationId) => {
  dashboardStore.dismissAlert(notificationId)
}

const getNotificationIcon = (type) => {
  const icons = {
    info: 'fas fa-info-circle',
    success: 'fas fa-check-circle',
    warning: 'fas fa-exclamation-triangle',
    error: 'fas fa-exclamation-circle'
  }
  return icons[type] || 'fas fa-bell'
}

const formatTime = (timestamp) => {
  const now = new Date()
  const time = new Date(timestamp)
  const diffInMinutes = Math.floor((now - time) / (1000 * 60))
  
  if (diffInMinutes < 1) return 'Agora'
  if (diffInMinutes < 60) return `${diffInMinutes}m atrás`
  
  const diffInHours = Math.floor(diffInMinutes / 60)
  if (diffInHours < 24) return `${diffInHours}h atrás`
  
  const diffInDays = Math.floor(diffInHours / 24)
  return `${diffInDays}d atrás`
}

// Close notifications when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.notification-center')) {
    showNotifications.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.notification-center {
  position: relative;
}

.notification-trigger {
  position: relative;
  padding: 8px;
  border-radius: 50%;
  background-color: transparent;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
  color: var(--text-secondary);
}

.notification-trigger:hover {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
}

.notification-trigger i {
  font-size: 1.25rem;
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: var(--color-danger);
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.notifications-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  width: 380px;
  max-height: 500px;
  background-color: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  overflow: hidden;
}

.notifications-header {
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--bg-secondary);
}

.notifications-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: var(--spacing-sm);
  align-items: center;
}

.mark-all-read {
  font-size: 0.875rem;
  color: var(--color-primary);
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  transition: background-color 0.2s;
}

.mark-all-read:hover {
  background-color: var(--color-primary-light);
}

.close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--text-secondary);
  border-radius: var(--radius-sm);
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: var(--bg-tertiary);
  color: var(--text-primary);
}

.notifications-content {
  max-height: 350px;
  overflow-y: auto;
}

.no-notifications {
  padding: var(--spacing-xl);
  text-align: center;
  color: var(--text-secondary);
}

.no-notifications i {
  font-size: 2rem;
  margin-bottom: var(--spacing-sm);
  opacity: 0.5;
}

.notification-item {
  display: flex;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  cursor: pointer;
  transition: background-color 0.2s;
}

.notification-item:hover {
  background-color: var(--bg-secondary);
}

.notification-item.unread {
  background-color: var(--color-primary-light);
  border-left: 3px solid var(--color-primary);
}

.notification-icon {
  margin-right: var(--spacing-sm);
  width: 24px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 2px;
}

.notification-info .notification-icon { color: var(--color-info); }
.notification-success .notification-icon { color: var(--color-success); }
.notification-warning .notification-icon { color: var(--color-warning); }
.notification-error .notification-icon { color: var(--color-danger); }

.notification-content {
  flex: 1;
}

.notification-content h4 {
  margin: 0 0 4px 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.notification-content p {
  margin: 0 0 4px 0;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

.notification-time {
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.notification-actions {
  margin-left: var(--spacing-sm);
}

.dismiss-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  color: var(--text-tertiary);
  border-radius: var(--radius-sm);
  transition: all 0.2s;
  opacity: 0;
}

.notification-item:hover .dismiss-btn {
  opacity: 1;
}

.dismiss-btn:hover {
  background-color: var(--color-danger-light);
  color: var(--color-danger);
}

.notifications-footer {
  padding: var(--spacing-sm) var(--spacing-md);
  border-top: 1px solid var(--border-color);
  background-color: var(--bg-secondary);
  text-align: center;
}

.view-all-link {
  color: var(--color-primary);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
}

.view-all-link:hover {
  text-decoration: underline;
}

.notification-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
}

/* Animations */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>