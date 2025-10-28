import logger from '@/utils/logger'
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'

export function useVirtualScroll(options = {}) {
  const {
    itemHeight = 50,
    containerHeight = 400,
    buffer = 5,
    threshold = 0.8
  } = options

  // Reactive state
  const scrollTop = ref(0)
  const containerRef = ref(null)
  const items = ref([])
  const loading = ref(false)
  const hasMore = ref(true)

  // Computed properties
  const visibleCount = computed(() => Math.ceil(containerHeight / itemHeight))
  const totalHeight = computed(() => items.value.length * itemHeight)
  
  const startIndex = computed(() => {
    const index = Math.floor(scrollTop.value / itemHeight) - buffer
    return Math.max(0, index)
  })
  
  const endIndex = computed(() => {
    const index = startIndex.value + visibleCount.value + buffer * 2
    return Math.min(items.value.length, index)
  })
  
  const visibleItems = computed(() => {
    return items.value.slice(startIndex.value, endIndex.value).map((item, index) => ({
      ...item,
      index: startIndex.value + index,
      top: (startIndex.value + index) * itemHeight
    }))
  })
  
  const offsetY = computed(() => startIndex.value * itemHeight)

  // Methods
  const handleScroll = (event) => {
    scrollTop.value = event.target.scrollTop
    
    // Check if we need to load more items
    const scrollHeight = event.target.scrollHeight
    const clientHeight = event.target.clientHeight
    const scrollPosition = scrollTop.value + clientHeight
    
    if (scrollPosition >= scrollHeight * threshold && hasMore.value && !loading.value) {
      loadMore()
    }
  }

  const loadMore = async () => {
    if (loading.value || !hasMore.value) return
    
    loading.value = true
    
    try {
      // Emit event for parent to handle loading
      if (options.onLoadMore) {
        const newItems = await options.onLoadMore()
        if (newItems && newItems.length > 0) {
          items.value.push(...newItems)
        } else {
          hasMore.value = false
        }
      }
    } catch (error) {
      logger.error('Error loading more items:', error)
    } finally {
      loading.value = false
    }
  }

  const scrollToIndex = (index) => {
    if (!containerRef.value) return
    
    const targetScrollTop = index * itemHeight
    containerRef.value.scrollTop = targetScrollTop
    scrollTop.value = targetScrollTop
  }

  const scrollToTop = () => {
    scrollToIndex(0)
  }

  const scrollToBottom = () => {
    if (!containerRef.value) return
    
    containerRef.value.scrollTop = containerRef.value.scrollHeight
  }

  const setItems = (newItems) => {
    items.value = newItems
    hasMore.value = true
    scrollToTop()
  }

  const addItems = (newItems) => {
    items.value.push(...newItems)
  }

  const removeItem = (index) => {
    items.value.splice(index, 1)
  }

  const updateItem = (index, newItem) => {
    if (index >= 0 && index < items.value.length) {
      items.value[index] = { ...items.value[index], ...newItem }
    }
  }

  const reset = () => {
    items.value = []
    scrollTop.value = 0
    loading.value = false
    hasMore.value = true
  }

  // Intersection Observer for better performance
  const observerRef = ref(null)
  
  const setupIntersectionObserver = () => {
    if (!window.IntersectionObserver) return
    
    observerRef.value = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            // Item is visible, can trigger animations or lazy loading
            const index = parseInt(entry.target.dataset.index)
            if (options.onItemVisible) {
              options.onItemVisible(index, items.value[index])
            }
          }
        })
      },
      {
        root: containerRef.value,
        rootMargin: '50px',
        threshold: 0.1
      }
    )
  }

  const observeItem = (element, index) => {
    if (observerRef.value && element) {
      element.dataset.index = index
      observerRef.value.observe(element)
    }
  }

  const unobserveItem = (element) => {
    if (observerRef.value && element) {
      observerRef.value.unobserve(element)
    }
  }

  // Lifecycle
  onMounted(() => {
    nextTick(() => {
      setupIntersectionObserver()
    })
  })

  onUnmounted(() => {
    if (observerRef.value) {
      observerRef.value.disconnect()
    }
  })

  // Search and filter functionality
  const searchQuery = ref('')
  const filteredItems = computed(() => {
    if (!searchQuery.value) return items.value
    
    const query = searchQuery.value.toLowerCase()
    return items.value.filter(item => {
      if (typeof item === 'string') {
        return item.toLowerCase().includes(query)
      }
      
      // Search in object properties
      return Object.values(item).some(value => 
        String(value).toLowerCase().includes(query)
      )
    })
  })

  const setSearchQuery = (query) => {
    searchQuery.value = query
    scrollToTop()
  }

  // Performance monitoring
  const performanceMetrics = ref({
    renderTime: 0,
    scrollEvents: 0,
    lastRenderTime: 0
  })

  const measureRenderTime = (callback) => {
    const start = performance.now()
    callback()
    const end = performance.now()
    
    performanceMetrics.value.renderTime = end - start
    performanceMetrics.value.lastRenderTime = Date.now()
  }

  // Debounced scroll handler for better performance
  let scrollTimeout = null
  const debouncedHandleScroll = (event) => {
    performanceMetrics.value.scrollEvents++
    
    if (scrollTimeout) {
      clearTimeout(scrollTimeout)
    }
    
    scrollTimeout = setTimeout(() => {
      handleScroll(event)
    }, 16) // ~60fps
  }

  return {
    // Refs
    containerRef,
    scrollTop,
    items,
    loading,
    hasMore,
    searchQuery,
    
    // Computed
    visibleItems,
    filteredItems,
    totalHeight,
    offsetY,
    startIndex,
    endIndex,
    visibleCount,
    performanceMetrics,
    
    // Methods
    handleScroll: debouncedHandleScroll,
    loadMore,
    scrollToIndex,
    scrollToTop,
    scrollToBottom,
    setItems,
    addItems,
    removeItem,
    updateItem,
    reset,
    setSearchQuery,
    observeItem,
    unobserveItem,
    measureRenderTime
  }
}

// Helper function for creating virtual scroll directive
export const vVirtualScroll = {
  mounted(el, binding) {
    const { observeItem } = binding.value
    const index = el.dataset.index
    if (observeItem && index !== undefined) {
      observeItem(el, parseInt(index))
    }
  },
  
  unmounted(el, binding) {
    const { unobserveItem } = binding.value
    if (unobserveItem) {
      unobserveItem(el)
    }
  }
}