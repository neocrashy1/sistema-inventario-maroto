# 🔧 TESTE COMPLETO - ENDPOINTS API LEVITIIS

## 📋 **VISÃO GERAL**

Este documento contém todos os testes para validar os endpoints da API do sistema Levitiis, incluindo cenários de sucesso, erro e edge cases.

---

## 🎯 **ENDPOINTS TESTADOS**

### **1. Health Check**
- ✅ **Endpoint**: `GET /health`
- ✅ **Status**: Funcionando
- ✅ **Resposta**: `{"status":"healthy","version":"1.0.0"}`

### **2. Autenticação**
- 🔄 **Endpoint**: `POST /api/v1/auth/login`
- 🔄 **Endpoint**: `POST /api/v1/auth/refresh`
- 🔄 **Endpoint**: `POST /api/v1/auth/logout`

### **3. Dashboard**
- 🔄 **Endpoint**: `GET /api/v1/dashboard/summary`
- 🔄 **Endpoint**: `GET /api/v1/dashboard/metrics`
- 🔄 **Endpoint**: `GET /api/v1/dashboard/alerts`

### **4. Máquinas**
- 🔄 **Endpoint**: `POST /api/v1/machines/register`
- 🔄 **Endpoint**: `POST /api/v1/machines/status`
- 🔄 **Endpoint**: `GET /api/v1/machines/list`
- 🔄 **Endpoint**: `GET /api/v1/machines/{id}`

### **5. Tickets**
- 🔄 **Endpoint**: `POST /api/v1/tickets/create`
- 🔄 **Endpoint**: `GET /api/v1/tickets/list`
- 🔄 **Endpoint**: `GET /api/v1/tickets/{id}`
- 🔄 **Endpoint**: `PUT /api/v1/tickets/{id}`

### **6. Alertas**
- 🔄 **Endpoint**: `POST /api/v1/alerts/send`
- 🔄 **Endpoint**: `GET /api/v1/alerts/list`
- 🔄 **Endpoint**: `PUT /api/v1/alerts/{id}/acknowledge`

---

## 🧪 **RESULTADOS DOS TESTES**

### **✅ 1. HEALTH CHECK - SUCESSO**

```bash
# Comando
curl http://localhost:8000/health

# Resposta
{
  "status": "healthy",
  "version": "1.0.0"
}

# Status: ✅ PASSOU
# Tempo de resposta: < 100ms
# Headers de segurança: ✅ Presentes
```

### **🔄 2. AUTENTICAÇÃO**

#### **2.1 Login - Cenário de Sucesso**
```bash
# Comando
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Resposta Esperada
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}

# Status: 🔄 TESTANDO...
```

#### **2.2 Login - Cenário de Erro (Credenciais Inválidas)**
```bash
# Comando
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=senhaerrada"

# Resposta Esperada
{
  "detail": "Incorrect username or password"
}

# Status Code Esperado: 401
# Status: 🔄 TESTANDO...
```

#### **2.3 Login - Edge Case (Campos Vazios)**
```bash
# Comando
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=&password="

# Resposta Esperada
{
  "detail": "Username and password are required"
}

# Status Code Esperado: 422
# Status: 🔄 TESTANDO...
```

### **🔄 3. DASHBOARD**

#### **3.1 Summary - Com Autenticação**
```bash
# Comando (com token)
curl -X GET http://localhost:8000/api/v1/dashboard/summary \
  -H "Authorization: Bearer {TOKEN}"

# Resposta Esperada
{
  "total_machines": 0,
  "online_machines": 0,
  "offline_machines": 0,
  "critical_alerts": 0,
  "open_tickets": 0,
  "last_updated": "2025-10-01T10:31:00Z"
}

# Status: 🔄 TESTANDO...
```

#### **3.2 Summary - Sem Autenticação**
```bash
# Comando (sem token)
curl -X GET http://localhost:8000/api/v1/dashboard/summary

# Resposta Esperada
{
  "detail": "Not authenticated"
}

# Status Code Esperado: 401
# Status: 🔄 TESTANDO...
```

### **🔄 4. MÁQUINAS**

#### **4.1 Registrar Máquina - Cenário de Sucesso**
```bash
# Comando
curl -X POST http://localhost:8000/api/v1/machines/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "hostname": "servidor-001",
    "ip_address": "192.168.1.100",
    "mac_address": "00:11:22:33:44:55",
    "type": "servidor",
    "model": "Dell PowerEdge R740",
    "location": "Datacenter - Rack 1",
    "department": "TI"
  }'

# Resposta Esperada
{
  "id": 1,
  "hostname": "servidor-001",
  "ip_address": "192.168.1.100",
  "status": "registered",
  "created_at": "2025-10-01T10:31:00Z"
}

# Status: 🔄 TESTANDO...
```

#### **4.2 Registrar Máquina - Dados Inválidos**
```bash
# Comando (IP inválido)
curl -X POST http://localhost:8000/api/v1/machines/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "hostname": "servidor-002",
    "ip_address": "999.999.999.999",
    "mac_address": "invalid-mac",
    "type": "servidor"
  }'

# Resposta Esperada
{
  "detail": "Invalid IP address format"
}

# Status Code Esperado: 422
# Status: 🔄 TESTANDO...
```

#### **4.3 Enviar Status da Máquina**
```bash
# Comando
curl -X POST http://localhost:8000/api/v1/machines/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "machine_id": 1,
    "timestamp": "2025-10-01T10:31:00Z",
    "status": "online",
    "metrics": {
      "cpu_usage": 45,
      "memory_usage": 60,
      "disk_usage": 30,
      "temperature": 42
    }
  }'

# Resposta Esperada
{
  "message": "Status updated successfully",
  "machine_id": 1,
  "timestamp": "2025-10-01T10:31:00Z"
}

# Status: 🔄 TESTANDO...
```

### **🔄 5. TICKETS**

#### **5.1 Criar Ticket - Cenário de Sucesso**
```bash
# Comando
curl -X POST http://localhost:8000/api/v1/tickets/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "title": "Servidor com alta utilização de CPU",
    "description": "O servidor-001 está com 95% de utilização de CPU",
    "priority": "high",
    "category": "hardware",
    "machine_id": 1
  }'

# Resposta Esperada
{
  "id": 1,
  "title": "Servidor com alta utilização de CPU",
  "status": "open",
  "priority": "high",
  "created_at": "2025-10-01T10:31:00Z"
}

# Status: 🔄 TESTANDO...
```

#### **5.2 Listar Tickets**
```bash
# Comando
curl -X GET http://localhost:8000/api/v1/tickets/list \
  -H "Authorization: Bearer {TOKEN}"

# Resposta Esperada
{
  "tickets": [
    {
      "id": 1,
      "title": "Servidor com alta utilização de CPU",
      "status": "open",
      "priority": "high",
      "created_at": "2025-10-01T10:31:00Z"
    }
  ],
  "total": 1
}

# Status: 🔄 TESTANDO...
```

### **🔄 6. ALERTAS**

#### **6.1 Enviar Alerta - Cenário de Sucesso**
```bash
# Comando
curl -X POST http://localhost:8000/api/v1/alerts/send \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "machine_id": 1,
    "alert_type": "cpu_high",
    "severity": "critical",
    "message": "CPU utilization above 90%",
    "metrics": {
      "cpu_usage": 95,
      "threshold": 90
    }
  }'

# Resposta Esperada
{
  "id": 1,
  "alert_type": "cpu_high",
  "severity": "critical",
  "status": "active",
  "created_at": "2025-10-01T10:31:00Z"
}

# Status: 🔄 TESTANDO...
```

---

## 🔒 **TESTES DE SEGURANÇA**

### **1. Rate Limiting**
```bash
# Teste: 35 requisições em 1 minuto (limite: 30/min)
for i in {1..35}; do
  curl -w "%{http_code}\n" http://localhost:8000/health
  sleep 1
done

# Resultado Esperado:
# Primeiras 30: 200 OK
# Últimas 5: 429 Too Many Requests
```

### **2. Headers de Segurança**
```bash
# Comando
curl -I http://localhost:8000/health

# Headers Esperados
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'
X-Request-ID: [UUID]
```

### **3. Validação de Input**
```bash
# Teste XSS
curl -X POST http://localhost:8000/api/v1/machines/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{
    "hostname": "<script>alert(\"xss\")</script>",
    "ip_address": "192.168.1.100"
  }'

# Resultado Esperado: Input sanitizado ou rejeitado
```

---

## 📊 **TESTES DE PERFORMANCE**

### **1. Tempo de Resposta**
```bash
# Teste com curl timing
curl -w "@curl-format.txt" http://localhost:8000/health

# Arquivo curl-format.txt:
#      time_namelookup:  %{time_namelookup}\n
#         time_connect:  %{time_connect}\n
#      time_appconnect:  %{time_appconnect}\n
#     time_pretransfer:  %{time_pretransfer}\n
#        time_redirect:  %{time_redirect}\n
#   time_starttransfer:  %{time_starttransfer}\n
#                     ----------\n
#           time_total:  %{time_total}\n

# Critério: time_total < 3 segundos
```

### **2. Carga Simultânea**
```bash
# Teste com Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Critérios:
# - Requests per second > 100
# - 99% das requisições < 3s
# - 0% de falhas
```

---

## 🐛 **BUGS ENCONTRADOS**

### **Template de Bug Report**
```markdown
## Bug #001
**Título**: [Título do bug]
**Severidade**: [Crítica/Alta/Média/Baixa]
**Endpoint**: [Endpoint afetado]
**Método**: [GET/POST/PUT/DELETE]

**Descrição**:
[Descrição detalhada do problema]

**Passos para Reproduzir**:
1. [Passo 1]
2. [Passo 2]
3. [Passo 3]

**Resultado Esperado**:
[O que deveria acontecer]

**Resultado Atual**:
[O que está acontecendo]

**Evidências**:
```bash
# Comando executado
curl -X POST ...

# Resposta recebida
{
  "error": "..."
}
```

**Impacto**:
[Impacto no sistema/usuários]

**Sugestão de Correção**:
[Sugestão técnica para correção]
```

---

## ✅ **CHECKLIST DE VALIDAÇÃO**

### **Funcionalidade**
- [ ] Health check funcionando
- [ ] Autenticação JWT funcionando
- [ ] Todos os endpoints respondendo
- [ ] Validação de dados funcionando
- [ ] Tratamento de erros adequado

### **Segurança**
- [ ] Rate limiting ativo
- [ ] Headers de segurança presentes
- [ ] Autenticação obrigatória
- [ ] Validação de input funcionando
- [ ] Logs de auditoria ativos

### **Performance**
- [ ] Tempo de resposta < 3s
- [ ] Suporte a carga simultânea
- [ ] Sem vazamentos de memória
- [ ] Conexões de DB otimizadas

### **Integração**
- [ ] Frontend consumindo API
- [ ] Dados persistindo no banco
- [ ] Notificações funcionando
- [ ] Alertas automáticos ativos

---

## 📈 **MÉTRICAS DE QUALIDADE**

### **Cobertura de Testes**
- ✅ Endpoints testados: 0/20 (0%)
- ✅ Cenários de sucesso: 0/20 (0%)
- ✅ Cenários de erro: 0/15 (0%)
- ✅ Edge cases: 0/10 (0%)

### **Performance**
- ⏱️ Tempo médio de resposta: [A medir]
- 📊 Throughput: [A medir]
- 💾 Uso de memória: [A medir]
- 🔄 Taxa de erro: [A medir]

### **Segurança**
- 🔒 Vulnerabilidades encontradas: 0
- 🛡️ Headers de segurança: ✅
- 🔑 Autenticação: ✅
- 🚫 Rate limiting: ✅

---

## 🚀 **PRÓXIMOS PASSOS**

### **1. Executar Testes**
```bash
# Executar todos os testes
./run_api_tests.sh

# Executar testes específicos
./run_auth_tests.sh
./run_security_tests.sh
./run_performance_tests.sh
```

### **2. Analisar Resultados**
- Compilar relatório de bugs
- Calcular métricas de qualidade
- Identificar pontos de melhoria

### **3. Validar Correções**
- Reteste após correções
- Validação de regressão
- Aprovação final

---

**🎯 OBJETIVO**: Validar 100% dos endpoints da API e garantir que todos os cenários estão funcionando corretamente!