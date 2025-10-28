<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <div class="header-info">
          <h2>
            <i :class="getCategoriaIcon(ativo.categoria)"></i>
            {{ ativo.descricao }}
          </h2>
          <div class="header-meta">
            <span class="badge" :class="getStatusClass(ativo.status)">
              {{ getStatusLabel(ativo.status) }}
            </span>
            <span class="codigo">{{ ativo.codigo }}</span>
          </div>
        </div>
        
        <div class="header-actions">
          <button class="btn btn-outline btn-sm" @click="$emit('edit', ativo)">
            <i class="fas fa-edit"></i>
            Editar
          </button>
          <button class="btn-close" @click="$emit('close')">
            <i class="fas fa-times"></i>
          </button>
        </div>
      </div>

      <div class="modal-body">
        <div class="content-grid">
          <!-- Informações Principais -->
          <div class="info-section">
            <div class="section-header">
              <h3>
                <i class="fas fa-info-circle"></i>
                Informações Básicas
              </h3>
            </div>
            
            <div class="info-grid">
              <div class="info-item">
                <label>Código do Ativo</label>
                <span>{{ ativo.codigo }}</span>
              </div>
              
              <div class="info-item" v-if="ativo.patrimonio">
                <label>Nº Patrimônio</label>
                <span>{{ ativo.patrimonio }}</span>
              </div>
              
              <div class="info-item">
                <label>Categoria</label>
                <span>{{ ativo.categoria }}</span>
              </div>
              
              <div class="info-item" v-if="ativo.subcategoria">
                <label>Subcategoria</label>
                <span>{{ ativo.subcategoria }}</span>
              </div>
              
              <div class="info-item">
                <label>Marca</label>
                <span>{{ ativo.marca || '-' }}</span>
              </div>
              
              <div class="info-item">
                <label>Modelo</label>
                <span>{{ ativo.modelo || '-' }}</span>
              </div>
              
              <div class="info-item" v-if="ativo.numero_serie">
                <label>Número de Série</label>
                <span class="serial">{{ ativo.numero_serie }}</span>
              </div>
              
              <div class="info-item">
                <label>Estado</label>
                <span class="badge badge-outline">{{ getEstadoLabel(ativo.estado) }}</span>
              </div>
            </div>
          </div>

          <!-- QR Code -->
          <div class="qr-section">
            <div class="section-header">
              <h3>
                <i class="fas fa-qrcode"></i>
                Identificação
              </h3>
            </div>
            
            <div class="qr-container">
              <canvas ref="qrCanvas"></canvas>
              <div class="qr-actions">
                <button class="btn btn-outline btn-sm" @click="imprimirEtiqueta">
                  <i class="fas fa-print"></i>
                  Imprimir
                </button>
                <button class="btn btn-outline btn-sm" @click="baixarQR">
                  <i class="fas fa-download"></i>
                  Baixar
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Informações Financeiras -->
        <div class="info-section">
          <div class="section-header">
            <h3>
              <i class="fas fa-dollar-sign"></i>
              Informações Financeiras
            </h3>
          </div>
          
          <div class="info-grid">
            <div class="info-item">
              <label>Valor de Aquisição</label>
              <span class="valor">{{ formatarMoeda(ativo.valor_aquisicao) }}</span>
            </div>
            
            <div class="info-item">
              <label>Valor Atual</label>
              <span class="valor">{{ formatarMoeda(ativo.valor_atual) }}</span>
            </div>
            
            <div class="info-item" v-if="ativo.data_compra">
              <label>Data da Compra</label>
              <span>{{ formatarData(ativo.data_compra) }}</span>
            </div>
            
            <div class="info-item" v-if="ativo.nota_fiscal">
              <label>Nota Fiscal</label>
              <span>{{ ativo.nota_fiscal }}</span>
            </div>
            
            <div class="info-item" v-if="ativo.vida_util_meses">
              <label>Vida Útil</label>
              <span>{{ ativo.vida_util_meses }} meses</span>
            </div>
            
            <div class="info-item" v-if="ativo.centro_custo">
              <label>Centro de Custo</label>
              <span>{{ ativo.centro_custo.codigo }} - {{ ativo.centro_custo.nome }}</span>
            </div>
            
            <div class="info-item" v-if="ativo.fornecedor">
              <label>Fornecedor</label>
              <span>{{ ativo.fornecedor.nome }}</span>
            </div>
            
            <div class="info-item" v-if="ativo.garantia_ate">
              <label>Garantia até</label>
              <span :class="{ 'garantia-vencida': isGarantiaVencida(ativo.garantia_ate) }">
                {{ formatarData(ativo.garantia_ate) }}
                <i v-if="isGarantiaVencida(ativo.garantia_ate)" class="fas fa-exclamation-triangle"></i>
              </span>
            </div>
          </div>
        </div>

        <!-- Localização e Responsabilidade -->
        <div class="info-section">
          <div class="section-header">
            <h3>
              <i class="fas fa-map-marker-alt"></i>
              Localização e Responsabilidade
            </h3>
          </div>
          
          <div class="info-grid">
            <div class="info-item">
              <label>Setor</label>
              <span>{{ ativo.setor?.nome || '-' }}</span>
            </div>
            
            <div class="info-item">
              <label>Localização Física</label>
              <span>{{ ativo.local?.nome_completo || '-' }}</span>
            </div>
            
            <div class="info-item">
              <label>Responsável</label>
              <span>{{ ativo.responsavel?.nome || '-' }}</span>
            </div>
            
            <div class="info-item">
              <label>Data de Entrada</label>
              <span>{{ formatarData(ativo.data_entrada) }}</span>
            </div>
          </div>
        </div>

        <!-- Observações e Tags -->
        <div class="info-section" v-if="ativo.observacoes || ativo.tags?.length">
          <div class="section-header">
            <h3>
              <i class="fas fa-sticky-note"></i>
              Informações Adicionais
            </h3>
          </div>
          
          <div v-if="ativo.observacoes" class="observacoes">
            <label>Observações</label>
            <p>{{ ativo.observacoes }}</p>
          </div>
          
          <div v-if="ativo.tags?.length" class="tags-container">
            <label>Tags</label>
            <div class="tags-list">
              <span v-for="tag in ativo.tags" :key="tag" class="tag">
                {{ tag }}
              </span>
            </div>
          </div>
        </div>

        <!-- Fotos -->
        <div class="info-section" v-if="ativo.fotos?.length">
          <div class="section-header">
            <h3>
              <i class="fas fa-images"></i>
              Fotos do Ativo
            </h3>
          </div>
          
          <div class="fotos-gallery">
            <div 
              v-for="(foto, index) in ativo.fotos" 
              :key="index"
              class="foto-item"
              @click="abrirFoto(foto, index)"
            >
              <img :src="foto.url" :alt="foto.nome">
            </div>
          </div>
        </div>

        <!-- Histórico de Movimentações -->
        <div class="info-section">
          <div class="section-header">
            <h3>
              <i class="fas fa-history"></i>
              Histórico de Movimentações
            </h3>
            <button class="btn btn-outline btn-sm" @click="carregarHistorico">
              <i class="fas fa-sync"></i>
              Atualizar
            </button>
          </div>
          
          <div v-if="carregandoHistorico" class="loading">
            <i class="fas fa-spinner fa-spin"></i>
            Carregando histórico...
          </div>
          
          <div v-else-if="historico.length === 0" class="empty-state">
            <i class="fas fa-inbox"></i>
            <p>Nenhuma movimentação registrada</p>
          </div>
          
          <div v-else class="historico-list">
            <div 
              v-for="item in historico" 
              :key="item.id"
              class="historico-item"
            >
              <div class="historico-icon">
                <i :class="getTipoMovimentacaoIcon(item.tipo)"></i>
              </div>
              <div class="historico-content">
                <div class="historico-header">
                  <span class="tipo">{{ getTipoMovimentacaoLabel(item.tipo) }}</span>
                  <span class="data">{{ formatarDataHora(item.data_movimentacao) }}</span>
                </div>
                <div class="historico-details">
                  <span v-if="item.local_origem">De: {{ item.local_origem.nome_completo }}</span>
                  <span v-if="item.local_destino">Para: {{ item.local_destino.nome_completo }}</span>
                  <span v-if="item.responsavel">Por: {{ item.responsavel.nome }}</span>
                </div>
                <div v-if="item.observacoes" class="historico-obs">
                  {{ item.observacoes }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Manutenções -->
        <div class="info-section">
          <div class="section-header">
            <h3>
              <i class="fas fa-tools"></i>
              Manutenções
            </h3>
            <button class="btn btn-primary btn-sm" @click="novaManutencao">
              <i class="fas fa-plus"></i>
              Nova Manutenção
            </button>
          </div>
          
          <div v-if="manutencoes.length === 0" class="empty-state">
            <i class="fas fa-tools"></i>
            <p>Nenhuma manutenção registrada</p>
          </div>
          
          <div v-else class="manutencoes-list">
            <div 
              v-for="manutencao in manutencoes" 
              :key="manutencao.id"
              class="manutencao-item"
            >
              <div class="manutencao-header">
                <span class="ticket">{{ manutencao.numero_ticket }}</span>
                <span class="badge" :class="getStatusManutencaoClass(manutencao.status)">
                  {{ manutencao.status }}
                </span>
              </div>
              <div class="manutencao-content">
                <h4>{{ manutencao.tipo }} - {{ manutencao.categoria }}</h4>
                <p>{{ manutencao.descricao_problema }}</p>
                <div class="manutencao-meta">
                  <span><i class="fas fa-calendar"></i> {{ formatarData(manutencao.data_abertura) }}</span>
                  <span v-if="manutencao.fornecedor">
                    <i class="fas fa-building"></i> {{ manutencao.fornecedor.nome }}
                  </span>
                  <span v-if="manutencao.custo_estimado">
                    <i class="fas fa-dollar-sign"></i> {{ formatarMoeda(manutencao.custo_estimado) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Modal de Foto -->
      <div v-if="fotoModal.show" class="foto-modal" @click="fecharFotoModal">
        <div class="foto-modal-content" @click.stop>
          <button class="btn-close-foto" @click="fecharFotoModal">
            <i class="fas fa-times"></i>
          </button>
          <img :src="fotoModal.foto?.url" :alt="fotoModal.foto?.nome">
          <div class="foto-navigation">
            <button 
              class="btn btn-outline" 
              @click="fotoAnterior"
              :disabled="fotoModal.index === 0"
            >
              <i class="fas fa-chevron-left"></i>
            </button>
            <span>{{ fotoModal.index + 1 }} de {{ ativo.fotos.length }}</span>
            <button 
              class="btn btn-outline" 
              @click="proximaFoto"
              :disabled="fotoModal.index === ativo.fotos.length - 1"
            >
              <i class="fas fa-chevron-right"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import logger from '@/utils/logger'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import QRCode from 'qrcode'

// Props
const props = defineProps({
  ativo: {
    type: Object,
    required: true
  }
})

// Emits
const emit = defineEmits(['close', 'edit'])

// Router
const router = useRouter()

// Estados
const carregandoHistorico = ref(false)
const historico = ref([])
const manutencoes = ref([])
const fotoModal = ref({
  show: false,
  foto: null,
  index: 0
})

// Métodos
const carregarHistorico = async () => {
  carregandoHistorico.value = true
  try {
    // Simular carregamento do histórico
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    historico.value = [
      {
        id: 1,
        tipo: 'entrada',
        data_movimentacao: '2024-01-15T10:30:00',
        local_destino: { nome_completo: 'Sede - 1º Andar - Sala 101' },
        responsavel: { nome: 'João Silva' },
        observacoes: 'Ativo recebido e catalogado'
      },
      {
        id: 2,
        tipo: 'transferencia',
        data_movimentacao: '2024-02-20T14:15:00',
        local_origem: { nome_completo: 'Sede - 1º Andar - Sala 101' },
        local_destino: { nome_completo: 'Sede - 2º Andar - Sala 201' },
        responsavel: { nome: 'Maria Santos' },
        observacoes: 'Transferência para novo setor'
      }
    ]
  } catch (error) {
    logger.error('Erro ao carregar histórico:', error)
  } finally {
    carregandoHistorico.value = false
  }
}

const carregarManutencoes = async () => {
  try {
    // Simular carregamento das manutenções
    manutencoes.value = [
      {
        id: 1,
        numero_ticket: 'MNT-2024-001',
        tipo: 'Preventiva',
        categoria: 'Limpeza',
        status: 'concluida',
        descricao_problema: 'Limpeza preventiva do equipamento',
        data_abertura: '2024-01-10',
        fornecedor: { nome: 'TechService Ltda' },
        custo_estimado: 150.00
      }
    ]
  } catch (error) {
    logger.error('Erro ao carregar manutenções:', error)
  }
}

const gerarQRCode = async () => {
  const canvas = document.querySelector('canvas')
  if (canvas) {
    const qrData = JSON.stringify({
      id: props.ativo.id,
      codigo: props.ativo.codigo,
      tipo: 'ativo'
    })
    
    await QRCode.toCanvas(canvas, qrData, {
      width: 150,
      margin: 2,
      color: {
        dark: '#000000',
        light: '#FFFFFF'
      }
    })
  }
}

const imprimirEtiqueta = () => {
  window.print()
}

const baixarQR = async () => {
  const canvas = document.querySelector('canvas')
  if (canvas) {
    const link = document.createElement('a')
    link.download = `qr-${props.ativo.codigo}.png`
    link.href = canvas.toDataURL()
    link.click()
  }
}

const abrirFoto = (foto, index) => {
  fotoModal.value = {
    show: true,
    foto,
    index
  }
}

const fecharFotoModal = () => {
  fotoModal.value.show = false
}

const fotoAnterior = () => {
  if (fotoModal.value.index > 0) {
    fotoModal.value.index--
    fotoModal.value.foto = props.ativo.fotos[fotoModal.value.index]
  }
}

const proximaFoto = () => {
  if (fotoModal.value.index < props.ativo.fotos.length - 1) {
    fotoModal.value.index++
    fotoModal.value.foto = props.ativo.fotos[fotoModal.value.index]
  }
}

const novaManutencao = () => {
  router.push(`/manutencao/nova?ativo=${props.ativo.id}`)
}

// Helpers
const formatarMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(valor || 0)
}

const formatarData = (data) => {
  if (!data) return '-'
  return new Date(data).toLocaleDateString('pt-BR')
}

const formatarDataHora = (data) => {
  if (!data) return '-'
  return new Date(data).toLocaleString('pt-BR')
}

const isGarantiaVencida = (data) => {
  if (!data) return false
  return new Date(data) < new Date()
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

const getEstadoLabel = (estado) => {
  const labels = {
    'novo': 'Novo',
    'uso': 'Em Uso',
    'obsoleto': 'Obsoleto',
    'sucata': 'Sucata'
  }
  return labels[estado] || estado
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

const getTipoMovimentacaoIcon = (tipo) => {
  const icons = {
    'entrada': 'fas fa-sign-in-alt',
    'saida': 'fas fa-sign-out-alt',
    'transferencia': 'fas fa-exchange-alt',
    'baixa': 'fas fa-trash'
  }
  return icons[tipo] || 'fas fa-arrow-right'
}

const getTipoMovimentacaoLabel = (tipo) => {
  const labels = {
    'entrada': 'Entrada',
    'saida': 'Saída',
    'transferencia': 'Transferência',
    'baixa': 'Baixa'
  }
  return labels[tipo] || tipo
}

const getStatusManutencaoClass = (status) => {
  const classes = {
    'aberta': 'badge-warning',
    'em_andamento': 'badge-info',
    'concluida': 'badge-success',
    'cancelada': 'badge-danger'
  }
  return classes[status] || 'badge-secondary'
}

// Lifecycle
onMounted(async () => {
  await Promise.all([
    gerarQRCode(),
    carregarHistorico(),
    carregarManutencoes()
  ])
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
  max-width: 1000px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-info h2 {
  margin: 0 0 8px 0;
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-primary);
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 12px;
}

.codigo {
  color: var(--text-secondary);
  font-family: monospace;
  font-size: 14px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
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

.content-grid {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 24px;
  margin-bottom: 32px;
}

.info-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.info-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item span {
  color: var(--text-primary);
  font-weight: 500;
}

.serial {
  font-family: monospace;
  background: var(--background-secondary);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.valor {
  font-weight: 600;
  color: var(--success-color);
}

.garantia-vencida {
  color: var(--danger-color) !important;
  display: flex;
  align-items: center;
  gap: 4px;
}

.qr-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.qr-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.qr-actions {
  display: flex;
  gap: 8px;
}

.observacoes {
  margin-bottom: 20px;
}

.observacoes label {
  display: block;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.observacoes p {
  margin: 0;
  color: var(--text-primary);
  line-height: 1.5;
}

.tags-container label {
  display: block;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: var(--primary-light);
  color: var(--primary-color);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.fotos-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
}

.foto-item {
  aspect-ratio: 1;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.foto-item:hover {
  transform: scale(1.05);
}

.foto-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: var(--text-secondary);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-secondary);
  text-align: center;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.historico-list,
.manutencoes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.historico-item,
.manutencao-item {
  background: var(--background-secondary);
  border-radius: 8px;
  padding: 16px;
  border: 1px solid var(--border-color);
}

.historico-item {
  display: flex;
  gap: 16px;
}

.historico-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-light);
  color: var(--primary-color);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.historico-content {
  flex: 1;
}

.historico-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.historico-header .tipo {
  font-weight: 600;
  color: var(--text-primary);
}

.historico-header .data {
  font-size: 14px;
  color: var(--text-secondary);
}

.historico-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
  color: var(--text-secondary);
}

.historico-obs {
  margin-top: 8px;
  font-style: italic;
  color: var(--text-secondary);
}

.manutencao-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.ticket {
  font-family: monospace;
  font-weight: 600;
  color: var(--text-primary);
}

.manutencao-content h4 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.manutencao-content p {
  margin: 0 0 12px 0;
  color: var(--text-secondary);
  line-height: 1.4;
}

.manutencao-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: var(--text-secondary);
}

.manutencao-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* Modal de Foto */
.foto-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1100;
}

.foto-modal-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.foto-modal-content img {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: 8px;
}

.btn-close-foto {
  position: absolute;
  top: -50px;
  right: 0;
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 24px;
  padding: 8px;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.2s ease;
}

.btn-close-foto:hover {
  background: rgba(255, 255, 255, 0.3);
}

.foto-navigation {
  display: flex;
  align-items: center;
  gap: 16px;
  color: white;
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
  .modal-container {
    margin: 0;
    height: 100vh;
    max-height: 100vh;
    border-radius: 0;
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .header-actions {
    flex-direction: column;
  }
  
  .historico-item {
    flex-direction: column;
    text-align: center;
  }
  
  .manutencao-meta {
    flex-direction: column;
    gap: 8px;
  }
}
</style>