# ============================================
# setup.ps1 - Full Project Setup Script
# ============================================
Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Indian Journal Citation Parser Setup   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python version
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "❌ Python not found! Please install Python 3.10+" -ForegroundColor Red
    exit 1
}
$ver = python --version 2>&1
Write-Host "✅ Found: $ver" -ForegroundColor Green

# Create venv
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate and install
Write-Host "📥 Installing dependencies..." -ForegroundColor Yellow
& .\venv\Scripts\pip install -r requirements.txt --quiet

# Create .env if not exists
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️  .env file created from template. Add your OPENAI_API_KEY!" -ForegroundColor Yellow
} else {
    Write-Host "✅ .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║           Setup Complete! 🎉              ║" -ForegroundColor Green
Write-Host "╠══════════════════════════════════════════╣" -ForegroundColor Green
Write-Host "║  Start server:  python main.py           ║" -ForegroundColor White
Write-Host "║  OR double-click: start.bat              ║" -ForegroundColor White
Write-Host "║                                          ║" -ForegroundColor White
Write-Host "║  Frontend:  http://localhost:8000        ║" -ForegroundColor Cyan
Write-Host "║  API Docs:  http://localhost:8000/docs   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
