import React from 'react'

export default function AlertsTable({ alerts = [], selected, onToggle }) {
  const handleToggle = (id) => {
    if (typeof onToggle === 'function') onToggle(id)
  }

  return (
    <div className="table">
      <div className="row header">
        <div>ID</div>
        <div>Título</div>
        <div>Severidade</div>
        <div>Status</div>
        <div>Ações</div>
      </div>
      {alerts.map(a => (
        <div className="row" key={a.id}>
          <div>
            <input type="checkbox" checked={selected?.has?.(a.id)} onChange={() => handleToggle(a.id)} /> {a.id}
          </div>
          <div>{a.title}</div>
          <div>{a.severity}</div>
          <div>{a.status}</div>
          <div><button onClick={() => handleToggle(a.id)}>Selecionar</button></div>
        </div>
      ))}
    </div>
  )
}