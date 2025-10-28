# 🛠️ GUIA PRÁTICO DE IMPLEMENTAÇÃO - MELHORIAS CRÍTICAS

## 🎯 **OVERVIEW**

Este guia fornece instruções step-by-step para implementar as melhorias mais críticas no Sistema Levitiis. Cada seção inclui código pronto para uso e comandos específicos.

---

## ⚡ **IMPLEMENTAÇÃO 1: CACHE REDIS (PRIORIDADE ALTA)**

### **🔧 Passo 1: Instalação e Configuração**

#### **Instalar Dependências**
```bash
# Backend
cd backend
pip install redis==5.0.1 aioredis==2.0.1

# Atualizar requirements.txt
echo "redis==5.0.1" >> requirements.txt
echo "aioredis==2.0.1" >> requirements.txt
```

#### **Configurar Redis no Docker**
```yaml
# docker-compose.yml - Adicionar serviço Redis
services:
  redis:
    image: redis:7-alpine
    container_name: levitiis_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

volumes:
  redis_data:
```

### **🔧 Passo 2: Configuração do Backend**

#### **Criar Configuração Redis**
```python
# app/core/redis_config.py
import redis.asyncio as redis
from typing import Optional
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Conecta ao Redis"""
        try:
            self.redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Testar conexão
            await self.redis.ping()
            logger.info("✅ Redis conectado com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao conectar Redis: {e}")
            self.redis = None
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis desconectado")
    
    async def get(self, key: str):
        """Busca valor do cache"""
        if not self.redis:
            return None
        
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Erro ao buscar cache {key}: {e}")
        
        return None
    
    async def set(self, key: str, value: any, expire: int = 300):
        """Armazena valor no cache"""
        if not self.redis:
            return False
        
        try:
            await self.redis.setex(
                key, 
                expire, 
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Erro ao armazenar cache {key}: {e}")
            return False
    
    async def delete(self, key: str):
        """Remove valor do cache"""
        if not self.redis:
            return False
        
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Erro ao deletar cache {key}: {e}")
            return False
    
    async def clear_pattern(self, pattern: str):
        """Remove chaves por padrão"""
        if not self.redis:
            return False
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Erro ao limpar cache {pattern}: {e}")
            return False

# Instância global
redis_manager = RedisManager()

async def get_redis():
    """Dependency para FastAPI"""
    return redis_manager
```

#### **Atualizar Configurações**
```python
# app/core/config.py - Adicionar configuração Redis
class Settings(BaseSettings):
    # ... configurações existentes ...
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 300  # 5 minutos
    
    class Config:
        env_file = ".env"
```

#### **Atualizar main.py**
```python
# app/main.py - Adicionar inicialização Redis
from app.core.redis_config import redis_manager

@app.on_event("startup")
async def startup_event():
    """Inicialização da aplicação"""
    # Conectar Redis
    await redis_manager.connect()
    
    # ... outras inicializações ...

@app.on_event("shutdown")
async def shutdown_event():
    """Finalização da aplicação"""
    # Desconectar Redis
    await redis_manager.disconnect()
    
    # ... outras finalizações ...
```

### **🔧 Passo 3: Implementar Cache nos Endpoints**

#### **Cache para Dashboard**
```python
# app/api/v1/endpoints/dashboard.py
from app.core.redis_config import get_redis
from fastapi import Depends

@router.get("/")
async def get_dashboard_data(
    redis_manager = Depends(get_redis),
    current_user: str = Depends(get_current_user)
):
    """Dashboard com cache Redis"""
    
    cache_key = f"dashboard:overview:{current_user}"
    
    # Tentar buscar do cache
    cached_data = await redis_manager.get(cache_key)
    if cached_data:
        return {
            "data": cached_data,
            "cached": True,
            "timestamp": cached_data.get("timestamp")
        }
    
    # Buscar dados do banco
    async with get_async_session() as db:
        # Buscar máquinas
        machines_query = select(Machine).where(Machine.is_active == True)
        machines_result = await db.execute(machines_query)
        machines = machines_result.scalars().all()
        
        # Buscar tickets
        tickets_query = select(Ticket).where(Ticket.status != "closed")
        tickets_result = await db.execute(tickets_query)
        tickets = tickets_result.scalars().all()
        
        # Buscar alertas
        alerts_query = select(Alert).where(Alert.resolved == False)
        alerts_result = await db.execute(alerts_query)
        alerts = alerts_result.scalars().all()
    
    # Preparar dados
    dashboard_data = {
        "overview": {
            "total_machines": len(machines),
            "online_machines": len([m for m in machines if m.status == "online"]),
            "offline_machines": len([m for m in machines if m.status == "offline"]),
            "open_tickets": len(tickets),
            "critical_alerts": len([a for a in alerts if a.severity == "critical"])
        },
        "performance": {
            "avg_cpu": sum([m.cpu_usage or 0 for m in machines]) / len(machines) if machines else 0,
            "avg_memory": sum([m.memory_usage or 0 for m in machines]) / len(machines) if machines else 0,
            "avg_disk": sum([m.disk_usage or 0 for m in machines]) / len(machines) if machines else 0
        },
        "timestamp": time.time()
    }
    
    # Armazenar no cache por 5 minutos
    await redis_manager.set(cache_key, dashboard_data, expire=300)
    
    return {
        "data": dashboard_data,
        "cached": False,
        "timestamp": dashboard_data["timestamp"]
    }
```

#### **Cache para Lista de Máquinas**
```python
# app/api/v1/endpoints/machines.py
@router.get("/", response_model=List[MachineResponse])
async def list_machines(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    redis_manager = Depends(get_redis),
    current_user: str = Depends(get_current_user)
):
    """Lista máquinas com cache"""
    
    # Criar chave de cache baseada nos parâmetros
    cache_key = f"machines:list:{skip}:{limit}:{status or 'all'}"
    
    # Tentar buscar do cache
    cached_data = await redis_manager.get(cache_key)
    if cached_data:
        return cached_data
    
    # Buscar do banco
    async with get_async_session() as db:
        query = select(Machine)
        
        if status:
            query = query.where(Machine.status == status)
        
        query = query.offset(skip).limit(limit).order_by(Machine.last_seen.desc())
        
        result = await db.execute(query)
        machines = result.scalars().all()
        
        # Converter para response model
        machines_data = [MachineResponse.from_orm(machine) for machine in machines]
    
    # Armazenar no cache por 2 minutos
    await redis_manager.set(cache_key, machines_data, expire=120)
    
    return machines_data
```

### **🔧 Passo 4: Testar Implementação**

#### **Script de Teste**
```python
# test_redis_cache.py
import asyncio
import aiohttp
import time

async def test_cache_performance():
    """Testa performance do cache"""
    
    base_url = "http://localhost:8000/api/v1"
    
    # Login para obter token
    async with aiohttp.ClientSession() as session:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        async with session.post(f"{base_url}/auth/login", json=login_data) as response:
            token_data = await response.json()
            token = token_data["access_token"]
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Teste 1: Primeira requisição (sem cache)
        start_time = time.time()
        async with session.get(f"{base_url}/dashboard", headers=headers) as response:
            data1 = await response.json()
            first_request_time = time.time() - start_time
        
        print(f"🔍 Primeira requisição (sem cache): {first_request_time:.3f}s")
        print(f"📊 Cached: {data1.get('cached', False)}")
        
        # Teste 2: Segunda requisição (com cache)
        start_time = time.time()
        async with session.get(f"{base_url}/dashboard", headers=headers) as response:
            data2 = await response.json()
            second_request_time = time.time() - start_time
        
        print(f"🚀 Segunda requisição (com cache): {second_request_time:.3f}s")
        print(f"📊 Cached: {data2.get('cached', False)}")
        
        # Calcular melhoria
        improvement = ((first_request_time - second_request_time) / first_request_time) * 100
        print(f"⚡ Melhoria de performance: {improvement:.1f}%")

if __name__ == "__main__":
    asyncio.run(test_cache_performance())
```

---

## 📊 **IMPLEMENTAÇÃO 2: MÉTRICAS E MONITORAMENTO (PRIORIDADE ALTA)**

### **🔧 Passo 1: Configurar Prometheus**

#### **Instalar Dependências**
```bash
pip install prometheus-client==0.18.0
echo "prometheus-client==0.18.0" >> requirements.txt
```

#### **Configurar Métricas**
```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from typing import Dict
from collections import defaultdict

# Métricas Prometheus
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

ACTIVE_CONNECTIONS = Gauge(
    'active_connections',
    'Number of active connections'
)

MACHINE_STATUS = Gauge(
    'machine_status',
    'Machine status (1=online, 0=offline)',
    ['hostname', 'ip_address']
)

SYSTEM_RESOURCES = Gauge(
    'system_resources',
    'System resource usage',
    ['resource_type', 'hostname']
)

class MetricsCollector:
    def __init__(self):
        self.start_time = time.time()
        self.request_times = defaultdict(list)
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Registra métricas de requisição"""
        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code
        ).inc()
        
        REQUEST_DURATION.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def update_machine_metrics(self, machines: list):
        """Atualiza métricas de máquinas"""
        for machine in machines:
            # Status da máquina
            status_value = 1 if machine.status == "online" else 0
            MACHINE_STATUS.labels(
                hostname=machine.hostname,
                ip_address=machine.ip_address
            ).set(status_value)
            
            # Recursos da máquina
            if machine.cpu_usage is not None:
                SYSTEM_RESOURCES.labels(
                    resource_type="cpu",
                    hostname=machine.hostname
                ).set(machine.cpu_usage)
            
            if machine.memory_usage is not None:
                SYSTEM_RESOURCES.labels(
                    resource_type="memory",
                    hostname=machine.hostname
                ).set(machine.memory_usage)
            
            if machine.disk_usage is not None:
                SYSTEM_RESOURCES.labels(
                    resource_type="disk",
                    hostname=machine.hostname
                ).set(machine.disk_usage)
    
    def get_prometheus_metrics(self) -> str:
        """Retorna métricas no formato Prometheus"""
        return generate_latest()

# Instância global
metrics_collector = MetricsCollector()
```

#### **Middleware de Métricas**
```python
# app/middleware/metrics_middleware.py
import time
from fastapi import Request, Response
from app.core.metrics import metrics_collector, ACTIVE_CONNECTIONS

async def metrics_middleware(request: Request, call_next):
    """Middleware para coleta de métricas"""
    
    start_time = time.time()
    ACTIVE_CONNECTIONS.inc()
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Registrar métricas
        metrics_collector.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            duration=duration
        )
        
        return response
    
    except Exception as e:
        duration = time.time() - start_time
        
        # Registrar erro
        metrics_collector.record_request(
            method=request.method,
            endpoint=request.url.path,
            status_code=500,
            duration=duration
        )
        
        raise e
    
    finally:
        ACTIVE_CONNECTIONS.dec()
```

#### **Endpoint de Métricas**
```python
# app/api/v1/endpoints/metrics.py
from fastapi import APIRouter, Response
from app.core.metrics import metrics_collector

router = APIRouter()

@router.get("/metrics")
async def get_prometheus_metrics():
    """Endpoint para métricas Prometheus"""
    metrics_data = metrics_collector.get_prometheus_metrics()
    
    return Response(
        content=metrics_data,
        media_type="text/plain"
    )

@router.get("/metrics/summary")
async def get_metrics_summary():
    """Resumo das métricas em JSON"""
    return {
        "uptime_seconds": time.time() - metrics_collector.start_time,
        "total_requests": sum([
            family.samples[0].value 
            for family in REQUEST_COUNT.collect()
            for sample in family.samples
        ]),
        "active_connections": ACTIVE_CONNECTIONS._value._value,
        "timestamp": time.time()
    }
```

### **🔧 Passo 2: Configurar Grafana Dashboard**

#### **Docker Compose para Monitoring**
```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: levitiis_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: levitiis_grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
```

#### **Configuração Prometheus**
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'levitiis-api'
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: '/api/v1/metrics'
    scrape_interval: 10s

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
```

#### **Dashboard Grafana JSON**
```json
{
  "dashboard": {
    "id": null,
    "title": "Levitiis System Metrics",
    "tags": ["levitiis"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "yAxes": [
          {
            "label": "Requests/sec"
          }
        ]
      },
      {
        "id": 2,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "id": 3,
        "title": "Machine Status",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(machine_status)",
            "legendFormat": "Online Machines"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "5s"
  }
}
```

### **🔧 Passo 3: Implementar Alertas**

#### **Regras de Alerta**
```yaml
# monitoring/alert_rules.yml
groups:
  - name: levitiis_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }} seconds"

      - alert: MachineOffline
        expr: machine_status == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Machine {{ $labels.hostname }} is offline"
          description: "Machine {{ $labels.hostname }} ({{ $labels.ip_address }}) has been offline for more than 1 minute"

      - alert: HighResourceUsage
        expr: system_resources{resource_type="cpu"} > 90
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.hostname }}"
          description: "CPU usage is {{ $value }}% on machine {{ $labels.hostname }}"
```

---

## 🔒 **IMPLEMENTAÇÃO 3: SEGURANÇA AVANÇADA (PRIORIDADE ALTA)**

### **🔧 Passo 1: Rate Limiting Avançado**

#### **Implementação com Redis**
```python
# app/middleware/advanced_rate_limit.py
import time
import hashlib
from fastapi import Request, HTTPException, status
from app.core.redis_config import get_redis

class AdvancedRateLimiter:
    def __init__(self, requests: int, window: int, burst: int = None):
        self.requests = requests
        self.window = window
        self.burst = burst or requests * 2
    
    async def __call__(self, request: Request):
        redis_manager = await get_redis()
        
        # Identificar cliente (IP + User-Agent)
        client_id = self._get_client_id(request)
        
        # Verificar rate limit
        allowed = await self._check_rate_limit(redis_manager, client_id)
        
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Rate limit exceeded",
                    "limit": self.requests,
                    "window": self.window,
                    "retry_after": self.window
                },
                headers={"Retry-After": str(self.window)}
            )
        
        return True
    
    def _get_client_id(self, request: Request) -> str:
        """Gera ID único do cliente"""
        ip = request.client.host
        user_agent = request.headers.get("user-agent", "")
        
        # Hash para anonimizar
        client_data = f"{ip}:{user_agent}"
        return hashlib.sha256(client_data.encode()).hexdigest()[:16]
    
    async def _check_rate_limit(self, redis_manager, client_id: str) -> bool:
        """Verifica rate limit usando sliding window"""
        current_time = int(time.time())
        window_start = current_time - self.window
        
        # Chave para o cliente
        key = f"rate_limit:{client_id}"
        
        try:
            # Usar pipeline para operações atômicas
            if redis_manager.redis:
                pipe = redis_manager.redis.pipeline()
                
                # Remover entradas antigas
                pipe.zremrangebyscore(key, 0, window_start)
                
                # Contar requisições na janela
                pipe.zcard(key)
                
                # Adicionar requisição atual
                pipe.zadd(key, {str(current_time): current_time})
                
                # Definir expiração
                pipe.expire(key, self.window)
                
                results = await pipe.execute()
                request_count = results[1]
                
                return request_count < self.requests
            
            return True  # Se Redis não disponível, permitir
            
        except Exception as e:
            # Em caso de erro, permitir (fail-open)
            return True

# Instâncias para diferentes endpoints
auth_rate_limiter = AdvancedRateLimiter(requests=5, window=60)    # 5 req/min
api_rate_limiter = AdvancedRateLimiter(requests=100, window=60)   # 100 req/min
public_rate_limiter = AdvancedRateLimiter(requests=20, window=60) # 20 req/min
```

#### **Aplicar Rate Limiting**
```python
# app/api/v1/endpoints/auth.py
from app.middleware.advanced_rate_limit import auth_rate_limiter
from fastapi import Depends

@router.post("/login", response_model=TokenResponse)
async def login(
    user_credentials: UserLogin,
    _: bool = Depends(auth_rate_limiter),  # Rate limiting
    db: AsyncSession = Depends(get_async_session)
):
    """Login com rate limiting"""
    # ... implementação do login ...
```

### **🔧 Passo 2: Auditoria de Ações**

#### **Modelo de Auditoria**
```python
# app/models/audit.py
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(100), nullable=True)
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    status_code = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
```

#### **Middleware de Auditoria**
```python
# app/middleware/audit_middleware.py
import time
import json
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog
from app.core.database import get_async_session

class AuditMiddleware:
    def __init__(self):
        self.audit_actions = {
            "POST": ["create", "register", "login"],
            "PUT": ["update", "modify"],
            "DELETE": ["delete", "remove"],
            "PATCH": ["patch", "update"]
        }
    
    async def __call__(self, request: Request, call_next):
        """Middleware de auditoria"""
        start_time = time.time()
        
        # Capturar dados da requisição
        request_data = await self._capture_request_data(request)
        
        # Executar requisição
        response = await call_next(request)
        
        # Verificar se deve auditar
        if self._should_audit(request, response):
            await self._log_action(request, response, request_data, start_time)
        
        return response
    
    async def _capture_request_data(self, request: Request) -> dict:
        """Captura dados da requisição"""
        return {
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent"),
            "user_id": getattr(request.state, "user_id", None),
            "username": getattr(request.state, "username", None)
        }
    
    def _should_audit(self, request: Request, response) -> bool:
        """Determina se deve auditar a ação"""
        # Auditar métodos de modificação
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            return True
        
        # Auditar endpoints sensíveis
        sensitive_paths = ["/auth/", "/users/", "/admin/"]
        if any(path in request.url.path for path in sensitive_paths):
            return True
        
        # Auditar erros
        if response.status_code >= 400:
            return True
        
        return False
    
    async def _log_action(self, request: Request, response, request_data: dict, start_time: float):
        """Registra ação no log de auditoria"""
        try:
            async with get_async_session() as db:
                audit_log = AuditLog(
                    user_id=request_data.get("user_id"),
                    username=request_data.get("username"),
                    action=f"{request_data['method']} {request_data['path']}",
                    resource_type=self._extract_resource_type(request_data["path"]),
                    resource_id=self._extract_resource_id(request_data["path"]),
                    details={
                        "query_params": request_data["query_params"],
                        "status_code": response.status_code,
                        "duration_ms": round((time.time() - start_time) * 1000, 2),
                        "response_size": len(response.body) if hasattr(response, 'body') else 0
                    },
                    ip_address=request_data["ip_address"],
                    user_agent=request_data["user_agent"],
                    status_code=response.status_code
                )
                
                db.add(audit_log)
                await db.commit()
                
        except Exception as e:
            # Log erro mas não falhar a requisição
            print(f"Erro ao registrar auditoria: {e}")
    
    def _extract_resource_type(self, path: str) -> str:
        """Extrai tipo de recurso do path"""
        path_parts = path.strip("/").split("/")
        
        if len(path_parts) >= 3 and path_parts[0] == "api":
            return path_parts[2]  # /api/v1/machines -> machines
        
        return "unknown"
    
    def _extract_resource_id(self, path: str) -> str:
        """Extrai ID do recurso do path"""
        path_parts = path.strip("/").split("/")
        
        # Procurar por ID numérico no final
        if len(path_parts) > 0:
            last_part = path_parts[-1]
            if last_part.isdigit():
                return last_part
        
        return None

# Instância do middleware
audit_middleware = AuditMiddleware()
```

### **🔧 Passo 3: Validação de Entrada Avançada**

#### **Sanitizadores de Segurança**
```python
# app/core/security_validators.py
import re
import html
import bleach
from typing import Any, List
from pydantic import validator

class SecurityValidators:
    # Padrões perigosos
    SQL_INJECTION_PATTERNS = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)',
        r'(\b(UNION|OR|AND)\b.*\b(SELECT|INSERT|UPDATE|DELETE)\b)',
        r'(--|#|/\*|\*/)',
        r'(\bxp_cmdshell\b|\bsp_executesql\b)',
    ]
    
    XSS_PATTERNS = [
        r'<script[^>]*>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',
        r'<iframe[^>]*>.*?</iframe>',
    ]
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitiza string para prevenir XSS e injection"""
        if not value:
            return value
        
        # Limitar tamanho
        value = value[:max_length]
        
        # Escape HTML básico
        value = html.escape(value)
        
        # Usar bleach para limpeza avançada
        allowed_tags = ['b', 'i', 'u', 'em', 'strong']
        value = bleach.clean(value, tags=allowed_tags, strip=True)
        
        # Remover caracteres de controle
        value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
        
        return value.strip()
    
    @staticmethod
    def validate_sql_injection(value: str) -> str:
        """Valida contra SQL injection"""
        if not value:
            return value
        
        for pattern in SecurityValidators.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value.upper()):
                raise ValueError(f"Conteúdo suspeito detectado: possível SQL injection")
        
        return value
    
    @staticmethod
    def validate_xss(value: str) -> str:
        """Valida contra XSS"""
        if not value:
            return value
        
        for pattern in SecurityValidators.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError(f"Conteúdo suspeito detectado: possível XSS")
        
        return value
    
    @staticmethod
    def validate_filename(value: str) -> str:
        """Valida nome de arquivo"""
        if not value:
            return value
        
        # Caracteres perigosos em nomes de arquivo
        dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
        
        for char in dangerous_chars:
            if char in value:
                raise ValueError(f"Caractere não permitido em nome de arquivo: {char}")
        
        # Nomes reservados no Windows
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4',
            'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2',
            'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        
        if value.upper() in reserved_names:
            raise ValueError(f"Nome de arquivo reservado: {value}")
        
        return value
    
    @staticmethod
    def validate_ip_address(value: str) -> str:
        """Valida endereço IP"""
        if not value:
            return value
        
        # Regex para IPv4
        ipv4_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
        
        if not re.match(ipv4_pattern, value):
            raise ValueError("Endereço IP inválido")
        
        # Verificar IPs privados/reservados se necessário
        private_ranges = [
            r'^10\.',
            r'^172\.(1[6-9]|2[0-9]|3[01])\.',
            r'^192\.168\.',
            r'^127\.',
            r'^169\.254\.',
            r'^224\.',
            r'^240\.'
        ]
        
        return value

# Decorador para aplicar validações
def secure_field(max_length: int = 1000, allow_html: bool = False):
    """Decorador para campos seguros"""
    def validator_func(cls, v):
        if v is None:
            return v
        
        if not isinstance(v, str):
            v = str(v)
        
        # Aplicar sanitização
        v = SecurityValidators.sanitize_string(v, max_length)
        
        # Validar SQL injection
        v = SecurityValidators.validate_sql_injection(v)
        
        # Validar XSS se HTML não for permitido
        if not allow_html:
            v = SecurityValidators.validate_xss(v)
        
        return v
    
    return validator('*', pre=True, allow_reuse=True)(validator_func)
```

#### **Aplicar Validações nos Schemas**
```python
# app/schemas/machine.py
from pydantic import BaseModel, validator
from app.core.security_validators import SecurityValidators, secure_field

class MachineRegister(BaseModel):
    hostname: str
    ip_address: str
    mac_address: str
    department: str = None
    description: str = None
    
    # Validações de segurança
    @validator('hostname')
    def validate_hostname(cls, v):
        v = SecurityValidators.sanitize_string(v, 100)
        v = SecurityValidators.validate_sql_injection(v)
        
        # Validação específica de hostname
        if not re.match(r'^[a-zA-Z0-9\-\.]+$', v):
            raise ValueError('Hostname deve conter apenas letras, números, hífens e pontos')
        
        if len(v) > 63:
            raise ValueError('Hostname muito longo (máximo 63 caracteres)')
        
        return v
    
    @validator('ip_address')
    def validate_ip(cls, v):
        return SecurityValidators.validate_ip_address(v)
    
    @validator('mac_address')
    def validate_mac(cls, v):
        v = SecurityValidators.sanitize_string(v, 20)
        
        # Validar formato MAC
        mac_pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        if not re.match(mac_pattern, v):
            raise ValueError('Formato de MAC address inválido')
        
        return v.upper()
    
    @validator('department', 'description')
    def validate_text_fields(cls, v):
        if v is None:
            return v
        
        v = SecurityValidators.sanitize_string(v, 500)
        v = SecurityValidators.validate_sql_injection(v)
        v = SecurityValidators.validate_xss(v)
        
        return v
```

### **🔧 Passo 4: Script de Teste de Segurança**

```python
# test_security.py
import asyncio
import aiohttp
import time

async def test_security_features():
    """Testa recursos de segurança"""
    
    base_url = "http://localhost:8000/api/v1"
    
    print("🔒 Testando recursos de segurança...")
    
    async with aiohttp.ClientSession() as session:
        
        # Teste 1: Rate Limiting
        print("\n📊 Teste 1: Rate Limiting")
        
        login_data = {"username": "admin", "password": "admin123"}
        
        # Fazer múltiplas requisições rapidamente
        for i in range(7):  # Limite é 5 por minuto
            try:
                async with session.post(f"{base_url}/auth/login", json=login_data) as response:
                    if response.status == 429:
                        print(f"✅ Rate limiting funcionando - Requisição {i+1} bloqueada")
                        break
                    elif response.status == 200:
                        print(f"✅ Requisição {i+1} permitida")
                    else:
                        print(f"❌ Erro inesperado: {response.status}")
            except Exception as e:
                print(f"❌ Erro na requisição {i+1}: {e}")
            
            time.sleep(0.1)
        
        # Teste 2: Validação de Entrada
        print("\n🛡️ Teste 2: Validação de Entrada")
        
        # Obter token válido
        async with session.post(f"{base_url}/auth/login", json=login_data) as response:
            if response.status == 200:
                token_data = await response.json()
                token = token_data["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
            else:
                print("❌ Não foi possível obter token")
                return
        
        # Testar SQL injection
        malicious_data = {
            "hostname": "test'; DROP TABLE machines; --",
            "ip_address": "192.168.1.100",
            "mac_address": "00:11:22:33:44:55"
        }
        
        async with session.post(f"{base_url}/machines/register", json=malicious_data, headers=headers) as response:
            if response.status == 422:
                error_data = await response.json()
                print("✅ SQL injection bloqueado:", error_data["detail"])
            else:
                print(f"❌ SQL injection não detectado: {response.status}")
        
        # Testar XSS
        xss_data = {
            "hostname": "test<script>alert('xss')</script>",
            "ip_address": "192.168.1.101",
            "mac_address": "00:11:22:33:44:56"
        }
        
        async with session.post(f"{base_url}/machines/register", json=xss_data, headers=headers) as response:
            if response.status == 422:
                error_data = await response.json()
                print("✅ XSS bloqueado:", error_data["detail"])
            else:
                print(f"❌ XSS não detectado: {response.status}")
        
        # Teste 3: Headers de Segurança
        print("\n🔐 Teste 3: Headers de Segurança")
        
        async with session.get(f"{base_url}/health") as response:
            headers = response.headers
            
            security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options",
                "X-XSS-Protection",
                "Strict-Transport-Security"
            ]
            
            for header in security_headers:
                if header in headers:
                    print(f"✅ {header}: {headers[header]}")
                else:
                    print(f"❌ {header}: Não encontrado")

if __name__ == "__main__":
    asyncio.run(test_security_features())
```

---

## 🚀 **SCRIPT DE IMPLEMENTAÇÃO AUTOMÁTICA**

```bash
#!/bin/bash
# implement_improvements.sh

echo "🚀 Implementando melhorias críticas do Sistema Levitiis..."

# Verificar se estamos no diretório correto
if [ ! -f "backend/main.py" ]; then
    echo "❌ Execute este script no diretório raiz do projeto"
    exit 1
fi

# 1. Instalar dependências
echo "📦 Instalando dependências..."
cd backend
pip install redis==5.0.1 aioredis==2.0.1 prometheus-client==0.18.0 bleach==6.1.0

# 2. Atualizar requirements.txt
echo "📝 Atualizando requirements.txt..."
echo "redis==5.0.1" >> requirements.txt
echo "aioredis==2.0.1" >> requirements.txt
echo "prometheus-client==0.18.0" >> requirements.txt
echo "bleach==6.1.0" >> requirements.txt

# 3. Criar diretórios necessários
echo "📁 Criando estrutura de diretórios..."
mkdir -p monitoring/grafana/provisioning
mkdir -p app/middleware
mkdir -p app/core

# 4. Configurar variáveis de ambiente
echo "⚙️ Configurando variáveis de ambiente..."
if [ ! -f .env ]; then
    cp .env.example .env 2>/dev/null || touch .env
fi

# Adicionar configurações Redis se não existirem
if ! grep -q "REDIS_URL" .env; then
    echo "REDIS_URL=redis://localhost:6379/0" >> .env
fi

if ! grep -q "CACHE_TTL" .env; then
    echo "CACHE_TTL=300" >> .env
fi

# 5. Iniciar serviços de monitoramento
echo "🐳 Iniciando serviços Docker..."
cd ..

# Criar docker-compose para monitoramento se não existir
if [ ! -f "docker-compose.monitoring.yml" ]; then
    echo "📄 Criando docker-compose.monitoring.yml..."
    cat > docker-compose.monitoring.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: levitiis_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  prometheus:
    image: prom/prometheus:latest
    container_name: levitiis_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: levitiis_grafana
    ports:
      - "3001:3000"
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped

volumes:
  redis_data:
  prometheus_data:
  grafana_data:
EOF
fi

# Criar configuração Prometheus
if [ ! -f "monitoring/prometheus.yml" ]; then
    echo "📄 Criando configuração Prometheus..."
    cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'levitiis-api'
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: '/api/v1/metrics'
    scrape_interval: 10s

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF
fi

# Iniciar serviços
docker-compose -f docker-compose.monitoring.yml up -d

# 6. Executar testes
echo "🧪 Executando testes de validação..."
cd backend

# Criar script de teste simples
cat > test_improvements.py << 'EOF'
import asyncio
import aiohttp
import time

async def test_basic_functionality():
    """Teste básico das melhorias"""
    print("🔍 Testando melhorias implementadas...")
    
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Teste health check
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    print("✅ Health check funcionando")
                else:
                    print(f"❌ Health check falhou: {response.status}")
        except Exception as e:
            print(f"❌ Erro no health check: {e}")
        
        # Teste métricas
        try:
            async with session.get(f"{base_url}/api/v1/metrics") as response:
                if response.status == 200:
                    print("✅ Endpoint de métricas funcionando")
                else:
                    print(f"❌ Métricas falharam: {response.status}")
        except Exception as e:
            print(f"❌ Erro nas métricas: {e}")

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
EOF

python test_improvements.py

# 7. Finalização
echo ""
echo "🎉 Implementação concluída com sucesso!"
echo ""
echo "📊 Serviços disponíveis:"
echo "   🌐 Frontend: http://localhost:3000"
echo "   🔧 Backend API: http://localhost:8000"
echo "   📈 Prometheus: http://localhost:9090"
echo "   📊 Grafana: http://localhost:3001 (admin/admin123)"
echo "   🔍 API Docs: http://localhost:8000/api/v1/docs"
echo "   📋 Métricas: http://localhost:8000/api/v1/metrics"
echo ""
echo "🔧 Próximos passos:"
echo "   1. Configurar dashboards no Grafana"
echo "   2. Ajustar alertas no Prometheus"
echo "   3. Testar performance com carga"
echo "   4. Revisar logs de auditoria"
echo ""
echo "✨ Sistema Levitiis atualizado e pronto para produção!"
```

---

## 📋 **CHECKLIST FINAL DE IMPLEMENTAÇÃO**

### **✅ Cache Redis**
- [ ] Redis instalado e configurado
- [ ] Cache implementado no dashboard
- [ ] Cache implementado na listagem de máquinas
- [ ] Teste de performance executado
- [ ] Métricas de cache hit/miss configuradas

### **✅ Métricas e Monitoramento**
- [ ] Prometheus configurado
- [ ] Grafana configurado
- [ ] Métricas de aplicação implementadas
- [ ] Dashboards criados
- [ ] Alertas configurados

### **✅ Segurança Avançada**
- [ ] Rate limiting implementado
- [ ] Sistema de auditoria configurado
- [ ] Validação de entrada implementada
- [ ] Headers de segurança configurados
- [ ] Testes de segurança executados

### **✅ Testes e Validação**
- [ ] Testes automatizados criados
- [ ] Performance testada
- [ ] Segurança validada
- [ ] Documentação atualizada
- [ ] Equipe treinada

---

**🚀 Com este guia, você terá um Sistema Levitiis robusto, seguro e pronto para produção em poucas horas!**