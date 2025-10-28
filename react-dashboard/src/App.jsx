import { Routes, Route, NavLink } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import Machines from './pages/Machines'
import Tickets from './pages/Tickets'
import Alerts from './pages/Alerts'
import { getToken } from './lib/api'

function Protected({ children }) {
  const t = getToken()
  if (!t) return <div className="card"><p>Você precisa estar autenticado. Autenticação será fornecida pelo projeto "Sistema de Análise Computadores".</p></div>
  return children
}

export default function App() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <h1 className="logo">LeviTIIS</h1>
        <nav>
          <NavLink to="/" end>Dashboard</NavLink>
          <NavLink to="/machines">Máquinas</NavLink>
          <NavLink to="/tickets">Tickets</NavLink>
          <NavLink to="/alerts">Alertas</NavLink>
          {/* Link placeholder para projeto futuro */}
          <a href="#" className="right" onClick={(e) => e.preventDefault()}>Sistema de Análise Computadores</a>
        </nav>
      </aside>
      <main className="content">
        <Routes>
          {/* Rota de login removida e separada para projeto futuro */}
          {/* <Route path="/login" element={<Login />} /> */}
          <Route path="/" element={<Protected><Dashboard /></Protected>} />
          <Route path="/machines" element={<Protected><Machines /></Protected>} />
          <Route path="/tickets" element={<Protected><Tickets /></Protected>} />
          <Route path="/alerts" element={<Protected><Alerts /></Protected>} />
        </Routes>
      </main>
    </div>
  )
}