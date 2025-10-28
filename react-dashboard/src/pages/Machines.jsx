import { useEffect, useState } from 'react'
import { apiGet } from '../lib/api'
import MachineList from '../components/MachineList'

export default function Machines() {
  const [machines, setMachines] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    apiGet('/machines')
      .then(setMachines)
      .catch(err => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div>
      <h2>Máquinas</h2>
      {loading && <p>Carregando...</p>}
      {error && <p className="error">Erro: {error}</p>}
      <MachineList machines={machines} />
    </div>
  )
}