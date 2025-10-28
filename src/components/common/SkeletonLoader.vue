<template>
  <div class="skeleton-loader" :aria-busy="true" aria-label="Placeholder loading">
    <div
      v-for="row in rows"
      :key="row"
      class="skeleton-row"
      :style="{ '--skeleton-height': rowHeight + 'px', '--skeleton-width': rowWidth }
    ">
      <div
        v-for="col in columns"
        :key="col"
        class="skeleton-item"
        :class="{ 'skeleton-animated': animated }"
        :style="itemStyle"
      />
    </div>
  </div>
</template>

<script>
export default {
  name: 'SkeletonLoader',
  props: {
    rows: { type: Number, default: 3 },
    columns: { type: Number, default: 1 },
    rowHeight: { type: Number, default: 14 },
    rowWidth: { type: String, default: '100%' },
    gap: { type: String, default: '12px' },
    animated: { type: Boolean, default: true }
  },
  computed: {
    itemStyle() {
      return {
        height: this.rowHeight + 'px',
        width: this.rowWidth,
        marginRight: this.gap
      }
    }
  }
}
</script>

<style scoped>
.skeleton-loader {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.skeleton-row {
  display: flex;
  align-items: center;
}
.skeleton-item {
  background: linear-gradient(90deg, var(--skeleton-bg, #e6e6e6) 25%, var(--skeleton-highlight, #f5f5f5) 37%, var(--skeleton-bg, #e6e6e6) 63%);
  background-size: 400% 100%;
  border-radius: 6px;
  flex-shrink: 0;
}
.skeleton-animated {
  animation: skeleton-shimmer 1.4s ease-in-out infinite;
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Reduced motion */
@media (prefers-reduced-motion: reduce) {
  .skeleton-animated {
    animation: none;
    background: var(--skeleton-bg, #e6e6e6);
  }
}
</style>
