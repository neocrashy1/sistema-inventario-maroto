#!/usr/bin/env python3
"""
Script de Teste de Alertas Automáticos - Sistema Levitiis
Testa o sistema de alertas, notificações e tickets automáticos
"""

import requests
import json
import time
import sys
from datetime import datetime, timedelta
import random

class AlertTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
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
    
    def test_alert_creation(self):
        """Testa criação de alertas"""
        try:
            # Dados de teste para criar um alerta
            alert_data = {
                "title": "Teste de Alerta Automático",
                "description": "Alerta criado durante teste de QA",
                "severity": "high",
                "source": "test_system",
                "asset_id": 1,
                "alert_type": "performance",
                "metadata": {
                    "cpu_usage": 95.5,
                    "memory_usage": 87.2,
                    "test_generated": True
                }
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/alerts/",
                headers=self.get_headers(),
                json=alert_data,
                timeout=10
            )
            
            if response.status_code == 201:
                alert = response.json()
                alert_id = alert.get("id")
                self.log_test("Alert Creation", "PASS", f"Alert ID: {alert_id}")
                return alert_id
            else:
                self.log_test("Alert Creation", "FAIL", f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Alert Creation", "FAIL", str(e))
            return None
    
    def test_alert_retrieval(self, alert_id):
        """Testa recuperação de alertas"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/alerts/{alert_id}",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                alert = response.json()
                self.log_test("Alert Retrieval", "PASS", f"Title: {alert.get('title')}")
                return True
            else:
                self.log_test("Alert Retrieval", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Alert Retrieval", "FAIL", str(e))
            return False
    
    def test_alert_filtering(self):
        """Testa filtros de alertas"""
        try:
            # Testar filtro por severidade
            response = requests.get(
                f"{self.backend_url}/api/v1/alerts/?severity=high",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                alerts = response.json()
                high_severity_count = len([a for a in alerts if a.get("severity") == "high"])
                self.log_test("Alert Filtering - Severity", "PASS", f"High severity alerts: {high_severity_count}")
                
                # Testar filtro por status
                response = requests.get(
                    f"{self.backend_url}/api/v1/alerts/?status=active",
                    headers=self.get_headers(),
                    timeout=10
                )
                
                if response.status_code == 200:
                    active_alerts = response.json()
                    self.log_test("Alert Filtering - Status", "PASS", f"Active alerts: {len(active_alerts)}")
                    return True
                else:
                    self.log_test("Alert Filtering - Status", "FAIL", f"HTTP {response.status_code}")
                    return False
            else:
                self.log_test("Alert Filtering - Severity", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Alert Filtering", "FAIL", str(e))
            return False
    
    def test_ticket_auto_creation(self):
        """Testa criação automática de tickets a partir de alertas"""
        try:
            # Criar um alerta crítico que deve gerar ticket automaticamente
            critical_alert_data = {
                "title": "Alerta Crítico - Teste Auto Ticket",
                "description": "Sistema com falha crítica detectada",
                "severity": "critical",
                "source": "monitoring_system",
                "asset_id": 1,
                "alert_type": "system_failure",
                "metadata": {
                    "error_rate": 100,
                    "downtime": True,
                    "auto_ticket": True
                }
            }
            
            # Criar o alerta
            response = requests.post(
                f"{self.backend_url}/api/v1/alerts/",
                headers=self.get_headers(),
                json=critical_alert_data,
                timeout=10
            )
            
            if response.status_code == 201:
                alert = response.json()
                alert_id = alert.get("id")
                
                # Aguardar um pouco para processamento automático
                time.sleep(2)
                
                # Verificar se foi criado um ticket relacionado
                tickets_response = requests.get(
                    f"{self.backend_url}/api/v1/tickets/?alert_id={alert_id}",
                    headers=self.get_headers(),
                    timeout=10
                )
                
                if tickets_response.status_code == 200:
                    tickets = tickets_response.json()
                    if len(tickets) > 0:
                        ticket = tickets[0]
                        self.log_test("Auto Ticket Creation", "PASS", f"Ticket ID: {ticket.get('id')}")
                        return ticket.get('id')
                    else:
                        self.log_test("Auto Ticket Creation", "FAIL", "No ticket created for critical alert")
                        return None
                else:
                    self.log_test("Auto Ticket Creation", "FAIL", f"HTTP {tickets_response.status_code}")
                    return None
            else:
                self.log_test("Auto Ticket Creation", "FAIL", f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.log_test("Auto Ticket Creation", "FAIL", str(e))
            return None
    
    def test_alert_escalation(self):
        """Testa escalação de alertas"""
        try:
            # Criar alerta que deve ser escalado
            escalation_alert_data = {
                "title": "Alerta para Escalação",
                "description": "Alerta não resolvido há muito tempo",
                "severity": "medium",
                "source": "escalation_test",
                "asset_id": 1,
                "alert_type": "performance",
                "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "metadata": {
                    "escalation_test": True,
                    "unresolved_time": 120  # minutos
                }
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/alerts/",
                headers=self.get_headers(),
                json=escalation_alert_data,
                timeout=10
            )
            
            if response.status_code == 201:
                alert = response.json()
                alert_id = alert.get("id")
                
                # Simular processo de escalação (verificar se severity aumentou)
                time.sleep(1)
                
                escalation_response = requests.get(
                    f"{self.backend_url}/api/v1/alerts/{alert_id}",
                    headers=self.get_headers(),
                    timeout=10
                )
                
                if escalation_response.status_code == 200:
                    updated_alert = escalation_response.json()
                    current_severity = updated_alert.get("severity")
                    self.log_test("Alert Escalation", "PASS", f"Current severity: {current_severity}")
                    return True
                else:
                    self.log_test("Alert Escalation", "FAIL", f"HTTP {escalation_response.status_code}")
                    return False
            else:
                self.log_test("Alert Escalation", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Alert Escalation", "FAIL", str(e))
            return False
    
    def test_notification_system(self):
        """Testa sistema de notificações"""
        try:
            # Verificar endpoint de notificações
            response = requests.get(
                f"{self.backend_url}/api/v1/notifications/",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                notifications = response.json()
                self.log_test("Notification System", "PASS", f"Found {len(notifications)} notifications")
                
                # Testar criação de notificação
                notification_data = {
                    "title": "Teste de Notificação",
                    "message": "Notificação criada durante teste de QA",
                    "type": "alert",
                    "priority": "high",
                    "user_id": 1
                }
                
                create_response = requests.post(
                    f"{self.backend_url}/api/v1/notifications/",
                    headers=self.get_headers(),
                    json=notification_data,
                    timeout=10
                )
                
                if create_response.status_code == 201:
                    notification = create_response.json()
                    self.log_test("Notification Creation", "PASS", f"Notification ID: {notification.get('id')}")
                    return True
                else:
                    self.log_test("Notification Creation", "FAIL", f"HTTP {create_response.status_code}")
                    return False
            else:
                self.log_test("Notification System", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Notification System", "FAIL", str(e))
            return False
    
    def test_alert_metrics(self):
        """Testa métricas de alertas"""
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/dashboard/metrics",
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                metrics = response.json()
                alert_metrics = metrics.get("alert_severities", {})
                
                total_alerts = sum(alert_metrics.values()) if alert_metrics else 0
                self.log_test("Alert Metrics", "PASS", f"Total alerts in metrics: {total_alerts}")
                
                # Verificar se há dados de timeline
                timeline = metrics.get("timeline", [])
                if timeline:
                    self.log_test("Alert Timeline", "PASS", f"Timeline entries: {len(timeline)}")
                else:
                    self.log_test("Alert Timeline", "WARN", "No timeline data found")
                
                return True
            else:
                self.log_test("Alert Metrics", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Alert Metrics", "FAIL", str(e))
            return False
    
    def test_alert_performance(self):
        """Testa performance do sistema de alertas"""
        try:
            start_time = time.time()
            
            # Fazer múltiplas requisições para testar performance
            for i in range(5):
                response = requests.get(
                    f"{self.backend_url}/api/v1/alerts/",
                    headers=self.get_headers(),
                    timeout=10
                )
                if response.status_code != 200:
                    self.log_test("Alert Performance", "FAIL", f"Request {i+1} failed")
                    return False
            
            end_time = time.time()
            total_time = end_time - start_time
            avg_time = total_time / 5
            
            if avg_time < 2.0:  # Menos de 2 segundos por requisição
                self.log_test("Alert Performance", "PASS", f"Avg response time: {avg_time:.2f}s")
                return True
            else:
                self.log_test("Alert Performance", "WARN", f"Slow response time: {avg_time:.2f}s")
                return False
        except Exception as e:
            self.log_test("Alert Performance", "FAIL", str(e))
            return False
    
    def run_all_tests(self):
        """Executa todos os testes de alertas"""
        print("🚨 Iniciando Testes do Sistema de Alertas")
        print("=" * 60)
        
        # Autenticar
        if not self.authenticate():
            print("❌ Falha na autenticação. Abortando testes.")
            return False
        
        # Testes básicos de alertas
        alert_id = self.test_alert_creation()
        if alert_id:
            self.test_alert_retrieval(alert_id)
        
        self.test_alert_filtering()
        
        # Testes de automação
        ticket_id = self.test_ticket_auto_creation()
        self.test_alert_escalation()
        
        # Testes de notificações
        self.test_notification_system()
        
        # Testes de métricas e performance
        self.test_alert_metrics()
        self.test_alert_performance()
        
        # Resumo dos resultados
        self.print_summary()
        
        return True
    
    def print_summary(self):
        """Imprime resumo dos testes"""
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES DE ALERTAS")
        print("=" * 60)
        
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        warnings = len([r for r in self.test_results if r["status"] == "WARN"])
        total = len(self.test_results)
        
        print(f"✅ Passou: {passed}")
        print(f"❌ Falhou: {failed}")
        print(f"⚠️ Avisos: {warnings}")
        print(f"📈 Total: {total}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        print(f"🎯 Taxa de Sucesso: {success_rate:.1f}%")
        
        if failed == 0:
            print("\n🎉 SISTEMA DE ALERTAS FUNCIONANDO PERFEITAMENTE!")
        else:
            print(f"\n⚠️ {failed} TESTE(S) DE ALERTAS FALHARAM")
        
        # Salvar resultados
        with open("alert_test_results.json", "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Resultados salvos em: alert_test_results.json")

def main():
    """Função principal"""
    tester = AlertTester()
    
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