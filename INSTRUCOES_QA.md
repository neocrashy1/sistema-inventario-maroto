# 🎯 INSTRUÇÕES PARA QA - SISTEMA LEVITIIS

## 📋 RESUMO DO PROJETO IMPLEMENTADO

O Sistema Levitiis está **100% funcional** com:
- ✅ **Frontend Vue.js 3** - Interface completa e responsiva
- ✅ **Backend FastAPI** - API REST com autenticação JWT
- ✅ **Segurança** - Rate limiting, validação, headers de segurança
- ✅ **Deploy** - Configuração Docker para produção
- ✅ **Documentação** - Completa e atualizada

## 🚀 COMO INICIAR OS TESTES

### **1. Verificar Ambiente Atual**
```bash
# Verificar se os serviços estão rodando
# Frontend: http://localhost:3000
# Backend: http://localhost:8000

# Se não estiverem rodando, execute:
cd C:\Users\Michel Maik\Desktop\Projetos\levitiis-vue

# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend  
npm run dev
```

### **2. URLs de Teste**
- **Frontend Principal**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentação API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Página de Testes**: http://localhost:3000/test-functionalities

## 🧪 PLANO DE TESTES QA

### **FASE 1: Testes Funcionais Básicos**

#### **1.1 Backend API (http://localhost:8000)**
```bash
# Teste de Health Check
curl http://localhost:8000/health

# Teste de Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"

# Teste de Dashboard (com token)
curl -H "Authorization: Bearer [TOKEN]" \
  http://localhost:8000/api/v1/dashboard/stats
```

#### **1.2 Frontend Interface**
- [ ] **Login**: Testar login com admin/admin123
- [ ] **Dashboard**: Verificar carregamento de dados
- [ ] **Navegação**: Testar todas as rotas
- [ ] **Responsividade**: Testar em diferentes resoluções
- [ ] **Notificações**: Verificar sistema de alertas

### **FASE 2: Testes de Segurança**

#### **2.1 Rate Limiting**
```bash
# Testar limite de requisições (30/min)
for i in {1..35}; do
  curl -w "%{http_code}\n" http://localhost:8000/health
  sleep 1
done
# Deve retornar 429 após 30 requisições
```

#### **2.2 Headers de Segurança**
```bash
# Verificar headers de segurança
curl -I http://localhost:8000/health
# Deve incluir: X-Frame-Options, X-XSS-Protection, etc.
```

#### **2.3 Validação de Input**
```bash
# Testar payload malicioso
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"<script>alert(1)</script>","password":"test"}'
```

### **FASE 3: Testes de Integração**

#### **3.1 Frontend ↔ Backend**
- [ ] **Autenticação**: Login/logout funcionando
- [ ] **Dashboard**: Dados carregando do backend
- [ ] **Error Handling**: Tratamento de erros da API
- [ ] **Loading States**: Estados de carregamento

#### **3.2 Persistência de Dados**
- [ ] **Tokens**: JWT sendo armazenado/renovado
- [ ] **Session**: Manutenção de sessão
- [ ] **Logout**: Limpeza de dados

### **FASE 4: Testes de Performance**

#### **4.1 Load Testing**
```bash
# Instalar Apache Bench (se necessário)
# Teste de carga no backend
ab -n 1000 -c 10 http://localhost:8000/health

# Teste de carga na API autenticada
ab -n 500 -c 5 -H "Authorization: Bearer [TOKEN]" \
  http://localhost:8000/api/v1/dashboard/stats
```

#### **4.2 Frontend Performance**
- [ ] **Lighthouse**: Score > 90 em Performance
- [ ] **Bundle Size**: Verificar tamanho dos chunks
- [ ] **Loading Time**: Tempo de carregamento < 3s

## 🐛 CENÁRIOS DE TESTE ESPECÍFICOS

### **Teste 1: Fluxo Completo de Usuário**
1. Acessar http://localhost:3000
2. Fazer login (admin/admin123)
3. Navegar pelo dashboard
4. Verificar dados em tempo real
5. Testar logout

### **Teste 2: Tratamento de Erros**
1. Desligar o backend
2. Tentar acessar o frontend
3. Verificar mensagens de erro
4. Religar backend
5. Verificar reconexão automática

### **Teste 3: Segurança**
1. Tentar acessar rotas protegidas sem token
2. Testar token expirado
3. Verificar rate limiting
4. Testar inputs maliciosos

### **Teste 4: Responsividade**
1. Testar em desktop (1920x1080)
2. Testar em tablet (768x1024)
3. Testar em mobile (375x667)
4. Verificar menu mobile

## 📊 CRITÉRIOS DE ACEITAÇÃO

### **✅ Deve Passar**
- [ ] Todos os endpoints retornam 200/201
- [ ] Login/logout funcionando
- [ ] Dashboard carregando dados
- [ ] Rate limiting ativo (429 após limite)
- [ ] Headers de segurança presentes
- [ ] Interface responsiva
- [ ] Tratamento de erros funcionando
- [ ] Performance aceitável (< 3s loading)

### **❌ Bugs Críticos**
- [ ] Falha de autenticação
- [ ] Dados não carregando
- [ ] Erros 500 no backend
- [ ] Interface quebrada
- [ ] Vulnerabilidades de segurança

## 🔧 FERRAMENTAS RECOMENDADAS

### **API Testing**
- **Postman**: Coleção de testes da API
- **curl**: Testes via linha de comando
- **Insomnia**: Alternative ao Postman

### **Frontend Testing**
- **Chrome DevTools**: Debug e performance
- **Lighthouse**: Auditoria de performance
- **Vue DevTools**: Debug específico do Vue

### **Security Testing**
- **OWASP ZAP**: Scan de vulnerabilidades
- **Burp Suite**: Teste de penetração
- **curl**: Teste de headers e rate limiting

## 📝 RELATÓRIO DE TESTES

### **Template de Bug Report**
```
**Título**: [Descrição breve do bug]
**Severidade**: Crítica/Alta/Média/Baixa
**Ambiente**: Frontend/Backend/Integração
**Passos para Reproduzir**:
1. 
2. 
3. 

**Resultado Esperado**: 
**Resultado Atual**: 
**Screenshots**: [Se aplicável]
**Logs**: [Logs relevantes]
```

### **Checklist Final**
- [ ] Todos os testes funcionais passaram
- [ ] Segurança validada
- [ ] Performance aceitável
- [ ] Documentação atualizada
- [ ] Bugs críticos resolvidos
- [ ] Deploy testado

## 🚀 PRÓXIMOS PASSOS APÓS QA

### **Se Testes Passarem**
1. **Deploy em Staging**: Usar `docker-compose.yml`
2. **Testes de Aceitação**: Com usuários finais
3. **Deploy em Produção**: Usar `./deploy.sh deploy`
4. **Monitoramento**: Configurar alertas

### **Se Houver Bugs**
1. **Documentar**: Usar template de bug report
2. **Priorizar**: Críticos primeiro
3. **Corrigir**: Implementar fixes
4. **Re-testar**: Validar correções

## 📞 CONTATOS E SUPORTE

- **Documentação**: `README.md`
- **Logs**: `/var/log/levitiis/` (produção)
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs

---

**🎯 OBJETIVO**: Garantir que o Sistema Levitiis está pronto para produção com qualidade, segurança e performance adequadas.

**⏰ PRAZO SUGERIDO**: 2-3 dias para testes completos

**✅ ENTREGA**: Sistema validado e pronto para deploy em produção