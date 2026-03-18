# setup.ps1 - Script de Setup Automatizado do Bot Júlio V3 (Telegram)
# Execute este script como Administrador no PowerShell dentro da pasta bot_julio

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=========================================="  -ForegroundColor Cyan
Write-Host " BOT JÚLIO V3 — Setup Automatizado" -ForegroundColor Cyan
Write-Host "=========================================="  -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "1/5 Verificando instalação do Python..." -ForegroundColor Yellow
$pyPath = @(
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python312\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python311\python.exe",
    "C:\Users\$env:USERNAME\AppData\Local\Programs\Python\Python310\python.exe",
    "C:\Python312\python.exe",
    "C:\Python311\python.exe",
    "C:\Python310\python.exe"
)

$pythonExe = $null
foreach ($path in $pyPath) {
    if (Test-Path $path) {
        $pythonExe = $path
        break
    }
}

if (-not $pythonExe) {
    Write-Host ""
    Write-Host "ERRO: Python não encontrado!" -ForegroundColor Red
    Write-Host "Instale o Python 3.11 ou superior em: https://www.python.org/downloads/" -ForegroundColor Red
    Write-Host "IMPORTANTE: Marque a opção 'Add Python to PATH' durante a instalação." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "Python encontrado em: $pythonExe" -ForegroundColor Green
& $pythonExe --version

# 2. Criar ambiente virtual
Write-Host ""
Write-Host "2/5 Criando ambiente virtual (venv)..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "venv já existe. Pulando criação." -ForegroundColor DarkGray
} else {
    & $pythonExe -m venv venv
    Write-Host "venv criado com sucesso!" -ForegroundColor Green
}

# 3. Ativar e instalar dependências
Write-Host ""
Write-Host "3/5 Instalando dependências do requirements.txt..." -ForegroundColor Yellow
& .\venv\Scripts\pip.exe install -r requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erro ao instalar pacotes. Verifique a conexão com a internet." -ForegroundColor Red
    exit 1
}
Write-Host "Dependências instaladas com sucesso!" -ForegroundColor Green

# 4. Configurar .env
Write-Host ""
Write-Host "4/5 Verificando .env..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ".env criado a partir do .env.example" -ForegroundColor Green
    Write-Host ""
    Write-Host "==> AÇÃO NECESSÁRIA: Edite o arquivo .env e preencha:" -ForegroundColor Red
    Write-Host "   - ANTHROPIC_API_KEY" -ForegroundColor White
    Write-Host "   - OPENAI_API_KEY" -ForegroundColor White
    Write-Host "   - TELEGRAM_BOT_TOKEN" -ForegroundColor White
    Write-Host "   - TELEGRAM_ADMIN_USER_ID" -ForegroundColor White
    Write-Host "   - DATABASE_URL" -ForegroundColor White
    Write-Host "   - MONGODB_URI" -ForegroundColor White
    Write-Host "   - REDIS_URL" -ForegroundColor White
} else {
    Write-Host ".env já existe. Não sobrescrito." -ForegroundColor DarkGray
}

# 5. Instruções Finais
Write-Host ""
Write-Host "5/5 Próximos passos manuais:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  a) Certifique-se que PostgreSQL, MongoDB e Redis estão rodando." -ForegroundColor White
Write-Host "  b) Conecte ao PostgreSQL e execute o schema:" -ForegroundColor White
Write-Host "       psql -U seu_usuario -d botjulio_test -f app\db\migrations\001_initial.sql" -ForegroundColor Cyan
Write-Host ""
Write-Host "  c) Execute os seeds:" -ForegroundColor White
Write-Host "       .\venv\Scripts\python.exe scripts\seed_participants.py" -ForegroundColor Cyan
Write-Host "       .\venv\Scripts\python.exe scripts\seed_knowledge.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  d) Inicie o bot:" -ForegroundColor White
Write-Host "       .\venv\Scripts\python.exe app\main.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  e) No Telegram, acesse o bot e use /start para começar o onboarding." -ForegroundColor White
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " Setup finalizado!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
