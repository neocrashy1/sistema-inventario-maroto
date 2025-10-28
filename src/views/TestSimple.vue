<template>
  <div class="test-page">
    <h1>Teste Simples</h1>
    <p>Esta é uma página de teste para verificar se o Vue está funcionando corretamente.</p>
    <button @click="showMessage">Clique aqui</button>
    <p v-if="message">{{ message }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const message = ref('')

const showMessage = () => {
  message.value = 'Vue está funcionando!'
}
</script>

<style scoped>
.test-page {
  padding: 2rem;
  text-align: center;
}

h1 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

button {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  margin: 1rem 0;
}

button:hover {
  background-color: #2980b9;
}
</style>