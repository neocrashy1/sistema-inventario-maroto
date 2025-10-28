<template>
  <div class="optimized-virtual-list" :class="{ 'is-loading': loading }">
    <!-- Header com controles -->
    <div v-if="showHeader" class="virtual-list-header">
      <div class="header-left">
        <slot name="header-left">
          <span class="item-count">{{ totalItemsText }}</span>
        </slot>
      </div>
      
      <div class="header-center">
        <slot name="header-center">
          <!-- Search input -->
          <div v-if="searchable" class="search-container">
            <input
              v-model="searchQuery"
              type="text"
              :placeholder="searchPlaceholder"
              class="search-input"
              @input="debouncedSearch"
              @keydown.escape="clearSearch"
            />
            <button
              v-if="searchQuery"
              @click="clearSearch"
              class="clear-search"
              type="button"
            >
              ×
            </button>
          </div>
        </slot>
      </div>
      
      <div class="header-right">
        <slot name="header-right">
          <!-- View controls -->
          <div class="view-controls">
            <button
              @click="toggleDensity"
              class="density-toggle"
              :title="densityText"
              type="button"
            >
              ⋮⋮⋮
            </button>
          </div>
        </slot>
      </div>
    </div>

    <!-- Virtual scroll viewport -->
    <div
      ref="viewportRef"
      class="virtual-viewport"
      :style="viewportStyle"
      @scroll="handleScroll"
      @wheel="handleWheel"
      role="listbox"
      :aria-label="ariaLabel"
      tabindex="0"
      @keydown="handleKeydown"
    >
      <!-- Scroll container -->
      <div
        class="scroll-container"
        :style="{ height: totalHeight + 'px' }"
      >
        <!-- Visible items -->
        <div
          class="items-container"
          :style="{ transform: `translateY(${offsetY}px)` }"
        >
          <div
            v-for="(item, index) in visibleItems"
            :key="getItemKey(item.data, item.index)"
            :data-index="item.index"
            class="virtual-item"
            :class="[
              `density-${density}`,
              { 
                'is-selected': isSelected(item.data),
                'is-highlighted': highlightedIndex === item.index,
                'is-even': item.index % 2 === 0,
                'is-odd': item.index % 2 === 1
              }
            ]"
            :style="getItemStyle(item)"
            @click="handleItemClick(item.data, item.index)"
            @mouseenter="handleItemHover(item.index)"
            @mouseleave="handleItemLeave"
            role="option"
            :aria-selected="isSelected(item.data)"
            :aria-posinset="item.index + 1"
            :aria-setsize="totalItems"
          >
            <!-- Item content slot -->
            <slot
              name="item"
              :item="item.data"
              :index="item.index"
              :selected="isSelected(item.data)"
              :highlighted="highlightedIndex === item.index"
            >
              <!-- Default item content -->
              <div class="default-item-content">
                {{ getItemLabel(item.data) }}
              </div>
            </slot>
          </div>
        </div>
      </div>

      <!-- Loading indicator -->
      <div
        v-if="loading && visibleItems.length > 0"
        class="loading-indicator"
        role="status"
        aria-label="Carregando mais itens"
      >
        <div class="loading-spinner"></div>
        <span class="loading-text">{{ loadingText }}</span>
      </div>

      <!-- Empty state -->
      <div
        v-if="!loading && filteredItems.length === 0"
        class="empty-state"
        role="status"
      >
        <slot name="empty">
          <div class="empty-content">
            <div class="empty-icon">📭</div>
            <p class="empty-text">{{ emptyText }}</p>
          </div>
        </slot>
      </div>
    </div>

    <!-- Footer com informações -->
    <div v-if="showFooter" class="virtual-list-footer">
      <slot name="footer">
        <div class="footer-info">
          <span class="visible-range">
            {{ visibleRangeText }}
          </span>
          <span v-if="showPerformanceMetrics" class="performance-metrics">
            Render: {{ renderTime }}ms | FPS: {{ fps }}
          </span>
        </div>
      </slot>
    </div>

    <!-- Scroll to top button -->
    <transition name="fade">
      <button
        v-if="showScrollToTop && scrollTop > viewportHeight"
        @click="scrollToTop"
        class="scroll-to-top"
        type="button"
        aria-label="Voltar ao topo"
      >
        ↑
      </button>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { debounce } from '@/utils/debounce'

// Props
const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  itemHeight: {
    type: [Number, Function],
    default: 50
  },
  viewportHeight: {
    type: Number,
    default: 400
  },
  buffer: {
    type: Number,
    default: 10
  },
  threshold: {
    type: Number,
    default: 0.8
  },
  searchable: {
    type: Boolean,
    default: false
  },
  searchPlaceholder: {
    type: String,
    default: 'Pesquisar...'
  },
  searchFields: {
    type: Array,
    default: () => ['name', 'title', 'label']
  },
  keyField: {
    type: String,
    default: 'id'
  },
  labelField: {
    type: String,
    default: 'name'
  },
  selectedItems: {
    type: Array,
    default: () => []
  },
  loadingText: {
    type: String,
    default: 'Carregando...'
  },
  emptyText: {
    type: String,
    default: 'Nenhum item encontrado'
  },
  ariaLabel: {
    type: String,
    default: 'Lista virtual'
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showFooter: {
    type: Boolean,
    default: true
  },
  showScrollToTop: {
    type: Boolean,
    default: true
  },
  showPerformanceMetrics: {
    type: Boolean,
    default: false
  },
  enableVirtualization: {
    type: Boolean,
    default: true
  },
  density: {
    type: String,
    default: 'normal',
    validator: (value) => ['compact', 'normal', 'comfortable'].includes(value)
  }
})

// Emits
const emit = defineEmits([
  'load-more',
  'item-click',
  'item-hover',
  'selection-change',
  'search',
  'scroll',
  'density-change'
])

// Reactive state
const viewportRef = ref(null)
const scrollTop = ref(0)
const searchQuery = ref('')
const loading = ref(false)
const highlightedIndex = ref(-1)
const currentDensity = ref(props.density)

// Performance tracking
const renderTime = ref(0)
const fps = ref(0)
const lastFrameTime = ref(0)
const frameCount = ref(0)

// Computed properties
const actualItemHeight = computed(() => {
  const densityMultiplier = {
    compact: 0.8,
    normal: 1,
    comfortable: 1.2
  }
  
  const baseHeight = typeof props.itemHeight === 'function' 
    ? props.itemHeight 
    : props.itemHeight
    
  return Math.round(baseHeight * densityMultiplier[currentDensity.value])
})

const filteredItems = computed(() => {
  if (!searchQuery.value || !props.searchable) {
    return props.items
  }
  
  const query = searchQuery.value.toLowerCase()
  return props.items.filter(item => {
    return props.searchFields.some(field => {
      const value = item[field]
      return value && String(value).toLowerCase().includes(query)
    })
  })
})

const totalItems = computed(() => filteredItems.value.length)

const visibleCount = computed(() => {
  return Math.ceil(props.viewportHeight / actualItemHeight.value) + props.buffer * 2
})

const startIndex = computed(() => {
  if (!props.enableVirtualization) return 0
  
  const index = Math.floor(scrollTop.value / actualItemHeight.value) - props.buffer
  return Math.max(0, index)
})

const endIndex = computed(() => {
  if (!props.enableVirtualization) return filteredItems.value.length
  
  const index = startIndex.value + visibleCount.value
  return Math.min(filteredItems.value.length, index)
})

const visibleItems = computed(() => {
  const start = performance.now()
  
  const items = filteredItems.value
    .slice(startIndex.value, endIndex.value)
    .map((item, index) => {
      const actualIndex = startIndex.value + index
      return {
        data: item,
        index: actualIndex,
        top: actualIndex * actualItemHeight.value,
        height: typeof props.itemHeight === 'function' 
          ? props.itemHeight(item, actualIndex)
          : actualItemHeight.value
      }
    })
  
  renderTime.value = Math.round((performance.now() - start) * 100) / 100
  return items
})

const totalHeight = computed(() => {
  return filteredItems.value.length * actualItemHeight.value
})

const offsetY = computed(() => {
  return startIndex.value * actualItemHeight.value
})

const viewportStyle = computed(() => ({
  height: `${props.viewportHeight}px`,
  overflow: 'auto'
}))

const totalItemsText = computed(() => {
  const total = totalItems.value
  const filtered = filteredItems.value.length
  
  if (searchQuery.value && filtered !== props.items.length) {
    return `${filtered} de ${props.items.length} itens`
  }
  
  return `${total} ${total === 1 ? 'item' : 'itens'}`
})

const visibleRangeText = computed(() => {
  if (totalItems.value === 0) return ''
  
  const start = startIndex.value + 1
  const end = Math.min(endIndex.value, totalItems.value)
  
  return `${start}-${end} de ${totalItems.value}`
})

const densityText = computed(() => {
  const texts = {
    compact: 'Compacto',
    normal: 'Normal',
    comfortable: 'Confortável'
  }
  return texts[currentDensity.value]
})

// Methods
const getItemKey = (item, index) => {
  if (typeof item === 'object' && item !== null) {
    return item[props.keyField] || `item-${index}`
  }
  return `item-${index}`
}

const getItemLabel = (item) => {
  if (typeof item === 'string') return item
  if (typeof item === 'object' && item !== null) {
    return item[props.labelField] || item.name || item.title || String(item)
  }
  return String(item)
}

const getItemStyle = (item) => ({
  height: `${item.height}px`,
  position: 'absolute',
  top: `${item.top}px`,
  left: 0,
  right: 0
})

const isSelected = (item) => {
  const key = getItemKey(item)
  return props.selectedItems.some(selected => getItemKey(selected) === key)
}

const handleScroll = (event) => {
  scrollTop.value = event.target.scrollTop
  
  // Performance tracking
  const now = performance.now()
  if (lastFrameTime.value) {
    const delta = now - lastFrameTime.value
    frameCount.value++
    
    if (frameCount.value % 10 === 0) {
      fps.value = Math.round(1000 / delta)
    }
  }
  lastFrameTime.value = now
  
  emit('scroll', {
    scrollTop: scrollTop.value,
    scrollHeight: event.target.scrollHeight,
    clientHeight: event.target.clientHeight
  })
  
  // Check for load more
  checkLoadMore(event.target)
}

const handleWheel = (event) => {
  // Smooth scrolling optimization
  if (Math.abs(event.deltaY) > 100) {
    event.preventDefault()
    const delta = event.deltaY > 0 ? 100 : -100
    viewportRef.value.scrollTop += delta
  }
}

const checkLoadMore = (target) => {
  const { scrollTop, scrollHeight, clientHeight } = target
  const scrollPercentage = (scrollTop + clientHeight) / scrollHeight
  
  if (scrollPercentage >= props.threshold && !loading.value) {
    emit('load-more')
  }
}

const handleItemClick = (item, index) => {
  emit('item-click', { item, index })
}

const handleItemHover = (index) => {
  highlightedIndex.value = index
  emit('item-hover', { index })
}

const handleItemLeave = () => {
  highlightedIndex.value = -1
}

const handleKeydown = (event) => {
  const { key } = event
  
  switch (key) {
    case 'ArrowDown':
      event.preventDefault()
      navigateDown()
      break
    case 'ArrowUp':
      event.preventDefault()
      navigateUp()
      break
    case 'Home':
      event.preventDefault()
      scrollToTop()
      break
    case 'End':
      event.preventDefault()
      scrollToBottom()
      break
    case 'Enter':
    case ' ':
      event.preventDefault()
      if (highlightedIndex.value >= 0) {
        const item = filteredItems.value[highlightedIndex.value]
        handleItemClick(item, highlightedIndex.value)
      }
      break
  }
}

const navigateDown = () => {
  if (highlightedIndex.value < totalItems.value - 1) {
    highlightedIndex.value++
    scrollToIndex(highlightedIndex.value)
  }
}

const navigateUp = () => {
  if (highlightedIndex.value > 0) {
    highlightedIndex.value--
    scrollToIndex(highlightedIndex.value)
  }
}

const scrollToIndex = (index) => {
  if (!viewportRef.value) return
  
  const targetScrollTop = index * actualItemHeight.value
  const viewportTop = scrollTop.value
  const viewportBottom = viewportTop + props.viewportHeight
  
  if (targetScrollTop < viewportTop) {
    viewportRef.value.scrollTop = targetScrollTop
  } else if (targetScrollTop + actualItemHeight.value > viewportBottom) {
    viewportRef.value.scrollTop = targetScrollTop - props.viewportHeight + actualItemHeight.value
  }
}

const scrollToTop = () => {
  if (viewportRef.value) {
    viewportRef.value.scrollTop = 0
  }
}

const scrollToBottom = () => {
  if (viewportRef.value) {
    viewportRef.value.scrollTop = viewportRef.value.scrollHeight
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  emit('search', '')
}

const toggleDensity = () => {
  const densities = ['compact', 'normal', 'comfortable']
  const currentIndex = densities.indexOf(currentDensity.value)
  const nextIndex = (currentIndex + 1) % densities.length
  currentDensity.value = densities[nextIndex]
  emit('density-change', currentDensity.value)
}

// Debounced search
const debouncedSearch = debounce((event) => {
  emit('search', event.target.value)
}, 300)

// Watchers
watch(searchQuery, (newQuery) => {
  highlightedIndex.value = -1
  scrollToTop()
})

watch(() => props.density, (newDensity) => {
  currentDensity.value = newDensity
})

// Lifecycle
onMounted(() => {
  if (viewportRef.value) {
    viewportRef.value.addEventListener('scroll', handleScroll, { passive: true })
  }
})

onUnmounted(() => {
  if (viewportRef.value) {
    viewportRef.value.removeEventListener('scroll', handleScroll)
  }
})

// Expose methods
defineExpose({
  scrollToTop,
  scrollToBottom,
  scrollToIndex,
  clearSearch,
  toggleDensity
})
</script>

<style scoped>
.optimized-virtual-list {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: var(--background-color);
  overflow: hidden;
}

.virtual-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-sm) var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  background: var(--background-secondary);
}

.header-left,
.header-right {
  flex: 0 0 auto;
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.item-count {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.search-container {
  position: relative;
  max-width: 300px;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  font-size: 0.875rem;
}

.clear-search {
  position: absolute;
  right: var(--spacing-xs);
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: var(--text-muted);
}

.view-controls {
  display: flex;
  gap: var(--spacing-xs);
}

.density-toggle {
  padding: var(--spacing-xs);
  background: none;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: 0.875rem;
}

.virtual-viewport {
  position: relative;
  overflow: auto;
  flex: 1;
}

.scroll-container {
  position: relative;
  width: 100%;
}

.items-container {
  position: relative;
  width: 100%;
}

.virtual-item {
  position: absolute;
  width: 100%;
  border-bottom: 1px solid var(--border-light);
  transition: background-color 0.15s ease;
}

.virtual-item:hover,
.virtual-item.is-highlighted {
  background-color: var(--hover-color);
}

.virtual-item.is-selected {
  background-color: var(--primary-light);
}

.virtual-item.density-compact {
  font-size: 0.875rem;
}

.virtual-item.density-comfortable {
  font-size: 1.1rem;
}

.default-item-content {
  padding: var(--spacing-sm) var(--spacing-md);
  display: flex;
  align-items: center;
}

.loading-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: var(--spacing-md);
  text-align: center;
  background: var(--background-color);
  border-top: 1px solid var(--border-color);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-top: 2px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto var(--spacing-xs);
}

.loading-text {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 200px;
}

.empty-content {
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: var(--spacing-md);
}

.empty-text {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.virtual-list-footer {
  padding: var(--spacing-xs) var(--spacing-md);
  border-top: 1px solid var(--border-color);
  background: var(--background-secondary);
  font-size: 0.8rem;
  color: var(--text-muted);
}

.footer-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.scroll-to-top {
  position: absolute;
  bottom: var(--spacing-md);
  right: var(--spacing-md);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
}

.scroll-to-top:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsividade */
@media (max-width: 768px) {
  .virtual-list-header {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .header-left,
  .header-center,
  .header-right {
    width: 100%;
  }
  
  .search-container {
    max-width: none;
  }
  
  .footer-info {
    flex-direction: column;
    gap: var(--spacing-xs);
  }
}

/* Acessibilidade */
@media (prefers-reduced-motion: reduce) {
  .virtual-item,
  .scroll-to-top,
  .loading-spinner {
    transition: none;
    animation: none;
  }
}
</style>