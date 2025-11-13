<template>
  <div class="payments-page">
    <div class="page-header">
      <div>
        <h1>Pagamentos</h1>
        <p>Registre aquisições, renovações e pagamentos relacionados a ativos e licenças.</p>
      </div>
      <div>
        <button class="btn btn-primary" @click="showAdd = true">Novo Pagamento</button>
      </div>
    </div>

    <LoadingState v-if="store.loading" />

    <div v-else>
      <table class="table">
        <thead><tr><th>Referência</th><th>Valor</th><th>Data</th><th>Fornecedor</th><th>Método</th><th></th></tr></thead>
        <tbody>
          <tr v-for="p in store.items" :key="p.id">
            <td>{{ p.reference }}</td>
            <td>{{ formatCurrency(p.amount) }}</td>
            <td>{{ p.date }}</td>
            <td>{{ p.vendor }}</td>
            <td>{{ p.method }}</td>
            <td>
              <button class="btn btn-sm" @click="edit(p)">Editar</button>
              <button class="btn btn-sm danger" @click="remove(p)">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="results-summary">Total: {{ formatCurrency(store.totalAmount) }}</div>
    </div>

    <div v-if="showAdd || editing" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header"><h3>{{ editing ? 'Editar Pagamento' : 'Novo Pagamento' }}</h3><button @click="closeModal">×</button></div>
        <div class="modal-body">
          <form @submit.prevent="save">
            <div class="form-group"><label>Referência</label><input v-model="form.reference" required /></div>
            <div class="form-group"><label>Valor</label><input type="number" step="0.01" v-model.number="form.amount" required /></div>
            <div class="form-group"><label>Data</label><input type="date" v-model="form.date" required /></div>
            <div class="form-group"><label>Fornecedor</label><input v-model="form.vendor" /></div>
            <div class="form-group"><label>Método</label><input v-model="form.method" /></div>
            <div class="modal-actions"><button type="button" @click="closeModal">Cancelar</button><button type="submit" class="btn btn-primary">Salvar</button></div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { usePaymentsStore } from '@/stores/payments'
import LoadingState from '@/components/common/LoadingState.vue'
import { useToast } from '@/composables/useToast'

const store = usePaymentsStore()
const { success, error } = useToast()

const showAdd = ref(false)
const editing = ref(null)
const form = ref({ reference: '', amount: 0, date: '', vendor: '', method: '' })

const reload = async () => {
  const res = await store.fetchPayments()
  if (!res.success) error('Erro ao carregar pagamentos')
}

const edit = (p) => { editing.value = p; form.value = { ...p } }
const closeModal = () => { showAdd.value = false; editing.value = null; form.value = { reference: '', amount: 0, date: '', vendor: '', method: '' } }

const save = async () => {
  if (editing.value) {
    const res = await store.updatePayment(editing.value.id, form.value)
    if (res.success) success('Pagamento atualizado')
    else error('Erro')
  } else {
    const res = await store.addPayment(form.value)
    if (res.success) success('Pagamento registrado')
    else error('Erro')
  }
  closeModal()
}

const remove = async (p) => {
  if (!confirm(`Excluir pagamento ${p.reference}?`)) return
  const res = await store.deletePayment(p.id)
  if (res.success) success('Removido')
  else error('Erro ao remover')
}

const formatCurrency = (v) => new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'}).format(Number(v||0))

onMounted(reload)
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;padding:1rem}
.table th,.table td{padding:0.5rem;border-bottom:1px solid #eee}
.results-summary{padding:1rem;font-weight:600}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center}
.modal{background:#fff;width:560px;border-radius:6px}
.modal-header{display:flex;justify-content:space-between;padding:1rem;border-bottom:1px solid #eee}
.modal-body{padding:1rem}
</style>
