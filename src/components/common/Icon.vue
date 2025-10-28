<template>
  <span
    v-if="faClass"
    :class="[faSetClass, faClass]"
    :style="iconStyle"
    v-bind="$attrs"
  />
  <span v-else class="icon-fallback" :style="iconStyle" v-bind="$attrs">?</span>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: null },
  color: { type: String, default: null },
  weight: { type: String, default: 'solid' } // 'solid' | 'regular' | 'brands'
})

// Mapeamento de nomes usados no projeto para classes do Font Awesome 6
const iconMap = {
  search: 'fa-magnifying-glass',
  x: 'fa-xmark',
  inbox: 'fa-inbox',
  'search-x': 'fa-magnifying-glass', // fallback para lupa
  'arrow-up': 'fa-arrow-up',
  'chevrons-left': 'fa-angles-left',
  'chevron-left': 'fa-chevron-left',
  'chevron-right': 'fa-chevron-right',
  'chevrons-right': 'fa-angles-right'
}

const faSetClass = computed(() => {
  switch (props.weight) {
    case 'regular':
      return 'fa-regular'
    case 'brands':
      return 'fa-brands'
    default:
      return 'fa-solid'
  }
})

const faClass = computed(() => iconMap[props.name] || null)

const iconStyle = computed(() => {
  const style = {}
  if (props.size) {
    style.fontSize = typeof props.size === 'number' ? `${props.size}px` : props.size
  }
  if (props.color) {
    style.color = props.color
  }
  return style
})
</script>

<style scoped>
.icon-fallback {
  display: inline-block;
  width: 1em;
  height: 1em;
  text-align: center;
  line-height: 1em;
}
</style>