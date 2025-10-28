<template>
  <div>
    <!-- Redirect to movements/Movements.vue -->
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  // Redirect to the actual movements page
  router.replace('/movements/list')
})
</script>