# 🌐 RESUMO: Instalação Ngrok no Node01

## ✅ Arquivos Criados

1. **`INSTALAR_NGROK_NODE01.md`** - Guia completo de instalação
2. **`scripts/install_ngrok.sh`** - Script de instalação automática
3. **`scripts/setup_ngrok_tunnel.sh`** - Script de configuração persistente

---

## 🚀 INSTRUÇÕES RÁPIDAS

### **1. No Node01, executar:**
```bash
# Instalar Ngrok
bash SistemaAnaliseComputadores/scripts/install_ngrok.sh

# Configurar token (criar conta em https://dashboard.ngrok.com)
ngrok config add-authtoken SEU_TOKEN_AQUI

# Configurar serviço persistente
bash SistemaAnaliseComputadores/scripts/setup_ngrok_tunnel.sh 3000
```

### **2. Resultado:**
- ✅ Túnel automático na porta 3000
- ✅ URL pública https://xxxx.ngrok-free.app
- ✅ Serviço persistente (inicia automaticamente)

---

## 📝 COMANDOS ÚTEIS

```bash
# Ver status do túnel
sudo systemctl status ngrok-levitiis

# Ver logs
sudo journalctl -u ngrok-levitiis -f

# Reiniciar
sudo systemctl restart ngrok-levitiis

# Ver URL atual
curl http://localhost:4040/api/tunnels
```

---

**Pronto para deploy público!** 🎉






