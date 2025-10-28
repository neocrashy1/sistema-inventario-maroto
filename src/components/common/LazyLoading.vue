<template>
  <div class="lazy-loading">
    <div class="loading-content">
      <div class="spinner">
        <div class="spinner-border" role="status">
          <span class="sr-only">Carregando...</span>
        </div>
      </div>
      <p class="loading-text">{{ message }}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LazyLoading',
  props: {
    message: {
      type: String,
      default: 'Carregando componente...'
    }
  }
}
</script>

<style scoped>
.lazy-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  padding: 2rem;
}

.loading-content {
  text-align: center;
}

.spinner {
  margin-bottom: 1rem;
}

.spinner-border {
  width: 3rem;
  height: 3rem;
  border: 0.25em solid #f3f3f3;
  border-top: 0.25em solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  color: #6c757d;
  font-size: 0.9rem;
  margin: 0;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>