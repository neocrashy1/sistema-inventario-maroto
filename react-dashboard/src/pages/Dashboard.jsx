import { useEffect, useState } from 'react'
import { apiGet } from '../lib/api'
import HealthIndicators from '../components/HealthIndicators'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [machines, setMachines] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    // Buscar dados de alertas e máquinas em paralelo
    Promise.all([
      apiGet('/alerts/dashboard/summary'),
      apiGet('/machines')
    ])
      .then(([summaryRes, machinesRes]) => {
        setSummary(summaryRes)
        setMachines(machinesRes || [])
      })
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const computeMetrics = (list) => {
    const avg = (arr) => arr.length ? Math.round(arr.reduce((a, b) => a + b, 0) / arr.length) : null
    const cpuAvg = avg(list.filter(m => typeof m.cpu_usage === 'number').map(m => m.cpu_usage))
    const ramAvg = avg(list.filter(m => typeof m.ram_usage === 'number').map(m => m.ram_usage))
    const diskAvg = avg(list.filter(m => typeof m.disk_usage === 'number').map(m => m.disk_usage))

    const onlineCount = list.filter(m => m.status === 'online').length
    const criticalCount = list.filter(m => m.status === 'critical').length
    const offlineCount = list.filter(m => m.status === 'offline').length

    return { cpuAvg, ramAvg, diskAvg, onlineCount, criticalCount, offlineCount, total: list.length }
  }

  const metrics = computeMetrics(machines)

  return (
    <div>
      <h2>Dashboard</h2>
      {loading && <p>Carregando...</p>}
      {error && <p className="error">Erro: {error}</p>}
      {summary && (
        <div className="cards">
          <div className="card">
            <h3>Alertas Abertos</h3>
            <p>{summary.open_count ?? 0}</p>
          </div>
          <div className="card">
            <h3>Críticos</h3>
            <p>{summary.critical_count ?? 0}</p>
          </div>
          <div className="card">
            <h3>Última atualização</h3>
            <p>{summary.last_updated ?? '-'}</p>
          </div>
        </div>
      )}

      {/* Indicadores de saúde (CPU, RAM, Disco) via componente */}
      {machines.length > 0 && (
        <HealthIndicators machines={machines} />
      )}

      {/* Status de máquinas */}
      {machines.length > 0 && (
        <div className="cards" style={{ marginTop: 16 }}>
          <div className="card">
            <h3>Online</h3>
            <p>{metrics.onlineCount}</p>
          </div>
          <div className="card">
            <h3>Críticas</h3>
            <p>{metrics.criticalCount}</p>
          </div>
          <div className="card">
            <h3>Offline</h3>
            <p>{metrics.offlineCount}</p>
          </div>
        </div>
      )}
    </div>
  )
}