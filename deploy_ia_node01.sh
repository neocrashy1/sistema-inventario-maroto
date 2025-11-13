#!/usr/bin/env bash
set -euo pipefail

# deploy_ia_node01.sh
# Run this on node01 (Linux) to install Docker (if missing) and start the IA stack.

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
IA_DIR="$PROJECT_DIR/deploy/ia"

echo "IA deploy helper"
echo "Project dir: $PROJECT_DIR"
echo "IA dir: $IA_DIR"

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker not found. Installing Docker CE..."
  # Install Docker (Debian/Ubuntu compatible). If your distro is different, install manually.
  curl -fsSL https://get.docker.com -o get-docker.sh
  sh get-docker.sh
  rm get-docker.sh
  sudo usermod -aG docker "$USER" || true
fi

if ! command -v docker-compose >/dev/null 2>&1; then
  echo "docker-compose not found. Installing docker-compose plugin or v2..."
  # docker compose v2 as plugin via pip is sometimes available; try apt-get fallback.
  if docker compose version >/dev/null 2>&1; then
    echo "docker compose plugin available via 'docker compose'"
  else
    echo "Attempting to install docker-compose via pip..."
    python3 -m pip install --user docker-compose || true
  fi
fi

mkdir -p "$IA_DIR/models" "$IA_DIR/extensions" "$IA_DIR/configs"

echo "Starting IA stack with docker compose (this will pull images and may download them)..."
cd "$IA_DIR"
docker compose up -d --build

echo "IA stack started."
echo "- text-generation-webui should be available at http://<node01-ip>:7860"
echo "- The agent will run and drop 'ia_suggestions.json' into the repository root."
echo "Next steps:"
echo "  * If no model installed, open the web UI and install a model under /workspace/models (or copy a quantized model into $IA_DIR/models)."
echo "  * Review deploy/ia/README.md for security notes and how to enable AUTONOMOUS=true."
