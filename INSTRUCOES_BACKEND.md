# 🔧 INSTRUÇÕES PARA INICIAR O BACKEND

## 📍 Situação Atual

O frontend está rodando em `http://172.30.0.61:3000` mas está com erro **ECONNREFUSED** ao tentar conectar ao backend em `http://172.30.0.61:8000`.

## ✅ O que foi configurado

- Frontend configurado para conectar em `172.30.0.61:8000`
- Proxy do Vite configurado corretamente
- Variáveis de ambiente preparadas

## 🚀 Como iniciar o Backend

### No servidor node01 (172.30.0.61)

```bash
# 1. Conectar ao servidor
ssh usuario@172.30.0.61

# 2. Ir para o diretório do backend
cd SistemaAnaliseComputadores/backend

# 3. Ativar ambiente virtual (se existir)
source venv/bin/activate
# ou no Windows:
# venv\Scripts\activate

# 4. Instalar dependências (se necessário)
pip install -r requirements.txt

# 5. Iniciar o servidor
python main.py
# ou se estiver configurado com uvicorn:
# uvicorn main:app --host 172.30.0.61 --port 8000
```

### Verificar se está rodando

```bash
# Deve retornar {"status": "healthy"}
curl http://172.30.0.61:8000/health

# Ou acessar no navegador
http://172.30.0.61:8000/docs  # Swagger UI
```

## 🔍 Troubleshooting

### Backend não inicia
```bash
# Verificar se a porta está em uso
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac

# Matar processo se necessário
kill -9 <PID>
```

### Frontend não conecta
```bash
# Verificar firewall
sudo ufw status          # Ubuntu
# Adicionar regra se necessário
sudo ufw allow 8000

# Testar conectividade
ping 172.30.0.61
telnet 172.30.0.61 8000
```

## 📝 Configuração Recomendada

### Backend deve rodar com:

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Aceita conexões de qualquer IP
        port=8000,
        reload=True,     # Auto-reload em desenvolvimento
        log_level="info"
    )
```

## ✅ Quando o backend estiver rodando

Você verá:
- ✅ Logs no terminal do backend
- ✅ Acesso em `http://172.30.0.61:8000/docs`
- ✅ O frontend funcionando completamente
- ✅ Sem erros ECONNREFUSED nos logs

## 🎯 Status Atual

- ✅ Frontend: Rodando em `http://172.30.0.61:3000`
- ⚠️ Backend: **Precisa ser iniciado em `http://172.30.0.61:8000`**
- ✅ Configuração: Pronta
- ✅ Proxy: Configurado

---

**Próximo Passo:** Iniciar o backend no node01


