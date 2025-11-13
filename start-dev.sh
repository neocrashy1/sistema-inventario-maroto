#!/usr/bin/env bash
set -euo pipefail

# start-dev.sh
# Script auxiliar para iniciar o frontend em modo desenvolvimento (Vite)
# Local: colocar em `SistemaAnaliseComputadores/` no servidor e executar a partir daí.
# Uso:
#   ./start-dev.sh [--branch BRANCH] [--background] [--port PORT]
# Exemplos:
#   ./start-dev.sh --branch feature/purchases
#   ./start-dev.sh --background --port 5173

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BRANCH="feature/purchases"
BACKGROUND=false
PORT=5173

while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch)
      BRANCH="$2"; shift 2;;
    --background)
      BACKGROUND=true; shift;;
    --port)
      PORT="$2"; shift 2;;
    -h|--help)
      sed -n '1,120p' "$0"; exit 0;;
    *)
      echo "Unknown arg: $1"; exit 1;;
  esac
done

echo "Project dir: $PROJECT_DIR"
echo "Branch: $BRANCH"
echo "Background: $BACKGROUND"
echo "Port: $PORT"

cd "$PROJECT_DIR"

if [ -d ".git" ]; then
  echo "Updating git repository..."
  git fetch --all --prune
  if git rev-parse --verify --quiet "$BRANCH" >/dev/null; then
    git checkout "$BRANCH"
  else
    git checkout -b "$BRANCH" origin/"$BRANCH" || true
  fi
  git pull --ff-only || true
fi

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js not found. Please install Node.js 18+ (recommended via nvm)." >&2
  exit 2
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Please install npm." >&2
  exit 2
fi

echo "Installing dependencies (using package-lock.json if present)..."
if [ -f package-lock.json ]; then
  npm ci --no-audit --no-fund
else
  npm install --no-audit --no-fund
fi

# Optional: export VITE_API_BASE_URL before running to point to backend
echo "Starting Vite dev server (host 0.0.0.0, port $PORT)"

if [ "$BACKGROUND" = true ]; then
  # Prefer tmux if available
  if command -v tmux >/dev/null 2>&1; then
    SESSION_NAME="levitii-dev"
    echo "Starting in tmux session '$SESSION_NAME'..."
    # If session exists, kill to start a fresh one
    if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
      echo "tmux session '$SESSION_NAME' already exists; killing it to restart"
      tmux kill-session -t "$SESSION_NAME"
    fi
    tmux new-session -d -s "$SESSION_NAME" "npx vite --host 0.0.0.0 --port '$PORT'"
    echo "Started tmux session '$SESSION_NAME'. Attach with: tmux attach -t $SESSION_NAME"
  else
    # Fallback to nohup
    LOGFILE="$HOME/levitii-dev.log"
    echo "tmux not found; starting with nohup, logs -> $LOGFILE"
    nohup npx vite --host 0.0.0.0 --port "$PORT" > "$LOGFILE" 2>&1 &
    echo "Started (PID: $!)"
    echo "To see logs: tail -f $LOGFILE"
  fi
else
  # Foreground (prints logs to terminal)
  npx vite --host 0.0.0.0 --port "$PORT"
fi
