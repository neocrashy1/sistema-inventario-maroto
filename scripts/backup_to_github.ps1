<#
.SYNOPSIS
  Cria um backup do repositório atual no GitHub (push mirror).

.DESCRIPTION
  Este script cria um novo repositório no GitHub para o usuário autenticado
  (token em GITHUB_TOKEN) e empurra um mirror completo do repositório atual.

.NOTES
  - Requer: git, PowerShell 5.1+ / PowerShell Core
  - Exige a variável de ambiente GITHUB_TOKEN com permissões repo (criar repositórios e push).
  - Uso seguro: prefira tokens com escopo mínimo e remova o token do ambiente após uso.

.EXAMPLE
  # Define token e executa (substitua pelo seu token em variável de ambiente)
  $env:GITHUB_TOKEN = 'ghp_XXXX'
  .\backup_to_github.ps1 -GitHubUser 'neocrashy1' -RepoName 'levitiiis-backup'
#>

param(
  [Parameter(Mandatory=$false)] [string]$RepoUrl,
  [Parameter(Mandatory=$false)] [string]$ArchiveName = "backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').zip",
  [switch]$UploadRelease
)

Set-StrictMode -Version Latest

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  Write-Error "git não encontrado no PATH. Instale o git antes de rodar este script."; exit 2
}

# Se RepoUrl não for informado, pede ao usuário
if (-not $RepoUrl) {
  $RepoUrl = Read-Host "Informe a URL remota do repositório (ex: https://github.com/owner/repo.git or git@github.com:owner/repo.git)"
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$tmp = Join-Path $env:TEMP "repo_backups_${timestamp}"
New-Item -ItemType Directory -Path $tmp -Force | Out-Null

Write-Host "Criando mirror do repositório atual em: $tmp" -ForegroundColor Cyan

# Cria um clone mirror (inclui todos refs)
& git clone --mirror . $tmp
if ($LASTEXITCODE -ne 0) { Write-Error "Falha ao criar mirror git."; exit 4 }

Write-Host "Configurando remote origin para: $RepoUrl" -ForegroundColor Cyan

Push-Location $tmp
try {
  # Usa o credential helper configurado no git (GCM ou outro). Não colocamos token na URL.
  & git remote set-url origin $RepoUrl
  if ($LASTEXITCODE -ne 0) { Write-Error "Falha ao setar remote URL."; exit 6 }

  Write-Host "Efetuando push --mirror (pode solicitar credenciais via Git Credential Manager ou usar SSH key)..." -ForegroundColor Yellow
  & git push --mirror origin
  if ($LASTEXITCODE -ne 0) { Write-Error "Falha no git push --mirror."; exit 7 }
  Write-Host "Push --mirror concluído." -ForegroundColor Green
}
finally {
  Pop-Location
}

# Gerar arquivo ZIP dos artefatos extras (working tree, sem .git)
$archivePath = Join-Path $tmp $ArchiveName
Write-Host "Gerando arquivo ZIP do working tree em: $archivePath" -ForegroundColor Cyan

try {
  # Usa git archive para criar snapshot do HEAD
  & git archive --format=zip -o $archivePath HEAD
  if ($LASTEXITCODE -ne 0) {
    # fallback: compacta manualmente excluindo .git
    Write-Host "git archive falhou — fallback para Compress-Archive" -ForegroundColor Yellow
    $workDir = (Get-Location).Path
    $files = Get-ChildItem -Path $workDir -Recurse -Force | Where-Object { $_.FullName -notmatch '\.git' }
    Compress-Archive -Path $files -DestinationPath $archivePath -Force
  }
}
catch {
  Write-Warning "Falha ao criar arquivo ZIP: $_. Exception.Message"
}

Write-Host "Arquivo de backup disponível em: $archivePath" -ForegroundColor Green

# Se o usuário quiser, e se existir GITHUB_TOKEN, podemos publicar o ZIP como release asset
if ($UploadRelease.IsPresent) {
  if (-not $env:GITHUB_TOKEN) {
    Write-Warning "GITHUB_TOKEN não definido — não será possível criar release automatizado. Pule ou defina a variável e rode novamente com -UploadRelease." 
  }
  else {
    # Tenta extrair owner/repo da RepoUrl
    $ownerRepo = $null
    if ($RepoUrl -match 'github.com[:/](.+?)/(.+?)(?:\.git)?$') {
      $owner = $Matches[1]; $repo = $Matches[2]; $ownerRepo = "$owner/$repo"
    }

    if ($ownerRepo) {
      Write-Host "Criando release no repositório $ownerRepo e fazendo upload do asset..." -ForegroundColor Cyan
      $headers = @{ Authorization = "token $env:GITHUB_TOKEN"; 'User-Agent' = 'backup-script' }
      $body = @{ tag_name = "backup-$timestamp"; name = "backup-$timestamp" } | ConvertTo-Json
      try {
        $release = Invoke-RestMethod -Method Post -Uri "https://api.github.com/repos/$ownerRepo/releases" -Headers $headers -Body $body -ContentType 'application/json'
        $uploadUrl = $release.upload_url -replace '\{.+\}$',''
        $fileBytes = [System.IO.File]::ReadAllBytes($archivePath)
        $uploadResp = Invoke-RestMethod -Method Post -Uri "$uploadUrl?name=$(Split-Path $archivePath -Leaf)" -Headers @{ Authorization = "token $env:GITHUB_TOKEN" } -InFile $archivePath -ContentType 'application/zip'
        Write-Host "Release criado e asset enviado: $($release.html_url)" -ForegroundColor Green
      }
      catch {
        Write-Warning "Falha ao criar release/upload asset: $_"
      }
    }
    else {
      Write-Warning "Não foi possível extrair owner/repo da URL fornecida. Upload via API cancelado. URL: $RepoUrl"
    }
  }
}

Write-Host "Backup (mirror + artefato ZIP) finalizado." -ForegroundColor Green
