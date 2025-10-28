<template>
  <div class="virtual-list-container">
    <!-- Search bar (optional) -->
    <div v-if="searchable" class="virtual-list-search">
      <div class="search-input-wrapper">
        <Icon name="search" class="search-icon" aria-hidden="true" />
        <input
          v-model="searchQuery"
          type="text"
          :placeholder="searchPlaceholder"
          class="search-input"
          :aria-label="searchPlaceholder"
          @input="handleSearch"
        />
        <button
          v-if="searchQuery"
          @click="clearSearch"
          class="clear-search-btn"
          type="button"
          aria-label="Limpar pesquisa"
        >
          <Icon name="x" aria-hidden="true" />
        </button>
      </div>
    </div>

    <!-- Virtual scroll container -->
    <div
      ref="containerRef"
      class="virtual-list-viewport"
      :style="{ height: containerHeight + 'px' }"
      @scroll="handleScroll"
      role="listbox"
      :aria-label="ariaLabel"
      :aria-busy="loading"
      tabindex="0"
      @keydown="handleKeydown"
    >
      <!-- Total height spacer -->
      <div
        class="virtual-list-spacer"
        :style="{ height: totalHeight + 'px' }"
      >
        <!-- Visible items container -->
        <div
          class="virtual-list-items"
          :style="{ transform: `translateY(${offsetY}px)` }"
        >
          <div
            v-for="item in visibleItems"
            :key="getItemKey(item)"
            :data-index="item.index"
            class="virtual-list-item"
            :style="{ height: itemHeight + 'px' }"
            role="option"
            :aria-selected="isSelected(item)"
            :aria-posinset="item.index + 1"
            :aria-setsize="totalItems"
            @click="handleItemClick(item)"
            @keydown.enter="handleItemClick(item)"
            @keydown.space.prevent="handleItemClick(item)"
            tabindex="-1"
            v-virtual-scroll="{ observeItem, unobserveItem }"
          >
            <!-- Custom item slot -->
            <slot
              name="item"
              :item="item"
              :index="item.index"
              :selected="isSelected(item)"
            >
              <!-- Default item rendering -->
              <div class="default-item">
                {{ getItemLabel(item) }}
              </div>
            </slot>
          </div>
        </div>
      </div>

      <!-- Loading indicator -->
      <div
        v-if="loading"
        class="virtual-list-loading"
        role="status"
        aria-label="Carregando mais itens"
      >
        <div class="loading-spinner" aria-hidden="true"></div>
        <span class="loading-text">{{ loadingText }}</span>
      </div>

      <!-- Empty state -->
      <div
        v-if="!loading && filteredItems.length === 0"
        class="virtual-list-empty"
        role="status"
      >
        <slot name="empty">
          <div class="empty-content">
            <Icon name="inbox" class="empty-icon" aria-hidden="true" />
            <p class="empty-text">{{ emptyText }}</p>
          </div>
        </slot>
      </div>

      <!-- No results state -->
      <div
        v-if="!loading && searchQuery && filteredItems.length === 0 && items.length > 0"
        class="virtual-list-no-results"
        role="status"
      >
        <slot name="no-results">
          <div class="no-results-content">
            <Icon name="search-x" class="no-results-icon" aria-hidden="true" />
            <p class="no-results-text">
              Nenhum resultado encontrado para "{{ searchQuery }}"
            </p>
            <button
              @click="clearSearch"
              class="clear-search-link"
              type="button"
            >
              Limpar pesquisa
            </button>
          </div>
        </slot>
      </div>
    </div>

    <!-- Scroll to top button -->
    <Transition name="fade">
      <button
        v-if="showScrollToTop && scrollTop > containerHeight"
        @click="scrollToTop"
        class="scroll-to-top-btn"
        type="button"
        aria-label="Voltar ao topo"
        title="Voltar ao topo"
      >
        <Icon name="arrow-up" aria-hidden="true" />
      </button>
    </Transition>

    <!-- Performance metrics (dev mode) -->
    <div
      v-if="showMetrics && isDev"
      class="virtual-list-metrics"
      role="status"
      aria-label="Métricas de performance"
    >
      <small>
        Itens: {{ visibleItems.length }}/{{ totalItems }} |
        Render: {{ performanceMetrics.renderTime.toFixed(2) }}ms |
        Scroll: {{ performanceMetrics.scrollEvents }}
      </small>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { useVirtualScroll, vVirtualScroll } from '@/composables/useVirtualScroll'
import Icon from '@/components/common/Icon.vue'

// Props
const props = defineProps({
  items: {
    type: Array,
    default: () => []
  },
  itemHeight: {
    type: Number,
    default: 50
  },
  containerHeight: {
    type: Number,
    default: 400
  },
  buffer: {
    type: Number,
    default: 5
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
    default: 'Lista de itens'
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
  showScrollToTop: {
    type: Boolean,
    default: true
  },
  showMetrics: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits([
  'load-more',
  'item-click',
  'selection-change',
  'search',
  'scroll'
])

// Virtual scroll composable
const {
  containerRef,
  scrollTop,
  items: virtualItems,
  loading,
  hasMore,
  searchQuery,
  visibleItems,
  filteredItems,
  totalHeight,
  offsetY,
  performanceMetrics,
  handleScroll: virtualHandleScroll,
  loadMore,
  scrollToTop,
  setItems,
  setSearchQuery,
  observeItem,
  unobserveItem,
  measureRenderTime
} = useVirtualScroll({
  itemHeight: props.itemHeight,
  containerHeight: props.containerHeight,
  buffer: props.buffer,
  threshold: props.threshold,
  onLoadMore: async () => {
    const result = await new Promise((resolve) => {
      emit('load-more', resolve)
    })
    return result
  }
})

// Computed
const totalItems = computed(() => filteredItems.value.length)
const isDev = computed(() => import.meta.env.DEV)

// Methods
const getItemKey = (item) => {
  if (typeof item === 'object' && item !== null) {
    return item[props.keyField] || item.id || JSON.stringify(item)
  }
  return item
}

const getItemLabel = (item) => {
  if (typeof item === 'string') return item
  if (typeof item === 'object' && item !== null) {
    return item[props.labelField] || item.name || item.title || String(item)
  }
  return String(item)
}

const isSelected = (item) => {
  const key = getItemKey(item)
  return props.selectedItems.some(selected => getItemKey(selected) === key)
}

const handleItemClick = (item) => {
  emit('item-click', item)
}

const handleSearch = () => {
  emit('search', searchQuery.value)
}

const clearSearch = () => {
  searchQuery.value = ''
  setSearchQuery('')
  emit('search', '')
}

const handleScroll = (event) => {
  measureRenderTime(() => {
    virtualHandleScroll(event)
  })
  emit('scroll', {
    scrollTop: scrollTop.value,
    scrollHeight: event.target.scrollHeight,
    clientHeight: event.target.clientHeight
  })
}

const handleKeydown = (event) => {
  const { key } = event
  const currentIndex = parseInt(event.target.dataset.index) || 0
  
  switch (key) {
    case 'ArrowDown':
      event.preventDefault()
      focusItem(currentIndex + 1)
      break
    case 'ArrowUp':
      event.preventDefault()
      focusItem(currentIndex - 1)
      break
    case 'Home':
      event.preventDefault()
      focusItem(0)
      break
    case 'End':
      event.preventDefault()
      focusItem(totalItems.value - 1)
      break
    case 'PageDown':
      event.preventDefault()
      focusItem(Math.min(currentIndex + 10, totalItems.value - 1))
      break
    case 'PageUp':
      event.preventDefault()
      focusItem(Math.max(currentIndex - 10, 0))
      break
  }
}

const focusItem = (index) => {
  if (index < 0 || index >= totalItems.value) return
  
  nextTick(() => {
    const item = containerRef.value?.querySelector(`[data-index="${index}"]`)
    if (item) {
      item.focus()
      // Ensure item is visible
      const itemTop = index * props.itemHeight
      const viewportTop = scrollTop.value
      const viewportBottom = viewportTop + props.containerHeight
      
      if (itemTop < viewportTop) {
        containerRef.value.scrollTop = itemTop
      } else if (itemTop + props.itemHeight > viewportBottom) {
        containerRef.value.scrollTop = itemTop - props.containerHeight + props.itemHeight
      }
    }
  })
}

// Watch for prop changes
watch(() => props.items, (newItems) => {
  setItems(newItems)
}, { immediate: true })

watch(searchQuery, (newQuery) => {
  setSearchQuery(newQuery)
})

// Expose methods for parent components
defineExpose({
  scrollToTop,
  scrollToIndex: (index) => focusItem(index),
  refresh: () => setItems(props.items),
  clearSearch,
  focusFirst: () => focusItem(0)
})
</script>

<style scoped>
.virtual-list-container {
  position: relative;
  width: 100%;
}

.virtual-list-search {
  margin-bottom: 1rem;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  width: 1rem;
  height: 1rem;
  color: var(--color-text-secondary);
  pointer-events: none;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 2.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  font-size: 0.875rem;
  background-color: var(--color-background);
  color: var(--color-text);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-alpha);
}

.clear-search-btn {
  position: absolute;
  right: 0.5rem;
  padding: 0.25rem;
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: 0.25rem;
  transition: color 0.2s ease, background-color 0.2s ease;
}

.clear-search-btn:hover {
  color: var(--color-text);
  background-color: var(--color-background-secondary);
}

.virtual-list-viewport {
  position: relative;
  overflow-y: auto;
  border: 1px solid var(--color-border);
  border-radius: 0.5rem;
  background-color: var(--color-background);
}

.virtual-list-viewport:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
}

.virtual-list-spacer {
  position: relative;
  width: 100%;
}

.virtual-list-items {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
}

.virtual-list-item {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.virtual-list-item:hover {
  background-color: var(--color-background-secondary);
}

.virtual-list-item:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: -2px;
  background-color: var(--color-background-secondary);
}

.virtual-list-item[aria-selected="true"] {
  background-color: var(--color-primary-light);
  color: var(--color-primary-dark);
}

.virtual-list-item:last-child {
  border-bottom: none;
}

.default-item {
  flex: 1;
  font-size: 0.875rem;
  color: var(--color-text);
}

.virtual-list-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 0.5rem;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
}

.virtual-list-empty,
.virtual-list-no-results {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3rem 2rem;
  text-align: center;
}

.empty-content,
.no-results-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.empty-icon,
.no-results-icon {
  width: 3rem;
  height: 3rem;
  color: var(--color-text-tertiary);
}

.empty-text,
.no-results-text {
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  margin: 0;
}

.clear-search-link {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  font-size: 0.875rem;
  text-decoration: underline;
  padding: 0;
}

.clear-search-link:hover {
  color: var(--color-primary-dark);
}

.scroll-to-top-btn {
  position: absolute;
  bottom: 1rem;
  right: 1rem;
  width: 2.5rem;
  height: 2.5rem;
  background-color: var(--color-primary);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
  z-index: 10;
}

.scroll-to-top-btn:hover {
  background-color: var(--color-primary-dark);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.scroll-to-top-btn:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.virtual-list-metrics {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-family: monospace;
  font-size: 0.75rem;
  pointer-events: none;
  z-index: 10;
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Animations */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* High contrast mode */
.high-contrast .virtual-list-item:focus {
  outline: 3px solid currentColor;
  outline-offset: -3px;
}

.high-contrast .virtual-list-item[aria-selected="true"] {
  background-color: Highlight;
  color: HighlightText;
}

/* Reduced motion */
.reduced-motion * {
  animation-duration: 0.01ms !important;
  animation-iteration-count: 1 !important;
  transition-duration: 0.01ms !important;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .virtual-list-item {
    padding: 1rem;
    min-height: 3rem;
  }
  
  .search-input {
    padding: 1rem 3rem 1rem 3rem;
    font-size: 1rem;
  }
  
  .scroll-to-top-btn {
    width: 3rem;
    height: 3rem;
  }
}

/* Print styles */
@media print {
  .virtual-list-container {
    overflow: visible !important;
    height: auto !important;
  }
  
  .virtual-list-viewport {
    overflow: visible !important;
    height: auto !important;
    border: none;
  }
  
  .scroll-to-top-btn,
  .virtual-list-metrics {
    display: none !important;
  }
}
</style>