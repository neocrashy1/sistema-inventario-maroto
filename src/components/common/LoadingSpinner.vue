<template>
  <div class="loading-spinner" role="status" aria-label="Carregando conteúdo">
    <div class="spinner">
      <div class="spinner-circle"></div>
    </div>
    <span class="loading-text" v-if="showText">{{ text }}</span>
  </div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    },
    text: {
      type: String,
      default: 'Carregando...'
    },
    showText: {
      type: Boolean,
      default: true
    },
    color: {
      type: String,
      default: 'primary'
    }
  }
}
</script>

<style scoped>
.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-md);
  min-height: 100px;
}

.spinner {
  position: relative;
  display: inline-block;
}

.spinner-circle {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top: 3px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* Tamanhos */
.loading-spinner[data-size="small"] .spinner-circle {
  width: 24px;
  height: 24px;
  border-width: 2px;
}

.loading-spinner[data-size="large"] .spinner-circle {
  width: 56px;
  height: 56px;
  border-width: 4px;
}

.loading-text {
  margin-top: var(--spacing-sm);
  font-size: 0.875rem;
  color: var(--text-muted);
  text-align: center;
}

/* Cores */
.loading-spinner[data-color="secondary"] .spinner-circle {
  border-top-color: var(--secondary-color);
}

.loading-spinner[data-color="success"] .spinner-circle {
  border-top-color: var(--success-color);
}

.loading-spinner[data-color="warning"] .spinner-circle {
  border-top-color: var(--warning-color);
}

.loading-spinner[data-color="danger"] .spinner-circle {
  border-top-color: var(--danger-color);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Acessibilidade */
@media (prefers-reduced-motion: reduce) {
  .spinner-circle {
    animation: none;
    border-top-color: var(--primary-color);
  }
  
  .loading-spinner::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    width: 8px;
    height: 8px;
    background: var(--primary-color);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    animation: pulse 1.5s ease-in-out infinite;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 1; }
}

/* Responsividade */
@media (max-width: 768px) {
  .loading-spinner {
    min-height: 80px;
    padding: var(--spacing-sm);
  }
  
  .loading-text {
    font-size: 0.8rem;
  }
}
</style>