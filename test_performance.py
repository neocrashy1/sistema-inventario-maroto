#!/usr/bin/env python3
"""
Script de Teste de Performance - Sistema Levitiis
Testa performance, carga e tempo de resposta do sistema
"""

import requests
import json
import time
import statistics
import threading
from datetime import datetime
import sys

class PerformanceTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.token = None
        self.test_results = []
        
    def log_test(self, test_name, status, details="", metrics=None):
        """Registra resultado de um teste"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "metrics": metrics or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   {details}")
        if metrics:
            for key, value in metrics.items():
                print(f"   📊 {key}: {value}")
    
    def authenticate(self):
        """Autentica no sistema"""
        try:
            login_data = {
                "username": "admin",
                "password": "admin123"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/auth/login",
                data=login_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                return True
            return False
        except Exception:
            return False
    
    def get_headers(self):
        """Retorna headers com autenticação"""
        return {"Authorization": f"Bearer {self.token}"}
    
    def test_response_times(self):
        """Testa tempos de resposta dos endpoints principais"""
        endpoints = [
            {"url": "/health", "name": "Health Check", "auth": False},
            {"url": "/api/v1/users/", "name": "Users API", "auth": True},
            {"url": "/api/v1/machines/", "name": "Machines API", "auth": True},
            {"url": "/api/v1/tickets/", "name": "Tickets API", "auth": True},
            {"url": "/api/v1/dashboard/stats", "name": "Dashboard Stats", "auth": True},
        ]
        
        for endpoint in endpoints:
            try:
                headers = self.get_headers() if endpoint["auth"] and self.token else {}
                
                # Fazer 10 requisições para cada endpoint
                response_times = []
                for _ in range(10):
                    start_time = time.time()
                    response = requests.get(
                        f"{self.backend_url}{endpoint['url']}",
                        headers=headers,
                        timeout=10
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        response_times.append(end_time - start_time)
                
                if response_times:
                    avg_time = statistics.mean(response_times)
                    min_time = min(response_times)
                    max_time = max(response_times)
                    
                    metrics = {
                        "avg_response_time": f"{avg_time:.3f}s",
                        "min_response_time": f"{min_time:.3f}s",
                        "max_response_time": f"{max_time:.3f}s",
                        "requests_tested": len(response_times)
                    }
                    
                    if avg_time < 1.0:  # Menos de 1 segundo
                        self.log_test(f"Response Time - {endpoint['name']}", "PASS", 
                                    f"Average: {avg_time:.3f}s", metrics)
                    elif avg_time < 3.0:  # Menos de 3 segundos
                        self.log_test(f"Response Time - {endpoint['name']}", "WARN", 
                                    f"Slow response: {avg_time:.3f}s", metrics)
                    else:
                        self.log_test(f"Response Time - {endpoint['name']}", "FAIL", 
                                    f"Very slow: {avg_time:.3f}s", metrics)
                else:
                    self.log_test(f"Response Time - {endpoint['name']}", "FAIL", 
                                "No successful responses")
                    
            except Exception as e:
                self.log_test(f"Response Time - {endpoint['name']}", "FAIL", str(e))
    
    def test_concurrent_load(self):
        """Testa carga com requisições concorrentes"""
        if not self.token:
            self.log_test("Concurrent Load Test", "SKIP", "No authentication token")
            return
        
        def make_requests(thread_id, num_requests, results_list):
            """Função para fazer requisições em thread"""
            headers = self.get_headers()
            thread_results = []
            
            for i in range(num_requests):
                try:
                    start_time = time.time()
                    response = requests.get(
                        f"{self.backend_url}/api/v1/users/",
                        headers=headers,
                        timeout=10
                    )
                    end_time = time.time()
                    
                    thread_results.append({
                        "thread_id": thread_id,
                        "request_id": i,
                        "status_code": response.status_code,
                        "response_time": end_time - start_time,
                        "success": response.status_code == 200
                    })
                    
                except Exception as e:
                    thread_results.append({
                        "thread_id": thread_id,
                        "request_id": i,
                        "status_code": 0,
                        "response_time": 0,
                        "success": False,
                        "error": str(e)
                    })
            
            results_list.extend(thread_results)
        
        # Configuração do teste
        num_threads = 5
        requests_per_thread = 10
        total_requests = num_threads * requests_per_thread
        
        print(f"   🚀 Iniciando teste de carga: {num_threads} threads x {requests_per_thread} requests")
        
        # Executar teste
        threads = []
        all_results = []
        
        start_time = time.time()
        
        for i in range(num_threads):
            thread = threading.Thread(
                target=make_requests, 
                args=(i, requests_per_thread, all_results)
            )
            threads.append(thread)
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analisar resultados
        successful_requests = len([r for r in all_results if r["success"]])
        failed_requests = total_requests - successful_requests
        
        if all_results:
            response_times = [r["response_time"] for r in all_results if r["success"]]
            if response_times:
                avg_response_time = statistics.mean(response_times)
                max_response_time = max(response_times)
                min_response_time = min(response_times)
            else:
                avg_response_time = max_response_time = min_response_time = 0
        else:
            avg_response_time = max_response_time = min_response_time = 0
        
        requests_per_second = total_requests / total_time if total_time > 0 else 0
        success_rate = (successful_requests / total_requests) * 100
        
        metrics = {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "success_rate": f"{success_rate:.1f}%",
            "total_time": f"{total_time:.2f}s",
            "requests_per_second": f"{requests_per_second:.2f}",
            "avg_response_time": f"{avg_response_time:.3f}s",
            "min_response_time": f"{min_response_time:.3f}s",
            "max_response_time": f"{max_response_time:.3f}s"
        }
        
        if success_rate >= 95 and avg_response_time < 2.0:
            self.log_test("Concurrent Load Test", "PASS", 
                        f"{successful_requests}/{total_requests} requests successful", metrics)
        elif success_rate >= 80:
            self.log_test("Concurrent Load Test", "WARN", 
                        f"Moderate performance: {success_rate:.1f}% success rate", metrics)
        else:
            self.log_test("Concurrent Load Test", "FAIL", 
                        f"Poor performance: {success_rate:.1f}% success rate", metrics)
    
    def test_memory_leak(self):
        """Testa vazamentos de memória com requisições repetidas"""
        if not self.token:
            self.log_test("Memory Leak Test", "SKIP", "No authentication token")
            return
        
        headers = self.get_headers()
        response_times = []
        memory_indicators = []
        
        print("   🧠 Testando vazamentos de memória (100 requisições)...")
        
        for i in range(100):
            try:
                start_time = time.time()
                response = requests.get(
                    f"{self.backend_url}/api/v1/users/",
                    headers=headers,
                    timeout=5
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    response_time = end_time - start_time
                    response_times.append(response_time)
                    
                    # Usar tamanho da resposta como indicador de memória
                    memory_indicators.append(len(response.content))
                
                # Pequena pausa para não sobrecarregar
                if i % 10 == 0:
                    time.sleep(0.1)
                    
            except Exception:
                break
        
        if len(response_times) >= 80:  # 80% de sucesso
            # Analisar tendências
            first_20 = response_times[:20]
            last_20 = response_times[-20:]
            
            avg_first = statistics.mean(first_20)
            avg_last = statistics.mean(last_20)
            
            performance_degradation = (avg_last / avg_first - 1) * 100
            
            metrics = {
                "total_requests": len(response_times),
                "avg_first_20": f"{avg_first:.3f}s",
                "avg_last_20": f"{avg_last:.3f}s",
                "performance_change": f"{performance_degradation:+.1f}%"
            }
            
            if performance_degradation < 20:  # Menos de 20% de degradação
                self.log_test("Memory Leak Test", "PASS", 
                            f"Stable performance over {len(response_times)} requests", metrics)
            elif performance_degradation < 50:
                self.log_test("Memory Leak Test", "WARN", 
                            f"Moderate degradation: {performance_degradation:.1f}%", metrics)
            else:
                self.log_test("Memory Leak Test", "FAIL", 
                            f"Significant degradation: {performance_degradation:.1f}%", metrics)
        else:
            self.log_test("Memory Leak Test", "FAIL", 
                        f"Only completed {len(response_times)}/100 requests")
    
    def test_frontend_performance(self):
        """Testa performance do frontend"""
        try:
            # Testar carregamento da página principal
            start_time = time.time()
            response = requests.get(self.frontend_url, timeout=10)
            end_time = time.time()
            
            load_time = end_time - start_time
            page_size = len(response.content)
            
            metrics = {
                "load_time": f"{load_time:.3f}s",
                "page_size": f"{page_size} bytes",
                "status_code": response.status_code
            }
            
            if response.status_code == 200:
                if load_time < 2.0:  # Menos de 2 segundos
                    self.log_test("Frontend Performance", "PASS", 
                                f"Page loaded in {load_time:.3f}s", metrics)
                elif load_time < 5.0:
                    self.log_test("Frontend Performance", "WARN", 
                                f"Slow loading: {load_time:.3f}s", metrics)
                else:
                    self.log_test("Frontend Performance", "FAIL", 
                                f"Very slow loading: {load_time:.3f}s", metrics)
            else:
                self.log_test("Frontend Performance", "FAIL", 
                            f"HTTP {response.status_code}", metrics)
                
        except Exception as e:
            self.log_test("Frontend Performance", "FAIL", str(e))
    
    def test_database_performance(self):
        """Testa performance de operações de banco de dados"""
        if not self.token:
            self.log_test("Database Performance", "SKIP", "No authentication token")
            return
        
        headers = self.get_headers()
        
        # Testar diferentes tipos de consulta
        db_tests = [
            {"endpoint": "/api/v1/users/", "name": "Users Query"},
            {"endpoint": "/api/v1/machines/", "name": "Machines Query"},
            {"endpoint": "/api/v1/tickets/", "name": "Tickets Query"},
            {"endpoint": "/api/v1/dashboard/stats", "name": "Dashboard Stats"},
        ]
        
        for test in db_tests:
            try:
                # Fazer 5 requisições para cada endpoint
                response_times = []
                
                for _ in range(5):
                    start_time = time.time()
                    response = requests.get(
                        f"{self.backend_url}{test['endpoint']}",
                        headers=headers,
                        timeout=10
                    )
                    end_time = time.time()
                    
                    if response.status_code == 200:
                        response_times.append(end_time - start_time)
                
                if response_times:
                    avg_time = statistics.mean(response_times)
                    
                    metrics = {
                        "avg_query_time": f"{avg_time:.3f}s",
                        "queries_tested": len(response_times)
                    }
                    
                    if avg_time < 0.5:  # Menos de 500ms
                        self.log_test(f"DB Performance - {test['name']}", "PASS", 
                                    f"Fast queries: {avg_time:.3f}s", metrics)
                    elif avg_time < 2.0:
                        self.log_test(f"DB Performance - {test['name']}", "WARN", 
                                    f"Moderate speed: {avg_time:.3f}s", metrics)
                    else:
                        self.log_test(f"DB Performance - {test['name']}", "FAIL", 
                                    f"Slow queries: {avg_time:.3f}s", metrics)
                else:
                    self.log_test(f"DB Performance - {test['name']}", "FAIL", 
                                "No successful queries")
                    
            except Exception as e:
                self.log_test(f"DB Performance - {test['name']}", "FAIL", str(e))
    
    def run_all_tests(self):
        """Executa todos os testes de performance"""
        print("🚀 Iniciando Testes de Performance e Carga")
        print("=" * 60)
        
        # Testar frontend primeiro (não precisa de auth)
        self.test_frontend_performance()
        
        # Autenticar para testes do backend
        if self.authenticate():
            print("\n🔐 Autenticado - Executando testes de performance...")
            
            self.test_response_times()
            self.test_concurrent_load()
            self.test_memory_leak()
            self.test_database_performance()
        else:
            print("\n❌ Falha na autenticação - Pulando testes do backend")
        
        # Resumo dos resultados
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES DE PERFORMANCE")
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
        
        if total > 0:
            success_rate = (passed / total * 100)
            print(f"🎯 Taxa de Sucesso: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("\n🚀 PERFORMANCE EXCELENTE!")
            elif success_rate >= 70:
                print(f"\n⚡ PERFORMANCE BOA - {warnings} AVISOS")
            elif success_rate >= 50:
                print(f"\n⚠️ PERFORMANCE MODERADA - OTIMIZAÇÕES NECESSÁRIAS")
            else:
                print(f"\n🐌 PERFORMANCE RUIM - OTIMIZAÇÕES CRÍTICAS NECESSÁRIAS")
        
        # Salvar resultados
        with open("performance_test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Resultados salvos em: performance_test_results.json")

def main():
    """Função principal"""
    tester = PerformanceTester()
    
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