# 🏗️ ARQUITETURA DO SISTEMA - LEVITIIS
## Definição de Arquitetura Cliente-Servidor

> **Status da Implementação:** ✅ Frontend Completo | 🔄 Backend em Desenvolvimento | 🧪 Integração API Implementada

---

## 📋 STACK TECNOLÓGICA ESCOLHIDA

### **Frontend (Cliente)**
- **Framework:** Vue.js 3.4.21 + Composition API
- **State Management:** Pinia 2.1.7
- **Roteamento:** Vue Router 4.3.0
- **Build Tool:** Vite 5.1.6
- **HTTP Client:** Axios
- **Visualizações:** Chart.js + Vue-ChartJS
- **Estilização:** SCSS/Sass
- **Utilitários:** @vueuse/core, date-fns

### **Backend (Servidor) - Recomendado**
- **Runtime:** Python 3.11+
- **Framework:** FastAPI ou Django REST Framework
- **Banco de Dados:** PostgreSQL 15+ (Produção) / SQL Server (Alternativa)
- **ORM:** SQLAlchemy (FastAPI) / Django ORM
- **Autenticação:** JWT + OAuth2
- **Cache:** Redis
- **Queue:** Celery + Redis
- **Monitoramento:** Prometheus + Grafana

---

## 🏛️ ARQUITETURA CLIENTE-SERVIDOR

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENTE (Frontend)                       │
├─────────────────────────────────────────────────────────────┤
│  Vue.js 3 + Pinia + Vue Router                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ Components  │ │   Stores    │ │   Router    │          │
│  │             │ │             │ │             │          │
│  │ - Dashboard │ │ - Auth      │ │ - Guards    │          │
│  │ - Assets    │ │ - Assets    │ │ - Routes    │          │
│  │ - Users     │ │ - Users     │ │ - Meta      │          │
│  │ - Reports   │ │ - Notif.    │ │             │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              HTTP Client (Axios)                    │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/TLS
                              │ REST API
                              │
┌─────────────────────────────────────────────────────────────┐
│                   SERVIDOR (Backend)                        │
├─────────────────────────────────────────────────────────────┤
│  Python Agent + API REST                                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │   API       │ │  Business   │ │   Data      │          │
│  │  Gateway    │ │   Logic     │ │   Layer     │          │
│  │             │ │             │ │             │          │
│  │ - Auth      │ │ - Services  │ │ - Models    │          │
│  │ - Routes    │ │ - Rules     │ │ - Repos     │          │
│  │ - Middleware│ │ - Validation│ │ - Queries   │          │
│  │ - CORS      │ │ - Processing│ │             │          │
│  └─────────────┘ └─────────────┘ └─────────────┘          │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Database Layer                          │   │
│  │  PostgreSQL / SQL Server                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ PLANEJAMENTO DO BANCO DE DADOS

### **Estrutura Principal**

```sql
-- Tabelas Core
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    permissions JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE machines (
    id SERIAL PRIMARY KEY,
    hostname VARCHAR(100) NOT NULL,
    ip_address INET,
    mac_address MACADDR,
    service_tag VARCHAR(50),
    model VARCHAR(100),
    manufacturer VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active',
    location_id INTEGER REFERENCES locations(id),
    registered_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP
);

CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES locations(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE assets (
    id SERIAL PRIMARY KEY,
    asset_tag VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    machine_id INTEGER REFERENCES machines(id),
    user_id INTEGER REFERENCES users(id),
    location_id INTEGER REFERENCES locations(id),
    status VARCHAR(20) DEFAULT 'available',
    purchase_date DATE,
    warranty_end DATE,
    value DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    priority VARCHAR(10) DEFAULT 'medium',
    status VARCHAR(20) DEFAULT 'open',
    asset_id INTEGER REFERENCES assets(id),
    assigned_to INTEGER REFERENCES users(id),
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(10) DEFAULT 'info',
    machine_id INTEGER REFERENCES machines(id),
    user_id INTEGER REFERENCES users(id),
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INTEGER,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### **Índices para Performance**

```sql
-- Índices essenciais
CREATE INDEX idx_machines_ip ON machines(ip_address);
CREATE INDEX idx_machines_status ON machines(status);
CREATE INDEX idx_assets_tag ON assets(asset_tag);
CREATE INDEX idx_assets_status ON assets(status);
CREATE INDEX idx_tickets_status ON tickets(status);
CREATE INDEX idx_alerts_created_at ON alerts(created_at);
CREATE INDEX idx_audit_logs_user_action ON audit_logs(user_id, action);
```

---

## 🔌 DEFINIÇÃO DE ENDPOINTS DA API

### **Autenticação e Usuários**
```
POST   /api/auth/login          # Login do usuário
POST   /api/auth/logout         # Logout do usuário
POST   /api/auth/refresh        # Refresh token
GET    /api/auth/me             # Dados do usuário atual

GET    /api/users               # Listar usuários
POST   /api/users               # Criar usuário
GET    /api/users/{id}          # Obter usuário
PUT    /api/users/{id}          # Atualizar usuário
DELETE /api/users/{id}          # Deletar usuário
```

### **Máquinas e Dispositivos**
```
POST   /api/machines/register   # Registrar nova máquina
GET    /api/machines            # Listar máquinas
GET    /api/machines/{id}       # Obter máquina específica
PUT    /api/machines/{id}       # Atualizar dados da máquina
DELETE /api/machines/{id}       # Remover máquina
POST   /api/machines/scan       # Iniciar scan de rede
GET    /api/machines/status     # Status geral das máquinas
```

### **Ativos**
```
GET    /api/assets              # Listar ativos
POST   /api/assets              # Criar ativo
GET    /api/assets/{id}         # Obter ativo
PUT    /api/assets/{id}         # Atualizar ativo
DELETE /api/assets/{id}         # Deletar ativo
POST   /api/assets/import       # Importar ativos em lote
GET    /api/assets/export       # Exportar ativos
```

### **Tickets e Ordens de Serviço**
```
GET    /api/tickets             # Listar tickets
POST   /api/tickets/create      # Criar novo ticket
GET    /api/tickets/{id}        # Obter ticket
PUT    /api/tickets/{id}        # Atualizar ticket
DELETE /api/tickets/{id}        # Deletar ticket
POST   /api/tickets/{id}/assign # Atribuir ticket
```

### **Alertas e Notificações**
```
GET    /api/alerts              # Listar alertas
POST   /api/alerts/send         # Enviar alerta
PUT    /api/alerts/{id}/ack     # Confirmar alerta
DELETE /api/alerts/{id}         # Deletar alerta
GET    /api/notifications       # Obter notificações do usuário
POST   /api/notifications/mark-read # Marcar como lida
```

### **Relatórios e Dashboard**
```
GET    /api/dashboard/stats     # Estatísticas do dashboard
GET    /api/reports/assets      # Relatório de ativos
GET    /api/reports/usage       # Relatório de uso
GET    /api/reports/maintenance # Relatório de manutenção
POST   /api/reports/generate    # Gerar relatório customizado
```

---

## 🔒 PADRÕES DE SEGURANÇA

### **Autenticação e Autorização**
```python
# JWT Token Structure
{
  "sub": "user_id",
  "username": "john.doe",
  "role": "admin",
  "permissions": ["read:assets", "write:users"],
  "exp": 1640995200,
  "iat": 1640908800
}

# Role-Based Access Control (RBAC)
ROLES = {
    "admin": ["*"],  # Acesso total
    "manager": ["read:*", "write:assets", "write:tickets"],
    "technician": ["read:assets", "write:tickets", "read:machines"],
    "user": ["read:own_assets", "create:tickets"]
}
```

### **Comunicação Segura**
- **TLS 1.3:** Criptografia em trânsito
- **CORS:** Configuração restritiva de origens
- **Rate Limiting:** 100 req/min por IP
- **Input Validation:** Sanitização de todas as entradas
- **SQL Injection Prevention:** Prepared statements
- **XSS Protection:** Content Security Policy

### **Middleware de Segurança**
```python
# Exemplo FastAPI
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    # Rate limiting
    # CORS validation
    # Authentication check
    # Audit logging
    response = await call_next(request)
    return response
```

---

## 📊 DIAGRAMA DE COMPONENTES

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │   Vue.js    │    │    Pinia    │    │ Vue Router  │     │
│  │ Components  │◄──►│   Stores    │◄──►│   Guards    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │          │
│         └───────────────────┼───────────────────┘          │
│                             │                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Axios HTTP Client                      │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/REST
                              │
┌─────────────────────────────────────────────────────────────┐
│                     API LAYER                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │    Auth     │    │   Routes    │    │ Middleware  │     │
│  │  Service    │◄──►│  Handler    │◄──►│  Security   │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                   │                   │          │
│         └───────────────────┼───────────────────┘          │
│                             │                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Business Logic Layer                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ ORM/SQL
                              │
┌─────────────────────────────────────────────────────────────┐
│                   DATABASE LAYER                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │ PostgreSQL  │    │    Redis    │    │   Backup    │     │
│  │  Primary    │◄──►│   Cache     │◄──►│  Storage    │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 IMPLEMENTAÇÃO RECOMENDADA

### **Fase 1: Backend Core (4 semanas)**
1. **Semana 1-2:** Setup do projeto Python + FastAPI
2. **Semana 3:** Implementação da autenticação JWT
3. **Semana 4:** Endpoints básicos (users, machines, assets)

### **Fase 2: Integração Frontend (2 semanas)**
1. **Semana 5:** Configuração do Axios e stores
2. **Semana 6:** Integração completa e testes

### **Fase 3: Funcionalidades Avançadas (4 semanas)**
1. **Semana 7-8:** Sistema de tickets e alertas
2. **Semana 9-10:** Relatórios e dashboard analytics

### **Fase 4: Produção (2 semanas)**
1. **Semana 11:** Deploy e configuração de produção
2. **Semana 12:** Monitoramento e otimizações

---

## 📈 MONITORAMENTO E MÉTRICAS

### **Métricas de Performance**
- Response time < 200ms (95th percentile)
- Uptime > 99.9%
- Database query time < 50ms
- Frontend bundle size < 2MB

### **Métricas de Segurança**
- Failed login attempts
- API rate limit violations
- Suspicious activity patterns
- Data access audit trails

### **Métricas de Negócio**
- Active users
- Asset utilization
- Ticket resolution time
- System adoption rate

---

## 📊 STATUS ATUAL DA IMPLEMENTAÇÃO

### **✅ Frontend Completo (100%)**
- **Framework:** Vue.js 3 + Composition API implementado
- **State Management:** Pinia stores configurados (auth, assets, dashboard, notifications)
- **Roteamento:** Vue Router com guards de autenticação
- **Componentes:** Dashboard, Assets, Users, Reports, Inventory
- **Integração API:** Axios configurado com interceptors e tratamento de erros
- **UI/UX:** Interface responsiva com componentes reutilizáveis
- **Notificações:** Sistema de notificações em tempo real
- **Testes:** Página de teste das funcionalidades implementada

### **🔄 Backend em Desenvolvimento (0%)**
- **Estrutura:** Aguardando implementação
- **Endpoints:** Definidos mas não implementados
- **Banco de Dados:** Schema planejado
- **Autenticação:** JWT strategy definida
- **Segurança:** Padrões TLS e rate limiting planejados

### **🧪 Integração API (90%)**
- **HTTP Client:** Axios configurado com base URL e interceptors
- **Error Handling:** Sistema robusto de tratamento de erros
- **Fallback:** Dados mock para desenvolvimento sem backend
- **Environment:** Configuração de variáveis de ambiente
- **Testing:** Ferramentas de teste da API implementadas

### **📋 Próximos Passos**
1. **Implementar Backend Python/FastAPI**
2. **Configurar PostgreSQL/SQL Server**
3. **Implementar autenticação JWT**
4. **Conectar frontend com backend real**
5. **Deploy e configuração de produção**

### **🔗 URLs de Teste**
- **Frontend:** http://localhost:5173
- **Página de Testes:** http://localhost:5173/test-functionalities
- **Backend:** http://localhost:8000 (quando implementado)

---

**Arquitetura definida por:** Sistema de Auditoria Arquitetural  
**Última atualização:** $(Get-Date -Format "dd/MM/yyyy HH:mm")
**Data:** Janeiro 2025  
**Versão:** 1.0