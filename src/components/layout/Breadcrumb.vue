<template>
  <nav class="breadcrumb">
    <ol class="breadcrumb-list">
      <li 
        v-for="(item, index) in items" 
        :key="index"
        class="breadcrumb-item"
        :class="{ active: index === items.length - 1 }"
      >
        <router-link 
          v-if="item.to && index !== items.length - 1" 
          :to="item.to"
          class="breadcrumb-link"
        >
          {{ item.text }}
        </router-link>
        <span v-else class="breadcrumb-text">
          {{ item.text }}
        </span>
        
        <i 
          v-if="index < items.length - 1" 
          class="fas fa-chevron-right breadcrumb-separator"
        ></i>
      </li>
    </ol>
  </nav>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    required: true,
    default: () => []
  }
})
</script>

<style scoped>
.breadcrumb {
  margin-bottom: var(--spacing-lg);
}

.breadcrumb-list {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  list-style: none;
  margin: 0;
  padding: 0;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.breadcrumb-link {
  color: var(--text-muted);
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.2s ease;
}

.breadcrumb-link:hover {
  color: var(--primary-color);
}

.breadcrumb-text {
  color: var(--text-primary);
  font-size: 0.875rem;
  font-weight: 500;
}

.breadcrumb-item.active .breadcrumb-text {
  color: var(--text-primary);
}

.breadcrumb-separator {
  color: var(--text-muted);
  font-size: 0.75rem;
}
</style>