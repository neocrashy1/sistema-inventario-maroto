<template>
  <div class="discovery-report">
    <div class="report-header">
      <h3>
        <i class="fas fa-chart-line"></i>
        Relatório de Descoberta de Rede
      </h3>
      <div class="report-actions">
        <button class="btn btn-secondary btn-sm" @click="refreshData">
          <i class="fas fa-sync-alt"></i>
          Atualizar
        </button>
        <button class="btn btn-primary btn-sm" @click="exportReport">
          <i class="fas fa-download"></i>
          Exportar PDF
        </button>
      </div>
    </div>

    <!-- Summary Cards -->
    <div class="summary-section">
      <div class="summary-cards">
        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-search text-blue"></i>
          </div>
          <div class="card-content">
            <h4>{{ reportData.totalScans }}</h4>
            <p>Total de Scans</p>
            <span class="trend positive">+{{ reportData.scansThisMonth }} este mês</span>
          </div>
        </div>
        
        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-desktop text-green"></i>
          </div>
          <div class="card-content">
            <h4>{{ reportData.devicesDiscovered }}</h4>
            <p>Dispositivos Descobertos</p>
            <span class="trend positive">+{{ reportData.newDevicesThisWeek }} esta semana</span>
          </div>
        </div>
        
        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-plus-circle text-orange"></i>
          </div>
          <div class="card-content">
            <h4>{{ reportData.autoRegistered }}</h4>
            <p>Cadastros Automáticos</p>
            <span class="trend">{{ reportData.registrationRate }}% taxa de sucesso</span>
          </div>
        </div>
        
        <div class="summary-card">
          <div class="card-icon">
            <i class="fas fa-exclamation-triangle text-red"></i>
          </div>
          <div class="card-content">
            <h4>{{ reportData.errors }}</h4>
            <p>Erros de Descoberta</p>
            <span class="trend negative">{{ reportData.errorRate }}% taxa de erro</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <div class="chart-row">
        <!-- Discovery Timeline -->
        <div class="chart-container">
          <div class="chart-header">
            <h4>Descobertas por Período</h4>
          </div>
          <div class="chart-content">
            <canvas ref="discoveryTimelineChart" width="400" height="200"></canvas>
          </div>
        </div>

        <!-- Vendor Distribution -->
        <div class="chart-container">
          <div class="chart-header">
            <h4>Distribuição por Fabricante</h4>
          </div>
          <div class="chart-content">
            <div class="vendor-chart">
              <div 
                v-for="vendor in reportData.vendorDistribution" 
                :key="vendor.name"
                class="vendor-item"
              >
                <div class="vendor-info">
                  <i :class="getVendorIcon(vendor.name)"></i>
                  <span class="vendor-name">{{ vendor.name }}</span>
                </div>
                <div class="vendor-stats">
                  <div class="vendor-bar">
                    <div 
                      class="vendor-fill"
                      :style="{ width: vendor.percentage + '%', backgroundColor: vendor.color }"
                    ></div>
                  </div>
                  <span class="vendor-count">{{ vendor.count }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-row">
        <!-- Tipos de Dispositivo removido -->
 
         <!-- Network Status -->
        <div class="chart-container">
          <div class="chart-header">
            <h4>Status da Rede</h4>
          </div>
          <div class="chart-content">
            <div class="network-status">
              <div class="status-item">
                <div class="status-indicator online"></div>
                <div class="status-info">
                  <span class="status-label">Online</span>
                  <span class="status-count">{{ reportData.networkStatus.online }}</span>
                </div>
              </div>
              <div class="status-item">
                <div class="status-indicator offline"></div>
                <div class="status-info">
                  <span class="status-label">Offline</span>
                  <span class="status-count">{{ reportData.networkStatus.offline }}</span>
                </div>
              </div>
              <div class="status-item">
                <div class="status-indicator unknown"></div>
                <div class="status-info">
                  <span class="status-label">Desconhecido</span>
                  <span class="status-count">{{ reportData.networkStatus.unknown }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Discoveries Table -->
    <div class="recent-discoveries">
      <div class="table-header">
        <h4>
          <i class="fas fa-clock"></i>
          Descobertas Recentes
        </h4>
        <div class="table-filters">
          <select v-model="filterPeriod" class="filter-select">
            <option value="today">Hoje</option>
            <option value="week">Esta Semana</option>
            <option value="month">Este Mês</option>
          </select>
        </div>
      </div>
      <div class="table-container">
        <table class="discoveries-table">
          <thead>
            <tr>
              <th>Data/Hora</th>
              <th>IP</th>
              <th>Hostname</th>
              <th>Fabricante</th>
              <th>Tipo</th>
              <th>Status</th>
              <th>Ação</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="discovery in filteredDiscoveries" :key="discovery.id">
              <td class="datetime-cell">
                {{ formatDateTime(discovery.discoveryDate) }}
              </td>
              <td class="ip-cell">{{ discovery.ip }}</td>
              <td class="hostname-cell">{{ discovery.hostname || 'N/A' }}</td>
              <td class="vendor-cell">
                <div class="vendor-info">
                  <i :class="getVendorIcon(discovery.vendor)"></i>
                  {{ discovery.vendor }}
                </div>
              </td>
              <td class="type-cell">{{ discovery.deviceType }}</td>
              <td class="status-cell">
                <span 
                  class="status-badge"
                  :class="getActionStatusClass(discovery.action)"
                >
                  {{ getActionStatusText(discovery.action) }}
                </span>
              </td>
              <td class="action-cell">
                <button 
                  class="btn btn-sm btn-primary"
                  @click="viewDiscoveryDetails(discovery)"
                  title="Ver Detalhes"
                >
                  <i class="fas fa-eye"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DiscoveryReport',
  data() {
    return {
      filterPeriod: 'week',
      reportData: {
        totalScans: 45,
        scansThisMonth: 12,
        devicesDiscovered: 234,
        newDevicesThisWeek: 18,
        autoRegistered: 198,
        registrationRate: 85,
        errors: 8,
        errorRate: 3.4,
        vendorDistribution: [
          { name: 'Dell Inc.', count: 89, percentage: 38, color: '#3b82f6' },
          { name: 'Hewlett Packard', count: 67, percentage: 29, color: '#10b981' },
          { name: 'VMware', count: 34, percentage: 15, color: '#8b5cf6' },
          { name: 'Microsoft Corporation', count: 23, percentage: 10, color: '#f59e0b' },
          { name: 'Apple Inc.', count: 12, percentage: 5, color: '#6b7280' },
          { name: 'Outros', count: 9, percentage: 3, color: '#ef4444' }
        ],
        deviceTypes: [
          { name: 'Desktop', count: 98, percentage: 42 },
          { name: 'Laptop', count: 76, percentage: 32 },
          { name: 'Server', count: 34, percentage: 15 },
          { name: 'Printer', count: 18, percentage: 8 },
          { name: 'Switch', count: 5, percentage: 2 },
          { name: 'Router', count: 3, percentage: 1 }
        ],
        networkStatus: {
          online: 198,
          offline: 28,
          unknown: 8
        }
      },
      recentDiscoveries: [
        {
          id: 1,
          discoveryDate: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
          ip: '192.168.1.156',
          hostname: 'DELL-DESKTOP-8901',
          vendor: 'Dell Inc.',
          deviceType: 'Desktop',
          action: 'registered'
        },
        {
          id: 2,
          discoveryDate: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
          ip: '192.168.1.157',
          hostname: 'HP-PRINTER-M404',
          vendor: 'Hewlett Packard',
          deviceType: 'Printer',
          action: 'existing'
        },
        {
          id: 3,
          discoveryDate: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
          ip: '192.168.1.158',
          hostname: 'DELL-LAPTOP-5520',
          vendor: 'Dell Inc.',
          deviceType: 'Laptop',
          action: 'registered'
        },
        {
          id: 4,
          discoveryDate: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
          ip: '192.168.1.159',
          hostname: 'VMWARE-SERVER-01',
          vendor: 'VMware',
          deviceType: 'Server',
          action: 'error'
        },
        {
          id: 5,
          discoveryDate: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
          ip: '192.168.1.160',
          hostname: 'HP-ELITEDESK-800',
          vendor: 'Hewlett Packard',
          deviceType: 'Desktop',
          action: 'registered'
        }
      ]
    }
  },
  computed: {
    filteredDiscoveries() {
      const now = new Date()
      const filterDate = new Date()
      
      switch (this.filterPeriod) {
        case 'today':
          filterDate.setHours(0, 0, 0, 0)
          break
        case 'week':
          filterDate.setDate(now.getDate() - 7)
          break
        case 'month':
          filterDate.setMonth(now.getMonth() - 1)
          break
      }
      
      return this.recentDiscoveries.filter(discovery => 
        new Date(discovery.discoveryDate) >= filterDate
      )
    }
  },
  mounted() {
    this.initializeCharts()
  },
  methods: {
    refreshData() {
      // Simula atualização dos dados
      this.$toast.info('Atualizando dados do relatório...')
      setTimeout(() => {
        this.$toast.success('Dados atualizados com sucesso!')
      }, 1000)
    },

    exportReport() {
      // Simula exportação para PDF
      this.$toast.info('Gerando relatório PDF...')
      setTimeout(() => {
        this.$toast.success('Relatório exportado com sucesso!')
      }, 2000)
    },

    initializeCharts() {
      // Inicializa gráfico de timeline de descobertas
      this.createDiscoveryTimelineChart()
    },

    createDiscoveryTimelineChart() {
      const canvas = this.$refs.discoveryTimelineChart
      if (!canvas) return

      const ctx = canvas.getContext('2d')
      const width = canvas.width
      const height = canvas.height

      // Limpa o canvas
      ctx.clearRect(0, 0, width, height)

      // Dados simulados para os últimos 7 dias
      const data = [12, 19, 8, 15, 23, 18, 25]
      const labels = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
      
      const maxValue = Math.max(...data)
      const padding = 40
      const chartWidth = width - 2 * padding
      const chartHeight = height - 2 * padding

      // Desenha eixos
      ctx.strokeStyle = '#e5e7eb'
      ctx.lineWidth = 1
      
      // Eixo Y
      ctx.beginPath()
      ctx.moveTo(padding, padding)
      ctx.lineTo(padding, height - padding)
      ctx.stroke()
      
      // Eixo X
      ctx.beginPath()
      ctx.moveTo(padding, height - padding)
      ctx.lineTo(width - padding, height - padding)
      ctx.stroke()

      // Desenha linha do gráfico
      ctx.strokeStyle = '#3b82f6'
      ctx.lineWidth = 2
      ctx.beginPath()

      data.forEach((value, index) => {
        const x = padding + (index * chartWidth) / (data.length - 1)
        const y = height - padding - (value / maxValue) * chartHeight
        
        if (index === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })
      
      ctx.stroke()

      // Desenha pontos
      ctx.fillStyle = '#3b82f6'
      data.forEach((value, index) => {
        const x = padding + (index * chartWidth) / (data.length - 1)
        const y = height - padding - (value / maxValue) * chartHeight
        
        ctx.beginPath()
        ctx.arc(x, y, 4, 0, 2 * Math.PI)
        ctx.fill()
      })

      // Desenha labels
      ctx.fillStyle = '#6b7280'
      ctx.font = '12px Arial'
      ctx.textAlign = 'center'
      
      labels.forEach((label, index) => {
        const x = padding + (index * chartWidth) / (data.length - 1)
        ctx.fillText(label, x, height - padding + 20)
      })
    },

    getVendorIcon(vendor) {
      if (vendor.includes('Dell')) return 'fas fa-desktop text-blue'
      if (vendor.includes('HP') || vendor.includes('Hewlett')) return 'fas fa-print text-orange'
      if (vendor.includes('Apple')) return 'fab fa-apple text-gray'
      if (vendor.includes('Microsoft')) return 'fab fa-microsoft text-blue'
      if (vendor.includes('VMware')) return 'fas fa-cloud text-purple'
      return 'fas fa-microchip text-gray'
    },

    getDeviceTypeIcon(type) {
      switch (type) {
        case 'Desktop': return 'fas fa-desktop text-blue'
        case 'Laptop': return 'fas fa-laptop text-green'
        case 'Server': return 'fas fa-server text-purple'
        case 'Printer': return 'fas fa-print text-orange'
        case 'Switch': return 'fas fa-network-wired text-gray'
        case 'Router': return 'fas fa-wifi text-blue'
        default: return 'fas fa-microchip text-gray'
      }
    },

    getActionStatusClass(action) {
      switch (action) {
        case 'registered': return 'status-success'
        case 'existing': return 'status-info'
        case 'error': return 'status-error'
        default: return 'status-unknown'
      }
    },

    getActionStatusText(action) {
      switch (action) {
        case 'registered': return 'Cadastrado'
        case 'existing': return 'Já Existia'
        case 'error': return 'Erro'
        default: return 'Desconhecido'
      }
    },

    formatDateTime(dateString) {
      return new Date(dateString).toLocaleString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    },

    viewDiscoveryDetails(discovery) {
      this.$emit('view-details', discovery)
    }
  }
}
</script>

<style scoped>
.discovery-report {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.report-header {
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-header h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 8px;
}

.report-actions {
  display: flex;
  gap: 8px;
}

/* Summary Section */
.summary-section {
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.summary-card {
  background: #f9fafb;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.card-icon {
  font-size: 24px;
}

.card-content h4 {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 700;
  color: #1a1a1a;
}

.card-content p {
  margin: 0 0 4px 0;
  color: #666;
  font-size: 14px;
}

.trend {
  font-size: 12px;
  font-weight: 500;
}

.trend.positive {
  color: #10b981;
}

.trend.negative {
  color: #ef4444;
}

/* Charts Section */
.charts-section {
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.chart-row:last-child {
  margin-bottom: 0;
}

.chart-container {
  background: #f9fafb;
  border-radius: 8px;
  padding: 20px;
}

.chart-header {
  margin-bottom: 16px;
}

.chart-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

.chart-content {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Vendor Chart */
.vendor-chart {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.vendor-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.vendor-info {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 120px;
  font-size: 14px;
  font-weight: 500;
}

.vendor-stats {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
}

.vendor-bar {
  flex: 1;
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.vendor-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.vendor-count {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  min-width: 30px;
  text-align: right;
}

/* Device Types Grid */
.device-types-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  width: 100%;
}

.device-type-card {
  text-align: center;
  padding: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.device-type-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.device-type-info h5 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
}

.device-type-info p {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #666;
}

.percentage {
  font-size: 12px;
  color: #3b82f6;
  font-weight: 500;
}

/* Network Status */
.network-status {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-indicator.online {
  background: #10b981;
}

.status-indicator.offline {
  background: #ef4444;
}

.status-indicator.unknown {
  background: #6b7280;
}

.status-info {
  flex: 1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-label {
  font-size: 14px;
  color: #374151;
}

.status-count {
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
}

/* Recent Discoveries */
.recent-discoveries {
  padding: 24px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-header h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
  display: flex;
  align-items: center;
  gap: 8px;
}

.table-filters {
  display: flex;
  gap: 8px;
}

.filter-select {
  padding: 6px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.table-container {
  overflow-x: auto;
}

.discoveries-table {
  width: 100%;
  border-collapse: collapse;
}

.discoveries-table th,
.discoveries-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.discoveries-table th {
  background: #f9fafb;
  font-weight: 600;
  color: #374151;
  font-size: 14px;
}

.discoveries-table td {
  font-size: 14px;
  color: #1a1a1a;
}

.vendor-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.status-success {
  background: #dcfce7;
  color: #166534;
}

.status-info {
  background: #dbeafe;
  color: #1e40af;
}

.status-error {
  background: #fee2e2;
  color: #dc2626;
}

.status-unknown {
  background: #f3f4f6;
  color: #6b7280;
}

/* Utility Classes */
.text-blue { color: #3b82f6; }
.text-green { color: #10b981; }
.text-orange { color: #f59e0b; }
.text-red { color: #ef4444; }
.text-purple { color: #8b5cf6; }
.text-gray { color: #6b7280; }

/* Buttons */
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

/* Responsive */
@media (max-width: 768px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
  
  .summary-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .device-types-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .report-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .table-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style>