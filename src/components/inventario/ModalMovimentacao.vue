<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2>
          <i class="fas fa-exchange-alt"></i>
          Movimentação de {{ ativos.length === 1 ? 'Ativo' : 'Ativos' }}
        </h2>
        <button class="btn-close" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <!-- Ativos Selecionados -->
        <div class="ativos-section">
          <h3>
            <i class="fas fa-boxes"></i>
            {{ ativos.length === 1 ? 'Ativo Selecionado' : `${ativos.length} Ativos Selecionados` }}
          </h3>
          
          <div class="ativos-list">
            <div v-for="ativo in ativos" :key="ativo.id" class="ativo-item">
              <div class="ativo-icon">
                <i :class="getCategoriaIcon(ativo.categoria)"></i>
              </div>
              <div class="ativo-info">
                <h4>{{ ativo.descricao }}</h4>
                <p>{{ ativo.codigo }} - {{ ativo.patrimonio }}</p>
                <div class="ativo-meta">
                  <span class="categoria">{{ ativo.categoria }}</span>
                  <span class="local-atual">
                    <i class="fas fa-map-marker-alt"></i>
                    {{ ativo.local?.nome_completo || 'Sem localização' }}
                  </span>
                </div>
              </div>
              <div class="ativo-status">
                <span class="badge" :class="getStatusClass(ativo.status)">
                  {{ getStatusLabel(ativo.status) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Formulário de Movimentação -->
        <form @submit.prevent="salvar" class="movimentacao-form">
          <div class="form-section">
            <h3>Dados da Movimentação</h3>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="tipo">Tipo de Movimentação *</label>
                <select 
                  id="tipo" 
                  v-model="form.tipo" 
                  required
                  @change="onTipoChange"
                >
                  <option value="">Selecione...</option>
                  <option value="transferencia">Transferência</option>
                  <option value="alocacao">Alocação</option>
                  <option value="devolucao">Devolução</option>
                  <option value="manutencao">Envio para Manutenção</option>
                  <option value="baixa">Baixa do Ativo</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="data_movimentacao">Data da Movimentação *</label>
                <input 
                  id="data_movimentacao"
                  type="datetime-local" 
                  v-model="form.data_movimentacao"
                  required
                  :max="dataMaxima"
                >
              </div>
            </div>
          </div>

          <!-- Localização -->
          <div class="form-section" v-if="mostrarLocalizacao">
            <h3>Nova Localização</h3>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="setor_destino">Setor de Destino *</label>
                <select 
                  id="setor_destino" 
                  v-model="form.setor_destino_id" 
                  required
                  @change="filtrarLocaisDestino"
                >
                  <option value="">Selecione...</option>
                  <option v-for="setor in setores" :key="setor.id" :value="setor.id">
                    {{ setor.nome }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="local_destino">Local de Destino *</label>
                <select 
                  id="local_destino" 
                  v-model="form.local_destino_id" 
                  required
                  :disabled="!form.setor_destino_id"
                >
                  <option value="">Selecione...</option>
                  <option v-for="local in locaisDestinoFiltrados" :key="local.id" :value="local.id">
                    {{ local.nome_completo }}
                  </option>
                </select>
              </div>
            </div>
          </div>

          <!-- Responsabilidade -->
          <div class="form-section" v-if="mostrarResponsavel">
            <h3>Responsabilidade</h3>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="responsavel_destino">Novo Responsável</label>
                <select id="responsavel_destino" v-model="form.responsavel_destino_id">
                  <option value="">Selecione...</option>
                  <option v-for="resp in responsaveis" :key="resp.id" :value="resp.id">
                    {{ resp.nome }} - {{ resp.cargo }}
                  </option>
                </select>
              </div>
              
              <div class="form-group" v-if="form.tipo === 'alocacao'">
                <label for="data_devolucao_prevista">Data de Devolução Prevista</label>
                <input 
                  id="data_devolucao_prevista"
                  type="date" 
                  v-model="form.data_devolucao_prevista"
                  :min="dataMinima"
                >
              </div>
            </div>
          </div>

          <!-- Manutenção -->
          <div class="form-section" v-if="form.tipo === 'manutencao'">
            <h3>Dados da Manutenção</h3>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="fornecedor_manutencao">Fornecedor de Manutenção *</label>
                <select id="fornecedor_manutencao" v-model="form.fornecedor_id" required>
                  <option value="">Selecione...</option>
                  <option v-for="forn in fornecedores" :key="forn.id" :value="forn.id">
                    {{ forn.nome }}
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="tipo_manutencao">Tipo de Manutenção *</label>
                <select id="tipo_manutencao" v-model="form.tipo_manutencao" required>
                  <option value="">Selecione...</option>
                  <option value="preventiva">Preventiva</option>
                  <option value="corretiva">Corretiva</option>
                  <option value="preditiva">Preditiva</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="previsao_retorno">Previsão de Retorno</label>
                <input 
                  id="previsao_retorno"
                  type="date" 
                  v-model="form.previsao_retorno"
                  :min="dataMinima"
                >
              </div>
            </div>
          </div>

          <!-- Baixa -->
          <div class="form-section" v-if="form.tipo === 'baixa'">
            <h3>Dados da Baixa</h3>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="motivo_baixa">Motivo da Baixa *</label>
                <select id="motivo_baixa" v-model="form.motivo_baixa" required>
                  <option value="">Selecione...</option>
                  <option value="obsolescencia">Obsolescência</option>
                  <option value="defeito_irreparavel">Defeito Irreparável</option>
                  <option value="perda">Perda</option>
                  <option value="furto">Furto</option>
                  <option value="venda">Venda</option>
                  <option value="doacao">Doação</option>
                  <option value="descarte">Descarte</option>
                </select>
              </div>
              
              <div class="form-group" v-if="['venda', 'doacao'].includes(form.motivo_baixa)">
                <label for="valor_baixa">Valor da {{ form.motivo_baixa === 'venda' ? 'Venda' : 'Avaliação' }}</label>
                <div class="input-group">
                  <span class="input-prefix">R$</span>
                  <input 
                    id="valor_baixa"
                    type="number" 
                    step="0.01"
                    v-model="form.valor_baixa"
                    placeholder="0,00"
                  >
                </div>
              </div>
              
              <div class="form-group" v-if="form.motivo_baixa === 'venda'">
                <label for="comprador">Comprador</label>
                <input 
                  id="comprador"
                  type="text" 
                  v-model="form.comprador"
                  placeholder="Nome do comprador"
                >
              </div>
            </div>
          </div>

          <!-- Observações -->
          <div class="form-section">
            <h3>Observações</h3>
            
            <div class="form-group">
              <label for="observacoes">Observações da Movimentação</label>
              <textarea 
                id="observacoes"
                v-model="form.observacoes"
                rows="3"
                placeholder="Descreva detalhes sobre a movimentação..."
              ></textarea>
            </div>
            
            <div class="form-group">
              <label for="anexos">Anexos</label>
              <div class="upload-area" @drop="handleDrop" @dragover.prevent @dragenter.prevent>
                <input 
                  type="file" 
                  ref="fileInput"
                  multiple 
                  accept=".pdf,.doc,.docx,.jpg,.jpeg,.png"
                  @change="handleFileSelect"
                  style="display: none"
                >
                <div class="upload-content" @click="$refs.fileInput.click()">
                  <i class="fas fa-paperclip"></i>
                  <p>Clique ou arraste arquivos aqui</p>
                  <small>PDF, DOC, JPG até 10MB cada</small>
                </div>
              </div>
              
              <div v-if="form.anexos.length > 0" class="anexos-list">
                <div 
                  v-for="(anexo, index) in form.anexos" 
                  :key="index" 
                  class="anexo-item"
                >
                  <i :class="getFileIcon(anexo.tipo)"></i>
                  <span>{{ anexo.nome }}</span>
                  <button type="button" @click="removerAnexo(index)">
                    <i class="fas fa-times"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Resumo -->
          <div class="resumo-section">
            <h3>Resumo da Movimentação</h3>
            
            <div class="resumo-content">
              <div class="resumo-item">
                <label>Tipo:</label>
                <span>{{ getTipoLabel(form.tipo) }}</span>
              </div>
              
              <div class="resumo-item">
                <label>Data:</label>
                <span>{{ formatarDataHora(form.data_movimentacao) }}</span>
              </div>
              
              <div class="resumo-item" v-if="localDestinoSelecionado">
                <label>Destino:</label>
                <span>{{ localDestinoSelecionado.nome_completo }}</span>
              </div>
              
              <div class="resumo-item" v-if="responsavelDestinoSelecionado">
                <label>Responsável:</label>
                <span>{{ responsavelDestinoSelecionado.nome }}</span>
              </div>
              
              <div class="resumo-item" v-if="form.tipo === 'baixa'">
                <label>Motivo:</label>
                <span>{{ getMotivoBaixaLabel(form.motivo_baixa) }}</span>
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
          {{ salvando ? 'Salvando...' : 'Confirmar Movimentação' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'

// Props
const props = defineProps({
  ativos: {
    type: Array,
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'save'])

// Estados
const salvando = ref(false)
const setores = ref([])
const locais = ref([])
const responsaveis = ref([])
const fornecedores = ref([])

// Formulário
const form = ref({
  tipo: '',
  data_movimentacao: new Date().toISOString().slice(0, 16),
  setor_destino_id: '',
  local_destino_id: '',
  responsavel_destino_id: '',
  data_devolucao_prevista: '',
  fornecedor_id: '',
  tipo_manutencao: '',
  previsao_retorno: '',
  motivo_baixa: '',
  valor_baixa: '',
  comprador: '',
  observacoes: '',
  anexos: []
})

// Computed
const dataMaxima = computed(() => {
  return new Date().toISOString().slice(0, 16)
})

const dataMinima = computed(() => {
  return new Date().toISOString().slice(0, 10)
})

const mostrarLocalizacao = computed(() => {
  return ['transferencia', 'alocacao', 'devolucao'].includes(form.value.tipo)
})

const mostrarResponsavel = computed(() => {
  return ['transferencia', 'alocacao', 'devolucao'].includes(form.value.tipo)
})

const locaisDestinoFiltrados = computed(() => {
  if (!form.value.setor_destino_id) return []
  return locais.value.filter(local => local.setor_id === form.value.setor_destino_id)
})

const localDestinoSelecionado = computed(() => {
  return locais.value.find(local => local.id === form.value.local_destino_id)
})

const responsavelDestinoSelecionado = computed(() => {
  return responsaveis.value.find(resp => resp.id === form.value.responsavel_destino_id)
})

// Métodos
const carregarDados = async () => {
  // Simular carregamento de dados
  setores.value = [
    { id: 1, nome: 'TI' },
    { id: 2, nome: 'Administrativo' },
    { id: 3, nome: 'Comercial' },
    { id: 4, nome: 'Financeiro' }
  ]
  
  locais.value = [
    { id: 1, nome_completo: 'Sede - 1º Andar - Sala 101', setor_id: 1 },
    { id: 2, nome_completo: 'Sede - 1º Andar - Sala 102', setor_id: 2 },
    { id: 3, nome_completo: 'Sede - 2º Andar - Sala 201', setor_id: 3 },
    { id: 4, nome_completo: 'Almoxarifado Central', setor_id: 2 },
    { id: 5, nome_completo: 'Oficina de Manutenção', setor_id: 1 }
  ]
  
  responsaveis.value = [
    { id: 1, nome: 'João Silva', cargo: 'Analista de TI' },
    { id: 2, nome: 'Maria Santos', cargo: 'Gerente Administrativo' },
    { id: 3, nome: 'Pedro Oliveira', cargo: 'Coordenador Comercial' },
    { id: 4, nome: 'Ana Costa', cargo: 'Assistente Financeiro' }
  ]
  
  fornecedores.value = [
    { id: 1, nome: 'TechService Ltda' },
    { id: 2, nome: 'InfoManutenção' },
    { id: 3, nome: 'Assistência Técnica ABC' }
  ]
}

const onTipoChange = () => {
  // Limpar campos específicos quando mudar o tipo
  form.value.setor_destino_id = ''
  form.value.local_destino_id = ''
  form.value.responsavel_destino_id = ''
  form.value.fornecedor_id = ''
  form.value.motivo_baixa = ''
}

const filtrarLocaisDestino = () => {
  form.value.local_destino_id = ''
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
    if (file.size <= 10 * 1024 * 1024) { // 10MB
      form.value.anexos.push({
        nome: file.name,
        tipo: file.type,
        arquivo: file
      })
    }
  })
}

const removerAnexo = (index) => {
  form.value.anexos.splice(index, 1)
}

const salvar = async () => {
  salvando.value = true
  
  try {
    // Validações
    if (!form.value.tipo) {
      throw new Error('Selecione o tipo de movimentação')
    }
    
    if (mostrarLocalizacao.value && !form.value.local_destino_id) {
      throw new Error('Selecione o local de destino')
    }
    
    if (form.value.tipo === 'manutencao' && !form.value.fornecedor_id) {
      throw new Error('Selecione o fornecedor de manutenção')
    }
    
    if (form.value.tipo === 'baixa' && !form.value.motivo_baixa) {
      throw new Error('Selecione o motivo da baixa')
    }
    
    // Preparar dados para envio
    const dadosMovimentacao = {
      ...form.value,
      ativos_ids: props.ativos.map(a => a.id)
    }
    
    emit('save', dadosMovimentacao)
  } catch (error) {
    useToast().showToast(error.message, 'error')
  } finally {
    salvando.value = false
  }
}

// Helpers
const getCategoriaIcon = (categoria) => {
  const icons = {
    'Informática': 'fas fa-laptop',
    'Móveis': 'fas fa-chair',
    'Equipamentos': 'fas fa-cogs',
    'Veículos': 'fas fa-car'
  }
  return icons[categoria] || 'fas fa-box'
}

const getStatusClass = (status) => {
  const classes = {
    'ativo': 'badge-success',
    'alocado': 'badge-info',
    'em_manutencao': 'badge-warning',
    'baixado': 'badge-danger'
  }
  return classes[status] || 'badge-secondary'
}

const getStatusLabel = (status) => {
  const labels = {
    'ativo': 'Ativo',
    'alocado': 'Alocado',
    'em_manutencao': 'Em Manutenção',
    'baixado': 'Baixado'
  }
  return labels[status] || status
}

const getTipoLabel = (tipo) => {
  const labels = {
    'transferencia': 'Transferência',
    'alocacao': 'Alocação',
    'devolucao': 'Devolução',
    'manutencao': 'Envio para Manutenção',
    'baixa': 'Baixa do Ativo'
  }
  return labels[tipo] || tipo
}

const getMotivoBaixaLabel = (motivo) => {
  const labels = {
    'obsolescencia': 'Obsolescência',
    'defeito_irreparavel': 'Defeito Irreparável',
    'perda': 'Perda',
    'furto': 'Furto',
    'venda': 'Venda',
    'doacao': 'Doação',
    'descarte': 'Descarte'
  }
  return labels[motivo] || motivo
}

const getFileIcon = (tipo) => {
  if (tipo.includes('pdf')) return 'fas fa-file-pdf'
  if (tipo.includes('word')) return 'fas fa-file-word'
  if (tipo.includes('image')) return 'fas fa-file-image'
  return 'fas fa-file'
}

const formatarDataHora = (data) => {
  if (!data) return '-'
  return new Date(data).toLocaleString('pt-BR')
}

// Lifecycle
onMounted(() => {
  carregarDados()
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
  max-width: 800px;
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

.ativos-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.ativos-section h3 {
  margin: 0 0 20px 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.ativos-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ativo-item {
  background: var(--background-secondary);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 16px;
}

.ativo-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--primary-light);
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.ativo-info {
  flex: 1;
}

.ativo-info h4 {
  margin: 0 0 4px 0;
  color: var(--text-primary);
  font-size: 16px;
}

.ativo-info p {
  margin: 0 0 8px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.ativo-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
}

.categoria {
  background: var(--info-light);
  color: var(--info-color);
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
}

.local-atual {
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
}

.ativo-status {
  flex-shrink: 0;
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
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
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

.anexos-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.anexo-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--background-secondary);
  border-radius: 6px;
  border: 1px solid var(--border-color);
}

.anexo-item i {
  color: var(--text-secondary);
}

.anexo-item span {
  flex: 1;
  font-size: 14px;
  color: var(--text-primary);
}

.anexo-item button {
  background: none;
  border: none;
  color: var(--danger-color);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.anexo-item button:hover {
  background: var(--danger-light);
}

.resumo-section {
  background: var(--background-secondary);
  border-radius: 8px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.resumo-section h3 {
  margin: 0 0 16px 0;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
}

.resumo-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.resumo-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.resumo-item label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.resumo-item span {
  color: var(--text-primary);
  font-weight: 500;
}

.modal-footer {
  padding: 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Badges */
.badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.badge-success {
  background: var(--success-light);
  color: var(--success-color);
}

.badge-info {
  background: var(--info-light);
  color: var(--info-color);
}

.badge-warning {
  background: var(--warning-light);
  color: var(--warning-color);
}

.badge-danger {
  background: var(--danger-light);
  color: var(--danger-color);
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
  
  .resumo-content {
    grid-template-columns: 1fr;
  }
  
  .ativo-item {
    flex-direction: column;
    text-align: center;
  }
}
</style>