<template>
  <div class="error-fallback">
    <div class="error-content">
      <div class="error-icon">
        <i class="fas fa-exclamation-triangle"></i>
      </div>
      <h3 class="error-title">Erro ao Carregar Componente</h3>
      <p class="error-message">
        Ocorreu um erro ao carregar esta página. Verifique sua conexão com a internet e tente novamente.
      </p>
      <div class="error-actions">
        <button @click="reloadPage" class="btn btn-primary">
          <i class="fas fa-redo"></i>
          Recarregar Página
        </button>
        <button @click="goHome" class="btn btn-secondary">
          <i class="fas fa-home"></i>
          Ir para Dashboard
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ErrorFallback',
  methods: {
    reloadPage() {
      window.location.reload()
    },
    goHome() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.error-fallback {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 2rem;
  background-color: #f8f9fa;
}

.error-content {
  text-align: center;
  max-width: 500px;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.error-icon {
  font-size: 4rem;
  color: #dc3545;
  margin-bottom: 1rem;
}

.error-title {
  color: #343a40;
  margin-bottom: 1rem;
  font-size: 1.5rem;
  font-weight: 600;
}

.error-message {
  color: #6c757d;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary {
  background-color: #007bff;
  color: white;
}

.btn-primary:hover {
  background-color: #0056b3;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}

@media (max-width: 576px) {
  .error-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>