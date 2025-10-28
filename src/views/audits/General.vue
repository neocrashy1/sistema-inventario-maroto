<template>
  <div class="general-audits">
    <!-- Page Header -->
    <div class="page-header">
      <div class="page-header-content">
        <h1 class="page-title">Auditoria Geral</h1>
        <p class="page-subtitle">Controle e acompanhamento de auditorias de ativos</p>
      </div>
      
      <div class="page-actions">
        <button class="btn btn-secondary">
          <i class="fas fa-download"></i>
          Exportar
        </button>
        <button class="btn btn-primary">
          <i class="fas fa-plus"></i>
          Nova Auditoria
        </button>
      </div>
    </div>
    
    <!-- Content -->
    <div class="content-placeholder">
      <div class="placeholder-icon">
        <i class="fas fa-search"></i>
      </div>
      <h3>Auditoria Geral</h3>
      <p>Este módulo está em desenvolvimento e será implementado em breve.</p>
    </div>
  </div>
</template>

<script setup>
// Component logic will be implemented
</script>

<style scoped>
.general-audits {
  padding: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-lg);
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.page-header-content h1 {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-xs) 0;
}

.page-header-content p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.875rem;
}

.page-actions {
  display: flex;
  gap: var(--spacing-md);
}

.content-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  background-color: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  text-align: center;
}

.placeholder-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: var(--success-color);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  margin-bottom: var(--spacing-lg);
}

.content-placeholder h3 {
  color: var(--text-primary);
  margin-bottom: var(--spacing-md);
}

.content-placeholder p {
  color: var(--text-muted);
  max-width: 400px;
}
</style>