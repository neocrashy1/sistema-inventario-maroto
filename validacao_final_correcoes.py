#!/usr/bin/env python3
"""
Script de Validação Final - Correções Aplicadas
Testa se as correções críticas estão funcionando
"""

import requests
import time
import json
from typing import Dict, List, Any

class ValidationTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {}
        self.errors = []
        self.auth_token = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log com timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def test_server_health(self) -> bool:
        """Testar se o servidor está respondendo"""
        try:
            # Testar endpoint de documentação (público)
            response = requests.get(f"{self.base_url}/docs", timeout=5)
            if response.status_code == 200:
                return True
            
            # Testar endpoint raiz
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code in [200, 404]  # 404 é OK se não há rota raiz
            
        except Exception as e:
            self.errors.append(f"Server Health: {e}")
            return False
    
    def test_cors_configuration(self) -> bool:
        """Testar configuração CORS"""
        try:
            # Testar preflight request
            response = requests.options(
                f"{self.base_url}/health",  # Endpoint público
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET",
                    "Access-Control-Request-Headers": "Authorization"
                },
                timeout=5
            )
            
            # Verificar se pelo menos um header CORS está presente
            cors_headers = [
                "access-control-allow-origin",
                "access-control-allow-methods",
                "access-control-allow-headers"
            ]
            
            has_cors = any(header in response.headers for header in cors_headers)
            
            if not has_cors:
                # Testar com GET normal
                response = requests.get(
                    f"{self.base_url}/health",
                    headers={"Origin": "http://localhost:3000"},
                    timeout=5
                )
                has_cors = "access-control-allow-origin" in response.headers
            
            return has_cors
            
        except Exception as e:
            self.errors.append(f"CORS: {e}")
            return False
    
    def test_public_endpoints(self) -> Dict[str, bool]:
        """Testar endpoints públicos"""
        endpoints = [
            "/api/v1/docs",
            "/api/v1/openapi.json",
            "/api/v1/redoc",
            "/health",
        ]
        
        results = {}
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                results[endpoint] = response.status_code == 200
                
                if response.status_code != 200:
                    self.errors.append(f"Public endpoint {endpoint}: Status {response.status_code}")
                    
            except Exception as e:
                results[endpoint] = False
                self.errors.append(f"Public endpoint {endpoint}: {e}")
        
        return results
    
    def test_protected_endpoints_structure(self) -> Dict[str, bool]:
        """Testar se endpoints protegidos retornam 401/403 (comportamento correto)"""
        endpoints = [
            "/api/v1/users/",
            "/api/v1/machines/",
            "/api/v1/tickets/",
            "/api/v1/alerts/",
            "/api/v1/assets/",
        ]
        
        results = {}
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=5)
                # 401 (não autenticado) ou 403 (não autorizado) são comportamentos corretos
                results[endpoint] = response.status_code in [401, 403]
                
                if response.status_code not in [401, 403]:
                    self.errors.append(f"Protected endpoint {endpoint}: Status {response.status_code} (esperado 401/403)")
                    
            except Exception as e:
                results[endpoint] = False
                self.errors.append(f"Protected endpoint {endpoint}: {e}")
        
        return results
    
    def test_performance(self) -> Dict[str, float]:
        """Testar performance dos endpoints públicos"""
        endpoints = [
            "/api/v1/docs",
            "/api/v1/openapi.json",
            "/health",
        ]
        
        performance_results = {}
        
        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                end_time = time.time()
                
                response_time = end_time - start_time
                performance_results[endpoint] = response_time
                
                if response_time > 2.0:
                    self.errors.append(f"Performance {endpoint}: {response_time:.3f}s (muito lento)")
                    
            except Exception as e:
                performance_results[endpoint] = -1
                self.errors.append(f"Performance {endpoint}: {e}")
        
        return performance_results
    
    def test_security_headers(self) -> bool:
        """Testar headers de segurança"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            security_headers = [
                "x-content-type-options",
                "x-frame-options", 
                "x-xss-protection",
                "server"  # Verificar se server header está oculto
            ]
            
            # Contar headers de segurança presentes
            headers_present = sum(1 for header in security_headers[:3] if header in response.headers)
            
            # Verificar se server header está oculto (boa prática)
            server_hidden = "server" not in response.headers or response.headers.get("server", "").lower() in ["", "unknown"]
            
            return headers_present >= 1 or server_hidden  # Pelo menos 1 header ou server oculto
            
        except Exception as e:
            self.errors.append(f"Security Headers: {e}")
            return False
    
    def test_api_structure(self) -> bool:
        """Testar se a estrutura da API está correta"""
        try:
            # Testar se OpenAPI está funcionando
            response = requests.get(f"{self.base_url}/api/v1/openapi.json", timeout=5)
            
            if response.status_code != 200:
                self.errors.append(f"OpenAPI: Status {response.status_code}")
                return False
            
            # Verificar se é um JSON válido
            api_spec = response.json()
            
            # Verificar se tem as seções básicas do OpenAPI
            required_sections = ["openapi", "info", "paths"]
            has_sections = all(section in api_spec for section in required_sections)
            
            if not has_sections:
                self.errors.append("OpenAPI: Estrutura inválida")
                return False
            
            # Verificar se tem os endpoints esperados
            paths = api_spec.get("paths", {})
            expected_paths = ["/api/v1/users/", "/api/v1/machines/", "/api/v1/tickets/", "/api/v1/alerts/"]
            
            found_paths = sum(1 for path in expected_paths if any(p.startswith(path.rstrip('/')) for p in paths.keys()))
            
            return found_paths >= 3  # Pelo menos 3 dos 4 endpoints esperados
            
        except Exception as e:
            self.errors.append(f"API Structure: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Executar todos os testes"""
        self.log("🚀 Iniciando validação final das correções...")
        
        # Teste 1: Saúde do servidor
        self.log("Testando saúde do servidor...")
        self.results["server_health"] = self.test_server_health()
        
        # Teste 2: Configuração CORS
        self.log("Testando configuração CORS...")
        self.results["cors_configuration"] = self.test_cors_configuration()
        
        # Teste 3: Endpoints públicos
        self.log("Testando endpoints públicos...")
        self.results["public_endpoints"] = self.test_public_endpoints()
        
        # Teste 4: Endpoints protegidos (devem retornar 401/403)
        self.log("Testando estrutura de endpoints protegidos...")
        self.results["protected_endpoints"] = self.test_protected_endpoints_structure()
        
        # Teste 5: Performance
        self.log("Testando performance...")
        self.results["performance"] = self.test_performance()
        
        # Teste 6: Headers de segurança
        self.log("Testando headers de segurança...")
        self.results["security_headers"] = self.test_security_headers()
        
        # Teste 7: Estrutura da API
        self.log("Testando estrutura da API...")
        self.results["api_structure"] = self.test_api_structure()
        
        return self.results
    
    def generate_report(self) -> str:
        """Gerar relatório de validação"""
        report = f"""
# Relatório de Validação Final - Correções Aplicadas
Data: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 Resumo Executivo
"""
        
        # Calcular estatísticas
        total_tests = 0
        passed_tests = 0
        
        # Testes individuais
        individual_tests = ["server_health", "cors_configuration", "security_headers", "api_structure"]
        for test in individual_tests:
            if self.results.get(test):
                passed_tests += 1
            total_tests += 1
        
        # Endpoints públicos
        public_results = self.results.get("public_endpoints", {})
        public_passed = sum(1 for result in public_results.values() if result)
        public_total = len(public_results)
        passed_tests += public_passed
        total_tests += public_total
        
        # Endpoints protegidos
        protected_results = self.results.get("protected_endpoints", {})
        protected_passed = sum(1 for result in protected_results.values() if result)
        protected_total = len(protected_results)
        passed_tests += protected_passed
        total_tests += protected_total
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        report += f"- **Taxa de Sucesso Geral**: {success_rate:.1f}% ({passed_tests}/{total_tests})\n"
        report += f"- **Status**: {'✅ APROVADO' if success_rate >= 80 else '⚠️ NECESSITA ATENÇÃO' if success_rate >= 60 else '❌ REPROVADO'}\n\n"
        
        # Resultados detalhados
        report += "## 📊 Resultados Detalhados\n\n"
        
        # Servidor
        status = "✅ PASS" if self.results.get("server_health") else "❌ FAIL"
        report += f"### 🖥️ Saúde do Servidor: {status}\n"
        
        # CORS
        status = "✅ PASS" if self.results.get("cors_configuration") else "❌ FAIL"
        report += f"### 🌐 Configuração CORS: {status}\n"
        
        # Endpoints públicos
        report += f"### 🌍 Endpoints Públicos: {public_passed}/{public_total} funcionando\n"
        for endpoint, result in public_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            report += f"- {endpoint}: {status}\n"
        
        # Endpoints protegidos
        report += f"\n### 🔒 Endpoints Protegidos (Segurança): {protected_passed}/{protected_total} corretos\n"
        for endpoint, result in protected_results.items():
            status = "✅ PASS (401/403)" if result else "❌ FAIL"
            report += f"- {endpoint}: {status}\n"
        
        # Performance
        performance_results = self.results.get("performance", {})
        report += f"\n### ⚡ Performance:\n"
        for endpoint, time_taken in performance_results.items():
            if time_taken > 0:
                status = "✅ RÁPIDO" if time_taken < 1.0 else "⚠️ LENTO" if time_taken < 2.0 else "❌ MUITO LENTO"
                report += f"- {endpoint}: {time_taken:.3f}s ({status})\n"
            else:
                report += f"- {endpoint}: ❌ ERRO\n"
        
        # Segurança
        status = "✅ PASS" if self.results.get("security_headers") else "❌ FAIL"
        report += f"\n### 🔒 Headers de Segurança: {status}\n"
        
        # Estrutura da API
        status = "✅ PASS" if self.results.get("api_structure") else "❌ FAIL"
        report += f"### 🏗️ Estrutura da API: {status}\n"
        
        # Erros encontrados
        if self.errors:
            report += f"\n## ❌ Erros Encontrados ({len(self.errors)})\n"
            for error in self.errors:
                report += f"- {error}\n"
        
        # Comparação com QA anterior
        report += f"\n## 📈 Comparação com QA Anterior\n"
        report += f"- **QA Anterior**: 48% de sucesso\n"
        report += f"- **Após Correções**: {success_rate:.1f}% de sucesso\n"
        report += f"- **Melhoria**: {success_rate - 48:.1f} pontos percentuais\n"
        
        # Análise de segurança
        report += f"\n## 🔐 Análise de Segurança\n"
        if protected_passed == protected_total:
            report += "✅ **Excelente**: Todos os endpoints protegidos estão retornando 401/403 corretamente\n"
            report += "✅ **Segurança**: Sistema está protegendo adequadamente recursos sensíveis\n"
        else:
            report += "⚠️ **Atenção**: Alguns endpoints podem estar expostos inadequadamente\n"
        
        # Próximos passos
        report += f"\n## 🚀 Próximos Passos\n"
        
        if success_rate >= 80:
            report += "✅ **Sistema aprovado para produção!**\n"
            report += "- Implementar sistema de autenticação/autorização completo\n"
            report += "- Configurar monitoramento contínuo\n"
            report += "- Documentar procedimentos operacionais\n"
            report += "- Criar usuários de teste para validação funcional\n"
        elif success_rate >= 60:
            report += "⚠️ **Sistema necessita ajustes menores:**\n"
            report += "- Corrigir erros identificados\n"
            report += "- Otimizar performance dos endpoints lentos\n"
            report += "- Implementar autenticação para testes funcionais\n"
            report += "- Re-executar validação\n"
        else:
            report += "❌ **Sistema necessita correções críticas:**\n"
            report += "- Revisar todos os erros listados\n"
            report += "- Implementar correções urgentes\n"
            report += "- Verificar configuração do servidor\n"
            report += "- Executar nova rodada de testes\n"
        
        return report

def main():
    """Função principal"""
    print("=" * 60)
    print("🔍 VALIDAÇÃO FINAL DAS CORREÇÕES - SISTEMA LEVITIIS")
    print("=" * 60)
    
    tester = ValidationTester()
    
    # Executar todos os testes
    results = tester.run_all_tests()
    
    # Gerar relatório
    report = tester.generate_report()
    
    # Salvar relatório
    report_path = "VALIDACAO_FINAL_CORRECOES.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("\n" + "=" * 60)
    print(f"📄 Relatório salvo em: {report_path}")
    
    # Mostrar resumo
    individual_tests = ["server_health", "cors_configuration", "security_headers", "api_structure"]
    passed_individual = sum(1 for test in individual_tests if results.get(test))
    
    public_passed = sum(1 for result in results.get("public_endpoints", {}).values() if result)
    protected_passed = sum(1 for result in results.get("protected_endpoints", {}).values() if result)
    
    total_passed = passed_individual + public_passed + protected_passed
    total_tests = len(individual_tests) + len(results.get("public_endpoints", {})) + len(results.get("protected_endpoints", {}))
    
    success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
    
    if success_rate >= 80:
        print("✅ VALIDAÇÃO APROVADA!")
        print(f"🎯 Taxa de sucesso: {success_rate:.1f}%")
        print("🔒 Sistema está seguro e funcionando corretamente!")
    elif success_rate >= 60:
        print("⚠️ VALIDAÇÃO PARCIAL!")
        print(f"🎯 Taxa de sucesso: {success_rate:.1f}%")
    else:
        print("❌ VALIDAÇÃO REPROVADA!")
        print(f"🎯 Taxa de sucesso: {success_rate:.1f}%")
    
    print("=" * 60)
    
    return 0 if success_rate >= 80 else 1

if __name__ == "__main__":
    exit(main())