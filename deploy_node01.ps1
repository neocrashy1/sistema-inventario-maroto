<#
k

.SYNOPSIS
  Script de deploy para node01 (172.30.0.61) usando OpenSSH nativo do Windows.

.USAGE
  # Exemplo usando parâmetros posix no PowerShell
  .\deploy_node01.ps1 -SSHUser 'maroro' -SSHHost '172.30.0.61' -ProjectPath '/home/maroro/levitiis' -Branch 'main' -RunTests:$false

  # Exemplo usando variáveis de ambiente (PS):
  $env:SSH_USER='maroro'; $env:SSH_HOST='172.30.0.61'; $env:PROJECT_PATH='/home/maroro/levitiis'; $env:BRANCH='main'
  .\deploy_node01.ps1

# NOTES
# - Recomenda-se autenticação por chave SSH. Não deixar senhas em scripts.
# - O script envia um bloco de comandos para o servidor remoto que atualiza o código,
#   detecta `docker-compose.yml` e usa Docker se presente; caso contrário executa npm ci/build.
# - Se precisar autenticar por senha em ambiente controlado, execute o script manualmente
#   abrindo uma sessão SSH e colando os comandos remotos.
#>

param(
  [string]$SSHUser = $(if ($env:SSH_USER) { $env:SSH_USER } else { 'maroro' }),
  [string]$SSHHost = $(if ($env:SSH_HOST) { $env:SSH_HOST } else { '172.30.0.61' }),
  [int]$SSHPort = $(if ($env:SSH_PORT) { [int]$env:SSH_PORT } else { 22 }),
  [string]$Branch = $(if ($env:BRANCH) { $env:BRANCH } else { 'main' }),
  [string]$ProjectPath = $(if ($env:PROJECT_PATH) { $env:PROJECT_PATH } else { "/home/maroto/projects/Levitiisl/current" }),
  [switch]$RunTests
)

Set-StrictMode -Version Latest

Write-Host "Deploy para $SSHUser@$SSHHost`:$SSHPort" -ForegroundColor Cyan
Write-Host "Projeto remoto: $ProjectPath" -ForegroundColor Cyan
Write-Host "Branch: $Branch" -ForegroundColor Cyan

$remoteScript = @'
set -e
echo "[remote] Entrando em $PROJECT_PATH"
cd "$PROJECT_PATH" || { echo "[remote] ERRO: não foi possível entrar em $PROJECT_PATH"; exit 2; }

if [ -d .git ]; then
  echo "[remote] .git encontrado — atualizando repositório via git"
  git fetch --all --prune || true
  if git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
    git checkout "$BRANCH" || true
  else
    git checkout -b "$BRANCH" || true
  fi
  git reset --hard "origin/$BRANCH" || true
  git pull origin "$BRANCH" || true
else
  echo "[remote] .git NÃO encontrado — supondo release/copied files (pulando git)"
fi

if [ -f docker-compose.yml ]; then
  echo "[remote] docker-compose.yml encontrado — usando Docker Compose"
  # tenta rodar docker-compose; se não existir, tenta docker compose
  if command -v docker-compose >/dev/null 2>&1; then
    docker-compose pull || true
    docker-compose up -d --build || true
  else
    if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
      docker compose pull || true
      docker compose up -d --build || true
    else
      echo "[remote] Aviso: Docker Compose não encontrado — não será possível subir containers" >&2
    fi
  fi
  echo "[remote] docker-compose (ou docker compose) concluído"
else
  if [ -f package.json ]; then
    echo "[remote] package.json encontrado — instalando dependências e construindo"
    npm ci --prefer-offline --no-audit --no-fund || true
    if [ "${RUN_TESTS}" = "true" ]; then
      echo "[remote] Executando testes (vitest)"
      npm run test:run || true
    fi
    echo "[remote] Gerando build (npm run build)"
    npm run build || true
    if command -v pm2 >/dev/null 2>&1; then
      echo "[remote] Reiniciando processos pm2"
      pm2 restart all || true
    fi
  else
    echo "[remote] Nenhum package.json ou docker-compose.yml encontrado — nada para fazer aqui"
  fi
fi

echo "[remote] Deploy finalizado"
'@

# Substituir variáveis no script remoto com valores passados
$remoteScript = $remoteScript -replace '\$PROJECT_PATH', ($ProjectPath.Replace('\','\\'))
$remoteScript = $remoteScript -replace '\$BRANCH', $Branch
$remoteScript = $remoteScript -replace '\$RUN_TESTS', ($(if ($RunTests) { 'true' } else { 'false' }))

# Normalizar quebras de linha para LF (importante para execução remota via stdin)
$remoteScript = $remoteScript -replace "`r`n", "`n"

Write-Host "Executando comandos remotos via SSH..." -ForegroundColor Yellow

# Enviar o script remoto via stdin para o ssh (usamos $remoteScript diretamente)

# Construir comando SSH
$sshCommand = "ssh -p $SSHPort $SSHUser@$SSHHost 'bash -s'"

Write-Host "Comando: $sshCommand" -ForegroundColor DarkGray

function Invoke-RemoteScriptOverSsh {
  param(
    [string]$ShellCmd # e.g. "bash -s" or "sh -s"
  )

  $startInfo = New-Object System.Diagnostics.ProcessStartInfo
  $startInfo.FileName = 'ssh'
  $startInfo.Arguments = "-p $SSHPort $SSHUser@$SSHHost '$ShellCmd'"
  $startInfo.RedirectStandardInput = $true
  $startInfo.RedirectStandardOutput = $true
  $startInfo.RedirectStandardError = $true
  $startInfo.UseShellExecute = $false
  $startInfo.CreateNoWindow = $true

  $proc = New-Object System.Diagnostics.Process
  $proc.StartInfo = $startInfo
  $proc.Start() | Out-Null

  $stdIn = $proc.StandardInput
  $stdIn.Write($remoteScript)
  $stdIn.Close()

  $allOut = New-Object System.Collections.Generic.List[string]
  $allErr = New-Object System.Collections.Generic.List[string]

  while (-not $proc.HasExited) {
    Start-Sleep -Milliseconds 200
    while (-not $proc.StandardOutput.EndOfStream) {
      $line = $proc.StandardOutput.ReadLine()
      if ($line) { $allOut.Add($line); Write-Host "[remote] $line" }
    }
    while (-not $proc.StandardError.EndOfStream) {
      $eline = $proc.StandardError.ReadLine()
      if ($eline) { $allErr.Add($eline); Write-Host "[remote][ERR] $eline" -ForegroundColor Red }
    }
  }

  while (-not $proc.StandardOutput.EndOfStream) { $line = $proc.StandardOutput.ReadLine(); $allOut.Add($line); Write-Host "[remote] $line" }
  while (-not $proc.StandardError.EndOfStream) { $eline = $proc.StandardError.ReadLine(); $allErr.Add($eline); Write-Host "[remote][ERR] $eline" -ForegroundColor Red }

  return @{ ExitCode = $proc.ExitCode; StdOut = $allOut; StdErr = $allErr }
}

try {
  # Primeiro tenta usar bash - se não existir, faz fallback para sh
  $result = Invoke-RemoteScriptOverSsh -ShellCmd 'bash -s'
  if ($result.ExitCode -ne 0) {
    # detecta 'command not found' ou código 127 para fallback
    $errText = ($result.StdErr -join "`n")
    if ($errText -match 'command not found' -or $result.ExitCode -eq 127) {
      Write-Host "bash não disponível no remoto, tentando fallback para sh" -ForegroundColor Yellow
      $result2 = Invoke-RemoteScriptOverSsh -ShellCmd 'sh -s'
      if ($result2.ExitCode -ne 0) {
        Write-Host "sh também falhou (tentando enviar script sem forçar shell — fallback final)" -ForegroundColor Yellow

        function Invoke-RemoteScriptOverSshNoShell {
          # envia o script para o ssh sem passar um comando shell explícito; isso deixa o shell de login ler do stdin
          $startInfo = New-Object System.Diagnostics.ProcessStartInfo
          $startInfo.FileName = 'ssh'
          $startInfo.Arguments = "-p $SSHPort $SSHUser@$SSHHost"
          $startInfo.RedirectStandardInput = $true
          $startInfo.RedirectStandardOutput = $true
          $startInfo.RedirectStandardError = $true
          $startInfo.UseShellExecute = $false
          $startInfo.CreateNoWindow = $true

          $proc = New-Object System.Diagnostics.Process
          $proc.StartInfo = $startInfo
          $proc.Start() | Out-Null

          $stdIn = $proc.StandardInput
          $stdIn.Write($remoteScript)
          $stdIn.Close()

          $allOut = New-Object System.Collections.Generic.List[string]
          $allErr = New-Object System.Collections.Generic.List[string]

          while (-not $proc.HasExited) {
            Start-Sleep -Milliseconds 200
            while (-not $proc.StandardOutput.EndOfStream) {
              $line = $proc.StandardOutput.ReadLine()
              if ($line) { $allOut.Add($line); Write-Host "[remote] $line" }
            }
            while (-not $proc.StandardError.EndOfStream) {
              $eline = $proc.StandardError.ReadLine()
              if ($eline) { $allErr.Add($eline); Write-Host "[remote][ERR] $eline" -ForegroundColor Red }
            }
          }

          while (-not $proc.StandardOutput.EndOfStream) { $line = $proc.StandardOutput.ReadLine(); $allOut.Add($line); Write-Host "[remote] $line" }
          while (-not $proc.StandardError.EndOfStream) { $eline = $proc.StandardError.ReadLine(); $allErr.Add($eline); Write-Host "[remote][ERR] $eline" -ForegroundColor Red }

          return @{ ExitCode = $proc.ExitCode; StdOut = $allOut; StdErr = $allErr }
        }

        $result3 = Invoke-RemoteScriptOverSshNoShell
        if ($result3.ExitCode -ne 0) {
          Write-Host "SSH (stdin) retornou código $($result3.ExitCode)" -ForegroundColor Red
          exit $result3.ExitCode
        }
      }
    }
    else {
      Write-Host "SSH (bash) retornou código $($result.ExitCode)" -ForegroundColor Red
      exit $result.ExitCode
    }
  }
}
catch {
  Write-Host "Falha ao executar SSH: $_" -ForegroundColor Red
  throw
}

Write-Host "Deploy PowerShell finalizado." -ForegroundColor Green
