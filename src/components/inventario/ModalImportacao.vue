<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h2>
          <i class="fas fa-file-import"></i>
          Importação de Ativos
        </h2>
        <button class="btn-close" @click="$emit('close')">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <!-- Etapas -->
        <div class="steps-container">
          <div class="step" :class="{ active: etapaAtual === 1, completed: etapaAtual > 1 }">
            <div class="step-number">1</div>
            <div class="step-label">Arquivo</div>
          </div>
          <div class="step-line" :class="{ completed: etapaAtual > 1 }"></div>
          <div class="step" :class="{ active: etapaAtual === 2, completed: etapaAtual > 2 }">
            <div class="step-number">2</div>
            <div class="step-label">Mapeamento</div>
          </div>
          <div class="step-line" :class="{ completed: etapaAtual > 2 }"></div>
          <div class="step" :class="{ active: etapaAtual === 3, completed: etapaAtual > 3 }">
            <div class="step-number">3</div>
            <div class="step-label">Validação</div>
          </div>
          <div class="step-line" :class="{ completed: etapaAtual > 3 }"></div>
          <div class="step" :class="{ active: etapaAtual === 4 }">
            <div class="step-number">4</div>
            <div class="step-label">Importação</div>
          </div>
        </div>

        <!-- Etapa 1: Upload do Arquivo -->
        <div v-if="etapaAtual === 1" class="etapa-content">
          <div class="etapa-header">
            <h3>Selecione o arquivo CSV</h3>
            <p>Faça o upload do arquivo CSV contendo os dados dos ativos para importação.</p>
          </div>

          <!-- Template de Exemplo -->
          <div class="template-section">
            <h4>
              <i class="fas fa-download"></i>
              Template de Importação
            </h4>
            <p>Baixe o template para garantir que seu arquivo esteja no formato correto:</p>
            <button class="btn btn-outline" @click="baixarTemplate">
              <i class="fas fa-download"></i>
              Baixar Template CSV
            </button>
          </div>

          <!-- Upload Area -->
          <div class="upload-section">
            <div 
              class="upload-area" 
              :class="{ 'drag-over': dragOver }"
              @drop="handleDrop" 
              @dragover.prevent="dragOver = true"
              @dragleave="dragOver = false"
              @dragenter.prevent
            >
              <input 
                type="file" 
                ref="fileInput"
                accept=".csv"
                @change="handleFileSelect"
                style="display: none"
              >
              
              <div v-if="!arquivo" class="upload-content" @click="$refs.fileInput.click()">
                <i class="fas fa-cloud-upload-alt"></i>
                <h4>Arraste o arquivo CSV aqui</h4>
                <p>ou clique para selecionar</p>
                <small>Apenas arquivos .csv são aceitos</small>
              </div>
              
              <div v-else class="arquivo-selecionado">
                <div class="arquivo-info">
                  <i class="fas fa-file-csv"></i>
                  <div class="arquivo-detalhes">
                    <h4>{{ arquivo.name }}</h4>
                    <p>{{ formatarTamanho(arquivo.size) }} • {{ totalLinhas }} linhas</p>
                  </div>
                </div>
                <button class="btn-remover" @click="removerArquivo">
                  <i class="fas fa-times"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Configurações de Importação -->
          <div v-if="arquivo" class="config-section">
            <h4>Configurações do Arquivo</h4>
            
            <div class="config-grid">
              <div class="form-group">
                <label for="separador">Separador</label>
                <select id="separador" v-model="configuracao.separador" @change="processarArquivo">
                  <option value=",">Vírgula (,)</option>
                  <option value=";">Ponto e vírgula (;)</option>
                  <option value="\t">Tab</option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="codificacao">Codificação</label>
                <select id="codificacao" v-model="configuracao.codificacao" @change="processarArquivo">
                  <option value="UTF-8">UTF-8</option>
                  <option value="ISO-8859-1">ISO-8859-1</option>
                  <option value="Windows-1252">Windows-1252</option>
                </select>
              </div>
              
              <div class="form-group">
                <label class="checkbox-label">
                  <input 
                    type="checkbox" 
                    v-model="configuracao.primeiraLinhaCabecalho"
                    @change="processarArquivo"
                  >
                  Primeira linha contém cabeçalhos
                </label>
              </div>
            </div>
          </div>

          <!-- Preview dos Dados -->
          <div v-if="dadosPreview.length > 0" class="preview-section">
            <h4>Preview dos Dados</h4>
            <div class="preview-table-container">
              <table class="preview-table">
                <thead>
                  <tr>
                    <th v-for="(coluna, index) in colunas" :key="index">
                      Coluna {{ index + 1 }}
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(linha, index) in dadosPreview.slice(0, 5)" :key="index">
                    <td v-for="(valor, colIndex) in linha" :key="colIndex">
                      {{ valor }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p class="preview-info">
              Mostrando as primeiras 5 linhas de {{ totalLinhas }} total
            </p>
          </div>
        </div>

        <!-- Etapa 2: Mapeamento de Colunas -->
        <div v-if="etapaAtual === 2" class="etapa-content">
          <div class="etapa-header">
            <h3>Mapeamento de Colunas</h3>
            <p>Associe as colunas do seu arquivo aos campos do sistema.</p>
          </div>

          <div class="mapeamento-container">
            <div class="mapeamento-grid">
              <div class="coluna-origem">
                <h4>Colunas do Arquivo</h4>
                <div class="colunas-list">
                  <div 
                    v-for="(coluna, index) in colunas" 
                    :key="index"
                    class="coluna-item"
                    :class="{ 'mapeada': mapeamento[index] }"
                  >
                    <div class="coluna-header">
                      <span class="coluna-numero">{{ index + 1 }}</span>
                      <span class="coluna-nome">{{ coluna || `Coluna ${index + 1}` }}</span>
                    </div>
                    <div class="coluna-preview">
                      {{ dadosPreview[0]?.[index] || '-' }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="mapeamento-arrows">
                <i class="fas fa-arrow-right"></i>
              </div>

              <div class="campos-destino">
                <h4>Campos do Sistema</h4>
                <div class="campos-list">
                  <div 
                    v-for="campo in camposDisponiveis" 
                    :key="campo.key"
                    class="campo-item"
                    :class="{ 'obrigatorio': campo.obrigatorio, 'mapeado': isCampoMapeado(campo.key) }"
                  >
                    <div class="campo-header">
                      <span class="campo-nome">{{ campo.label }}</span>
                      <span v-if="campo.obrigatorio" class="campo-obrigatorio">*</span>
                    </div>
                    <select 
                      v-model="mapeamento[campo.key]" 
                      @change="atualizarMapeamento"
                      class="campo-select"
                    >
                      <option value="">Não mapear</option>
                      <option 
                        v-for="(coluna, index) in colunas" 
                        :key="index" 
                        :value="index"
                        :disabled="isColunaUsada(index, campo.key)"
                      >
                        {{ coluna || `Coluna ${index + 1}` }}
                      </option>
                    </select>
                    <div class="campo-descricao">{{ campo.descricao }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Resumo do Mapeamento -->
            <div class="mapeamento-resumo">
              <h4>Resumo do Mapeamento</h4>
              <div class="resumo-stats">
                <div class="stat-item">
                  <span class="stat-number">{{ camposMapeados }}</span>
                  <span class="stat-label">Campos Mapeados</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ camposObrigatoriosMapeados }}</span>
                  <span class="stat-label">Obrigatórios</span>
                </div>
                <div class="stat-item">
                  <span class="stat-number">{{ colunasNaoMapeadas }}</span>
                  <span class="stat-label">Colunas Ignoradas</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Etapa 3: Validação -->
        <div v-if="etapaAtual === 3" class="etapa-content">
          <div class="etapa-header">
            <h3>Validação dos Dados</h3>
            <p>Verificando a integridade dos dados antes da importação.</p>
          </div>

          <div v-if="validando" class="validacao-loading">
            <div class="loading-spinner"></div>
            <p>Validando dados...</p>
          </div>

          <div v-else class="validacao-resultados">
            <!-- Resumo da Validação -->
            <div class="validacao-resumo">
              <div class="resumo-card" :class="{ 'success': errosValidacao.length === 0, 'error': errosValidacao.length > 0 }">
                <div class="resumo-icon">
                  <i :class="errosValidacao.length === 0 ? 'fas fa-check-circle' : 'fas fa-exclamation-triangle'"></i>
                </div>
                <div class="resumo-content">
                  <h4>{{ errosValidacao.length === 0 ? 'Validação Concluída' : 'Erros Encontrados' }}</h4>
                  <p v-if="errosValidacao.length === 0">
                    Todos os {{ linhasValidas }} registros estão prontos para importação.
                  </p>
                  <p v-else>
                    {{ errosValidacao.length }} erro(s) encontrado(s) em {{ linhasComErro }} linha(s).
                  </p>
                </div>
              </div>
            </div>

            <!-- Lista de Erros -->
            <div v-if="errosValidacao.length > 0" class="erros-section">
              <h4>
                <i class="fas fa-exclamation-triangle"></i>
                Erros de Validação
              </h4>
              
              <div class="erros-list">
                <div 
                  v-for="erro in errosValidacao.slice(0, 10)" 
                  :key="`${erro.linha}-${erro.campo}`"
                  class="erro-item"
                >
                  <div class="erro-header">
                    <span class="erro-linha">Linha {{ erro.linha }}</span>
                    <span class="erro-campo">{{ erro.campo }}</span>
                  </div>
                  <div class="erro-mensagem">{{ erro.mensagem }}</div>
                  <div class="erro-valor">Valor: "{{ erro.valor }}"</div>
                </div>
              </div>
              
              <div v-if="errosValidacao.length > 10" class="erros-mais">
                E mais {{ errosValidacao.length - 10 }} erro(s)...
              </div>
            </div>

            <!-- Estatísticas -->
            <div class="estatisticas-section">
              <h4>Estatísticas da Importação</h4>
              <div class="stats-grid">
                <div class="stat-card">
                  <div class="stat-icon success">
                    <i class="fas fa-check"></i>
                  </div>
                  <div class="stat-content">
                    <span class="stat-number">{{ linhasValidas }}</span>
                    <span class="stat-label">Registros Válidos</span>
                  </div>
                </div>
                
                <div class="stat-card">
                  <div class="stat-icon error">
                    <i class="fas fa-times"></i>
                  </div>
                  <div class="stat-content">
                    <span class="stat-number">{{ linhasComErro }}</span>
                    <span class="stat-label">Registros com Erro</span>
                  </div>
                </div>
                
                <div class="stat-card">
                  <div class="stat-icon info">
                    <i class="fas fa-info"></i>
                  </div>
                  <div class="stat-content">
                    <span class="stat-number">{{ totalLinhas }}</span>
                    <span class="stat-label">Total de Linhas</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Etapa 4: Importação -->
        <div v-if="etapaAtual === 4" class="etapa-content">
          <div class="etapa-header">
            <h3>Importação em Andamento</h3>
            <p>Importando os dados validados para o sistema.</p>
          </div>

          <div v-if="importando" class="importacao-progress">
            <div class="progress-container">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: `${progressoImportacao}%` }"></div>
              </div>
              <div class="progress-text">
                {{ registrosImportados }} de {{ totalRegistros }} registros importados ({{ progressoImportacao }}%)
              </div>
            </div>
            
            <div class="importacao-detalhes">
              <p>Importando: {{ registroAtual }}</p>
            </div>
          </div>

          <div v-else-if="importacaoConcluida" class="importacao-sucesso">
            <div class="sucesso-icon">
              <i class="fas fa-check-circle"></i>
            </div>
            <h4>Importação Concluída!</h4>
            <p>{{ registrosImportados }} ativos foram importados com sucesso.</p>
            
            <div class="resultado-stats">
              <div class="resultado-item">
                <span class="resultado-label">Novos ativos:</span>
                <span class="resultado-valor">{{ resultadoImportacao.novos }}</span>
              </div>
              <div class="resultado-item">
                <span class="resultado-label">Atualizados:</span>
                <span class="resultado-valor">{{ resultadoImportacao.atualizados }}</span>
              </div>
              <div class="resultado-item">
                <span class="resultado-label">Ignorados:</span>
                <span class="resultado-valor">{{ resultadoImportacao.ignorados }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button 
          type="button" 
          class="btn btn-outline" 
          @click="$emit('close')"
          :disabled="importando"
        >
          {{ importacaoConcluida ? 'Fechar' : 'Cancelar' }}
        </button>
        
        <button 
          v-if="etapaAtual > 1 && !importacaoConcluida" 
          type="button" 
          class="btn btn-outline" 
          @click="voltarEtapa"
          :disabled="importando"
        >
          <i class="fas fa-arrow-left"></i>
          Voltar
        </button>
        
        <button 
          v-if="etapaAtual < 4" 
          type="button" 
          class="btn btn-primary" 
          @click="proximaEtapa"
          :disabled="!podeAvancar"
        >
          {{ etapaAtual === 3 ? 'Iniciar Importação' : 'Próximo' }}
          <i class="fas fa-arrow-right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useToast } from '@/composables/useToast'

// Emits
const emit = defineEmits(['close', 'imported'])

// Estados
const etapaAtual = ref(1)
const arquivo = ref(null)
const dragOver = ref(false)
const dadosPreview = ref([])
const colunas = ref([])
const totalLinhas = ref(0)
const validando = ref(false)
const importando = ref(false)
const importacaoConcluida = ref(false)

// Configuração
const configuracao = ref({
  separador: ',',
  codificacao: 'UTF-8',
  primeiraLinhaCabecalho: true
})

// Mapeamento
const mapeamento = ref({})
const camposDisponiveis = ref([
  { key: 'codigo', label: 'Código', obrigatorio: true, descricao: 'Código único do ativo' },
  { key: 'patrimonio', label: 'Patrimônio', obrigatorio: false, descricao: 'Número do patrimônio' },
  { key: 'descricao', label: 'Descrição', obrigatorio: true, descricao: 'Descrição do ativo' },
  { key: 'categoria', label: 'Categoria', obrigatorio: true, descricao: 'Categoria do ativo' },
  { key: 'subcategoria', label: 'Subcategoria', obrigatorio: false, descricao: 'Subcategoria do ativo' },
  { key: 'marca', label: 'Marca', obrigatorio: false, descricao: 'Marca do ativo' },
  { key: 'modelo', label: 'Modelo', obrigatorio: false, descricao: 'Modelo do ativo' },
  { key: 'numero_serie', label: 'Número de Série', obrigatorio: false, descricao: 'Número de série único' },
  { key: 'valor_aquisicao', label: 'Valor de Aquisição', obrigatorio: false, descricao: 'Valor pago na aquisição' },
  { key: 'data_aquisicao', label: 'Data de Aquisição', obrigatorio: false, descricao: 'Data da compra (DD/MM/AAAA)' },
  { key: 'fornecedor', label: 'Fornecedor', obrigatorio: false, descricao: 'Nome do fornecedor' },
  { key: 'setor', label: 'Setor', obrigatorio: false, descricao: 'Setor responsável' },
  { key: 'local', label: 'Localização', obrigatorio: false, descricao: 'Local físico do ativo' },
  { key: 'responsavel', label: 'Responsável', obrigatorio: false, descricao: 'Pessoa responsável' },
  { key: 'estado', label: 'Estado', obrigatorio: false, descricao: 'Estado de conservação' },
  { key: 'observacoes', label: 'Observações', obrigatorio: false, descricao: 'Observações gerais' }
])

// Validação
const errosValidacao = ref([])
const linhasValidas = ref(0)
const linhasComErro = ref(0)

// Importação
const progressoImportacao = ref(0)
const registrosImportados = ref(0)
const totalRegistros = ref(0)
const registroAtual = ref('')
const resultadoImportacao = ref({
  novos: 0,
  atualizados: 0,
  ignorados: 0
})

// Computed
const podeAvancar = computed(() => {
  switch (etapaAtual.value) {
    case 1:
      return arquivo.value && dadosPreview.value.length > 0
    case 2:
      return camposObrigatoriosMapeados.value === camposObrigatorios.value.length
    case 3:
      return !validando.value && errosValidacao.value.length === 0
    default:
      return false
  }
})

const camposObrigatorios = computed(() => {
  return camposDisponiveis.value.filter(campo => campo.obrigatorio)
})

const camposMapeados = computed(() => {
  return Object.values(mapeamento.value).filter(valor => valor !== '').length
})

const camposObrigatoriosMapeados = computed(() => {
  return camposObrigatorios.value.filter(campo => 
    mapeamento.value[campo.key] !== undefined && mapeamento.value[campo.key] !== ''
  ).length
})

const colunasNaoMapeadas = computed(() => {
  const colunasMapeadas = Object.values(mapeamento.value).filter(valor => valor !== '')
  return colunas.value.length - colunasMapeadas.length
})

// Métodos
const baixarTemplate = () => {
  const headers = camposDisponiveis.value.map(campo => campo.label)
  const csvContent = headers.join(',') + '\n'
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'template_importacao_ativos.csv'
  link.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    processarArquivoSelecionado(file)
  }
}

const handleDrop = (event) => {
  event.preventDefault()
  dragOver.value = false
  
  const file = event.dataTransfer.files[0]
  if (file && file.type === 'text/csv') {
    processarArquivoSelecionado(file)
  }
}

const processarArquivoSelecionado = (file) => {
  arquivo.value = file
  processarArquivo()
}

const processarArquivo = () => {
  if (!arquivo.value) return
  
  const reader = new FileReader()
  reader.onload = (e) => {
    const texto = e.target.result
    const linhas = texto.split('\n').filter(linha => linha.trim())
    
    totalLinhas.value = linhas.length
    
    if (configuracao.value.primeiraLinhaCabecalho && linhas.length > 0) {
      colunas.value = linhas[0].split(configuracao.value.separador)
      dadosPreview.value = linhas.slice(1).map(linha => linha.split(configuracao.value.separador))
    } else {
      const primeiraLinha = linhas[0]?.split(configuracao.value.separador) || []
      colunas.value = primeiraLinha.map((_, index) => `Coluna ${index + 1}`)
      dadosPreview.value = linhas.map(linha => linha.split(configuracao.value.separador))
    }
  }
  
  reader.readAsText(arquivo.value, configuracao.value.codificacao)
}

const removerArquivo = () => {
  arquivo.value = null
  dadosPreview.value = []
  colunas.value = []
  totalLinhas.value = 0
  mapeamento.value = {}
}

const isCampoMapeado = (campoKey) => {
  return mapeamento.value[campoKey] !== undefined && mapeamento.value[campoKey] !== ''
}

const isColunaUsada = (colunaIndex, campoAtual) => {
  return Object.entries(mapeamento.value).some(([campo, coluna]) => 
    campo !== campoAtual && coluna === colunaIndex
  )
}

const atualizarMapeamento = () => {
  // Lógica para atualizar mapeamento se necessário
}

const proximaEtapa = async () => {
  if (etapaAtual.value === 2) {
    await validarDados()
  } else if (etapaAtual.value === 3) {
    await iniciarImportacao()
  }
  
  if (etapaAtual.value < 4) {
    etapaAtual.value++
  }
}

const voltarEtapa = () => {
  if (etapaAtual.value > 1) {
    etapaAtual.value--
  }
}

const validarDados = async () => {
  validando.value = true
  errosValidacao.value = []
  linhasValidas.value = 0
  linhasComErro.value = 0
  
  try {
    // Simular validação
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Validar cada linha
    dadosPreview.value.forEach((linha, index) => {
      const numeroLinha = index + (configuracao.value.primeiraLinhaCabecalho ? 2 : 1)
      
      // Validar campos obrigatórios
      camposObrigatorios.value.forEach(campo => {
        const colunaIndex = mapeamento.value[campo.key]
        if (colunaIndex !== undefined) {
          const valor = linha[colunaIndex]
          if (!valor || valor.trim() === '') {
            errosValidacao.value.push({
              linha: numeroLinha,
              campo: campo.label,
              mensagem: 'Campo obrigatório não preenchido',
              valor: valor || ''
            })
          }
        }
      })
      
      // Validar formato de data
      const dataIndex = mapeamento.value['data_aquisicao']
      if (dataIndex !== undefined && linha[dataIndex]) {
        const data = linha[dataIndex]
        if (!/^\d{2}\/\d{2}\/\d{4}$/.test(data)) {
          errosValidacao.value.push({
            linha: numeroLinha,
            campo: 'Data de Aquisição',
            mensagem: 'Formato inválido. Use DD/MM/AAAA',
            valor: data
          })
        }
      }
      
      // Validar valor numérico
      const valorIndex = mapeamento.value['valor_aquisicao']
      if (valorIndex !== undefined && linha[valorIndex]) {
        const valor = linha[valorIndex].replace(',', '.')
        if (isNaN(parseFloat(valor))) {
          errosValidacao.value.push({
            linha: numeroLinha,
            campo: 'Valor de Aquisição',
            mensagem: 'Valor numérico inválido',
            valor: linha[valorIndex]
          })
        }
      }
    })
    
    linhasComErro.value = new Set(errosValidacao.value.map(erro => erro.linha)).size
    linhasValidas.value = dadosPreview.value.length - linhasComErro.value
    
  } finally {
    validando.value = false
  }
}

const iniciarImportacao = async () => {
  importando.value = true
  progressoImportacao.value = 0
  registrosImportados.value = 0
  totalRegistros.value = linhasValidas.value
  
  try {
    // Simular importação
    for (let i = 0; i < dadosPreview.value.length; i++) {
      const linha = dadosPreview.value[i]
      const numeroLinha = i + (configuracao.value.primeiraLinhaCabecalho ? 2 : 1)
      
      // Verificar se a linha tem erros
      const temErros = errosValidacao.value.some(erro => erro.linha === numeroLinha)
      if (temErros) continue
      
      registroAtual.value = linha[mapeamento.value['descricao']] || `Registro ${i + 1}`
      
      // Simular processamento
      await new Promise(resolve => setTimeout(resolve, 100))
      
      registrosImportados.value++
      progressoImportacao.value = Math.round((registrosImportados.value / totalRegistros.value) * 100)
      
      // Simular resultado
      if (Math.random() > 0.8) {
        resultadoImportacao.value.atualizados++
      } else {
        resultadoImportacao.value.novos++
      }
    }
    
    importacaoConcluida.value = true
    emit('imported', resultadoImportacao.value)
    
  } finally {
    importando.value = false
  }
}

const formatarTamanho = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Lifecycle
onMounted(() => {
  // Inicialização se necessário
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

/* Steps */
.steps-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 32px;
  padding: 20px;
  background: var(--background-secondary);
  border-radius: 8px;
}

.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.step-number {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--border-color);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  transition: all 0.3s ease;
}

.step.active .step-number {
  background: var(--primary-color);
  color: white;
}

.step.completed .step-number {
  background: var(--success-color);
  color: white;
}

.step-label {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
}

.step.active .step-label {
  color: var(--primary-color);
}

.step-line {
  width: 60px;
  height: 2px;
  background: var(--border-color);
  margin: 0 20px;
  transition: all 0.3s ease;
}

.step-line.completed {
  background: var(--success-color);
}

/* Etapa Content */
.etapa-content {
  min-height: 400px;
}

.etapa-header {
  text-align: center;
  margin-bottom: 32px;
}

.etapa-header h3 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
  font-size: 24px;
}

.etapa-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 16px;
}

/* Template Section */
.template-section {
  background: var(--info-light);
  border: 1px solid var(--info-color);
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 24px;
}

.template-section h4 {
  margin: 0 0 8px 0;
  color: var(--info-color);
  display: flex;
  align-items: center;
  gap: 8px;
}

.template-section p {
  margin: 0 0 16px 0;
  color: var(--text-secondary);
}

/* Upload Section */
.upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 24px;
}

.upload-area:hover,
.upload-area.drag-over {
  border-color: var(--primary-color);
  background: var(--primary-light);
}

.upload-content i {
  font-size: 48px;
  color: var(--text-secondary);
  margin-bottom: 16px;
}

.upload-content h4 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.upload-content p {
  margin: 0 0 8px 0;
  color: var(--text-secondary);
}

.upload-content small {
  color: var(--text-secondary);
  font-size: 12px;
}

.arquivo-selecionado {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--success-light);
  border: 2px solid var(--success-color);
  border-radius: 12px;
}

.arquivo-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.arquivo-info i {
  font-size: 32px;
  color: var(--success-color);
}

.arquivo-detalhes h4 {
  margin: 0 0 4px 0;
  color: var(--text-primary);
}

.arquivo-detalhes p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.btn-remover {
  background: var(--danger-color);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-remover:hover {
  background: var(--danger-dark);
}

/* Config Section */
.config-section {
  margin-bottom: 24px;
}

.config-section h4 {
  margin: 0 0 16px 0;
  color: var(--text-primary);
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
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

.form-group select,
.form-group input {
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

/* Preview Section */
.preview-section {
  margin-bottom: 24px;
}

.preview-section h4 {
  margin: 0 0 16px 0;
  color: var(--text-primary);
}

.preview-table-container {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
}

.preview-table th,
.preview-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--border-color);
}

.preview-table th {
  background: var(--background-secondary);
  font-weight: 600;
  color: var(--text-primary);
}

.preview-table td {
  color: var(--text-secondary);
  font-size: 14px;
}

.preview-info {
  margin: 12px 0 0 0;
  color: var(--text-secondary);
  font-size: 14px;
  text-align: center;
}

/* Mapeamento */
.mapeamento-container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.mapeamento-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 24px;
  align-items: start;
}

.coluna-origem h4,
.campos-destino h4 {
  margin: 0 0 16px 0;
  color: var(--text-primary);
}

.colunas-list,
.campos-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.coluna-item,
.campo-item {
  padding: 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--surface-color);
}

.coluna-item.mapeada {
  border-color: var(--success-color);
  background: var(--success-light);
}

.campo-item.obrigatorio {
  border-left: 4px solid var(--warning-color);
}

.campo-item.mapeado {
  border-color: var(--success-color);
  background: var(--success-light);
}

.coluna-header,
.campo-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.coluna-numero {
  background: var(--primary-color);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.campo-obrigatorio {
  color: var(--warning-color);
  font-weight: 600;
}

.coluna-preview {
  font-size: 12px;
  color: var(--text-secondary);
  font-style: italic;
}

.campo-select {
  margin: 8px 0;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
}

.campo-descricao {
  font-size: 12px;
  color: var(--text-secondary);
}

.mapeamento-arrows {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--primary-color);
}

/* Resumo Mapeamento */
.mapeamento-resumo {
  background: var(--background-secondary);
  border-radius: 8px;
  padding: 20px;
  border: 1px solid var(--border-color);
}

.mapeamento-resumo h4 {
  margin: 0 0 16px 0;
  color: var(--text-primary);
}

.resumo-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 24px;
  font-weight: 600;
  color: var(--primary-color);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Validação */
.validacao-loading {
  text-align: center;
  padding: 40px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.validacao-resumo {
  margin-bottom: 24px;
}

.resumo-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.resumo-card.success {
  background: var(--success-light);
  border-color: var(--success-color);
}

.resumo-card.error {
  background: var(--danger-light);
  border-color: var(--danger-color);
}

.resumo-icon {
  font-size: 32px;
}

.resumo-card.success .resumo-icon {
  color: var(--success-color);
}

.resumo-card.error .resumo-icon {
  color: var(--danger-color);
}

.resumo-content h4 {
  margin: 0 0 4px 0;
  color: var(--text-primary);
}

.resumo-content p {
  margin: 0;
  color: var(--text-secondary);
}

/* Erros */
.erros-section {
  margin-bottom: 24px;
}

.erros-section h4 {
  margin: 0 0 16px 0;
  color: var(--danger-color);
  display: flex;
  align-items: center;
  gap: 8px;
}

.erros-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.erro-item {
  padding: 12px;
  background: var(--danger-light);
  border: 1px solid var(--danger-color);
  border-radius: 6px;
}

.erro-header {
  display: flex;
  gap: 12px;
  margin-bottom: 4px;
}

.erro-linha {
  background: var(--danger-color);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.erro-campo {
  background: var(--warning-color);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.erro-mensagem {
  color: var(--text-primary);
  font-weight: 500;
  margin-bottom: 4px;
}

.erro-valor {
  color: var(--text-secondary);
  font-size: 12px;
  font-family: monospace;
}

.erros-mais {
  text-align: center;
  padding: 12px;
  color: var(--text-secondary);
  font-style: italic;
}

/* Estatísticas */
.estatisticas-section h4 {
  margin: 0 0 16px 0;
  color: var(--text-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.stat-icon.success {
  background: var(--success-light);
  color: var(--success-color);
}

.stat-icon.error {
  background: var(--danger-light);
  color: var(--danger-color);
}

.stat-icon.info {
  background: var(--info-light);
  color: var(--info-color);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary);
}

/* Importação */
.importacao-progress {
  text-align: center;
  padding: 40px;
}

.progress-container {
  margin-bottom: 24px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.progress-fill {
  height: 100%;
  background: var(--primary-color);
  transition: width 0.3s ease;
}

.progress-text {
  color: var(--text-primary);
  font-weight: 500;
}

.importacao-detalhes p {
  color: var(--text-secondary);
  font-style: italic;
}

.importacao-sucesso {
  text-align: center;
  padding: 40px;
}

.sucesso-icon {
  font-size: 64px;
  color: var(--success-color);
  margin-bottom: 16px;
}

.importacao-sucesso h4 {
  margin: 0 0 8px 0;
  color: var(--text-primary);
}

.importacao-sucesso p {
  margin: 0 0 24px 0;
  color: var(--text-secondary);
}

.resultado-stats {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 300px;
  margin: 0 auto;
}

.resultado-item {
  display: flex;
  justify-content: space-between;
  padding: 8px 0;
  border-bottom: 1px solid var(--border-color);
}

.resultado-label {
  color: var(--text-secondary);
}

.resultado-valor {
  color: var(--text-primary);
  font-weight: 600;
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
  
  .steps-container {
    padding: 16px;
  }
  
  .step-line {
    width: 30px;
    margin: 0 10px;
  }
  
  .mapeamento-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .mapeamento-arrows {
    transform: rotate(90deg);
  }
  
  .config-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>