<template>
  <div id="app">
    <Suspense>
      <template #default>
        <router-view />
      </template>
      <template #fallback>
        <LazyLoading message="Carregando página..." />
      </template>
    </Suspense>
    <ToastContainer position="top-right" />
    <AccessibilityToolbar />
  </div>
</template>

<script setup>
import { Suspense } from 'vue'
import ToastContainer from '@/components/common/ToastContainer.vue'
import LazyLoading from '@/components/common/LazyLoading.vue'
import AccessibilityToolbar from '@/components/common/AccessibilityToolbar.vue'
import { useTheme } from '@/composables/useTheme'

// Inicializar tema global no mount da aplicação
useTheme()
</script>

<style>
#app {
  font-family: 'Inter', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  height: 100vh;
  width: 100vw;
}
</style>