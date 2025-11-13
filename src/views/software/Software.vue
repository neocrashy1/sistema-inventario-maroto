<template>
  <div class="software-page">
    <div class="page-header">
      <div>
        <h1>Software</h1>
        <p>Inventário de aplicações instaladas e tipos de licença.</p>
      </div>
      <div>
        <button class="btn btn-primary" @click="showAdd = true">Novo Software</button>
      </div>
    </div>

    <LoadingState v-if="store.loading" />

    <div v-else>
      <table class="table">
        <thead>
          <tr><th>Nome</th><th>Versão</th><th>Licença</th><th>Instalado em</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="s in store.items" :key="s.id">
            <td>{{ s.name }}</td>
            <td>{{ s.version }}</td>
            <td>{{ s.license }}</td>
            <td>{{ s.installedOn }}</td>
            <td>
              <button class="btn btn-sm" @click="edit(s)">Editar</button>
              <button class="btn btn-sm danger" @click="remove(s)">Excluir</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="showAdd || editing" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header"><h3>{{ editing ? 'Editar' : 'Novo' }}</h3><button @click="closeModal">×</button></div>
        <div class="modal-body">
          <form @submit.prevent="save">
            <div class="form-group"><label>Nome</label><input v-model="form.name" required /></div>
            <div class="form-group"><label>Versão</label><input v-model="form.version" /></div>
            <div class="form-group"><label>Licença</label><input v-model="form.license" /></div>
            <div class="form-group"><label>Instalado em</label><input type="number" v-model.number="form.installedOn" /></div>
            <div class="modal-actions"><button type="button" @click="closeModal">Cancelar</button><button type="submit" class="btn btn-primary">Salvar</button></div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useSoftwareStore } from '@/stores/software'
import LoadingState from '@/components/common/LoadingState.vue'
import { useToast } from '@/composables/useToast'

const store = useSoftwareStore()
const { success, error } = useToast()

const showAdd = ref(false)
const editing = ref(null)
const form = ref({ name: '', version: '', license: '', installedOn: 0 })

const reload = async () => {
  const res = await store.fetchSoftware()
  if (!res.success) error('Erro ao carregar software')
}

const edit = (s) => { editing.value = s; form.value = { ...s } }
const closeModal = () => { showAdd.value = false; editing.value = null; form.value = { name: '', version: '', license: '', installedOn: 0 } }

const save = async () => {
  if (editing.value) {
    const res = await store.updateSoftware(editing.value.id, form.value)
    if (res.success) success('Software atualizado'); else error('Erro')
  } else {
    const res = await store.addSoftware(form.value)
    if (res.success) success('Software adicionado'); else error('Erro')
  }
  closeModal()
}

const remove = async (s) => {
  if (!confirm(`Excluir ${s.name}?`)) return
  const res = await store.deleteSoftware(s.id)
  if (res.success) success('Removido')
  else error('Erro ao remover')
}

onMounted(reload)
</script>

<style scoped>
.page-header{display:flex;justify-content:space-between;align-items:center;padding:1rem}
.table th,.table td{padding:0.5rem;border-bottom:1px solid #eee}
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center}
.modal{background:#fff;width:560px;border-radius:6px}
.modal-header{display:flex;justify-content:space-between;padding:1rem;border-bottom:1px solid #eee}
.modal-body{padding:1rem}
</style>
