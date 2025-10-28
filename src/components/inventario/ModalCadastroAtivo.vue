<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2>
          <i class="fas fa-box"></i>
          {{ ativo?.id ? 'Editar Ativo' : 'Novo Ativo' }}
        </h2>
        <button class="btn-close" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="salvar">
          <!-- Informações Básicas -->
          <div class="form-section">
            <h3>Informações Básicas</h3>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="codigo">Código do Ativo *</label>
                <input 
                  id="codigo"
                  type="text" 
                  v-model="form.codigo"
                  :readonly="!!ativo?.id"
                  required
                  placeholder="Ex: AT001"
                >
              </div>
              
              <div class="form-group">
                <label for="patrimonio">Nº Patrimônio</label>
                <input 
                  id="patrimonio"
                  type="text" 
                  v-model="form.patrimonio"
                  placeholder="Ex: PAT001"
                >
              </div>
              
              <div class="form-group">
                <label for="categoria">Categoria *</label>
                <select id="categoria" v-model="form.categoria_id" required>
                  <option value="">Selecione...</option>
                  <option v-for="cat in categorias" :key="cat.id" :value="cat.id">
                    {{ cat.nome }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="subcategoria">Subcategoria</label>
                <select id="subcategoria" v-model="form.subcategoria_id">
                  <option value="">Selecione...</option>
                  <option v-for="sub in subcategoriasFiltradas" :key="sub.id" :value="sub.id">
                    {{ sub.nome }}
                  </option>
                </select>
              </div>
            </div>
            
            <div class="form-group">
              <label for="descricao">Descrição *</label>
              <input 
                id="descricao"
                type="text" 
                v-model="form.descricao"
                required
                placeholder="Descrição detalhada do ativo"
              >
            </div>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="marca">Marca</label>
                <input 
                  id="marca"
                  type="text" 
                  v-model="form.marca"
                  placeholder="Ex: Dell, HP, Samsung"
                >
              </div>
              
              <div class="form-group">
                <label for="modelo">Modelo</label>
                <input 
                  id="modelo"
                  type="text" 
                  v-model="form.modelo"
                  placeholder="Ex: Latitude 5520"
                >
              </div>
              
              <div class="form-group">
                <label for="numero_serie">Número de Série</label>
                <input 
                  id="numero_serie"
                  type="text" 
                  v-model="form.numero_serie"
                  placeholder="Ex: ABC123456"
                >
              </div>
              
              <div class="form-group">
                <label for="estado">Estado *</label>
                <select id="estado" v-model="form.estado" required>
                  <option value="">Selecione...</option>
                  <option value="novo">Novo</option>
                  <option value="uso">Em Uso</option>
                  <option value="obsoleto">Obsoleto</option>
                  <option value="sucata">Sucata</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Informações Financeiras -->
          <div class="form-section">
            <h3>Informações Financeiras</h3>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="valor_aquisicao">Valor de Aquisição *</label>
                <div class="input-group">
                  <span class="input-prefix">R$</span>
                  <input 
                    id="valor_aquisicao"
                    type="number" 
                    step="0.01"
                    v-model="form.valor_aquisicao"
                    required
                    placeholder="0,00"
                  >
                </div>
              </div>
              
              <div class="form-group">
                <label for="data_compra">Data da Compra</label>
                <input 
                  id="data_compra"
                  type="date" 
                  v-model="form.data_compra"
                >
              </div>
              
              <div class="form-group">
                <label for="nota_fiscal">Nota Fiscal</label>
                <input 
                  id="nota_fiscal"
                  type="text" 
                  v-model="form.nota_fiscal"
                  placeholder="Ex: NF123456"
                >
              </div>
              
              <div class="form-group">
                <label for="vida_util_meses">Vida Útil (meses)</label>
                <input 
                  id="vida_util_meses"
                  type="number" 
                  v-model="form.vida_util_meses"
                  placeholder="Ex: 60"
                >
              </div>
            </div>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="centro_custo">Centro de Custo *</label>
                <select id="centro_custo" v-model="form.centro_custo_id" required>
                  <option value="">Selecione...</option>
                  <option v-for="cc in centrosCusto" :key="cc.id" :value="cc.id">
                    {{ cc.codigo }} - {{ cc.nome }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="fornecedor">Fornecedor</label>
                <select id="fornecedor" v-model="form.fornecedor_id">
                  <option value="">Selecione...</option>
                  <option v-for="forn in fornecedores" :key="forn.id" :value="forn.id">
                    {{ forn.nome }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="garantia_ate">Garantia até</label>
                <input 
                  id="garantia_ate"
                  type="date" 
                  v-model="form.garantia_ate"
                >
              </div>
            </div>
          </div>

          <!-- Localização e Responsabilidade -->
          <div class="form-section">
            <h3>Localização e Responsabilidade</h3>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="setor">Setor *</label>
                <select id="setor" v-model="form.setor_id" required @change="filtrarLocais">
                  <option value="">Selecione...</option>
                  <option v-for="setor in setores" :key="setor.id" :value="setor.id">
                    {{ setor.nome }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="local">Localização Física *</label>
                <select id="local" v-model="form.local_id" required>
                  <option value="">Selecione...</option>
                  <option v-for="local in locaisFiltrados" :key="local.id" :value="local.id">
                    {{ local.nome_completo }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="responsavel">Responsável</label>
                <select id="responsavel" v-model="form.responsavel_id">
                  <option value="">Selecione...</option>
                  <option v-for="resp in responsaveis" :key="resp.id" :value="resp.id">
                    {{ resp.nome }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="status">Status *</label>
                <select id="status" v-model="form.status" required>
                  <option value="">Selecione...</option>
                  <option value="ativo">Ativo</option>
                  <option value="alocado">Alocado</option>
                  <option value="em_manutencao">Em Manutenção</option>
                  <option value="baixado">Baixado</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Informações Adicionais -->
          <div class="form-section">
            <h3>Informações Adicionais</h3>
            
            <div class="form-group">
              <label for="observacoes">Observações</label>
              <textarea 
                id="observacoes"
                v-model="form.observacoes"
                rows="3"
                placeholder="Observações adicionais sobre o ativo"
              ></textarea>
            </div>
            
            <div class="form-group">
              <label for="tags">Tags</label>
              <div class="tags-input">
                <div class="tags-list">
                  <span 
                    v-for="(tag, index) in form.tags" 
                    :key="index" 
                    class="tag"
                  >
                    {{ tag }}
                    <button type="button" @click="removerTag(index)">
                      <i class="fas fa-times"></i>
                    </button>
                  </span>
                </div>
                <input 
                  type="text" 
                  v-model="novaTag"
                  @keydown.enter.prevent="adicionarTag"
                  @keydown.comma.prevent="adicionarTag"
                  placeholder="Digite uma tag e pressione Enter"
                >
              </div>
            </div>
            
            <!-- Upload de Fotos -->
            <div class="form-group">
              <label>Fotos do Ativo</label>
              <div class="upload-area" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
                <input 
                  type="file" 
                  ref="fileInput"
                  multiple 
                  accept="image/*"
                  @change="handleFileSelect"
                  style="display: none"
                >
                <div class="upload-content" @click="$refs.fileInput.click()">
                  <i class="fas fa-cloud-upload-alt"></i>
                  <p>Clique ou arraste fotos aqui</p>
                  <small>PNG, JPG até 5MB cada</small>
                </div>
              </div>
              
              <div v-if="form.fotos.length > 0" class="fotos-preview">
                <div 
                  v-for="(foto, index) in form.fotos" 
                  :key="index" 
                  class="foto-item"
                >
                  <img :src="foto.url" :alt="foto.nome">
                  <button type="button" @click="removerFoto(index)" class="btn-remove-foto">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- QR Code / NFC -->
          <div class="form-section" v-if="ativo?.id">
            <h3>Identificação</h3>
            
            <div class="qr-section">
              <div class="qr-info">
                <h4>QR Code / NFC</h4>
                <p>Use o código abaixo para identificar este ativo</p>
                <button type="button" class="btn btn-outline" @click="gerarEtiqueta">
                  <i class="fas fa-print"></i>
                  Imprimir Etiqueta
                </button>
              </div>
              <div class="qr-code">
                <canvas ref="qrCanvas"></canvas>
              </div>
            </div>
          </div>
        </form>
      </div>

      <div class="modal-footer">
        <button type="button" class="btn btn-outline" @click="$emit('close')">
          Cancelar
        </button>
        <button type="submit" class="btn btn-primary" @click="salvar" :disabled="salvando">
          <i class="fas fa-save"></i>
          {{ salvando ? 'Salvando...' : 'Salvar' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useToast } from '@/composables/useToast'
import QRCode from 'qrcode'

// Props
const props = defineProps({
  ativo: {
    type: Object,
    default: null
  }
})

// Emits
const emit = defineEmits(['close', 'save'])

// Estados
const salvando = ref(false)
const novaTag = ref('')

// Dados do formulário
const form = ref({
  codigo: '',
  patrimonio: '',
  categoria_id: '',
  subcategoria_id: '',
  descricao: '',
  marca: '',
  modelo: '',
  numero_serie: '',
  estado: '',
  valor_aquisicao: '',
  data_compra: '',
  nota_fiscal: '',
  vida_util_meses: 60,
  centro_custo_id: '',
  setor_id: '',
  local_id: '',
  responsavel_id: '',
  status: 'ativo',
  garantia_ate: '',
  fornecedor_id: '',
  observacoes: '',
  tags: [],
  fotos: []
})

// Dados de apoio
const categorias = ref([])
const subcategorias = ref([])
const centrosCusto = ref([])
const setores = ref([])
const locais = ref([])
const responsaveis = ref([])
const fornecedores = ref([])

// Computed
const subcategoriasFiltradas = computed(() => {
  if (!form.value.categoria_id) return []
  return subcategorias.value.filter(sub => sub.categoria_id === form.value.categoria_id)
})

const locaisFiltrados = computed(() => {
  if (!form.value.setor_id) return []
  return locais.value.filter(local => local.setor_id === form.value.setor_id)
})

// Métodos
const carregarDados = async () => {
  // Simular carregamento de dados
  categorias.value = [
    { id: 1, nome: 'Informática' },
    { id: 2, nome: 'Móveis' },
    { id: 3, nome: 'Equipamentos' },
    { id: 4, nome: 'Veículos' }
  ]
  
  subcategorias.value = [
    { id: 1, nome: 'Notebooks', categoria_id: 1 },
    { id: 2, nome: 'Desktops', categoria_id: 1 },
    { id: 3, nome: 'Monitores', categoria_id: 1 },
    { id: 4, nome: 'Mesas', categoria_id: 2 },
    { id: 5, nome: 'Cadeiras', categoria_id: 2 }
  ]
  
  centrosCusto.value = [
    { id: 1, codigo: 'TI001', nome: 'Tecnologia da Informação' },
    { id: 2, codigo: 'ADM001', nome: 'Administrativo' },
    { id: 3, codigo: 'COM001', nome: 'Comercial' }
  ]
  
  setores.value = [
    { id: 1, nome: 'TI' },
    { id: 2, nome: 'Administrativo' },
    { id: 3, nome: 'Comercial' },
    { id: 4, nome: 'Financeiro' }
  ]
  
  locais.value = [
    { id: 1, nome_completo: 'Sede - 1º Andar - Sala 101', setor_id: 1 },
    { id: 2, nome_completo: 'Sede - 1º Andar - Sala 102', setor_id: 2 },
    { id: 3, nome_completo: 'Sede - 2º Andar - Sala 201', setor_id: 3 }
  ]
  
  responsaveis.value = [
    { id: 1, nome: 'João Silva' },
    { id: 2, nome: 'Maria Santos' },
    { id: 3, nome: 'Pedro Oliveira' }
  ]
  
  fornecedores.value = [
    { id: 1, nome: 'Dell Computadores' },
    { id: 2, nome: 'HP Brasil' },
    { id: 3, nome: 'Móveis Escritório Ltda' }
  ]
}

const inicializarFormulario = () => {
  if (props.ativo) {
    Object.assign(form.value, {
      ...props.ativo,
      tags: props.ativo.tags || [],
      fotos: props.ativo.fotos || []
    })
  } else {
    // Gerar código automático para novo ativo
    form.value.codigo = gerarCodigoAtivo()
  }
}

const gerarCodigoAtivo = () => {
  const timestamp = Date.now().toString().slice(-6)
  return `AT${timestamp}`
}

const filtrarLocais = () => {
  form.value.local_id = ''
}

const adicionarTag = () => {
  if (novaTag.value.trim() && !form.value.tags.includes(novaTag.value.trim())) {
    form.value.tags.push(novaTag.value.trim())
    novaTag.value = ''
  }
}

const removerTag = (index) => {
  form.value.tags.splice(index, 1)
}

const handleFileSelect = (event) => {
  const files = Array.from(event.target.files)
  processarArquivos(files)
}

const handleDrop = (event) => {
  event.preventDefault()
  const files = Array.from(event.dataTransfer.files)
  processarArquivos(files)
}

const processarArquivos = (files) => {
  files.forEach(file => {
    if (file.type.startsWith('image/') && file.size <= 5 * 1024 * 1024) {
      const reader = new FileReader()
      reader.onload = (e) => {
        form.value.fotos.push({
          nome: file.name,
          url: e.target.result,
          arquivo: file
        })
      }
      reader.readAsDataURL(file)
    }
  })
}

const removerFoto = (index) => {
  form.value.fotos.splice(index, 1)
}

const gerarQRCode = async () => {
  if (props.ativo?.id) {
    const canvas = document.querySelector('canvas')
    if (canvas) {
      const qrData = JSON.stringify({
        id: props.ativo.id,
        codigo: props.ativo.codigo,
        tipo: 'ativo'
      })
      
      await QRCode.toCanvas(canvas, qrData, {
        width: 150,
        margin: 2
      })
    }
  }
}

const gerarEtiqueta = () => {
  // Implementar geração de etiqueta para impressão
  window.print()
}

const salvar = async () => {
  salvando.value = true
  
  try {
    // Validações
    if (!form.value.codigo || !form.value.descricao || !form.value.categoria_id) {
      throw new Error('Preencha todos os campos obrigatórios')
    }
    
    // Preparar dados para envio
    const dadosAtivo = {
      ...form.value,
      tags: form.value.tags.join(',')
    }
    
    emit('save', dadosAtivo)
  } catch (error) {
    useToast().showToast(error.message, 'error')
  } finally {
    salvando.value = false
  }
}

// Watchers
watch(() => form.value.subcategoria_id, () => {
  if (!subcategoriasFiltradas.value.find(sub => sub.id === form.value.subcategoria_id)) {
    form.value.subcategoria_id = ''
  }
})

// Lifecycle
onMounted(async () => {
  await carregarDados()
  inicializarFormulario()
  
  if (props.ativo?.id) {
    setTimeout(gerarQRCode, 100)
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: var(--surface-color);
  border-radius: 12px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-primary);
}

.btn-close {
  background: none;
  border: none;
  font-size: 20px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.btn-close:hover {
  background: var(--background-secondary);
  color: var(--text-primary);
}

.modal-body {
  padding: 24px;
  max-height: calc(90vh - 140px);
  overflow-y: auto;
}

.form-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.form-section h3 {
  margin: 0 0 20px 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--primary-color);
}

.input-group {
  display: flex;
  align-items: center;
}

.input-prefix {
  background: var(--background-secondary);
  border: 1px solid var(--border-color);
  border-right: none;
  padding: 12px;
  border-radius: 8px 0 0 8px;
  color: var(--text-secondary);
  font-weight: 500;
}

.input-group input {
  border-radius: 0 8px 8px 0;
}

.tags-input {
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 8px;
  min-height: 80px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.tag {
  background: var(--primary-light);
  color: var(--primary-color);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
}

.tag button {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0;
  font-size: 10px;
}

.tags-input input {
  border: none;
  outline: none;
  flex: 1;
  padding: 4px;
}

.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-area:hover {
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.upload-content i {
  font-size: 48px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.upload-content p {
  margin: 0 0 8px 0;
  color: var(--text-primary);
  font-weight: 500;
}

.upload-content small {
  color: var(--text-secondary);
}

.fotos-preview {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.foto-item {
  position: relative;
  border-radius: 8px;
  overflow: hidden;
  aspect-ratio: 1;
}

.foto-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-remove-foto {
  position: absolute;
  top: 4px;
  right: 4px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.qr-section {
  display: flex;
  gap: 24px;
  align-items: center;
}

.qr-info {
  flex: 1;
}

.qr-info h4 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.qr-info p {
  margin: 0 0 16px 0;
  color: var(--text-secondary);
}

.qr-code {
  flex-shrink: 0;
}

.modal-footer {
  padding: 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Responsive */
@media (max-width: 768px) {
  .modal-container {
    margin: 0;
    height: 100vh;
    max-height: 100vh;
    border-radius: 0;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .qr-section {
    flex-direction: column;
    text-align: center;
  }
}
</style>