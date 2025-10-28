import { useEffect, useState } from 'react'
import { apiGet, apiPost } from '../lib/api'
import AlertsTable from '../components/AlertsTable'

export default function Alerts() {
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [selected, setSelected] = useState(new Set())

  useEffect(() => {
    apiGet('/alerts')
      .then(setAlerts)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  const toggleSelect = (id) => {
    const next = new Set(selected)
    if (next.has(id)) next.delete(id); else next.add(id)
    setSelected(next)
  }

  const bulkAck = async () => {
    try {
      const ids = Array.from(selected)
      await apiPost('/alerts/bulk-acknowledge', ids)
      setAlerts(prev => prev.map(a => ids.includes(a.id) ? { ...a, status: 'acknowledged' } : a))
      setSelected(new Set())
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div>
      <h2>Alertas</h2>
      {loading && <p>Carregando...</p>}
      {error && <p className="error">Erro: {error}</p>}
      <AlertsTable alerts={alerts} selected={selected} onToggle={toggleSelect} />
      <div style={{ marginTop: 12 }}>
        <button disabled={selected.size === 0} onClick={bulkAck}>Reconhecer Selecionados</button>
      </div>
    </div>
  )
}