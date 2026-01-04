# Installation Script for Tsuana 3D World Generator
# Run this with: .\install.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TSUANA 3D World Generator" -ForegroundColor Cyan
Write-Host "  Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/5] Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python (\d+)\.(\d+)") {
    $major = [int]$matches[1]
    $minor = [int]$matches[2]
    if ($major -ge 3 -and $minor -ge 8) {
        Write-Host "  ✓ Python $major.$minor detected" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Python 3.8+ required (found $major.$minor)" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✗ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "[2/5] Installing Python packages..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Setup .env file
Write-Host ""
Write-Host "[3/5] Setting up environment file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "  ⚠ .env file already exists" -ForegroundColor Yellow
    $response = Read-Host "  Overwrite? (y/n)"
    if ($response -eq "y") {
        Copy-Item ".env.template" ".env" -Force
        Write-Host "  ✓ .env file created" -ForegroundColor Green
    } else {
        Write-Host "  → Keeping existing .env" -ForegroundColor Yellow
    }
} else {
    Copy-Item ".env.template" ".env"
    Write-Host "  ✓ .env file created" -ForegroundColor Green
}

# Create output directory
Write-Host ""
Write-Host "[4/5] Creating output directory..." -ForegroundColor Yellow
if (!(Test-Path "output")) {
    New-Item -ItemType Directory -Path "output" | Out-Null
    Write-Host "  ✓ output/ directory created" -ForegroundColor Green
} else {
    Write-Host "  → output/ directory already exists" -ForegroundColor Yellow
}

# Run setup check
Write-Host ""
Write-Host "[5/5] Verifying installation..." -ForegroundColor Yellow
python setup_check.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Installation Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Configure .env file (optional - uses defaults)" -ForegroundColor White
Write-Host "     Copy-Item .env.template .env" -ForegroundColor Gray
Write-Host "     Edit LOCAL_LLM_MODEL if needed" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Start the API server:" -ForegroundColor White
Write-Host "     uvicorn app.api:app --host 0.0.0.0 --port 8000" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Run example:" -ForegroundColor White
Write-Host "     python examples/generate_world_example.py" -ForegroundColor Gray
Write-Host ""
Write-Host "📖 Read README.md for full documentation" -ForegroundColor Cyan
Write-Host "🚀 Read QUICKSTART.md for quick start guide" -ForegroundColor Cyan
Write-Host ""
