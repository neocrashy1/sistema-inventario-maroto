<template>
  <nav
    class="pagination-container"
    :aria-label="getPaginationAriaLabel()"
    role="navigation"
  >
    <!-- Total info -->
    <div v-if="showTotal" class="pagination-total">
      <span class="total-text">
        {{ getTotalText() }}
      </span>
    </div>

    <!-- Page size selector -->
    <div v-if="showSizeChanger" class="pagination-size-changer">
      <label for="page-size-select" class="size-label">
        Itens por página:
      </label>
      <select
        id="page-size-select"
        v-model="currentPageSize"
        class="size-select"
        :aria-label="getPageSizeAriaLabel()"
        @change="handlePageSizeChange"
      >
        <option
          v-for="size in pageSizeOptions"
          :key="size"
          :value="size"
        >
          {{ size }}
        </option>
      </select>
    </div>

    <!-- Pagination controls -->
    <div class="pagination-controls">
      <!-- First page button -->
      <button
        v-if="showFirstLast"
        :disabled="!hasPrev || loading"
        class="pagination-btn pagination-first"
        type="button"
        :aria-label="'Ir para primeira página'"
        @click="handleFirstPage"
      >
        <Icon name="chevrons-left" aria-hidden="true" />
        <span v-if="showLabels" class="btn-label">Primeira</span>
      </button>

      <!-- Previous page button -->
      <button
        :disabled="!hasPrev || loading"
        class="pagination-btn pagination-prev"
        type="button"
        :aria-label="'Ir para página anterior'"
        @click="handlePrevPage"
      >
        <Icon name="chevron-left" aria-hidden="true" />
        <span v-if="showLabels" class="btn-label">Anterior</span>
      </button>

      <!-- Page numbers -->
      <div class="pagination-pages" role="group" aria-label="Páginas">
        <!-- First page if not visible -->
        <template v-if="visiblePages[0] > 1">
          <button
            class="pagination-btn pagination-page"
            type="button"
            :aria-label="getPageAriaLabel(1)"
            @click="handlePageClick(1)"
          >
            1
          </button>
          
          <!-- Ellipsis -->
          <span v-if="visiblePages[0] > 2" class="pagination-ellipsis" aria-hidden="true">
            ...
          </span>
        </template>

        <!-- Visible page numbers -->
        <button
          v-for="page in visiblePages"
          :key="page"
          class="pagination-btn pagination-page"
          :class="{ 'pagination-current': page === currentPage }"
          type="button"
          :aria-label="getPageAriaLabel(page)"
          :aria-current="page === currentPage ? 'page' : undefined"
          @click="handlePageClick(page)"
        >
          {{ page }}
        </button>

        <!-- Last page if not visible -->
        <template v-if="visiblePages[visiblePages.length - 1] < totalPages">
          <!-- Ellipsis -->
          <span
            v-if="visiblePages[visiblePages.length - 1] < totalPages - 1"
            class="pagination-ellipsis"
            aria-hidden="true"
          >
            ...
          </span>
          
          <button
            class="pagination-btn pagination-page"
            type="button"
            :aria-label="getPageAriaLabel(totalPages)"
            @click="handlePageClick(totalPages)"
          >
            {{ totalPages }}
          </button>
        </template>
      </div>

      <!-- Next page button -->
      <button
        :disabled="!hasNext || loading"
        class="pagination-btn pagination-next"
        type="button"
        :aria-label="'Ir para próxima página'"
        @click="handleNextPage"
      >
        <span v-if="showLabels" class="btn-label">Próxima</span>
        <Icon name="chevron-right" aria-hidden="true" />
      </button>

      <!-- Last page button -->
      <button
        v-if="showFirstLast"
        :disabled="!hasNext || loading"
        class="pagination-btn pagination-last"
        type="button"
        :aria-label="'Ir para última página'"
        @click="handleLastPage"
      >
        <span v-if="showLabels" class="btn-label">Última</span>
        <Icon name="chevrons-right" aria-hidden="true" />
      </button>
    </div>

    <!-- Quick jumper -->
    <div v-if="showQuickJumper" class="pagination-jumper">
      <label for="page-jumper-input" class="jumper-label">
        Ir para:
      </label>
      <input
        id="page-jumper-input"
        v-model="jumpPageInput"
        type="number"
        :min="1"
        :max="totalPages"
        class="jumper-input"
        :aria-label="'Número da página para navegar'"
        @keydown.enter="handleJumpToPage"
        @blur="handleJumpToPage"
      />
      <button
        class="jumper-btn"
        type="button"
        :disabled="loading"
        @click="handleJumpToPage"
      >
        Ir
      </button>
    </div>

    <!-- Loading indicator -->
    <div v-if="loading" class="pagination-loading" role="status" aria-label="Carregando">
      <div class="loading-spinner" aria-hidden="true"></div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import Icon from '@/components/common/Icon.vue'

// Props
const props = defineProps({
  currentPage: {
    type: Number,
    required: true
  },
  totalPages: {
    type: Number,
    required: true
  },
  total: {
    type: Number,
    required: true
  },
  pageSize: {
    type: Number,
    required: true
  },
  pageSizeOptions: {
    type: Array,
    default: () => [10, 20, 50, 100]
  },
  visiblePages: {
    type: Array,
    required: true
  },
  hasNext: {
    type: Boolean,
    required: true
  },
  hasPrev: {
    type: Boolean,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  showTotal: {
    type: Boolean,
    default: true
  },
  showSizeChanger: {
    type: Boolean,
    default: true
  },
  showQuickJumper: {
    type: Boolean,
    default: true
  },
  showFirstLast: {
    type: Boolean,
    default: true
  },
  showLabels: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits([
  'page-change',
  'page-size-change',
  'first-page',
  'last-page',
  'prev-page',
  'next-page'
])

// Local state
const currentPageSize = ref(props.pageSize)
const jumpPageInput = ref('')

// Methods
const handlePageClick = (page) => {
  if (page !== props.currentPage && !props.loading) {
    emit('page-change', page)
  }
}

const handlePrevPage = () => {
  if (props.hasPrev && !props.loading) {
    emit('prev-page')
  }
}

const handleNextPage = () => {
  if (props.hasNext && !props.loading) {
    emit('next-page')
  }
}

const handleFirstPage = () => {
  if (props.hasPrev && !props.loading) {
    emit('first-page')
  }
}

const handleLastPage = () => {
  if (props.hasNext && !props.loading) {
    emit('last-page')
  }
}

const handlePageSizeChange = () => {
  if (currentPageSize.value !== props.pageSize) {
    emit('page-size-change', currentPageSize.value)
  }
}

const handleJumpToPage = () => {
  const page = parseInt(jumpPageInput.value)
  if (page && page >= 1 && page <= props.totalPages && page !== props.currentPage) {
    emit('page-change', page)
    jumpPageInput.value = ''
  }
}

// Computed
const getTotalText = () => {
  const start = (props.currentPage - 1) * props.pageSize + 1
  const end = Math.min(props.currentPage * props.pageSize, props.total)
  
  if (props.total === 0) {
    return 'Nenhum item encontrado'
  }
  
  return `${start}-${end} de ${props.total} itens`
}

const getPageAriaLabel = (page) => {
  if (page === props.currentPage) {
    return `Página ${page}, página atual`
  }
  return `Ir para página ${page}`
}

const getPaginationAriaLabel = () => {
  return `Navegação de páginas, página ${props.currentPage} de ${props.totalPages}`
}

const getPageSizeAriaLabel = () => {
  return `Itens por página: ${props.pageSize}`
}

// Watch for prop changes
watch(() => props.pageSize, (newSize) => {
  currentPageSize.value = newSize
})
</script>

<style scoped>
.pagination-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1rem 0;
  font-size: 0.875rem;
}

.pagination-total {
  color: var(--color-text-secondary);
  font-weight: 500;
}

.pagination-size-changer {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.size-label {
  color: var(--color-text-secondary);
  font-weight: 500;
}

.size-select {
  padding: 0.375rem 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background-color: var(--color-background);
  color: var(--color-text);
  font-size: 0.875rem;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.size-select:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-alpha);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.pagination-pages {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  height: 2.5rem;
  padding: 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background-color: var(--color-background);
  color: var(--color-text);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  gap: 0.25rem;
}

.pagination-btn:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
  background-color: var(--color-primary-light);
}

.pagination-btn:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-alpha);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background-color: var(--color-background-secondary);
}

.pagination-current {
  background-color: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.pagination-current:hover {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
  color: white;
}

.pagination-ellipsis {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 2.5rem;
  height: 2.5rem;
  color: var(--color-text-secondary);
  font-weight: 500;
}

.pagination-jumper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.jumper-label {
  color: var(--color-text-secondary);
  font-weight: 500;
}

.jumper-input {
  width: 4rem;
  padding: 0.375rem 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: 0.375rem;
  background-color: var(--color-background);
  color: var(--color-text);
  font-size: 0.875rem;
  text-align: center;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.jumper-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-alpha);
}

.jumper-btn {
  padding: 0.375rem 0.75rem;
  border: 1px solid var(--color-primary);
  border-radius: 0.375rem;
  background-color: var(--color-primary);
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.jumper-btn:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
  border-color: var(--color-primary-dark);
}

.jumper-btn:focus {
  outline: none;
  box-shadow: 0 0 0 3px var(--color-primary-alpha);
}

.jumper-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-text-secondary);
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.btn-label {
  font-size: 0.75rem;
}

/* Compact mode */
.pagination-container.compact {
  gap: 0.5rem;
}

.compact .pagination-btn {
  min-width: 2rem;
  height: 2rem;
  padding: 0.25rem;
}

.compact .btn-label {
  display: none;
}

/* High contrast mode */
.high-contrast .pagination-btn:focus {
  outline: 3px solid currentColor;
  outline-offset: 2px;
}

.high-contrast .pagination-current {
  background-color: Highlight;
  color: HighlightText;
  border-color: Highlight;
}

/* Reduced motion */
.reduced-motion * {
  animation-duration: 0.01ms !important;
  animation-iteration-count: 1 !important;
  transition-duration: 0.01ms !important;
}

/* Mobile optimizations */
@media (max-width: 768px) {
  .pagination-container {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  
  .pagination-controls {
    justify-content: center;
  }
  
  .pagination-btn {
    min-width: 3rem;
    height: 3rem;
    touch-action: manipulation;
  }
  
  .pagination-total,
  .pagination-size-changer,
  .pagination-jumper {
    justify-content: center;
  }
  
  .btn-label {
    display: none;
  }
}

@media (max-width: 480px) {
  .pagination-pages {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .pagination-ellipsis {
    display: none;
  }
}

/* Print styles */
@media print {
  .pagination-container {
    display: none !important;
  }
}

/* Animations */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Focus management for keyboard navigation */
.pagination-btn:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

/* RTL support */
[dir="rtl"] .pagination-controls {
  direction: rtl;
}

[dir="rtl"] .pagination-btn {
  direction: ltr;
}
</style>