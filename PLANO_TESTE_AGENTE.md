# 🤖 PLANO DE TESTE - SIMULAÇÃO DE AGENTE LEVITIIS

## 📋 **VISÃO GERAL**

Este documento detalha o plano de testes para simular um agente Levitiis coletando dados de máquinas e enviando para o sistema central.

---

## 🎯 **OBJETIVOS DOS TESTES**

### **1. Validar Coleta de Dados**
- ✅ Simular dados de máquinas reais
- ✅ Testar diferentes tipos de equipamentos
- ✅ Validar formato e estrutura dos dados
- ✅ Testar cenários de erro e recuperação

### **2. Testar Comunicação API**
- ✅ Registro de máquinas
- ✅ Envio de status e métricas
- ✅ Criação de tickets automáticos
- ✅ Sistema de alertas

### **3. Validar Dashboard**
- ✅ Visualização de dados em tempo real
- ✅ Gráficos e métricas
- ✅ Alertas e notificações
- ✅ Relatórios automáticos

---

## 🏗️ **ARQUITETURA DE TESTE**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AGENTE FAKE   │───▶│   API BACKEND   │───▶│   DASHBOARD     │
│   (Simulador)   │    │   (FastAPI)     │    │   (Vue.js)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Dados Falsos   │    │  Banco de Dados │    │   Notificações  │
│  Realistas      │    │  (SQLite/Postgres)│    │   & Alertas     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 📊 **DADOS DE TESTE - MÁQUINAS SIMULADAS**

### **1. Tipos de Equipamentos**
```json
{
  "tipos_maquinas": [
    {
      "tipo": "servidor",
      "modelos": ["Dell PowerEdge R740", "HP ProLiant DL380", "IBM System x3650"],
      "metricas": ["cpu_usage", "memory_usage", "disk_usage", "network_io", "temperature"]
    },
    {
      "tipo": "workstation",
      "modelos": ["Dell OptiPlex 7090", "HP EliteDesk 800", "Lenovo ThinkCentre M920"],
      "metricas": ["cpu_usage", "memory_usage", "disk_usage", "uptime"]
    },
    {
      "tipo": "notebook",
      "modelos": ["Dell Latitude 7420", "HP EliteBook 840", "Lenovo ThinkPad X1"],
      "metricas": ["cpu_usage", "memory_usage", "battery_level", "temperature"]
    },
    {
      "tipo": "impressora",
      "modelos": ["HP LaserJet Pro 400", "Canon imageRUNNER", "Xerox WorkCentre"],
      "metricas": ["toner_level", "paper_level", "page_count", "status"]
    },
    {
      "tipo": "switch",
      "modelos": ["Cisco Catalyst 2960", "HP Aruba 2930F", "Ubiquiti UniFi"],
      "metricas": ["port_status", "bandwidth_usage", "uptime", "temperature"]
    }
  ]
}
```

### **2. Cenários de Dados**

#### **🟢 Cenário Normal (70% dos dados)**
```json
{
  "servidor_normal": {
    "cpu_usage": "15-45%",
    "memory_usage": "30-60%",
    "disk_usage": "20-70%",
    "temperature": "35-55°C",
    "status": "online"
  }
}
```

#### **🟡 Cenário Alerta (20% dos dados)**
```json
{
  "servidor_alerta": {
    "cpu_usage": "70-85%",
    "memory_usage": "80-90%",
    "disk_usage": "85-95%",
    "temperature": "65-75°C",
    "status": "warning"
  }
}
```

#### **🔴 Cenário Crítico (10% dos dados)**
```json
{
  "servidor_critico": {
    "cpu_usage": "90-100%",
    "memory_usage": "95-100%",
    "disk_usage": "95-100%",
    "temperature": "80-90°C",
    "status": "critical"
  }
}
```

---

## 🔧 **SCRIPTS DE TESTE**

### **1. Script Simulador de Agente**

```python
# agent_simulator.py
import requests
import json
import time
import random
from datetime import datetime, timedelta

class LevitiisAgentSimulator:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.machines = []
        self.auth_token = None
        
    def authenticate(self):
        """Autentica o agente no sistema"""
        response = requests.post(f"{self.base_url}/api/v1/auth/login", 
                               data={"username": "admin", "password": "admin123"})
        if response.status_code == 200:
            self.auth_token = response.json()["access_token"]
            return True
        return False
    
    def register_machines(self, count=50):
        """Registra máquinas simuladas"""
        machine_types = ["servidor", "workstation", "notebook", "impressora", "switch"]
        
        for i in range(count):
            machine_type = random.choice(machine_types)
            machine_data = {
                "hostname": f"{machine_type}-{i+1:03d}",
                "ip_address": f"192.168.1.{i+10}",
                "mac_address": self.generate_mac(),
                "type": machine_type,
                "model": self.get_random_model(machine_type),
                "location": f"Andar {random.randint(1, 5)} - Sala {random.randint(1, 20)}",
                "department": random.choice(["TI", "RH", "Financeiro", "Vendas", "Marketing"])
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/machines/register",
                json=machine_data,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code == 200:
                self.machines.append(response.json())
                print(f"✅ Máquina registrada: {machine_data['hostname']}")
            else:
                print(f"❌ Erro ao registrar: {machine_data['hostname']}")
    
    def send_metrics(self):
        """Envia métricas das máquinas"""
        for machine in self.machines:
            metrics = self.generate_metrics(machine["type"])
            
            status_data = {
                "machine_id": machine["id"],
                "timestamp": datetime.now().isoformat(),
                "status": metrics["status"],
                "metrics": metrics
            }
            
            response = requests.post(
                f"{self.base_url}/api/v1/machines/status",
                json=status_data,
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code == 200:
                print(f"📊 Métricas enviadas: {machine['hostname']}")
                
                # Criar ticket se status crítico
                if metrics["status"] == "critical":
                    self.create_ticket(machine, metrics)
            else:
                print(f"❌ Erro ao enviar métricas: {machine['hostname']}")
    
    def generate_metrics(self, machine_type):
        """Gera métricas baseadas no tipo de máquina"""
        scenario = random.choices(
            ["normal", "warning", "critical"],
            weights=[70, 20, 10]
        )[0]
        
        if machine_type == "servidor":
            return self.generate_server_metrics(scenario)
        elif machine_type == "workstation":
            return self.generate_workstation_metrics(scenario)
        elif machine_type == "notebook":
            return self.generate_notebook_metrics(scenario)
        elif machine_type == "impressora":
            return self.generate_printer_metrics(scenario)
        elif machine_type == "switch":
            return self.generate_switch_metrics(scenario)
    
    def generate_server_metrics(self, scenario):
        """Gera métricas específicas para servidores"""
        if scenario == "normal":
            return {
                "status": "online",
                "cpu_usage": random.randint(15, 45),
                "memory_usage": random.randint(30, 60),
                "disk_usage": random.randint(20, 70),
                "temperature": random.randint(35, 55),
                "network_io": random.randint(100, 1000),
                "uptime": random.randint(1, 365)
            }
        elif scenario == "warning":
            return {
                "status": "warning",
                "cpu_usage": random.randint(70, 85),
                "memory_usage": random.randint(80, 90),
                "disk_usage": random.randint(85, 95),
                "temperature": random.randint(65, 75),
                "network_io": random.randint(1000, 5000),
                "uptime": random.randint(1, 365)
            }
        else:  # critical
            return {
                "status": "critical",
                "cpu_usage": random.randint(90, 100),
                "memory_usage": random.randint(95, 100),
                "disk_usage": random.randint(95, 100),
                "temperature": random.randint(80, 90),
                "network_io": random.randint(5000, 10000),
                "uptime": random.randint(1, 365)
            }
    
    def create_ticket(self, machine, metrics):
        """Cria ticket automático para problemas críticos"""
        ticket_data = {
            "title": f"CRÍTICO: {machine['hostname']} - Recursos Esgotados",
            "description": f"""
            Máquina: {machine['hostname']} ({machine['ip_address']})
            Localização: {machine['location']}
            
            Métricas Críticas:
            - CPU: {metrics['cpu_usage']}%
            - Memória: {metrics['memory_usage']}%
            - Disco: {metrics['disk_usage']}%
            - Temperatura: {metrics['temperature']}°C
            
            Ação necessária: Verificação imediata
            """,
            "priority": "high",
            "category": "hardware",
            "machine_id": machine["id"]
        }
        
        response = requests.post(
            f"{self.base_url}/api/v1/tickets/create",
            json=ticket_data,
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        
        if response.status_code == 200:
            print(f"🎫 Ticket criado para: {machine['hostname']}")
    
    def generate_mac(self):
        """Gera endereço MAC aleatório"""
        return ":".join([f"{random.randint(0, 255):02x}" for _ in range(6)])
    
    def get_random_model(self, machine_type):
        """Retorna modelo aleatório baseado no tipo"""
        models = {
            "servidor": ["Dell PowerEdge R740", "HP ProLiant DL380", "IBM System x3650"],
            "workstation": ["Dell OptiPlex 7090", "HP EliteDesk 800", "Lenovo ThinkCentre M920"],
            "notebook": ["Dell Latitude 7420", "HP EliteBook 840", "Lenovo ThinkPad X1"],
            "impressora": ["HP LaserJet Pro 400", "Canon imageRUNNER", "Xerox WorkCentre"],
            "switch": ["Cisco Catalyst 2960", "HP Aruba 2930F", "Ubiquiti UniFi"]
        }
        return random.choice(models.get(machine_type, ["Modelo Genérico"]))

# Execução do simulador
if __name__ == "__main__":
    simulator = LevitiisAgentSimulator()
    
    print("🚀 Iniciando simulador de agente Levitiis...")
    
    # Autenticar
    if simulator.authenticate():
        print("✅ Autenticação realizada com sucesso")
        
        # Registrar máquinas
        print("📝 Registrando máquinas...")
        simulator.register_machines(50)
        
        # Loop de envio de métricas
        print("📊 Iniciando envio de métricas...")
        for cycle in range(10):  # 10 ciclos de teste
            print(f"\n🔄 Ciclo {cycle + 1}/10")
            simulator.send_metrics()
            time.sleep(30)  # Aguarda 30 segundos entre ciclos
            
        print("✅ Simulação concluída!")
    else:
        print("❌ Falha na autenticação")
```

### **2. Script de Teste de Carga**

```python
# load_test.py
import asyncio
import aiohttp
import time
from concurrent.futures import ThreadPoolExecutor

class LoadTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    async def test_endpoint(self, session, endpoint, method="GET", data=None):
        """Testa um endpoint específico"""
        start_time = time.time()
        try:
            if method == "GET":
                async with session.get(f"{self.base_url}{endpoint}") as response:
                    status = response.status
                    response_time = time.time() - start_time
                    return {"endpoint": endpoint, "status": status, "time": response_time}
            elif method == "POST":
                async with session.post(f"{self.base_url}{endpoint}", json=data) as response:
                    status = response.status
                    response_time = time.time() - start_time
                    return {"endpoint": endpoint, "status": status, "time": response_time}
        except Exception as e:
            return {"endpoint": endpoint, "status": "error", "time": time.time() - start_time, "error": str(e)}
    
    async def run_load_test(self, concurrent_users=10, requests_per_user=100):
        """Executa teste de carga"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            for user in range(concurrent_users):
                for request in range(requests_per_user):
                    # Testa diferentes endpoints
                    endpoints = [
                        "/health",
                        "/api/v1/dashboard/summary",
                        "/api/v1/machines/list",
                        "/api/v1/tickets/list"
                    ]
                    
                    endpoint = endpoints[request % len(endpoints)]
                    task = self.test_endpoint(session, endpoint)
                    tasks.append(task)
            
            results = await asyncio.gather(*tasks)
            self.results = results
            
            # Análise dos resultados
            self.analyze_results()
    
    def analyze_results(self):
        """Analisa os resultados do teste de carga"""
        total_requests = len(self.results)
        successful_requests = len([r for r in self.results if r["status"] == 200])
        failed_requests = total_requests - successful_requests
        
        response_times = [r["time"] for r in self.results if "time" in r]
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        print(f"""
        📊 RESULTADOS DO TESTE DE CARGA:
        
        Total de Requisições: {total_requests}
        Requisições Bem-sucedidas: {successful_requests}
        Requisições Falhadas: {failed_requests}
        Taxa de Sucesso: {(successful_requests/total_requests)*100:.2f}%
        
        Tempo de Resposta Médio: {avg_response_time:.3f}s
        Tempo de Resposta Mínimo: {min_response_time:.3f}s
        Tempo de Resposta Máximo: {max_response_time:.3f}s
        """)

# Execução do teste de carga
if __name__ == "__main__":
    tester = LoadTester()
    asyncio.run(tester.run_load_test(concurrent_users=20, requests_per_user=50))
```

---

## 📋 **CHECKLIST DE TESTES**

### **✅ Fase 1: Testes Básicos**
- [ ] Autenticação do agente
- [ ] Registro de máquinas
- [ ] Envio de métricas básicas
- [ ] Visualização no dashboard

### **✅ Fase 2: Testes de Cenários**
- [ ] Máquinas com status normal
- [ ] Máquinas com alertas
- [ ] Máquinas em estado crítico
- [ ] Criação automática de tickets

### **✅ Fase 3: Testes de Integração**
- [ ] Frontend exibindo dados do backend
- [ ] Notificações em tempo real
- [ ] Relatórios automáticos
- [ ] Sistema de alertas

### **✅ Fase 4: Testes de Performance**
- [ ] 50 máquinas simultâneas
- [ ] 100 requisições por minuto
- [ ] Rate limiting funcionando
- [ ] Tempo de resposta < 3s

### **✅ Fase 5: Testes de Segurança**
- [ ] Headers de segurança presentes
- [ ] Autenticação obrigatória
- [ ] Validação de input
- [ ] Rate limiting ativo

---

## 🎯 **CRITÉRIOS DE ACEITAÇÃO**

### **✅ Funcionalidade**
- ✅ 100% dos endpoints funcionando
- ✅ Dashboard exibindo dados em tempo real
- ✅ Alertas automáticos funcionando
- ✅ Tickets criados automaticamente

### **✅ Performance**
- ✅ Tempo de resposta < 3 segundos
- ✅ Suporte a 100+ máquinas simultâneas
- ✅ Rate limiting efetivo
- ✅ Sem vazamentos de memória

### **✅ Segurança**
- ✅ Autenticação JWT funcionando
- ✅ Headers de segurança presentes
- ✅ Validação de input ativa
- ✅ Logs de auditoria funcionando

---

## 📊 **RELATÓRIO DE EXECUÇÃO**

### **Template de Relatório**
```markdown
# RELATÓRIO DE TESTE - AGENTE LEVITIIS

## Resumo Executivo
- Data: [DATA]
- Duração: [TEMPO]
- Tester: [NOME]
- Ambiente: [DEV/STAGING/PROD]

## Resultados
- ✅ Testes Passaram: X/Y
- ❌ Testes Falharam: X/Y
- ⚠️ Bugs Encontrados: X
- 📊 Performance: [OK/ALERTA/CRÍTICO]

## Bugs Críticos
1. [Descrição do bug]
2. [Descrição do bug]

## Recomendações
1. [Recomendação 1]
2. [Recomendação 2]

## Próximos Passos
- [ ] Correção de bugs críticos
- [ ] Reteste após correções
- [ ] Aprovação para produção
```

---

## 🚀 **EXECUÇÃO DOS TESTES**

### **1. Preparação**
```bash
# Instalar dependências
pip install requests aiohttp asyncio

# Verificar se o sistema está rodando
curl http://localhost:8000/health
```

### **2. Executar Simulador**
```bash
python agent_simulator.py
```

### **3. Executar Teste de Carga**
```bash
python load_test.py
```

### **4. Verificar Dashboard**
- Acessar: http://localhost:3000
- Login: admin/admin123
- Verificar dados em tempo real

---

## 📞 **SUPORTE**

### **Contatos**
- **Desenvolvedor**: Sistema Levitiis
- **QA Lead**: [Nome do QA]
- **Documentação**: README.md

### **Logs Importantes**
- Backend: `backend/logs/`
- Frontend: Console do navegador
- Nginx: `/var/log/nginx/`

---

**🎯 OBJETIVO**: Validar 100% da funcionalidade do agente simulado e garantir que o sistema está pronto para produção!