# 🌐 Instalar Ngrok no Node01 - Sistema Levitiis

## 📋 Objetivo
Publicar o sistema Levitiis através do Ngrok para acesso externo.

---

## 🔧 INSTALAÇÃO NO NODE01 (Linux)

### **Passo 1: Conectar ao Node01**
```bash
ssh usuario@node01
```

### **Passo 2: Baixar e Instalar Ngrok**

#### **Opção A: Instalação Manual**
```bash
# Criar diretório para ngrok
mkdir -p ~/ngrok “”
cd ~/ngrok

# Baixar ngrok (versão Linux)
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz

# Descompactar
tar -xzf ngrok-v3-stable-linux-amd64.tgz

# Mover para /usr/local/bin (opcional, mas recomendado)
sudo mv ngrok /usr/local/bin/

# Verificar instalação
ngrok version
```

#### **Opção B: Via Snap (se disponível)**
```bash
sudo snap install ngrok
```

#### **Opção C: Via Homebrew (se disponível)**
```bash
brew install ngrok
```

---

## 🔑 CONFIGURAÇÃO INICIAL

### **Passo 3: Criar Conta no Ngrok**
1. Acesse: https://dashboard.ngrok.com/signup
2. Crie uma conta gratuita
3. Copie seu **authtoken** da dashboard

### **Passo 4: Configurar Token**
```bash
ngrok config add-authtoken SEU_AUTHTOKEN_AQUI
```

---

## 🚀 EXECUTAR TÚNEL

### **Passo 5: Iniciar o Frontend**
```bash
# No diretório do projeto
cd ~/SistemaAnaliseComputadores
npm run dev -- --port 3000 --host 0.0.0.0
```

### **Passo 6: Iniciar Ngrok Tunnel**
Em **outro terminal** (ou via screen/tmux):
```bash
# Túnel HTTP (porta 3000)
ngrok http 3000

# Ou túnel com domínio personalizado (se tiver plano pago)
ngrok http 3000 --domain=meu-dominio.ngrok-free.app
```

### **Resultado:**
```
Session Status                online
Account                       [seu-email] (Plan: Free)
Version                       3.x.x
Region                        United States (us)
Latency                       Xms
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://xxxx-xxxx-xxxx.ngrok-free.app -> http://localhost:3000
```

---

## 📱 ACESSO EXTERNO

### **URL Pública:**
```
https://xxxx-xxxx-xxxx.ngrok-free.app
```

---

## 🔒 CONFIGURAÇÕES AVANÇADAS

### **1. Arquivo de Configuração**
Criar `~/.ngrok2/ngrok.yml`:
```yaml
version: "2"
authtoken: SEU_AUTHTOKEN

tunnels:
  frontend:
    addr: 3000
    proto: http
    
  backend:
    addr: 8000
    proto: http

start:
  frontend:
    addr: 3000
  backend:
    addr: 8000
```

### **2. Executar com Config**
```bash
ngrok start --all
```

---

## 🛠️ MANTENDO O TÚNEL ATIVO

### **Opção 1: Via Systemd (Recomendado)**
```bash
# Criar serviço
sudo nano /etc/systemd/system/ngrok.service
```

**Conteúdo:**
```ini
[Unit]
Description=Ngrok Tunnel
After=network.target

[Service]
Type=simple
User=seu-usuario
ExecStart=/usr/local/bin/ngrok http 3000
Restart=always

[Install]
WantedBy=multi-user.target
```

**Ativar:**
```bash
sudo systemctl enable ngrok
sudo systemctl start ngrok
sudo systemctl status ngrok
```

### **Opção 2: Via Screen**
```bash
# Instalar screen
sudo apt install screen

# Criar sessão
screen -S ngrok

# Executar ngrok
ngrok http 3000

# Desanexar: Ctrl+A, depois D
# Ver sessão: screen -r ngrok
```

### **Opção 3: Via Tmux**
```bash
# Instalar tmux
sudo apt install tmux

# Criar sessão
tmux new -s ngrok

# Executar ngrok
ngrok http 3000

# Desanexar: Ctrl+B, depois D
# Ver sessão: tmux attach -t ngrok
```

---

## 🔐 SEGURANÇA

### **1. Adicionar Senha Básica**
```bash
ngrok http 3000 --basic-auth="usuario:senha"
```

### **2. Whitelist IP**
```bash
ngrok http 3000 --ip-whitelist="IP.ALLOWED.1,IP.ALLOWED.2"
```

### **3. OAuth**
```bash
ngrok http 3000 --oauth="google"
```

---

## 📊 MONITORAMENTO

### **Dashboard Web:**
```
http://localhost:4040
```
Acesse no navegador local para ver:
- Requisições HTTP
- Logs
- Métricas
- Replay de requisições

---

## 🔄 ATUALIZAÇÃO

```bash
# Desinstalar versão antiga
sudo rm /usr/local/bin/ngrok

# Baixar e instalar nova versão
cd ~/ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

---

## ⚠️ NOTAS IMPORTANTES

1. **Plano Gratuito:**
   - URLs aleatórias a cada reinício
   - Limite de 40 conexões/minuto
   - Banner de aviso

2. **Plano Pago:**
   - URLs fixas
   - Sem limites
   - Sem banner

3. **Timeout:**
   - Único processo ngrok ativo por vez

4. **Firewall:**
   - Garantir que porta 3000 está aberta internamente

---

## ✅ CHECKLIST

- [ ] Ngrok instalado
- [ ] Conta criada em ngrok.com
- [ ] Authtoken configurado
- [ ] Frontend rodando na porta 3000
- [ ] Ngrok tunnel ativo
- [ ] URL pública copiada
- [ ] Acesso testado externamente
- [ ] Serviço systemd configurado (opcional)

---

**Versão:** 1.0  
**Data:** Janeiro 2025






