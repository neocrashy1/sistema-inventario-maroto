import React from 'react'

export default function MachineList({ machines = [] }) {
  return (
    <div className="table">
      <div className="row header">
        <div>Hostname</div>
        <div>Status</div>
        <div>CPU</div>
        <div>RAM</div>
        <div>Disco</div>
      </div>
      {machines.map(m => (
        <div className="row" key={m.id}>
          <div>{m.hostname}</div>
          <div>{m.status}</div>
          <div>{m.cpu_usage ?? '-'}</div>
          <div>{m.ram_usage ?? '-'}</div>
          <div>{m.disk_usage ?? '-'}</div>
        </div>
      ))}
    </div>
  )
}