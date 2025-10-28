import React from 'react'

export default function HealthIndicators({ machines = [] }) {
  const avg = (arr) => arr.length ? Math.round(arr.reduce((a, b) => a + b, 0) / arr.length) : null
  const cpuAvg = avg(machines.filter(m => typeof m.cpu_usage === 'number').map(m => m.cpu_usage))
  const ramAvg = avg(machines.filter(m => typeof m.ram_usage === 'number').map(m => m.ram_usage))
  const diskAvg = avg(machines.filter(m => typeof m.disk_usage === 'number').map(m => m.disk_usage))

  return (
    <div className="cards" style={{ marginTop: 16 }}>
      <div className="card">
        <h3>CPU Média</h3>
        <p>{cpuAvg != null ? `${cpuAvg}%` : '-'}</p>
      </div>
      <div className="card">
        <h3>RAM Média</h3>
        <p>{ramAvg != null ? `${ramAvg}%` : '-'}</p>
      </div>
      <div className="card">
        <h3>Disco Médio</h3>
        <p>{diskAvg != null ? `${diskAvg}%` : '-'}</p>
      </div>
    </div>
  )
}