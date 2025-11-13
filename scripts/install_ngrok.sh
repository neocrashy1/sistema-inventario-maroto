#!/bin/bash

# Script de instalação do Ngrok para o Node01
set -e

echo "🚀 Instalando Ngrok no Node01..."

NGROK_VERSION="v3-stable"
ARCH="amd64"
INSTALL_DIR="/usr/local/bin"
DOWNLOAD_DIR="/tmp/ngrok-install"

mkdir -p "$DOWNLOAD_DIR"
cd "$DOWNLOAD_DIR"

echo "📥 Baixando Ngrok..."
wget -q "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-${NGROK_VERSION}-linux-${ARCH}.tgz"

echo "📦 Descompactando..."
tar -xzf "ngrok-${NGROK_VERSION}-linux-${ARCH}.tgz"

echo "📋 Instalando..."
sudo mv ngrok "$INSTALL_DIR/"
sudo chmod +x "${INSTALL_DIR}/ngrok"

rm -rf "$DOWNLOAD_DIR"

echo "✅ Ngrok instalado!"
ngrok version






