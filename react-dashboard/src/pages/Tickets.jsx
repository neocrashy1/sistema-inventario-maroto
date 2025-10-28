import { useEffect, useState } from 'react'
import { apiGet } from '../lib/api'
import TicketsTable from '../components/TicketsTable'

export default function Tickets() {
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    apiGet('/tickets')
      .then(setTickets)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <h2>Tickets</h2>
      {loading && <p>Carregando...</p>}
      {error && <p className="error">Erro: {error}</p>}
      <TicketsTable tickets={tickets} />
    </div>
  )
}