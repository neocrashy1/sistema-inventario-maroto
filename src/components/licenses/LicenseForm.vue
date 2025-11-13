<template>
  <div class="modal-overlay" @click.self="close">
    <div class="modal">
      <div class="modal-header">
        <h3>{{ license ? 'Editar Licença' : 'Nova Licença' }}</h3>
        <button class="btn-icon" @click="close">×</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="save">
          <div class="form-group">
            <label>Nome</label>
            <input v-model="form.name" required />
          </div>
          <div class="form-group">
            <label>Fornecedor</label>
            <input v-model="form.vendor" />
          </div>
          <div class="form-group">
            <label>Chave / Tipo</label>
            <input v-model="form.key" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>Assentos</label>
              <input type="number" v-model.number="form.seats" />
            </div>
            <div class="form-group">
              <label>Vencimento</label>
              <input type="date" v-model="form.expiry" />
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn" @click="close">Cancelar</button>
            <button type="submit" class="btn btn-primary">Salvar</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useLicensesStore } from '@/stores/licenses'
import { useToast } from '@/composables/useToast'

const props = defineProps({ license: { type: Object, default: null } })
const emit = defineEmits(['close','saved'])

const store = useLicensesStore()
const { success, error } = useToast()

const form = ref({ name: '', vendor: '', key: '', seats: 0, expiry: '' })

watch(() => props.license, (val) => {
  if (val) form.value = { ...val }
})

const close = () => emit('close')

const save = async () => {
  if (props.license) {
    const res = await store.updateLicense(props.license.id, form.value)
    if (res.success) { success('Licença atualizada'); emit('saved') ; close() }
    else error('Erro ao atualizar')
  } else {
    const res = await store.addLicense(form.value)
    if (res.success) { success('Licença criada'); emit('saved'); close() }
    else error('Erro ao criar')
  }
}
</script>

<style scoped>
.modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center}
.modal{background:white;width:560px;border-radius:8px;overflow:hidden}
.modal-header{display:flex;justify-content:space-between;padding:1rem;border-bottom:1px solid #eee}
.modal-body{padding:1rem}
.form-group{margin-bottom:0.75rem}
.form-row{display:flex;gap:1rem}
.modal-actions{display:flex;justify-content:flex-end;gap:0.5rem;margin-top:1rem}
</style>
