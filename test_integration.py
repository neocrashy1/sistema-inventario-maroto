#!/usr/bin/env python3
"""
Script de Teste de Integração Frontend/Backend - Sistema Levitiis
Testa a comunicação entre Vue.js frontend e FastAPI backend
"""

import requests
import json
import time
import sys
from datetime import datetime

class IntegrationTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, status, details=""):
        """Registra resultado de um teste"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   {details}")
    
    def test_backend_health(self):
        """Testa se o backend está respondendo"""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_test("Backend Health Check", "PASS", f"Version: {data.get('version')}")
                    return True
                else:
                    self.log_test("Backend Health Check", "FAIL", "Status not healthy")
                    return False
            else:
                self.log_test("Backend Health Check", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", "FAIL", str(e))
            return False
    
    def test_frontend_availability(self):
        """Testa se o frontend está disponível"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                if '<div id="app"></div>' in response.text:
                    self.log_test("Frontend Availability", "PASS", "Vue.js app container found")
                    return True
                else:
                    self.log_test("Frontend Availability", "FAIL", "App container not found")
                    return False
            else:
                self.log_test("Frontend Availability", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Availability", "FAIL", str(e))
            return False
    
    def test_authentication(self):
        """Testa autenticação JWT"""
        try:
            # Dados de login
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            # Fazer login
            response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                data=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.token = data["access_token"]
                    self.log_test("Authentication", "PASS", f"Token received for user: {data.get('username')}")
                    return True
                else:
                    self.log_test("Authentication", "FAIL", "No access token in response")
                    return False
            else:
                self.log_test("Authentication", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Authentication", "FAIL", str(e))
            return False
    
    def test_api_endpoints(self):
        """Testa endpoints principais da API"""
        if not self.token:
            self.log_test("API Endpoints", "SKIP", "No authentication token")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        endpoints = [
            ("/api/v1/users/", "Users"),
            ("/api/v1/assets/", "Assets"),
            ("/api/v1/tickets/", "Tickets"),
            ("/api/v1/alerts/", "Alerts"),
            ("/api/v1/dashboard/stats", "Dashboard Stats"),
            ("/api/v1/dashboard/metrics", "Dashboard Metrics")
        ]
        
        all_passed = True
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", headers=headers, timeout=10)
                if response.status_code == 200:
                    self.log_test(f"API - {name}", "PASS", f"Response size: {len(response.content)} bytes")
                else:
                    self.log_test(f"API - {name}", "FAIL", f"HTTP {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"API - {name}", "FAIL", str(e))
                all_passed = False
        
        return all_passed
    
    def test_cors_headers(self):
        """Testa configuração CORS"""
        try:
            response = requests.options(f"{self.backend_url}/api/v1/auth/login")
            cors_headers = [
                "Access-Control-Allow-Origin",
                "Access-Control-Allow-Methods",
                "Access-Control-Allow-Headers"
            ]
            
            found_headers = []
            for header in cors_headers:
                if header in response.headers:
                    found_headers.append(header)
            
            if len(found_headers) >= 2:
                self.log_test("CORS Configuration", "PASS", f"Found headers: {', '.join(found_headers)}")
                return True
            else:
                self.log_test("CORS Configuration", "FAIL", f"Missing CORS headers")
                return False
        except Exception as e:
            self.log_test("CORS Configuration", "FAIL", str(e))
            return False
    
    def test_security_headers(self):
        """Testa headers de segurança"""
        try:
            response = requests.get(f"{self.backend_url}/health")
            security_headers = [
                "X-Content-Type-Options",
                "X-Frame-Options", 
                "X-XSS-Protection",
                "Referrer-Policy"
            ]
            
            found_headers = []
            for header in security_headers:
                if header in response.headers:
                    found_headers.append(header)
            
            if len(found_headers) >= 3:
                self.log_test("Security Headers", "PASS", f"Found: {', '.join(found_headers)}")
                return True
            else:
                self.log_test("Security Headers", "WARN", f"Only found: {', '.join(found_headers)}")
                return False
        except Exception as e:
            self.log_test("Security Headers", "FAIL", str(e))
            return False
    
    def test_rate_limiting(self):
        """Testa rate limiting"""
        try:
            # Fazer várias requisições rápidas
            responses = []
            for i in range(5):
                response = requests.get(f"{self.backend_url}/health")
                responses.append(response)
            
            # Verificar headers de rate limiting
            last_response = responses[-1]
            if "x-ratelimit-limit" in last_response.headers:
                limit = last_response.headers.get("x-ratelimit-limit")
                remaining = last_response.headers.get("x-ratelimit-remaining")
                self.log_test("Rate Limiting", "PASS", f"Limit: {limit}, Remaining: {remaining}")
                return True
            else:
                self.log_test("Rate Limiting", "FAIL", "No rate limiting headers found")
                return False
        except Exception as e:
            self.log_test("Rate Limiting", "FAIL", str(e))
            return False
    
    def run_all_tests(self):
        """Executa todos os testes"""
        print("🚀 Iniciando Testes de Integração Frontend/Backend")
        print("=" * 60)
        
        # Testes básicos de conectividade
        backend_ok = self.test_backend_health()
        frontend_ok = self.test_frontend_availability()
        
        if not backend_ok:
            print("\n❌ Backend não está funcionando. Abortando testes.")
            return False
        
        if not frontend_ok:
            print("\n⚠️ Frontend com problemas, mas continuando testes de API.")
        
        # Testes de autenticação e API
        auth_ok = self.test_authentication()
        if auth_ok:
            self.test_api_endpoints()
        
        # Testes de segurança
        self.test_cors_headers()
        self.test_security_headers()
        self.test_rate_limiting()
        
        # Resumo dos resultados
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        warnings = len([r for r in self.test_results if r["status"] == "WARN"])
        skipped = len([r for r in self.test_results if r["status"] == "SKIP"])
        total = len(self.test_results)
        
        print(f"✅ Passou: {passed}")
        print(f"❌ Falhou: {failed}")
        print(f"⚠️ Avisos: {warnings}")
        print(f"⏭️ Pulados: {skipped}")
        print(f"📈 Total: {total}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Taxa de Sucesso: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 TODOS OS TESTES CRÍTICOS PASSARAM!")
        else:
            print(f"\n⚠️ {failed} TESTE(S) FALHARAM - REVISAR NECESSÁRIO")
        
        # Salvar resultados em arquivo
        with open("integration_test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Resultados salvos em: integration_test_results.json")

def main():
    """Função principal"""
    tester = IntegrationTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️ Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Erro inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()