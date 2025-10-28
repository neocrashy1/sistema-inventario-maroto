<template>
  <div class="purchase-form-overlay">
    <div class="purchase-form">
      <header>
        <h3>{{ model.id ? 'Editar Orçamento' : 'Novo Orçamento' }}</h3>
        <button class="close" @click="$emit('close')">×</button>
      </header>

      <form @submit.prevent="save">
        <div class="field">
          <label>Fornecedor</label>
          <input v-model="local.supplier" required />
        </div>

        <div class="field">
          <label>Itens (JSON)</label>
          <textarea v-model="itemsText" rows="4" />
          <small>Formato: [{"description":"Item A","qty":1,"unitPrice":10}]</small>
        </div>

        <div class="field">
          <label>Status</label>
          <select v-model="local.status">
            <option value="quote">Orçamento</option>
            <option value="ordered">Encomendado</option>
            <option value="received">Recebido</option>
            <option value="cancelled">Cancelado</option>
          </select>
        </div>

        <div class="actions">
          <button type="submit" class="btn btn-primary">Salvar</button>
          <button type="button" class="btn" @click="$emit('close')">Cancelar</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive, toRefs, computed } from 'vue'
defineProps({ modelValue: { type: Object, default: null } })
const emit = defineEmits(['close','save'])

const model = toRefs({ value: null }).value
const local = reactive(modelValue ? { ...modelValue } : { supplier: '', items: [], status: 'quote', notes: '' })
const itemsText = computed({
  get() { return JSON.stringify(local.items || [], null, 2) },
  set(v) { try { local.items = JSON.parse(v) } catch (e) { /* ignore parse error until save */ } }
})

const save = () => {
  // Recalculate total
  local.total = (local.items || []).reduce((s, it) => s + (it.qty || 0) * (it.unitPrice || 0), 0)
  emit('save', local)
}
</script>

<style scoped>
.purchase-form-overlay { position:fixed; inset:0; background:rgba(0,0,0,0.4); display:flex; align-items:center; justify-content:center }
.purchase-form { background:white; padding:1rem; width:600px; max-width:95%; border-radius:6px }
.purchase-form header { display:flex; justify-content:space-between; align-items:center }
.field { margin-bottom:0.75rem }
.field label { display:block; font-weight:600; margin-bottom:0.25rem }
.field input, .field textarea, .field select { width:100%; padding:0.5rem; }
.actions { display:flex; gap:0.5rem; justify-content:flex-end }
.close { background:none; border:none; font-size:1.3rem }
</style>
