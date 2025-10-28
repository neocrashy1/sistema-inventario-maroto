<template>
  <div class="test-charts">
    <h1>Teste dos Gráficos</h1>
    
    <div class="chart-container">
      <h2>Sistema funcionando!</h2>
      <p>Os componentes de gráficos serão testados em breve.</p>
      
      <div class="test-data">
        <h3>Dados de Teste:</h3>
        <ul>
          <li v-for="item in testData" :key="item.label">
            {{ item.label }}: {{ item.value }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const testData = ref([
  { label: 'Categoria A', value: 30 },
  { label: 'Categoria B', value: 25 },
  { label: 'Categoria C', value: 20 },
  { label: 'Categoria D', value: 25 }
])
</script>

<style scoped>
.test-charts {
  padding: 20px;
}

.chart-container {
  margin: 20px 0;
  padding: 20px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
}

h1, h2 {
  color: #374151;
}
</style>