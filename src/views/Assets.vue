<template>
  <div>
    <!-- Redirect to assets/Assets.vue -->
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

onMounted(() => {
  // Redirect to the actual assets page
  router.replace('/assets/list')
})
</script>