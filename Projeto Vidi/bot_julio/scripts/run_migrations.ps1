# ============================================================
# Bot Júlio v4.0 — Script de Migration Supabase
# Aplica as 3 migrations em ordem via psql ou exibe no terminal
# para copiar no SQL Editor do Supabase
# ============================================================

param(
    [switch]$ShowOnly   # Se passado, só exibe o SQL sem executar
)

$MigrationsDir = "$PSScriptRoot\..\app\db\migrations"

$files = @(
    "001_initial.sql",
    "002_whatsapp_migration.sql",
    "003_user_types.sql"
)

# Adiciona tabela chat_sessions (substitui MongoDB)
$chatSessionsSQL = @"
-- Migration 004: Tabela chat_sessions (histórico de sessão em JSONB)
CREATE TABLE IF NOT EXISTS chat_sessions (
    session_id       TEXT        UNIQUE NOT NULL,
    participant_id   UUID        REFERENCES participants(id) ON DELETE SET NULL,
    messages         JSONB       NOT NULL DEFAULT '[]',
    last_activity    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_participant
    ON chat_sessions(participant_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_activity
    ON chat_sessions(last_activity DESC);
"@

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Bot Julio v4.0 — Migrations Supabase" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if ($ShowOnly) {
    Write-Host ">>> Modo ShowOnly: exibindo SQL para copiar no Supabase`n" -ForegroundColor Yellow

    foreach ($f in $files) {
        $path = Join-Path $MigrationsDir $f
        Write-Host "---------- $f ----------" -ForegroundColor Magenta
        Get-Content $path -Encoding UTF8
        Write-Host ""
    }

    Write-Host "---------- 004_chat_sessions.sql ----------" -ForegroundColor Magenta
    Write-Host $chatSessionsSQL
    Write-Host ""
    Write-Host ">>> Copie o SQL acima e rode no SQL Editor do Supabase." -ForegroundColor Green
    Write-Host ">>> https://supabase.com/dashboard/project/qinkglwwtujaurkagjri/sql" -ForegroundColor Green
    exit 0
}

# Verificar DATABASE_URL no .env
$envFile = "$PSScriptRoot\..\..\.env"
if (-not (Test-Path $envFile)) {
    $envFile = "$PSScriptRoot\..\\.env"
}

$dbUrl = $null
if (Test-Path $envFile) {
    $lines = Get-Content $envFile -Encoding UTF8
    foreach ($line in $lines) {
        if ($line -match "^DATABASE_URL\s*=\s*(.+)$") {
            $dbUrl = $Matches[1].Trim().Trim('"').Trim("'")
            break
        }
    }
}

if (-not $dbUrl) {
    Write-Host "DATABASE_URL nao encontrada no .env" -ForegroundColor Red
    Write-Host "Exibindo SQL para aplicar manualmente no Supabase..." -ForegroundColor Yellow
    & $PSCommandPath -ShowOnly
    exit 1
}

# Checar se psql existe
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psqlPath) {
    Write-Host "psql nao encontrado no PATH." -ForegroundColor Red
    Write-Host "Exibindo SQL para aplicar manualmente no Supabase..." -ForegroundColor Yellow
    & $PSCommandPath -ShowOnly
    exit 1
}

Write-Host "Banco: $($dbUrl.Substring(0, [Math]::Min(50, $dbUrl.Length)))..." -ForegroundColor Gray
Write-Host ""

foreach ($f in $files) {
    $path = Join-Path $MigrationsDir $f
    Write-Host ">>> Aplicando $f ..." -ForegroundColor Cyan
    $result = psql $dbUrl -f $path 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "    OK" -ForegroundColor Green
    } else {
        Write-Host "    ERRO:" -ForegroundColor Red
        Write-Host $result
    }
}

# Migration 004 inline
Write-Host ">>> Aplicando 004_chat_sessions.sql ..." -ForegroundColor Cyan
$result = $chatSessionsSQL | psql $dbUrl 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "    OK" -ForegroundColor Green
} else {
    Write-Host "    ERRO:" -ForegroundColor Red
    Write-Host $result
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  Migrations concluidas! Proximo passo:" -ForegroundColor Green
Write-Host "  cd bot_julio && .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  python scripts/seed_participants.py" -ForegroundColor White
Write-Host "  python scripts/seed_knowledge.py" -ForegroundColor White
Write-Host "============================================================" -ForegroundColor Cyan
