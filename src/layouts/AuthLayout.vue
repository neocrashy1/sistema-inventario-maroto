<template>
  <div class="auth-layout">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <div class="logo">
            <i class="fas fa-cube"></i>
            <span>Sistema Inventario Levitiis</span>
          </div>
          <p class="subtitle">Sistema de Gerenciamento de Ativos</p>
        </div>
        
        <div class="auth-content">
          <router-view />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Layout para páginas de autenticação
</script>

<style scoped>
.auth-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-md);
}

.auth-container {
  width: 100%;
  max-width: 960px;
}

.auth-card {
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
}

.auth-header {
  padding: var(--spacing-2xl);
  text-align: center;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: var(--spacing-sm);
}

.logo i {
  font-size: 2rem;
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.875rem;
  margin: 0;
}

.auth-content {
  padding: var(--spacing-2xl);
}

/* Responsividade */
@media (max-width: 768px) {
  .auth-container {
    max-width: 100%;
  }
}

@media (min-width: 1200px) {
  .auth-container {
    max-width: 1100px;
  }
}
</style>