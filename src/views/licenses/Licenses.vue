<template>
  <div class="licenses-page">
    <div class="page-header">
      <div class="page-header-content">
        <h1>Licenças</h1>
        <p>Gerencie chaves, assentos e vencimentos de licenças.</p>
      </div>
      <div class="page-actions">
        <button class="btn btn-primary" @click="showAdd = true">Nova Licença</button>
      </div>
    </div>

    <LoadingState v-if="loading" />

    <div v-else>
      <table class="table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Fornecedor</th>
            <th>Chave/Tipo</th>
            <th>Assentos</th>
            <th>Vencimento</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="l in store.items" :key="l.id">
            <td>{{ l.name }}</td>
            <td>{{ l.vendor }}</td>
            <td class="asset-serial">{{ l.key }}</td>
            <td>{{ l.seats || '-' }}</td>
            <td>{{ l.expiry || '-' }}</td>
            <td>
              <button class="btn btn-sm" @click="edit(l)">Editar</button>
              <button class="btn btn-sm danger" @click="remove(l)">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <LicenseForm v-if="showAdd" @close="showAdd = false" @saved="reload" />
    <LicenseForm v-if="editing" :license="editing" @close="closeEdit" @saved="reload" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import LoadingState from '@/components/common/LoadingState.vue'
import LicenseForm from '@/components/licenses/LicenseForm.vue'
import { useLicensesStore } from '@/stores/licenses'
import { useToast } from '@/composables/useToast'

const store = useLicensesStore()
const { success, error } = useToast()

const showAdd = ref(false)
const editing = ref(null)

const reload = async () => {
  const res = await store.fetchLicenses()
  if (!res.success) error('Não foi possível carregar licenças')
}

const edit = (l) => { editing.value = l }
const closeEdit = () => { editing.value = null }

const remove = async (l) => {
  if (!confirm(`Excluir licença ${l.name}?`)) return
  const res = await store.deleteLicense(l.id)
  if (res.success) success('Licença removida')
  else error('Erro ao remover licença')
}

onMounted(reload)
</script>

<style scoped>
.page-header { display:flex; justify-content:space-between; align-items:center; padding:1rem }
.table { width:100%; border-collapse:collapse }
.table th, .table td { padding:0.5rem; border-bottom:1px solid #eee }
</style>
