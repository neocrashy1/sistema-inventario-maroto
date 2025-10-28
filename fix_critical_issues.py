#!/usr/bin/env python3
"""
Script Automatizado para Correções Críticas - Sistema Levitiis
Implementa as correções mais urgentes identificadas no QA
"""

import os
import sys
import subprocess
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any

class CriticalFixesImplementer:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_path = self.project_root / "backend"
        self.frontend_path = self.project_root / "frontend"
        self.fixes_applied = []
        self.errors = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_command(self, command: str, cwd: str = None) -> tuple:
        """Executar comando e retornar resultado"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timeout"
        except Exception as e:
            return False, "", str(e)
    
    def backup_file(self, file_path: Path) -> bool:
        """Criar backup de arquivo antes de modificar"""
        try:
            if file_path.exists():
                backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
                backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
                self.log(f"Backup criado: {backup_path}")
                return True
        except Exception as e:
            self.log(f"Erro ao criar backup de {file_path}: {e}", "ERROR")
            return False
        return True
    
    def fix_cors_configuration(self) -> bool:
        """Corrigir configuração CORS no backend"""
        self.log("🔧 Corrigindo configuração CORS...")
        
        main_py_path = self.backend_path / "main.py"
        if not main_py_path.exists():
            self.log("Arquivo main.py não encontrado", "ERROR")
            return False
        
        self.backup_file(main_py_path)
        
        try:
            content = main_py_path.read_text(encoding='utf-8')
            
            # Verificar se CORS já está configurado
            if "CORSMiddleware" in content:
                self.log("CORS já configurado, atualizando...")
                
                # Substituir configuração CORS existente
                cors_config = '''
# Configuração CORS corrigida
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://localhost:5173",  # Vite dev server
        "https://levitiis.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "X-Total-Count",
        "X-Page-Count",
    ],
    expose_headers=["X-Total-Count", "X-Page-Count"],
)
'''
                
                # Encontrar e substituir configuração CORS
                import re
                pattern = r'app\.add_middleware\(\s*CORSMiddleware.*?\)'
                content = re.sub(pattern, cors_config.strip(), content, flags=re.DOTALL)
                
            else:
                # Adicionar import e configuração CORS
                if "from fastapi.middleware.cors import CORSMiddleware" not in content:
                    # Adicionar import
                    import_line = "from fastapi.middleware.cors import CORSMiddleware\n"
                    content = content.replace("from fastapi import FastAPI", 
                                            f"from fastapi import FastAPI\n{import_line}")
                
                # Adicionar configuração após criação da app
                cors_config = '''
# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080", 
        "http://localhost:5173",  # Vite dev server
        "https://levitiis.com",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Authorization",
        "Content-Type", 
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "X-Total-Count",
        "X-Page-Count",
    ],
    expose_headers=["X-Total-Count", "X-Page-Count"],
)
'''
                
                # Inserir após a criação da app
                content = content.replace("app = FastAPI(", 
                                        f"app = FastAPI(\n{cors_config}")
            
            main_py_path.write_text(content, encoding='utf-8')
            self.log("✅ Configuração CORS corrigida")
            self.fixes_applied.append("CORS Configuration")
            return True
            
        except Exception as e:
            self.log(f"Erro ao corrigir CORS: {e}", "ERROR")
            self.errors.append(f"CORS: {e}")
            return False
    
    def fix_alerts_endpoints(self) -> bool:
        """Corrigir endpoints de alertas"""
        self.log("🔧 Corrigindo endpoints de alertas...")
        
        alerts_path = self.backend_path / "app" / "api" / "v1" / "endpoints" / "alerts.py"
        if not alerts_path.exists():
            self.log("Arquivo alerts.py não encontrado", "ERROR")
            return False
        
        self.backup_file(alerts_path)
        
        try:
            # Implementação básica dos endpoints faltantes
            alerts_fix = '''
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api import deps
from app.crud import crud_alert
from app.schemas.alert import AlertCreate, AlertUpdate, AlertResponse
from app.models.user import User

router = APIRouter()

@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    *,
    db: Session = Depends(deps.get_db),
    alert_in: AlertCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Criar novo alerta
    """
    try:
        alert = crud_alert.create(db=db, obj_in=alert_in, user_id=current_user.id)
        return alert
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao criar alerta: {str(e)}"
        )

@router.get("/", response_model=List[AlertResponse])
def read_alerts(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Listar alertas com filtros
    """
    try:
        filters = {}
        if severity:
            filters["severity"] = severity
        if status:
            filters["status"] = status
            
        alerts = crud_alert.get_multi_with_filters(
            db=db, skip=skip, limit=limit, filters=filters
        )
        return alerts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao buscar alertas: {str(e)}"
        )

@router.get("/{alert_id}", response_model=AlertResponse)
def read_alert(
    *,
    db: Session = Depends(deps.get_db),
    alert_id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Buscar alerta por ID
    """
    alert = crud_alert.get(db=db, id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta não encontrado"
        )
    return alert

@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(
    *,
    db: Session = Depends(deps.get_db),
    alert_id: int,
    alert_in: AlertUpdate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Atualizar alerta
    """
    alert = crud_alert.get(db=db, id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta não encontrado"
        )
    
    try:
        alert = crud_alert.update(db=db, db_obj=alert, obj_in=alert_in)
        return alert
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao atualizar alerta: {str(e)}"
        )

@router.delete("/{alert_id}")
def delete_alert(
    *,
    db: Session = Depends(deps.get_db),
    alert_id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Deletar alerta
    """
    alert = crud_alert.get(db=db, id=alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta não encontrado"
        )
    
    crud_alert.remove(db=db, id=alert_id)
    return {"message": "Alerta deletado com sucesso"}

@router.post("/send", response_model=AlertResponse)
def send_alert(
    *,
    db: Session = Depends(deps.get_db),
    alert_in: AlertCreate,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    Enviar alerta (compatibilidade com endpoint existente)
    """
    return create_alert(db=db, alert_in=alert_in, current_user=current_user)
'''
            
            alerts_path.write_text(alerts_fix, encoding='utf-8')
            self.log("✅ Endpoints de alertas corrigidos")
            self.fixes_applied.append("Alerts Endpoints")
            return True
            
        except Exception as e:
            self.log(f"Erro ao corrigir endpoints de alertas: {e}", "ERROR")
            self.errors.append(f"Alerts: {e}")
            return False
    
    def add_security_middleware(self) -> bool:
        """Adicionar middleware de segurança"""
        self.log("🔧 Adicionando middleware de segurança...")
        
        security_path = self.backend_path / "app" / "core" / "security.py"
        
        try:
            # Criar diretório se não existir
            security_path.parent.mkdir(parents=True, exist_ok=True)
            
            if security_path.exists():
                self.backup_file(security_path)
            
            security_middleware = '''
import re
import bleach
import hashlib
import time
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, rate_limit: int = 100):
        super().__init__(app)
        self.rate_limit = rate_limit
        self.request_counts: Dict[str, Dict[str, Any]] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Rate limiting
        client_ip = request.client.host
        current_time = time.time()
        
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {"count": 0, "window_start": current_time}
        
        client_data = self.request_counts[client_ip]
        
        # Reset window if needed (1 minute window)
        if current_time - client_data["window_start"] > 60:
            client_data["count"] = 0
            client_data["window_start"] = current_time
        
        client_data["count"] += 1
        
        if client_data["count"] > self.rate_limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Validação de segurança para dados de entrada
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode('utf-8')
                    if self._detect_malicious_content(body_str):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Malicious content detected"
                        )
            except UnicodeDecodeError:
                pass  # Binary data, skip validation
        
        response = await call_next(request)
        
        # Adicionar headers de segurança
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
    
    def _detect_malicious_content(self, content: str) -> bool:
        """Detectar conteúdo malicioso"""
        malicious_patterns = [
            r"'.*OR.*'.*=.*'",  # SQL Injection
            r"UNION.*SELECT",   # SQL Injection
            r"DROP.*TABLE",     # SQL Injection
            r"<script.*?>",     # XSS
            r"javascript:",     # XSS
            r"eval\(",          # Code injection
            r"exec\(",          # Code injection
        ]
        
        content_upper = content.upper()
        for pattern in malicious_patterns:
            if re.search(pattern, content_upper, re.IGNORECASE):
                return True
        
        return False

class InputSanitizer:
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitizar string contra XSS"""
        if not isinstance(value, str):
            return value
        
        # Remove tags HTML perigosos
        cleaned = bleach.clean(
            value,
            tags=[],  # Não permitir nenhuma tag
            attributes={},
            strip=True
        )
        
        return cleaned
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password_strength(password: str) -> bool:
        """Validar força da senha"""
        if len(password) < 8:
            return False
        
        # Deve ter pelo menos uma letra maiúscula, minúscula, número e símbolo
        patterns = [
            r'[A-Z]',  # Maiúscula
            r'[a-z]',  # Minúscula
            r'[0-9]',  # Número
            r'[!@#$%^&*(),.?":{}|<>]'  # Símbolo
        ]
        
        return all(re.search(pattern, password) for pattern in patterns)

def hash_password(password: str) -> str:
    """Hash seguro da senha"""
    salt = "levitiis_salt_2024"  # Em produção, usar salt aleatório
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()

def verify_password(password: str, hashed: str) -> bool:
    """Verificar senha"""
    return hash_password(password) == hashed
'''
            
            security_path.write_text(security_middleware, encoding='utf-8')
            self.log("✅ Middleware de segurança adicionado")
            self.fixes_applied.append("Security Middleware")
            return True
            
        except Exception as e:
            self.log(f"Erro ao adicionar middleware de segurança: {e}", "ERROR")
            self.errors.append(f"Security: {e}")
            return False
    
    def optimize_database_queries(self) -> bool:
        """Otimizar queries do banco de dados"""
        self.log("🔧 Otimizando queries do banco de dados...")
        
        try:
            # Criar arquivo de otimizações SQL
            sql_optimizations = self.backend_path / "database_optimizations.sql"
            
            sql_content = '''
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
'''
            
            sql_optimizations.write_text(sql_content, encoding='utf-8')
            self.log("✅ Script de otimização do banco criado")
            self.fixes_applied.append("Database Optimizations")
            return True
            
        except Exception as e:
            self.log(f"Erro ao criar otimizações do banco: {e}", "ERROR")
            self.errors.append(f"Database: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Instalar dependências necessárias"""
        self.log("🔧 Instalando dependências necessárias...")
        
        try:
            # Dependências Python para o backend
            requirements_additions = [
                "redis>=4.5.0",
                "bleach>=6.0.0",
                "python-multipart>=0.0.6",
                "aiofiles>=23.0.0",
            ]
            
            requirements_path = self.backend_path / "requirements.txt"
            
            if requirements_path.exists():
                current_requirements = requirements_path.read_text(encoding='utf-8')
                
                for dep in requirements_additions:
                    dep_name = dep.split('>=')[0]
                    if dep_name not in current_requirements:
                        current_requirements += f"\n{dep}"
                
                requirements_path.write_text(current_requirements, encoding='utf-8')
            else:
                requirements_path.write_text('\n'.join(requirements_additions), encoding='utf-8')
            
            # Instalar dependências
            success, stdout, stderr = self.run_command(
                "pip install -r requirements.txt",
                cwd=str(self.backend_path)
            )
            
            if success:
                self.log("✅ Dependências instaladas com sucesso")
                self.fixes_applied.append("Dependencies Installation")
                return True
            else:
                self.log(f"Erro ao instalar dependências: {stderr}", "ERROR")
                self.errors.append(f"Dependencies: {stderr}")
                return False
                
        except Exception as e:
            self.log(f"Erro ao instalar dependências: {e}", "ERROR")
            self.errors.append(f"Dependencies: {e}")
            return False
    
    def test_fixes(self) -> Dict[str, bool]:
        """Testar se as correções funcionaram"""
        self.log("🧪 Testando correções aplicadas...")
        
        results = {}
        
        # Testar se o servidor está rodando
        try:
            response = requests.get("http://localhost:8000/docs", timeout=5)
            results["server_running"] = response.status_code == 200
        except:
            results["server_running"] = False
        
        # Testar CORS
        try:
            response = requests.options(
                "http://localhost:8000/api/v1/users/",
                headers={"Origin": "http://localhost:3000"},
                timeout=5
            )
            results["cors_working"] = "access-control-allow-origin" in response.headers
        except:
            results["cors_working"] = False
        
        # Testar endpoints de alertas
        try:
            response = requests.get("http://localhost:8000/api/v1/alerts/", timeout=5)
            results["alerts_endpoint"] = response.status_code in [200, 401]  # 401 é OK (não autenticado)
        except:
            results["alerts_endpoint"] = False
        
        return results
    
    def generate_report(self) -> str:
        """Gerar relatório das correções aplicadas"""
        report = f"""
# Relatório de Correções Críticas - Sistema Levitiis
Data: {time.strftime('%Y-%m-%d %H:%M:%S')}

## ✅ Correções Aplicadas ({len(self.fixes_applied)})
"""
        
        for fix in self.fixes_applied:
            report += f"- {fix}\n"
        
        if self.errors:
            report += f"\n## ❌ Erros Encontrados ({len(self.errors)})\n"
            for error in self.errors:
                report += f"- {error}\n"
        
        # Testar correções
        test_results = self.test_fixes()
        report += f"\n## 🧪 Resultados dos Testes\n"
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            report += f"- {test_name}: {status}\n"
        
        success_rate = (len(self.fixes_applied) / (len(self.fixes_applied) + len(self.errors))) * 100 if (len(self.fixes_applied) + len(self.errors)) > 0 else 0
        
        report += f"\n## 📊 Resumo\n"
        report += f"- Taxa de Sucesso: {success_rate:.1f}%\n"
        report += f"- Correções Aplicadas: {len(self.fixes_applied)}\n"
        report += f"- Erros: {len(self.errors)}\n"
        
        report += f"\n## 🚀 Próximos Passos\n"
        report += "1. Reiniciar o servidor backend\n"
        report += "2. Executar testes de integração\n"
        report += "3. Validar funcionamento do frontend\n"
        report += "4. Aplicar otimizações do banco de dados\n"
        report += "5. Configurar monitoramento\n"
        
        return report
    
    def run_all_fixes(self) -> bool:
        """Executar todas as correções"""
        self.log("🚀 Iniciando aplicação de correções críticas...")
        
        fixes = [
            ("Configuração CORS", self.fix_cors_configuration),
            ("Endpoints de Alertas", self.fix_alerts_endpoints),
            ("Middleware de Segurança", self.add_security_middleware),
            ("Otimizações do Banco", self.optimize_database_queries),
            ("Dependências", self.install_dependencies),
        ]
        
        success_count = 0
        
        for fix_name, fix_function in fixes:
            self.log(f"Aplicando: {fix_name}")
            try:
                if fix_function():
                    success_count += 1
                    self.log(f"✅ {fix_name} aplicado com sucesso")
                else:
                    self.log(f"❌ Falha ao aplicar {fix_name}", "ERROR")
            except Exception as e:
                self.log(f"❌ Erro inesperado em {fix_name}: {e}", "ERROR")
                self.errors.append(f"{fix_name}: {e}")
        
        # Gerar relatório
        report = self.generate_report()
        report_path = self.project_root / "RELATORIO_CORRECOES_APLICADAS.md"
        report_path.write_text(report, encoding='utf-8')
        
        self.log(f"📄 Relatório salvo em: {report_path}")
        self.log(f"🎯 Correções aplicadas: {success_count}/{len(fixes)}")
        
        return success_count == len(fixes)

def main():
    """Função principal"""
    if len(sys.argv) != 2:
        print("Uso: python fix_critical_issues.py <caminho_do_projeto>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    
    if not os.path.exists(project_path):
        print(f"Erro: Caminho do projeto não existe: {project_path}")
        sys.exit(1)
    
    fixer = CriticalFixesImplementer(project_path)
    
    print("=" * 60)
    print("🔧 SISTEMA DE CORREÇÕES CRÍTICAS - LEVITIIS")
    print("=" * 60)
    
    success = fixer.run_all_fixes()
    
    print("=" * 60)
    if success:
        print("✅ TODAS AS CORREÇÕES APLICADAS COM SUCESSO!")
        print("🚀 Reinicie o servidor para aplicar as mudanças.")
    else:
        print("⚠️  ALGUMAS CORREÇÕES FALHARAM!")
        print("📄 Verifique o relatório para detalhes.")
    print("=" * 60)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())