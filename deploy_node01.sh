#!/usr/bin/env bash
set -euo pipefail

# Deploy helper para node01 (172.30.0.61)
# Uso: export SSH_USER=maroro SSH_HOST=172.30.0.61 SSH_PORT=22 PROJECT_PATH=/home/maroro/levitiis BRANCH=main ./deploy_node01.sh
# Exemplo (uma linha):
# SSH_USER=maroro SSH_HOST=172.30.0.61 PROJECT_PATH=/home/maroro/levitiis BRANCH=feature/xyz ./deploy_node01.sh
#
# Observação de segurança: evite colocar senhas em arquivos de script. Prefira chaves SSH.
# Se precisar usar senha e estiver em ambiente controlado, você pode usar sshpass (não recomendado em produção):
# sshpass -p 'maroto' ssh -o StrictHostKeyChecking=no -p $SSH_PORT $SSH_USER@$SSH_HOST 'echo Hello'

SSH_USER=${SSH_USER:-maroro}
SSH_HOST=${SSH_HOST:-172.30.0.61}
SSH_PORT=${SSH_PORT:-22}
BRANCH=${BRANCH:-main}
PROJECT_PATH=${PROJECT_PATH:-/home/${SSH_USER}/levitiis}
RUN_TESTS=${RUN_TESTS:-false}

echo "Deploy para $SSH_USER@$SSH_HOST"
echo "Projeto remoto: $PROJECT_PATH"
echo "Branch: $BRANCH"

REMOTE_CMDS=$(cat <<'REMOTE
set -e
echo "[remote] Entrando em $PROJECT_PATH"
cd "$PROJECT_PATH"
echo "[remote] Atualizando repositório"
git fetch --all --prune
git checkout "$BRANCH" || git switch -c "$BRANCH" "origin/$BRANCH"
git reset --hard "origin/$BRANCH"
git pull origin "$BRANCH"

if [ -f docker-compose.yml ]; then
  echo "[remote] docker-compose.yml encontrado — usando Docker Compose"
  docker-compose pull || true
  docker-compose up -d --build
  echo "[remote] docker-compose up concluído"
else
  if [ -f package.json ]; then
    echo "[remote] Instalando dependências (npm ci)"
    npm ci --prefer-offline --no-audit --no-fund
    if [ "$RUN_TESTS" = "true" ]; then
      echo "[remote] Executando testes (vitest)"
      npm run test:run || true
    fi
    echo "[remote] Gerando build (npm run build)"
    npm run build || true
    # Se pm2 estiver instalado, reiniciar processos gerenciados
    if command -v pm2 >/dev/null 2>&1; then
      echo "[remote] Reiniciando processos pm2"
      pm2 restart all || true
    fi
  else
    echo "[remote] Nenhum package.json ou docker-compose.yml encontrado — nada para fazer"
  fi
fi

echo "[remote] Deploy finalizado"
REMOTE
)

echo "Executando comandos remotos via SSH..."

# Executa os comandos remotos via SSH
ssh -p "$SSH_PORT" "$SSH_USER@$SSH_HOST" "bash -s" <<EOF
PROJECT_PATH="$PROJECT_PATH"
BRANCH="$BRANCH"
RUN_TESTS="$RUN_TESTS"
$REMOTE_CMDS
EOF

echo "Deploy script finalizado. Verifique logs e status no servidor remoto." 
