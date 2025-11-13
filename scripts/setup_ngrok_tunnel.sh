#!/bin/bash

# Script para configurar túnel Ngrok persistente
# Sistema Levitiis Asset Inventory

set -e

# Configurações
PORT=${1:-3000}
USER=$(whoami)
NGROK_PATH=$(command -v ngrok)
SERVICE_NAME="ngrok-levitiis"

echo "🔧 Configurando túnel Ngrok persistente na porta $PORT..."

# Verificar se ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ Ngrok não encontrado!"
    echo "   Execute primeiro: bash scripts/install_ngrok.sh"
    exit 1
fi

# Verificar authtoken
if [ ! -f ~/.config/ngrok/ngrok.yml ]; then
    echo "⚠️  Authtoken não configurado!"
    echo "   Execute: ngrok config add-authtoken SEU_TOKEN"
    echo ""
    read -p "Configurar agora? (s/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        read -p "Cole seu authtoken: " token
        ngrok config add-authtoken "$token"
    else
        exit 1
    fi
fi

# Criar serviço systemd
echo "📋 Criando serviço systemd..."
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null <<EOF
[Unit]
Description=Ngrok Tunnel for Levitiis System
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=$NGROK_PATH http $PORT --log=stdout
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Recarregar systemd
sudo systemctl daemon-reload

# Habilitar serviço
sudo systemctl enable ${SERVICE_NAME}.service

echo ""
echo "✅ Serviço criado com sucesso!"
echo ""
echo "📝 Comandos úteis:"
echo "   Iniciar: sudo systemctl start $SERVICE_NAME"
echo "   Parar:   sudo systemctl stop $SERVICE_NAME"
echo "   Status:  sudo systemctl status $SERVICE_NAME"
echo "   Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo ""
read -p "Iniciar o serviço agora? (s/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    sudo systemctl start $SERVICE_NAME
    echo "✅ Túnel iniciado!"
    sleep 2
    sudo systemctl status $SERVICE_NAME --no-pager
fi

echo ""
echo "🎉 Configuração concluída!"






