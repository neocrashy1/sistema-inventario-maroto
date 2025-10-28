import React from 'react'

export default function TicketsTable({ tickets = [] }) {
  return (
    <div className="table">
      <div className="row header">
        <div>#</div>
        <div>Título</div>
        <div>Status</div>
        <div>Prioridade</div>
        <div>Responsável</div>
      </div>
      {tickets.map(t => (
        <div className="row" key={t.id}>
          <div>{t.ticket_number}</div>
          <div>{t.title}</div>
          <div>{t.status}</div>
          <div>{t.priority}</div>
          <div>{t.assigned_to_name ?? '-'}</div>
        </div>
      ))}
    </div>
  )
}