
-- Otimizações de Performance - Sistema Levitiis
-- Execute este script no banco de dados para melhorar performance

-- Índices para tabela de alertas
CREATE INDEX IF NOT EXISTS idx_alerts_created_at ON alerts(created_at);
CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_type ON alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_alerts_machine_id ON alerts(machine_id);

-- Índices para tabela de máquinas
CREATE INDEX IF NOT EXISTS idx_machines_active ON machines(active);
CREATE INDEX IF NOT EXISTS idx_machines_status ON machines(status);
CREATE INDEX IF NOT EXISTS idx_machines_last_seen ON machines(last_seen);

-- Índices para tabela de tickets
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_created_at ON tickets(created_at);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned_to ON tickets(assigned_to);

-- Índices para tabela de usuários
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- Índices compostos para queries comuns
CREATE INDEX IF NOT EXISTS idx_alerts_severity_status ON alerts(severity, status);
CREATE INDEX IF NOT EXISTS idx_machines_active_status ON machines(active, status);
CREATE INDEX IF NOT EXISTS idx_tickets_status_priority ON tickets(status, priority);

-- Análise de performance (PostgreSQL)
-- ANALYZE alerts;
-- ANALYZE machines;
-- ANALYZE tickets;
-- ANALYZE users;

-- Limpeza de dados antigos (opcional)
-- DELETE FROM alerts WHERE created_at < NOW() - INTERVAL '90 days' AND status = 'resolved';
-- DELETE FROM tickets WHERE created_at < NOW() - INTERVAL '180 days' AND status = 'closed';
