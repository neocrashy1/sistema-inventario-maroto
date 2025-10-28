<template>
  <div class="main-layout">
    <!-- Mobile overlay -->
    <div 
      class="mobile-overlay" 
      :class="{ active: mobileMenuOpen }"
      @click="closeMobileMenu"
    ></div>
    
    <!-- Sidebar -->
    <Sidebar 
      :is-collapsed="sidebarCollapsed"
      :mobile-open="mobileMenuOpen"
      @toggle="toggleSidebar"
      @close-mobile="closeMobileMenu"
    />
    
    <!-- Main Content -->
    <div class="main-content" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <!-- Header -->
      <Header 
        :sidebar-collapsed="sidebarCollapsed"
        @toggle-sidebar="toggleSidebar"
        @toggle-mobile-menu="toggleMobileMenu"
      />
      
      <!-- Page Content -->
      <main class="page-content">
        <!-- Breadcrumb -->
        <Breadcrumb v-if="$route.meta.breadcrumb" :items="$route.meta.breadcrumb" />
        
        <!-- Page -->
        <div class="page-container">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import Sidebar from '@/components/layout/Sidebar.vue'
import Header from '@/components/layout/Header.vue'
import Breadcrumb from '@/components/layout/Breadcrumb.vue'

// State
const sidebarCollapsed = ref(false)
const mobileMenuOpen = ref(false)

// Methods
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  background-color: var(--bg-secondary);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 280px;
  transition: margin-left 0.3s ease;
}

.main-content.sidebar-collapsed {
  margin-left: 80px;
}

.page-content {
  flex: 1;
  padding: var(--spacing-lg);
  overflow-y: auto;
}

.page-container {
  max-width: 1400px;
  margin: 0 auto;
}

.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 998;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.3s ease, visibility 0.3s ease;
}

.mobile-overlay.active {
  opacity: 1;
  visibility: visible;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
  
  .main-content.sidebar-collapsed {
    margin-left: 0;
  }
}
</style>