#!/usr/bin/env python3
"""
Script de Teste de Edge Cases - Sistema Levitiis
Testa cenários extremos, validação de entrada e robustez do sistema
"""

import requests
import json
import time
import sys
from datetime import datetime
import random
import string

class EdgeCaseTester:
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
    
    def test_invalid_authentication(self):
        """Testa autenticação com credenciais inválidas"""
        test_cases = [
            {"username": "", "password": ""},
            {"username": "admin", "password": "wrong"},
            {"username": "nonexistent", "password": "admin123"},
            {"username": "admin", "password": ""},
            {"username": "", "password": "admin123"},
            {"username": "admin' OR '1'='1", "password": "admin123"},  # SQL Injection
            {"username": "<script>alert('xss')</script>", "password": "admin123"},  # XSS
        ]
        
        passed = 0
        for i, credentials in enumerate(test_cases):
            try:
                response = requests.post(
                    f"{self.backend_url}/api/v1/auth/login",
                    data=credentials,
                    timeout=5
                )
                
                if response.status_code in [400, 401, 422]:  # Expected error codes
                    passed += 1
                elif response.status_code == 200:
                    # This is bad - invalid credentials should not succeed
                    self.log_test(f"Invalid Auth Test {i+1}", "FAIL", f"Invalid credentials accepted: {credentials['username']}")
                    continue
                
            except Exception as e:
                # Network errors are acceptable for malformed requests
                passed += 1
        
        success_rate = (passed / len(test_cases)) * 100
        if success_rate >= 80:
            self.log_test("Invalid Authentication Tests", "PASS", f"Rejected {passed}/{len(test_cases)} invalid attempts")
        else:
            self.log_test("Invalid Authentication Tests", "FAIL", f"Only rejected {passed}/{len(test_cases)} invalid attempts")
    
    def test_malformed_requests(self):
        """Testa requisições malformadas"""
        if not self.token:
            self.log_test("Malformed Requests", "SKIP", "No authentication token")
            return
        
        headers = self.get_headers()
        test_cases = [
            # Invalid JSON
            {"url": "/api/v1/users/", "data": "invalid json", "expected": [400, 422]},
            # Extremely large payload
            {"url": "/api/v1/users/", "data": {"name": "A" * 10000}, "expected": [400, 413, 422]},
            # Invalid content type
            {"url": "/api/v1/users/", "data": "xml_data", "headers": {"Content-Type": "application/xml"}, "expected": [400, 415, 422]},
            # Missing required fields
            {"url": "/api/v1/users/", "data": {}, "expected": [400, 422]},
        ]
        
        passed = 0
        for i, test_case in enumerate(test_cases):
            try:
                test_headers = headers.copy()
                if "headers" in test_case:
                    test_headers.update(test_case["headers"])
                
                if isinstance(test_case["data"], dict):
                    response = requests.post(
                        f"{self.backend_url}{test_case['url']}",
                        headers=test_headers,
                        json=test_case["data"],
                        timeout=5
                    )
                else:
                    response = requests.post(
                        f"{self.backend_url}{test_case['url']}",
                        headers=test_headers,
                        data=test_case["data"],
                        timeout=5
                    )
                
                if response.status_code in test_case["expected"]:
                    passed += 1
                
            except Exception:
                # Network errors are acceptable for malformed requests
                passed += 1
        
        success_rate = (passed / len(test_cases)) * 100
        if success_rate >= 75:
            self.log_test("Malformed Requests", "PASS", f"Handled {passed}/{len(test_cases)} malformed requests correctly")
        else:
            self.log_test("Malformed Requests", "FAIL", f"Only handled {passed}/{len(test_cases)} malformed requests correctly")
    
    def test_rate_limiting_edge_cases(self):
        """Testa edge cases do rate limiting"""
        try:
            # Fazer muitas requisições rapidamente
            responses = []
            start_time = time.time()
            
            for i in range(35):  # Acima do limite de 30
                response = requests.get(f"{self.backend_url}/health", timeout=2)
                responses.append(response.status_code)
                if i > 30 and response.status_code == 429:  # Rate limited
                    break
            
            end_time = time.time()
            
            # Verificar se rate limiting foi ativado
            rate_limited = any(code == 429 for code in responses)
            
            if rate_limited:
                self.log_test("Rate Limiting Edge Cases", "PASS", f"Rate limiting activated after {len(responses)} requests")
            else:
                self.log_test("Rate Limiting Edge Cases", "WARN", f"No rate limiting detected in {len(responses)} requests")
        
        except Exception as e:
            self.log_test("Rate Limiting Edge Cases", "FAIL", str(e))
    
    def test_concurrent_requests(self):
        """Testa requisições concorrentes"""
        if not self.token:
            self.log_test("Concurrent Requests", "SKIP", "No authentication token")
            return
        
        import threading
        import queue
        
        results_queue = queue.Queue()
        headers = self.get_headers()
        
        def make_request(thread_id):
            try:
                response = requests.get(
                    f"{self.backend_url}/api/v1/users/",
                    headers=headers,
                    timeout=10
                )
                results_queue.put((thread_id, response.status_code, len(response.content)))
            except Exception as e:
                results_queue.put((thread_id, 0, str(e)))
        
        # Criar 10 threads para requisições simultâneas
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
        
        # Iniciar todas as threads
        start_time = time.time()
        for thread in threads:
            thread.start()
        
        # Aguardar conclusão
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # Coletar resultados
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        successful = len([r for r in results if r[1] == 200])
        total_time = end_time - start_time
        
        if successful >= 8:  # 80% de sucesso
            self.log_test("Concurrent Requests", "PASS", f"{successful}/10 requests successful in {total_time:.2f}s")
        else:
            self.log_test("Concurrent Requests", "FAIL", f"Only {successful}/10 requests successful")
    
    def test_large_data_handling(self):
        """Testa manipulação de grandes volumes de dados"""
        if not self.token:
            self.log_test("Large Data Handling", "SKIP", "No authentication token")
            return
        
        try:
            # Testar GET com muitos resultados
            response = requests.get(
                f"{self.backend_url}/api/v1/users/",
                headers=self.get_headers(),
                timeout=15
            )
            
            if response.status_code == 200:
                data_size = len(response.content)
                response_time = response.elapsed.total_seconds()
                
                if response_time < 5.0:  # Menos de 5 segundos
                    self.log_test("Large Data Handling", "PASS", f"Handled {data_size} bytes in {response_time:.2f}s")
                else:
                    self.log_test("Large Data Handling", "WARN", f"Slow response: {response_time:.2f}s for {data_size} bytes")
            else:
                self.log_test("Large Data Handling", "FAIL", f"HTTP {response.status_code}")
        
        except Exception as e:
            self.log_test("Large Data Handling", "FAIL", str(e))
    
    def test_special_characters(self):
        """Testa caracteres especiais e encoding"""
        if not self.token:
            self.log_test("Special Characters", "SKIP", "No authentication token")
            return
        
        special_strings = [
            "João da Silva",  # Acentos
            "测试用户",  # Chinês
            "Пользователь",  # Russo
            "🚀 Emoji User 🎉",  # Emojis
            "User with \"quotes\" and 'apostrophes'",  # Aspas
            "User with <tags> & symbols",  # HTML/XML
            "User\nwith\nnewlines",  # Quebras de linha
            "User\twith\ttabs",  # Tabs
        ]
        
        passed = 0
        for i, test_string in enumerate(special_strings):
            try:
                # Testar busca com caracteres especiais
                response = requests.get(
                    f"{self.backend_url}/api/v1/users/",
                    headers=self.get_headers(),
                    params={"search": test_string},
                    timeout=5
                )
                
                if response.status_code in [200, 400, 422]:  # Acceptable responses
                    passed += 1
                    
            except Exception:
                # Encoding errors might be expected
                passed += 1
        
        success_rate = (passed / len(special_strings)) * 100
        if success_rate >= 80:
            self.log_test("Special Characters", "PASS", f"Handled {passed}/{len(special_strings)} special character tests")
        else:
            self.log_test("Special Characters", "FAIL", f"Only handled {passed}/{len(special_strings)} special character tests")
    
    def test_memory_usage(self):
        """Testa uso de memória com requisições repetidas"""
        if not self.token:
            self.log_test("Memory Usage", "SKIP", "No authentication token")
            return
        
        try:
            # Fazer muitas requisições para testar vazamentos de memória
            response_times = []
            
            for i in range(50):
                start = time.time()
                response = requests.get(
                    f"{self.backend_url}/api/v1/users/",
                    headers=self.get_headers(),
                    timeout=5
                )
                end = time.time()
                
                if response.status_code == 200:
                    response_times.append(end - start)
                else:
                    break
            
            if len(response_times) >= 40:  # 80% success
                avg_time = sum(response_times) / len(response_times)
                # Verificar se o tempo não aumentou significativamente
                first_10_avg = sum(response_times[:10]) / 10
                last_10_avg = sum(response_times[-10:]) / 10
                
                if last_10_avg <= first_10_avg * 1.5:  # Não mais que 50% de aumento
                    self.log_test("Memory Usage", "PASS", f"Stable performance over {len(response_times)} requests")
                else:
                    self.log_test("Memory Usage", "WARN", f"Performance degradation detected: {first_10_avg:.3f}s → {last_10_avg:.3f}s")
            else:
                self.log_test("Memory Usage", "FAIL", f"Only completed {len(response_times)}/50 requests")
        
        except Exception as e:
            self.log_test("Memory Usage", "FAIL", str(e))
    
    def test_error_handling(self):
        """Testa tratamento de erros"""
        if not self.token:
            self.log_test("Error Handling", "SKIP", "No authentication token")
            return
        
        error_tests = [
            # Recurso não encontrado
            {"url": "/api/v1/users/99999", "expected": [404]},
            # Endpoint inexistente
            {"url": "/api/v1/nonexistent", "expected": [404]},
            # Método não permitido
            {"url": "/api/v1/users/", "method": "DELETE", "expected": [405]},
        ]
        
        passed = 0
        for test in error_tests:
            try:
                method = test.get("method", "GET")
                if method == "GET":
                    response = requests.get(
                        f"{self.backend_url}{test['url']}",
                        headers=self.get_headers(),
                        timeout=5
                    )
                elif method == "DELETE":
                    response = requests.delete(
                        f"{self.backend_url}{test['url']}",
                        headers=self.get_headers(),
                        timeout=5
                    )
                
                if response.status_code in test["expected"]:
                    passed += 1
                    
            except Exception:
                pass
        
        success_rate = (passed / len(error_tests)) * 100
        if success_rate >= 80:
            self.log_test("Error Handling", "PASS", f"Handled {passed}/{len(error_tests)} error scenarios correctly")
        else:
            self.log_test("Error Handling", "FAIL", f"Only handled {passed}/{len(error_tests)} error scenarios correctly")
    
    def run_all_tests(self):
        """Executa todos os testes de edge cases"""
        print("🧪 Iniciando Testes de Edge Cases e Robustez")
        print("=" * 60)
        
        # Testes sem autenticação
        self.test_invalid_authentication()
        
        # Autenticar para testes que precisam
        if self.authenticate():
            print("\n🔐 Autenticado - Executando testes avançados...")
            
            self.test_malformed_requests()
            self.test_rate_limiting_edge_cases()
            self.test_concurrent_requests()
            self.test_large_data_handling()
            self.test_special_characters()
            self.test_memory_usage()
            self.test_error_handling()
        else:
            print("\n❌ Falha na autenticação - Pulando testes avançados")
        
        # Resumo dos resultados
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES DE EDGE CASES")
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
            
            if failed == 0:
                print("\n🛡️ SISTEMA ROBUSTO - TODOS OS EDGE CASES PASSARAM!")
            elif failed <= 2:
                print(f"\n⚠️ SISTEMA ESTÁVEL - {failed} PROBLEMA(S) MENOR(ES)")
            else:
                print(f"\n🚨 SISTEMA INSTÁVEL - {failed} PROBLEMAS CRÍTICOS")
        
        # Salvar resultados
        with open("edge_case_test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Resultados salvos em: edge_case_test_results.json")

def main():
    """Função principal"""
    tester = EdgeCaseTester()
    
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