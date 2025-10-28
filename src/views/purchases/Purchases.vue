<template>
  <section class="page purchases-page">
    <header class="page-header">
      <h1>Compras & Orçamentos</h1>
      <div class="actions">
        <button @click="openNew" class="btn btn-primary">Novo Orçamento</button>
      </div>
    </header>

    <main>
      <div class="filters">
        <input v-model="search" placeholder="Buscar por código ou fornecedor" />
        <select v-model="statusFilter">
          <option value="">Todos</option>
          <option value="quote">Orçamento</option>
          <option value="ordered">Encomendado</option>
          <option value="received">Recebido</option>
          <option value="cancelled">Cancelado</option>
        </select>
      </div>

      <div v-if="loading">Carregando...</div>

      <table v-if="!loading" class="table">
        <thead>
          <tr>
            <th>Código</th>
            <th>Fornecedor</th>
            <th>Itens</th>
            <th>Total</th>
            <th>Status</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in filtered" :key="p.id">
            <td>{{ p.code }}</td>
            <td>{{ p.supplier }}</td>
            <td>{{ p.items ? p.items.length : 0 }}</td>
            <td>{{ formatCurrency(p.total) }}</td>
            <td>{{ statusLabel(p.status) }}</td>
            <td>
              <button @click="edit(p)" class="btn btn-sm">Editar</button>
              <button @click="remove(p.id)" class="btn btn-sm btn-danger">Deletar</button>
            </td>
          </tr>
        </tbody>
      </table>

      <PurchaseForm v-if="showForm" :modelValue="editing" @close="closeForm" @save="onSave" />
    </main>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { usePurchasesStore } from '@/stores/purchases'
import PurchaseForm from '@/components/purchases/PurchaseForm.vue'

const store = usePurchasesStore()
const loading = computed(() => store.loading)
const showForm = ref(false)
const editing = ref(null)
const search = ref('')
const statusFilter = ref('')

onMounted(() => {
  store.fetchPurchases()
})

const openNew = () => { editing.value = null; showForm.value = true }
const edit = (p) => { editing.value = { ...p }; showForm.value = true }
const closeForm = () => { showForm.value = false; editing.value = null }

const onSave = async (payload) => {
  if (payload.id) {
    await store.updatePurchase(payload.id, payload)
  } else {
    await store.createPurchase(payload)
  }
  closeForm()
}

const remove = async (id) => {
  if (!confirm('Confirma a exclusão deste orçamento?')) return
  await store.deletePurchase(id)
}

const filtered = computed(() => {
  const term = search.value
  store.setSearchTerm(term)
  store.setFilters({ status: statusFilter.value })
  return store.filteredPurchases
})

const formatCurrency = (v) => (v == null ? '-' : v.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }))
const statusLabel = (s) => ({ quote: 'Orçamento', ordered: 'Encomendado', received: 'Recebido', cancelled: 'Cancelado' }[s] || s)
</script>

<style scoped>
.purchases-page { padding: 1rem; }
.page-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem }
.filters { display:flex; gap:0.5rem; margin-bottom:1rem }
.table { width:100%; border-collapse:collapse }
.table th, .table td { padding:0.5rem; border-bottom:1px solid #eee }
.actions .btn { margin-left:0.5rem }
</style>
