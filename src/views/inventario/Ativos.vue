<template>
  <div class="ativos-page">
    <!-- Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <i class="fas fa-boxes"></i>
          Gestão de Ativos
        </h1>
        <p class="page-subtitle">
          Controle completo do inventário de ativos físicos da empresa
        </p>
      </div>
      
      <div class="header-actions">
        <button class="btn btn-outline" @click="showImportModal = true">
          <i class="fas fa-file-import"></i>
          Importar CSV
        </button>
        <button class="btn btn-secondary" @click="exportarAtivos">
          <i class="fas fa-download"></i>
          Exportar
        </button>
        <button class="btn btn-primary" @click="showCadastroModal = true">
          <i class="fas fa-plus"></i>
          Novo Ativo
        </button>
      </div>
    </div>

    <!-- Filtros Avançados -->
    <div class="filters-section">
      <div class="filters-header">
        <h3>Filtros</h3>
        <button class="btn btn-link" @click="limparFiltros">
          <i class="fas fa-times"></i>
          Limpar Filtros
        </button>
      </div>
      
      <div class="filters-grid">
        <div class="filter-group">
          <label>Busca Geral</label>
          <div class="search-input">
            <i class="fas fa-search"></i>
            <input 
              type="text" 
              placeholder="Código, patrimônio, descrição, marca..."
              v-model="filtros.texto"
              @input="aplicarFiltros"
            >
          </div>
        </div>
        
        <div class="filter-group">
          <label>Categoria</label>
          <select v-model="filtros.categoria" @change="aplicarFiltros">
            <option value="">Todas</option>
            <option v-for="cat in categorias" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Setor</label>
          <select v-model="filtros.setor" @change="aplicarFiltros">
            <option value="">Todos</option>
            <option v-for="setor in setores" :key="setor.id" :value="setor.id">{{ setor.nome }}</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Local</label>
          <select v-model="filtros.local" @change="aplicarFiltros">
            <option value="">Todos</option>
            <option v-for="local in locais" :key="local.id" :value="local.id">{{ local.nome_completo }}</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Status</label>
          <select v-model="filtros.status" @change="aplicarFiltros">
            <option value="">Todos</option>
            <option value="ativo">Ativo</option>
            <option value="alocado">Alocado</option>
            <option value="em_manutencao">Em Manutenção</option>
            <option value="baixado">Baixado</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Estado</label>
          <select v-model="filtros.estado" @change="aplicarFiltros">
            <option value="">Todos</option>
            <option value="novo">Novo</option>
            <option value="uso">Em Uso</option>
            <option value="obsoleto">Obsoleto</option>
            <option value="sucata">Sucata</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Estatísticas Rápidas -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-boxes"></i>
        </div>
        <div class="stat-content">
          <h3>{{ estatisticas.total_ativos }}</h3>
          <p>Total de Ativos</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">
          <i class="fas fa-dollar-sign"></i>
        </div>
        <div class="stat-content">
          <h3>{{ formatarMoeda(estatisticas.valor_total) }}</h3>
          <p>Valor Total</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon warning">
          <i class="fas fa-exclamation-triangle"></i>
        </div>
        <div class="stat-content">
          <h3>{{ estatisticas.sem_auditoria }}</h3>
          <p>Sem Auditoria (6m)</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon danger">
          <i class="fas fa-tools"></i>
        </div>
        <div class="stat-content">
          <h3>{{ estatisticas.em_manutencao }}</h3>
          <p>Em Manutenção</p>
        </div>
      </div>
    </div>

    <!-- Lista de Ativos -->
    <div class="table-section">
      <div class="table-header">
        <div class="table-info">
          <span class="results-count">
            {{ ativosFiltrados.length }} de {{ ativos.length }} ativos
          </span>
        </div>
        
        <div class="table-actions">
          <div class="bulk-actions" v-if="ativosSelecionados.length > 0">
            <span class="selected-count">{{ ativosSelecionados.length }} selecionados</span>
            <button class="btn btn-sm btn-outline" @click="movimentarSelecionados">
              <i class="fas fa-exchange-alt"></i>
              Movimentar
            </button>
            <button class="btn btn-sm btn-outline" @click="gerarEtiquetasSelecionados">
              <i class="fas fa-qrcode"></i>
              Etiquetas
            </button>
          </div>
          
          <div class="view-toggle">
            <button 
              class="btn-icon" 
              :class="{ active: modoVisualizacao === 'tabela' }"
              @click="modoVisualizacao = 'tabela'"
            >
              <i class="fas fa-list"></i>
            </button>
            <button 
              class="btn-icon" 
              :class="{ active: modoVisualizacao === 'cards' }"
              @click="modoVisualizacao = 'cards'"
            >
              <i class="fas fa-th"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Tabela -->
      <div v-if="modoVisualizacao === 'tabela'" class="table-container">
        <table class="table">
          <thead>
            <tr>
              <th>
                <input 
                  type="checkbox" 
                  v-model="selecionarTodos" 
                  @change="toggleSelecionarTodos"
                >
              </th>
              <th>Código</th>
              <th>Patrimônio</th>
              <th>Descrição</th>
              <th>Categoria</th>
              <th>Local</th>
              <th>Responsável</th>
              <th>Valor</th>
              <th>Status</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ativo in ativosPaginados" :key="ativo.id">
              <td>
                <input 
                  type="checkbox" 
                  :value="ativo.id" 
                  v-model="ativosSelecionados"
                >
              </td>
              <td>
                <div class="codigo-cell">
                  <span class="codigo">{{ ativo.codigo }}</span>
                  <button 
                    class="btn-icon btn-sm" 
                    @click="gerarEtiquetaQR(ativo)"
                    title="Gerar QR Code"
                  >
                    <i class="fas fa-qrcode"></i>
                  </button>
                </div>
              </td>
              <td>{{ ativo.patrimonio }}</td>
              <td>
                <div class="descricao-cell">
                  <strong>{{ ativo.descricao }}</strong>
                  <div class="detalhes">
                    {{ ativo.marca }} {{ ativo.modelo }}
                    <span v-if="ativo.numero_serie" class="serial">
                      S/N: {{ ativo.numero_serie }}
                    </span>
                  </div>
                </div>
              </td>
              <td>
                <span class="badge badge-outline">{{ ativo.categoria }}</span>
                <small v-if="ativo.subcategoria">{{ ativo.subcategoria }}</small>
              </td>
              <td>
                <div class="local-cell">
                  <span>{{ ativo.local?.nome_completo }}</span>
                  <small>{{ ativo.setor?.nome }}</small>
                </div>
              </td>
              <td>{{ ativo.responsavel?.nome }}</td>
              <td>
                <div class="valor-cell">
                  <span class="valor-atual">{{ formatarMoeda(ativo.valor_atual) }}</span>
                  <small v-if="ativo.valor_atual !== ativo.valor_aquisicao" class="valor-original">
                    Original: {{ formatarMoeda(ativo.valor_aquisicao) }}
                  </small>
                </div>
              </td>
              <td>
                <span class="badge" :class="getStatusClass(ativo.status)">
                  {{ getStatusLabel(ativo.status) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button class="btn-icon" @click="visualizarAtivo(ativo)" title="Visualizar">
                    <i class="fas fa-eye"></i>
                  </button>
                  <button class="btn-icon" @click="editarAtivo(ativo)" title="Editar">
                    <i class="fas fa-edit"></i>
                  </button>
                  <button class="btn-icon" @click="movimentarAtivo(ativo)" title="Movimentar">
                    <i class="fas fa-exchange-alt"></i>
                  </button>
                  <button class="btn-icon" @click="abrirManutencao(ativo)" title="Manutenção">
                    <i class="fas fa-tools"></i>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Cards -->
      <div v-else class="cards-container">
        <div v-for="ativo in ativosPaginados" :key="ativo.id" class="ativo-card">
          <div class="card-header">
            <input type="checkbox" :value="ativo.id" v-model="ativosSelecionados">
            <span class="badge" :class="getStatusClass(ativo.status)">
              {{ getStatusLabel(ativo.status) }}
            </span>
          </div>
          
          <div class="card-body">
            <div class="ativo-icon">
              <i :class="getCategoriaIcon(ativo.categoria)"></i>
            </div>
            
            <div class="ativo-info">
              <h3>{{ ativo.descricao }}</h3>
              <p class="codigo">{{ ativo.codigo }} - {{ ativo.patrimonio }}</p>
              <p class="marca">{{ ativo.marca }} {{ ativo.modelo }}</p>
              
              <div class="meta-info">
                <div class="meta-item">
                  <i class="fas fa-tag"></i>
                  <span>{{ ativo.categoria }}</span>
                </div>
                <div class="meta-item">
                  <i class="fas fa-map-marker-alt"></i>
                  <span>{{ ativo.local?.nome_completo }}</span>
                </div>
                <div class="meta-item">
                  <i class="fas fa-user"></i>
                  <span>{{ ativo.responsavel?.nome }}</span>
                </div>
                <div class="meta-item">
                  <i class="fas fa-dollar-sign"></i>
                  <span>{{ formatarMoeda(ativo.valor_atual) }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div class="card-actions">
            <button class="btn btn-sm btn-outline" @click="visualizarAtivo(ativo)">
              <i class="fas fa-eye"></i>
              Ver
            </button>
            <button class="btn btn-sm btn-outline" @click="editarAtivo(ativo)">
              <i class="fas fa-edit"></i>
              Editar
            </button>
            <button class="btn btn-sm btn-outline" @click="gerarEtiquetaQR(ativo)">
              <i class="fas fa-qrcode"></i>
              QR
            </button>
          </div>
        </div>
      </div>

      <!-- Paginação -->
      <div class="pagination-section">
        <div class="pagination-info">
          Mostrando {{ (paginaAtual - 1) * itensPorPagina + 1 }} a 
          {{ Math.min(paginaAtual * itensPorPagina, ativosFiltrados.length) }} 
          de {{ ativosFiltrados.length }} ativos
        </div>
        
        <div class="pagination-controls">
          <button 
            class="btn btn-outline btn-sm" 
            @click="paginaAtual--" 
            :disabled="paginaAtual === 1"
          >
            <i class="fas fa-chevron-left"></i>
            Anterior
          </button>
          
          <span class="page-numbers">
            <button 
              v-for="pagina in paginasVisiveis" 
              :key="pagina"
              class="btn btn-sm"
              :class="{ 'btn-primary': pagina === paginaAtual, 'btn-outline': pagina !== paginaAtual }"
              @click="paginaAtual = pagina"
            >
              {{ pagina }}
            </button>
          </span>
          
          <button 
            class="btn btn-outline btn-sm" 
            @click="paginaAtual++" 
            :disabled="paginaAtual === totalPaginas"
          >
            Próxima
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Modal de Cadastro -->
    <ModalCadastroAtivo 
      v-if="showCadastroModal"
      :ativo="ativoEdicao"
      @close="fecharModalCadastro"
      @save="salvarAtivo"
    />

    <!-- Modal de Visualização -->
    <ModalVisualizacaoAtivo 
      v-if="showVisualizacaoModal"
      :ativo="ativoVisualizacao"
      @close="showVisualizacaoModal = false"
      @edit="editarAtivo"
    />

    <!-- Modal de Movimentação -->
    <ModalMovimentacao 
      v-if="showMovimentacaoModal"
      :ativos="ativosParaMovimentar"
      @close="showMovimentacaoModal = false"
      @save="salvarMovimentacao"
    />

    <!-- Modal de Importação -->
    <ModalImportacao
      v-if="showImportModal"
      @close="showImportModal = false"
      @importacao-concluida="carregarAtivos"
    />

    <!-- Modal de QR Code -->
    <ModalQRCode
      v-if="showQRModal"
      :ativo="ativoSelecionado"
      @close="showQRModal = false"
    />

    <!-- Modal de QR Code -->
    <ModalQRCode 
      v-if="showQRModal"
      :ativo="ativoQR"
      @close="showQRModal = false"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from '@/composables/useToast'
import { useAtivosStore } from '@/stores/ativos'
import { useSetoresStore } from '@/stores/setores'
import { useLocaisStore } from '@/stores/locais'

// Componentes
import ModalCadastroAtivo from '@/components/inventario/ModalCadastroAtivo.vue'
import ModalVisualizacaoAtivo from '@/components/inventario/ModalVisualizacaoAtivo.vue'
import ModalMovimentacao from '@/components/inventario/ModalMovimentacao.vue'
import ModalImportacao from '@/components/inventario/ModalImportacao.vue'
import ModalQRCode from '@/components/inventario/ModalQRCode.vue'

// Stores
const ativosStore = useAtivosStore()
const setoresStore = useSetoresStore()
const locaisStore = useLocaisStore()

// Router e Toast
const router = useRouter()
const { showToast } = useToast()

// Estados reativas
const ativos = ref([])
const setores = ref([])
const locais = ref([])
const categorias = ref([])
const estatisticas = ref({})

// Filtros
const filtros = ref({
  texto: '',
  categoria: '',
  setor: '',
  local: '',
  status: '',
  estado: ''
})

// Paginação
const paginaAtual = ref(1)
const itensPorPagina = ref(20)

// Seleção
const ativosSelecionados = ref([])
const selecionarTodos = ref(false)

// Visualização
const modoVisualizacao = ref('tabela')

// Estados dos modais
const showCadastroModal = ref(false)
const showVisualizacaoModal = ref(false)
const showMovimentacaoModal = ref(false)
const showImportModal = ref(false)
const showQRModal = ref(false)

// Dados dos modais
const ativoEdicao = ref(null)
const ativoVisualizacao = ref(null)
const ativosParaMovimentar = ref([])
const ativoQR = ref(null)

// Computed
const ativosFiltrados = computed(() => {
  let resultado = ativos.value

  if (filtros.value.texto) {
    const texto = filtros.value.texto.toLowerCase()
    resultado = resultado.filter(ativo => 
      ativo.codigo.toLowerCase().includes(texto) ||
      ativo.patrimonio?.toLowerCase().includes(texto) ||
      ativo.descricao.toLowerCase().includes(texto) ||
      ativo.marca?.toLowerCase().includes(texto) ||
      ativo.modelo?.toLowerCase().includes(texto) ||
      ativo.numero_serie?.toLowerCase().includes(texto)
    )
  }

  if (filtros.value.categoria) {
    resultado = resultado.filter(ativo => ativo.categoria === filtros.value.categoria)
  }

  if (filtros.value.setor) {
    resultado = resultado.filter(ativo => ativo.setor_id === filtros.value.setor)
  }

  if (filtros.value.local) {
    resultado = resultado.filter(ativo => ativo.local_id === filtros.value.local)
  }

  if (filtros.value.status) {
    resultado = resultado.filter(ativo => ativo.status === filtros.value.status)
  }

  if (filtros.value.estado) {
    resultado = resultado.filter(ativo => ativo.estado === filtros.value.estado)
  }

  return resultado
})

const totalPaginas = computed(() => {
  return Math.ceil(ativosFiltrados.value.length / itensPorPagina.value)
})

const ativosPaginados = computed(() => {
  const inicio = (paginaAtual.value - 1) * itensPorPagina.value
  const fim = inicio + itensPorPagina.value
  return ativosFiltrados.value.slice(inicio, fim)
})

const paginasVisiveis = computed(() => {
  const total = totalPaginas.value
  const atual = paginaAtual.value
  const visivel = 5
  
  let inicio = Math.max(1, atual - Math.floor(visivel / 2))
  let fim = Math.min(total, inicio + visivel - 1)
  
  if (fim - inicio < visivel - 1) {
    inicio = Math.max(1, fim - visivel + 1)
  }
  
  const paginas = []
  for (let i = inicio; i <= fim; i++) {
    paginas.push(i)
  }
  
  return paginas
})

// Métodos
const carregarDados = async () => {
  try {
    await Promise.all([
      ativosStore.carregarAtivos(),
      setoresStore.carregarSetores(),
      locaisStore.carregarLocais(),
      ativosStore.carregarEstatisticas()
    ])
    
    ativos.value = ativosStore.ativos
    setores.value = setoresStore.setores
    locais.value = locaisStore.locais
    categorias.value = ativosStore.categorias
    estatisticas.value = ativosStore.estatisticas
  } catch (error) {
    showToast('Erro ao carregar dados', 'error')
  }
}

const aplicarFiltros = () => {
  paginaAtual.value = 1
}

const limparFiltros = () => {
  filtros.value = {
    texto: '',
    categoria: '',
    setor: '',
    local: '',
    status: '',
    estado: ''
  }
  aplicarFiltros()
}

const toggleSelecionarTodos = () => {
  if (selecionarTodos.value) {
    ativosSelecionados.value = ativosPaginados.value.map(a => a.id)
  } else {
    ativosSelecionados.value = []
  }
}

const visualizarAtivo = (ativo) => {
  ativoVisualizacao.value = ativo
  showVisualizacaoModal.value = true
}

const editarAtivo = (ativo) => {
  ativoEdicao.value = { ...ativo }
  showCadastroModal.value = true
}

const fecharModalCadastro = () => {
  showCadastroModal.value = false
  ativoEdicao.value = null
}

const salvarAtivo = async (dadosAtivo) => {
  try {
    if (dadosAtivo.id) {
      await ativosStore.atualizarAtivo(dadosAtivo.id, dadosAtivo)
      showToast('Ativo atualizado com sucesso', 'success')
    } else {
      await ativosStore.criarAtivo(dadosAtivo)
      showToast('Ativo criado com sucesso', 'success')
    }
    
    fecharModalCadastro()
    await carregarDados()
  } catch (error) {
    showToast('Erro ao salvar ativo', 'error')
  }
}

const movimentarAtivo = (ativo) => {
  ativosParaMovimentar.value = [ativo]
  showMovimentacaoModal.value = true
}

const movimentarSelecionados = () => {
  const ativos = ativosSelecionados.value.map(id => 
    ativos.value.find(a => a.id === id)
  )
  ativosParaMovimentar.value = ativos
  showMovimentacaoModal.value = true
}

const salvarMovimentacao = async (dadosMovimentacao) => {
  try {
    await ativosStore.criarMovimentacao(dadosMovimentacao)
    showToast('Movimentação criada com sucesso', 'success')
    showMovimentacaoModal.value = false
    ativosSelecionados.value = []
    await carregarDados()
  } catch (error) {
    showToast('Erro ao criar movimentação', 'error')
  }
}

const abrirModalQRCode = (ativo) => {
  ativoSelecionado.value = ativo
  showQRModal.value = true
}

const gerarEtiquetasSelecionados = () => {
  // Implementar geração em lote
  showToast('Funcionalidade em desenvolvimento', 'info')
}

const abrirManutencao = (ativo) => {
  router.push(`/manutencao/nova?ativo=${ativo.id}`)
}

const gerarEtiquetaQR = (ativo) => {
  ativoQR.value = ativo
  showQRModal.value = true
}

const exportarAtivos = async () => {
  try {
    await ativosStore.exportarAtivos(filtros.value)
    showToast('Exportação iniciada', 'success')
  } catch (error) {
    showToast('Erro ao exportar ativos', 'error')
  }
}

const importarAtivos = async (arquivo) => {
  try {
    await ativosStore.importarAtivos(arquivo)
    showToast('Importação realizada com sucesso', 'success')
    showImportModal.value = false
    await carregarDados()
  } catch (error) {
    showToast('Erro ao importar ativos', 'error')
  }
}

// Helpers
const formatarMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor || 0)
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

const getCategoriaIcon = (categoria) => {
  const icons = {
    'Informática': 'fas fa-laptop',
    'Móveis': 'fas fa-chair',
    'Equipamentos': 'fas fa-cogs',
    'Veículos': 'fas fa-car'
  }
  return icons[categoria] || 'fas fa-box'
}

// Watchers
watch(ativosSelecionados, (novos) => {
  selecionarTodos.value = novos.length === ativosPaginados.value.length && novos.length > 0
})

// Lifecycle
onMounted(() => {
  carregarDados()
})
</script>

<style scoped>
.ativos-page {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.header-content h1 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.filters-section {
  background: var(--surface-color);
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  border: 1px solid var(--border-color);
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.filter-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: var(--text-primary);
}

.search-input {
  position: relative;
}

.search-input i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
}

.search-input input {
  padding-left: 40px;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--surface-color);
  border-radius: 12px;
  padding: 24px;
  border: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color);
  color: white;
  font-size: 20px;
}

.stat-icon.warning {
  background: var(--warning-color);
}

.stat-icon.danger {
  background: var(--danger-color);
}

.stat-content h3 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.table-section {
  background: var(--surface-color);
  border-radius: 12px;
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.table-header {
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.bulk-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selected-count {
  color: var(--text-secondary);
  font-size: 14px;
}

.view-toggle {
  display: flex;
  gap: 4px;
}

.table-container {
  overflow-x: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.table th {
  background: var(--background-secondary);
  font-weight: 600;
  color: var(--text-primary);
}

.codigo-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.descricao-cell strong {
  display: block;
  margin-bottom: 4px;
}

.descricao-cell .detalhes {
  font-size: 14px;
  color: var(--text-secondary);
}

.descricao-cell .serial {
  display: block;
  font-size: 12px;
  color: var(--text-tertiary);
}

.local-cell span {
  display: block;
}

.local-cell small {
  color: var(--text-secondary);
}

.valor-cell .valor-atual {
  display: block;
  font-weight: 500;
}

.valor-cell .valor-original {
  font-size: 12px;
  color: var(--text-secondary);
}

.action-buttons {
  display: flex;
  gap: 4px;
}

.cards-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  padding: 24px;
}

.ativo-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.ativo-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border-color);
}

.card-body {
  padding: 20px;
  display: flex;
  gap: 16px;
}

.ativo-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.ativo-info h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
}

.ativo-info .codigo {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 4px;
}

.ativo-info .marca {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 16px;
}

.meta-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-secondary);
}

.meta-item i {
  width: 16px;
  color: var(--text-tertiary);
}

.card-actions {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  display: flex;
  gap: 8px;
}

.pagination-section {
  padding: 20px 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-numbers {
  display: flex;
  gap: 4px;
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

.badge-outline {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

/* Responsive */
@media (max-width: 768px) {
  .ativos-page {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: flex-end;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .table-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .cards-container {
    grid-template-columns: 1fr;
  }
  
  .pagination-section {
    flex-direction: column;
    gap: 16px;
  }
}
</style>