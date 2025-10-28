# Requisitos do Sistema de Inventário e Monitoramento

## 1. Visão Geral

Sistema de inventário de ativos e monitoramento de infraestrutura desenvolvido em FastAPI + PostgreSQL, com funcionalidades de:
- Inventário de hardware e software
- Monitoramento em tempo real
- Sistema de alertas
- Gestão de tickets
- Relatórios e dashboard

## 2. Requisitos Funcionais

### 2.1 Autenticação e Autorização
- ✅ **RF001**: Login com email/senha
- ✅ **RF002**: Tokens JWT (access + refresh)
- ✅ **RF003**: Controle de acesso baseado em roles (ADMIN, USER)
- ✅ **RF004**: Endpoint /auth/me para dados do usuário

### 2.2 Inventário de Ativos
- ⚠️ **RF005**: CRUD de ativos físicos (Status: 403 Forbidden)
- ✅ **RF006**: Campos obrigatórios: hostname, IP, tipo, localização
- ✅ **RF007**: Campos opcionais: marca, modelo, número série, especificações
- ✅ **RF008**: Histórico de alterações

### 2.3 Monitoramento
- ✅ **RF009**: Métricas de CPU, RAM, disco, rede
- ✅ **RF010**: Status de saúde dos serviços
- ✅ **RF011**: Endpoint /monitoring/health
- ✅ **RF012**: Endpoint /monitoring/metrics
- ✅ **RF013**: Detecção de processos em execução

### 2.4 Sistema de Alertas
- ✅ **RF014**: Regras configuráveis de alerta
- ✅ **RF015**: Thresholds personalizáveis
- ✅ **RF016**: Notificações por email/webhook
- ⚠️ **RF017**: Endpoint /alerts (Status: 404 Not Found no servidor principal)

### 2.5 Gestão de Tickets
- ✅ **RF018**: Criação automática de tickets por alertas
- ✅ **RF019**: CRUD manual de tickets
- ✅ **RF020**: Campos: título, descrição, prioridade, categoria, status
- ✅ **RF021**: Atribuição de responsáveis
- ✅ **RF022**: Controle de tempo (estimado vs real)

### 2.6 Dashboard e Relatórios
- ⚠️ **RF023**: Dashboard principal (Status: 404 Not Found)
- ✅ **RF024**: Métricas consolidadas
- ✅ **RF025**: Gráficos de performance
- ⚠️ **RF026**: Relatórios customizáveis (Status: 404 Not Found no servidor principal)

## 3. Requisitos Técnicos

### 3.1 Arquitetura
- ✅ **RT001**: FastAPI como framework web
- ✅ **RT002**: PostgreSQL como banco principal
- ⚠️ **RT003**: Redis para cache (Status: disconnected)
- ✅ **RT004**: SQLAlchemy ORM
- ✅ **RT005**: Alembic para migrações

### 3.2 Segurança
- ✅ **RT006**: Autenticação JWT
- ✅ **RT007**: Hash de senhas com bcrypt
- ✅ **RT008**: CORS configurado
- ✅ **RT009**: Rate limiting
- ✅ **RT010**: Validação de entrada com Pydantic

### 3.3 Performance
- ✅ **RT011**: Compressão GZip
- ✅ **RT012**: Conexões assíncronas
- ⚠️ **RT013**: Cache Redis (desconectado)
- ✅ **RT014**: Paginação em listagens

### 3.4 Monitoramento
- ✅ **RT015**: Health checks
- ✅ **RT016**: Métricas de sistema
- ✅ **RT017**: Logs estruturados
- ✅ **RT018**: Alertas automáticos

## 4. Métricas de Monitoramento

### 4.1 Métricas de Sistema
- **CPU**: Uso percentual, load average
- **Memória**: RAM total, usada, disponível, swap
- **Disco**: Espaço total, usado, disponível por partição
- **Rede**: Bytes enviados/recebidos, conexões ativas
- **Processos**: Lista de processos, uso de recursos

### 4.2 Métricas de Aplicação
- **Conexões**: Ativas, pool de conexões DB
- **Requests**: Total, por endpoint, tempo de resposta
- **Erros**: Taxa de erro, tipos de exceção
- **Uptime**: Tempo de atividade da aplicação

## 5. Regras de Alerta

### 5.1 Alertas Críticos
- **CPU > 90%** por 5 minutos consecutivos
- **RAM > 95%** por 3 minutos consecutivos
- **Disco > 90%** em qualquer partição
- **Aplicação down** (health check falha)

### 5.2 Alertas de Aviso
- **CPU > 80%** por 10 minutos
- **RAM > 85%** por 5 minutos
- **Disco > 80%** em qualquer partição
- **Taxa de erro > 5%** em 5 minutos

### 5.3 Alertas Informativos
- **Reinicialização** de serviços
- **Novos dispositivos** detectados
- **Atualizações** de software

## 6. Estrutura do Banco de Dados

### 6.1 Tabela: assets
```sql
- id (PK)
- hostname (UNIQUE)
- ip_address
- asset_type (server, workstation, network, etc.)
- location_code
- brand, model, serial_number
- specifications (JSON)
- status (active, inactive, maintenance)
- created_at, updated_at
```

### 6.2 Tabela: monitoring_data
```sql
- id (PK)
- asset_id (FK)
- metric_type (cpu, memory, disk, network)
- metric_value (JSON)
- timestamp
- created_at
```

### 6.3 Tabela: alerts
```sql
- id (PK)
- asset_id (FK)
- alert_type
- severity (critical, warning, info)
- message
- threshold_value
- current_value
- status (active, resolved, acknowledged)
- created_at, resolved_at
```

### 6.4 Tabela: tickets
```sql
- id (PK)
- ticket_number (UNIQUE)
- title, description
- status (open, in_progress, resolved, closed)
- priority (low, medium, high, critical)
- category (hardware, software, network)
- asset_id (FK), machine_hostname
- requester_name, requester_email
- assigned_to, assigned_to_name
- resolution
- estimated_hours, actual_hours
- created_at, updated_at, resolved_at
```

## 7. Status Atual dos Testes

### 7.1 Endpoints Funcionais ✅
- `/api/v1/auth/login` - Autenticação
- `/api/v1/auth/me` - Dados do usuário
- `/api/v1/monitoring/health` - Status do sistema
- `/api/v1/monitoring/metrics` - Métricas detalhadas
- `/api/v1/tickets` - Gestão de tickets
- `/health` - Health check básico

### 7.2 Endpoints com Problemas ⚠️
- `/api/v1/assets` - 403 Forbidden (problema de autorização)
- `/api/v1/dashboard` - 404 Not Found (rota não implementada)
- `/api/v1/alerts` - 404 Not Found (rota não implementada)
- `/api/v1/reports` - 404 Not Found (rota não implementada)

### 7.3 Serviços Externos
- **PostgreSQL**: ✅ Conectado e funcional
- **Redis**: ⚠️ Desconectado (impacta cache)

## 8. Próximos Passos

### 8.1 Correções Necessárias
1. **Investigar problema 403** no endpoint `/assets`
2. **Implementar rotas faltantes**: `/dashboard`, `/alerts`, `/reports`
3. **Configurar Redis** para cache
4. **Ajustar middlewares** que causam Internal Server Error

### 8.2 Melhorias Recomendadas
1. **Documentação OpenAPI** (/docs endpoint)
2. **Testes automatizados** mais abrangentes
3. **Monitoramento de logs** centralizados
4. **Backup automático** do banco de dados

### 8.3 Validações Pendentes
1. **Revisar thresholds** de alerta com equipe
2. **Validar campos obrigatórios** do inventário
3. **Definir SLAs** para resolução de tickets
4. **Aprovar estrutura** de relatórios

---

**Documento gerado em**: 2025-01-10  
**Versão**: 1.0  
**Status**: Pronto para validação com PM e Arquiteto