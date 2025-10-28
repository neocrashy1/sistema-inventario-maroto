<template>
  <div class="error-message" role="alert" :class="[`error-${type}`, { 'error-dismissible': dismissible }]">
    <div class="error-icon">
      <svg v-if="type === 'error'" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
        <line x1="15" y1="9" x2="9" y2="15" stroke="currentColor" stroke-width="2"/>
        <line x1="9" y1="9" x2="15" y2="15" stroke="currentColor" stroke-width="2"/>
      </svg>
      <svg v-else-if="type === 'warning'" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="m21.73 18-8-14a2 2 0 0 0-3.46 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" stroke="currentColor" stroke-width="2"/>
        <line x1="12" y1="9" x2="12" y2="13" stroke="currentColor" stroke-width="2"/>
        <circle cx="12" cy="17" r="1" fill="currentColor"/>
      </svg>
      <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
        <line x1="12" y1="8" x2="12" y2="12" stroke="currentColor" stroke-width="2"/>
        <circle cx="12" cy="16" r="1" fill="currentColor"/>
      </svg>
    </div>
    
    <div class="error-content">
      <h4 v-if="title" class="error-title">{{ title }}</h4>
      <p class="error-description">{{ message }}</p>
      
      <div v-if="details" class="error-details">
        <button 
          type="button" 
          class="details-toggle"
          @click="showDetails = !showDetails"
          :aria-expanded="showDetails"
        >
          {{ showDetails ? 'Ocultar detalhes' : 'Ver detalhes' }}
        </button>
        <div v-if="showDetails" class="details-content">
          <pre>{{ details }}</pre>
        </div>
      </div>
      
      <div v-if="actions.length > 0" class="error-actions">
        <button
          v-for="action in actions"
          :key="action.label"
          type="button"
          class="error-action"
          :class="action.variant || 'primary'"
          @click="action.handler"
        >
          {{ action.label }}
        </button>
      </div>
    </div>
    
    <button
      v-if="dismissible"
      type="button"
      class="error-dismiss"
      @click="$emit('dismiss')"
      aria-label="Fechar mensagem de erro"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
        <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
      </svg>
    </button>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'ErrorMessage',
  emits: ['dismiss'],
  props: {
    type: {
      type: String,
      default: 'error',
      validator: (value) => ['error', 'warning', 'info'].includes(value)
    },
    title: {
      type: String,
      default: ''
    },
    message: {
      type: String,
      default: 'Ocorreu um erro inesperado. Tente novamente.'
    },
    details: {
      type: String,
      default: ''
    },
    dismissible: {
      type: Boolean,
      default: true
    },
    actions: {
      type: Array,
      default: () => []
    }
  },
  setup() {
    const showDetails = ref(false)
    
    return {
      showDetails
    }
  }
}
</script>

<style scoped>
.error-message {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  border-radius: var(--border-radius);
  border: 1px solid;
  background-color: var(--background-color);
  position: relative;
}

.error-error {
  border-color: var(--danger-color);
  background-color: var(--danger-bg);
  color: var(--danger-text);
}

.error-warning {
  border-color: var(--warning-color);
  background-color: var(--warning-bg);
  color: var(--warning-text);
}

.error-info {
  border-color: var(--info-color);
  background-color: var(--info-bg);
  color: var(--info-text);
}

.error-icon {
  flex-shrink: 0;
  margin-top: 2px;
}

.error-content {
  flex: 1;
  min-width: 0;
}

.error-title {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
}

.error-description {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: 0.875rem;
  line-height: 1.5;
}

.error-details {
  margin-top: var(--spacing-sm);
}

.details-toggle {
  background: none;
  border: none;
  color: currentColor;
  text-decoration: underline;
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0;
}

.details-toggle:hover {
  text-decoration: none;
}

.details-content {
  margin-top: var(--spacing-xs);
  padding: var(--spacing-sm);
  background-color: rgba(0, 0, 0, 0.05);
  border-radius: var(--border-radius-sm);
  font-family: monospace;
  font-size: 0.8rem;
  overflow-x: auto;
}

.details-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
}

.error-actions {
  display: flex;
  gap: var(--spacing-xs);
  margin-top: var(--spacing-sm);
  flex-wrap: wrap;
}

.error-action {
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid transparent;
  border-radius: var(--border-radius-sm);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.error-action.primary {
  background-color: var(--primary-color);
  color: white;
}

.error-action.secondary {
  background-color: transparent;
  color: currentColor;
  border-color: currentColor;
}

.error-action:hover {
  opacity: 0.8;
  transform: translateY(-1px);
}

.error-dismiss {
  position: absolute;
  top: var(--spacing-sm);
  right: var(--spacing-sm);
  background: none;
  border: none;
  color: currentColor;
  cursor: pointer;
  padding: var(--spacing-xs);
  border-radius: var(--border-radius-sm);
  opacity: 0.7;
  transition: opacity 0.2s ease;
}

.error-dismiss:hover {
  opacity: 1;
}

.error-dismissible {
  padding-right: calc(var(--spacing-md) + 40px);
}

/* Responsividade */
@media (max-width: 768px) {
  .error-message {
    padding: var(--spacing-sm);
  }
  
  .error-actions {
    flex-direction: column;
  }
  
  .error-action {
    width: 100%;
    text-align: center;
  }
}

/* Acessibilidade */
@media (prefers-reduced-motion: reduce) {
  .error-action {
    transition: none;
  }
  
  .error-action:hover {
    transform: none;
  }
}
</style>