<template>
  <Teleport to="body">
    <div class="toast-container" :class="`toast-container--${position}`">
      <TransitionGroup name="toast" tag="div">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'toast',
            `toast--${toast.type}`,
            { 'toast--visible': toast.isVisible }
          ]"
          @mouseenter="handleMouseEnter(toast)"
          @mouseleave="handleMouseLeave(toast)"
        >
          <!-- Ícone do tipo -->
          <div class="toast__icon">
            <i :class="getIconClass(toast.type)"></i>
          </div>
          
          <!-- Conteúdo -->
          <div class="toast__content">
            <div class="toast__message">{{ toast.message }}</div>
            <div v-if="toast.details" class="toast__details">
              {{ toast.details }}
            </div>
          </div>
          
          <!-- Botão de fechar -->
          <button
            v-if="toast.showCloseButton"
            class="toast__close"
            @click="removeToast(toast.id)"
            aria-label="Fechar notificação"
          >
            <i class="fas fa-times"></i>
          </button>
          
          <!-- Barra de progresso -->
          <div
            v-if="toast.duration > 0"
            class="toast__progress"
            :class="{ 'toast__progress--paused': toast.isPaused }"
            :style="{ animationDuration: `${toast.duration}ms` }"
          ></div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  position: {
    type: String,
    default: 'top-right',
    validator: (value) => [
      'top-left', 'top-center', 'top-right',
      'bottom-left', 'bottom-center', 'bottom-right'
    ].includes(value)
  }
})

const { toasts, removeToast, pauseToast, resumeToast } = useToast()

// Filtrar toasts visíveis
const visibleToasts = computed(() => 
  toasts.filter(toast => toast.isVisible)
)

// Obter classe do ícone baseado no tipo
function getIconClass(type) {
  const iconMap = {
    success: 'fas fa-check-circle',
    error: 'fas fa-exclamation-circle',
    warning: 'fas fa-exclamation-triangle',
    info: 'fas fa-info-circle'
  }
  return iconMap[type] || iconMap.info
}

// Manipular hover para pausar/resumir
function handleMouseEnter(toast) {
  if (toast.pauseOnHover && !toast.isPaused) {
    pauseToast(toast.id)
  }
}

function handleMouseLeave(toast) {
  if (toast.pauseOnHover && toast.isPaused) {
    resumeToast(toast.id)
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  z-index: 9999;
  pointer-events: none;
  max-width: 400px;
  width: 100%;
}

/* Posicionamento */
.toast-container--top-left {
  top: 1rem;
  left: 1rem;
}

.toast-container--top-center {
  top: 1rem;
  left: 50%;
  transform: translateX(-50%);
}

.toast-container--top-right {
  top: 1rem;
  right: 1rem;
}

.toast-container--bottom-left {
  bottom: 1rem;
  left: 1rem;
}

.toast-container--bottom-center {
  bottom: 1rem;
  left: 50%;
  transform: translateX(-50%);
}

.toast-container--bottom-right {
  bottom: 1rem;
  right: 1rem;
}

/* Toast */
.toast {
  position: relative;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  margin-bottom: 0.5rem;
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  border-left: 4px solid;
  pointer-events: auto;
  overflow: hidden;
  max-width: 100%;
  word-wrap: break-word;
}

/* Tipos de toast */
.toast--success {
  border-left-color: var(--success-color);
}

.toast--error {
  border-left-color: var(--danger-color);
}

.toast--warning {
  border-left-color: var(--warning-color);
}

.toast--info {
  border-left-color: var(--info-color);
}

/* Ícone */
.toast__icon {
  flex-shrink: 0;
  width: 1.25rem;
  height: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 0.125rem;
}

.toast--success .toast__icon {
  color: var(--success-color);
}

.toast--error .toast__icon {
  color: var(--danger-color);
}

.toast--warning .toast__icon {
  color: var(--warning-color);
}

.toast--info .toast__icon {
  color: var(--info-color);
}

/* Conteúdo */
.toast__content {
  flex: 1;
  min-width: 0;
}

.toast__message {
  font-weight: 500;
  color: var(--text-primary);
  line-height: 1.4;
  margin-bottom: 0.25rem;
}

.toast__details {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.4;
}

/* Botão de fechar */
.toast__close {
  flex-shrink: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.toast__close:hover {
  color: var(--text-primary);
  background-color: var(--bg-secondary);
}

/* Barra de progresso */
.toast__progress {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, rgba(0, 0, 0, 0.1));
  animation: toast-progress linear forwards;
  transform-origin: left;
}

.toast--success .toast__progress {
  background: linear-gradient(90deg, var(--success-color), rgba(16, 185, 129, 0.3));
}

.toast--error .toast__progress {
  background: linear-gradient(90deg, var(--danger-color), rgba(239, 68, 68, 0.3));
}

.toast--warning .toast__progress {
  background: linear-gradient(90deg, #f59e0b, rgba(245, 158, 11, 0.3));
}

.toast--info .toast__progress {
  background: linear-gradient(90deg, #3b82f6, rgba(59, 130, 246, 0.3));
}

.toast__progress--paused {
  animation-play-state: paused;
}

/* Animações */
@keyframes toast-progress {
  from {
    transform: scaleX(1);
  }
  to {
    transform: scaleX(0);
  }
}

/* Transições */
.toast-enter-active {
  transition: all 0.3s ease-out;
}

.toast-leave-active {
  transition: all 0.3s ease-in;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

/* Responsividade */
@media (max-width: 640px) {
  .toast-container {
    left: 1rem !important;
    right: 1rem !important;
    max-width: none;
    transform: none !important;
  }
  
  .toast {
    margin-bottom: 0.75rem;
  }
}

/* Modo escuro */
@media (prefers-color-scheme: dark) {
  .toast {
    background: #1f2937;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  }
  
  .toast__message {
    color: #f9fafb;
  }
  
  .toast__details {
    color: #d1d5db;
  }
  
  .toast__close {
    color: #9ca3af;
  }
  
  .toast__close:hover {
    color: #d1d5db;
    background-color: #374151;
  }
}
</style>