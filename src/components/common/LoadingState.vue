<template>
  <div class="loading-state" :class="{ 'overlay': overlay, 'inline': inline }">
    <div class="loading-content">
      <div class="loading-spinner" :class="size">
        <i class="fas fa-spinner fa-spin"></i>
      </div>
      <div v-if="message" class="loading-message">{{ message }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  // Mensagem de loading personalizada
  message: {
    type: String,
    default: 'Carregando...'
  },
  
  // Tamanho do spinner
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  
  // Se deve ser um overlay sobre o conteúdo
  overlay: {
    type: Boolean,
    default: false
  },
  
  // Se deve ser inline (sem posicionamento absoluto)
  inline: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  min-height: 200px;
}

.loading-state.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(2px);
  z-index: 1000;
  min-height: auto;
}

.loading-state.inline {
  min-height: auto;
  padding: 1rem;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loading-spinner {
  color: var(--primary-color, #3b82f6);
  animation: pulse 2s infinite;
}

.loading-spinner.small i {
  font-size: 1rem;
}

.loading-spinner.medium i {
  font-size: 1.5rem;
}

.loading-spinner.large i {
  font-size: 2rem;
}

.loading-message {
  color: var(--text-secondary, #6b7280);
  font-size: 0.875rem;
  font-weight: 500;
  text-align: center;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .loading-state.overlay {
    background: rgba(17, 24, 39, 0.9);
  }
  
  .loading-message {
    color: var(--text-secondary-dark, #9ca3af);
  }
}
</style>