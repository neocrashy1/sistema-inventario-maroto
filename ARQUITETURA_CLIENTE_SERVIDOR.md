# Arquitetura Cliente-Servidor Levitiis (foco em Inventário)

Este documento consolida a stack tecnológica, a arquitetura cliente-servidor, o plano de banco de dados/APIs/comunicação segura e os endpoints iniciais com foco total em inventário, movimentações, empréstimos, localizações, manutenções, auditorias, compras & orçamentos e dashboards em tempo real.

## Stack Tecnológica
- Backend: FastAPI (Python) com SQLAlchemy/Alembic
- Banco de Dados: PostgreSQL (preferencial). Opcional: SQL Server (via ODBC/sqlalchemy)
- Agente: Python (scripts/serviços para hosts quando necessário)
- API: REST (FastAPI)
- Frontend: React (com estado global e roteamento)
- Client HTTP: Axios com interceptores e baseURL centralizada
- Autenticação: JWT (access + refresh), RBAC por papéis/permissões
- Deploy: Docker + docker-compose

## Arquitetura (alta nível)
Agente Python → API REST (FastAPI) → Banco (PostgreSQL/SQL Server) → Dashboard React.

Componentes principais:
- Inventário: gestão de ativos, localizações, categorias e anexos
- Movimentações/Empréstimos: registro, aprovação e termos de responsabilidade
- Auditorias: sessões, listas de contagem e reconciliação
- Manutenção: ordens de serviço, agendamentos e contratos/SLA
- Compras & Orçamentos: pedidos, fornecedores e cotações
- Dashboard: KPIs e eventos em tempo (near) real via WebSocket
- Agente (opcional): integração de máquinas quando aplicável

## Diagrama de Componentes
Arquivo: architecture/component-diagram.svg

## Endpoints da API (base)
- POST /machines/register — registrar máquina (se aplicável ao escopo)
- POST /machines/status — enviar status/heartbeat
- POST /tickets/create — abrir ticket
- POST /alerts/send — enviar alerta

Autenticação:
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
- GET  /auth/me

## Foco de Módulos de Inventário (v1)
- /ativos: CRUD de ativos, categorias, anexos, etiquetas QR
- /localizacoes: hierarquia (unidade → prédio → andar → sala), georreferência opcional
- /movimentacoes: transferências, empréstimos internos/terceiros, aprovação, trilha de auditoria
- /auditorias: sessão, lista de contagem, coletas, reconciliação e relatórios
- /manutencao: ordens de serviço, agendamentos, contratos/SLA, avaliações
- /compras: pedidos de compra, fornecedores, itens vinculados a ativos
- /orcamentos: cotações/orçamentos, comparação e seleção
- /dashboard: métricas, distribuição por categorias/localização/status, eventos

## Banco de Dados (planejamento)
Tabelas essenciais (chaves e relacionamentos em alto nível):
- users(id, username, email, password_hash, role) — RBAC
- roles(id, name), permissions(id, name), role_permissions(role_id, permission_id), user_roles(user_id, role_id)
- assets(id, name, category_id, tag, patrimonio, serial_number, purchase_value, supplier_id, location_id, status, lifecycle_state, created_at)
- asset_categories(id, name, parent_id)
- asset_attachments(id, asset_id, filename, url, uploaded_by, created_at)
- locations(id, name, parent_id, type, code)
- movements(id, asset_id, from_location_id, to_location_id, requester_id, approver_id, type, status, created_at)
- loans(id, asset_id, borrower_type, borrower_id, start_date, due_date, status, terms_doc_url)
- audits(id, name, scope, status, created_by, started_at, closed_at)
- audit_items(id, audit_id, asset_id, expected_location_id, found_location_id, status)
- maintenance_orders(id, asset_id, title, description, priority, status, scheduled_for, closed_at, supplier_id)
- maintenance_schedules(id, asset_id, period, next_run, last_run)
- maintenance_contracts(id, supplier_id, start_date, end_date, sla_json)
- suppliers(id, name, tax_id, contact, email, phone)
- purchase_orders(id, supplier_id, status, created_by, approved_by, total_value, created_at)
- purchase_order_items(id, purchase_order_id, asset_category_id, description, quantity, unit_value)
- budgets(id, supplier_id, status, total_value, created_by, created_at)
- alerts(id, type, severity, message, ticket_id, asset_id, created_at)
- tickets(id, title, description, status, assignee_id, related_asset_id, created_at)
- audit_logs(id, entity, entity_id, action, actor_id, data_json, created_at)

## Padrões de Segurança
- TLS: HTTPS obrigatório em produção (reverse proxy Nginx com certificados)
- Autenticação: Bearer token (JWT) — acesso ao dashboard e às APIs
- Refresh: fluxo robusto via /auth/refresh, tokens curtos (ex.: 15 min), refresh rotacionado
- Agente Python: token dedicado por agente (ex.: header X-Agent-Token) com escopo restrito aos endpoints /machines/*
- Proteções: CORS apenas para domínios confiáveis; rate limit em /auth/login; validação de payloads; TrustedHost
- Segredos: nunca versionar; usar variáveis de ambiente (.env) e gerenciadores de segredo

## Configuração de baseURL e Token (frontend)
- Variável: VITE_API_BASE_URL (ex.: http://localhost:8000)
- Axios: instância única com interceptores para Authorization Bearer
- Interceptor 401: tenta /auth/refresh e repete a requisição. Em falha, efetua logout

## Comunicação em Tempo Real
- WebSocket/Server-Sent Events para KPIs do dashboard e eventos de inventário

## Observações
- O foco do produto está nos módulos de inventário; itens de monitoramento/rede podem ser ocultados do menu inicialmente
- O backend já utiliza prefixo global /api/v1 e roteadores por domínio