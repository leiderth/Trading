# Trading System Pro V3.0 - Setup Script
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " INSTALACION TRADING SYSTEM PRO V3.0" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Instalar python-binance
Write-Host "[1/5] Instalando python-binance..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe -m pip install python-binance --quiet --disable-pip-version-check
if ($LASTEXITCODE -eq 0) {
    Write-Host "  OK - python-binance instalado" -ForegroundColor Green
} else {
    Write-Host "  ERROR - No se pudo instalar python-binance" -ForegroundColor Red
    exit 1
}

# Paso 2: Verificar torch
Write-Host "[2/5] Verificando torch..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe -c "import torch; print('  OK - torch version:', torch.__version__)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Instalando torch..." -ForegroundColor Yellow
    & .\venv\Scripts\python.exe -m pip install torch --quiet --disable-pip-version-check
}

# Paso 3: Verificar scipy
Write-Host "[3/5] Verificando scipy..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe -c "import scipy; print('  OK - scipy version:', scipy.__version__)"
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Instalando scipy..." -ForegroundColor Yellow
    & .\venv\Scripts\python.exe -m pip install scipy --quiet --disable-pip-version-check
}

# Paso 4: Crear directorios
Write-Host "[4/5] Creando directorios..." -ForegroundColor Yellow
$dirs = @("assets", "models", "logs", "backups")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Creado: $dir" -ForegroundColor Green
    } else {
        Write-Host "  Existe: $dir" -ForegroundColor Gray
    }
}

# Paso 5: Verificar instalación
Write-Host "[5/5] Verificando instalacion..." -ForegroundColor Yellow
& .\venv\Scripts\python.exe -c @"
import sys
try:
    import binance
    import torch
    import scipy
    import sklearn
    print('  OK - Todas las dependencias instaladas correctamente')
    sys.exit(0)
except ImportError as e:
    print(f'  ERROR - Falta dependencia: {e}')
    sys.exit(1)
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host " INSTALACION COMPLETADA" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Mejoras instaladas:" -ForegroundColor Cyan
    Write-Host "  - Binance Futures (Apalancamiento)" -ForegroundColor White
    Write-Host "  - IA Avanzada (5 modelos)" -ForegroundColor White
    Write-Host "  - 130+ Indicadores tecnicos" -ForegroundColor White
    Write-Host "  - Aprendizaje continuo" -ForegroundColor White
    Write-Host "  - Interfaz moderna" -ForegroundColor White
    Write-Host ""
    Write-Host "Para iniciar:" -ForegroundColor Yellow
    Write-Host "  .\start_trading_app.bat" -ForegroundColor White
    Write-Host ""
    Write-Host "Documentacion:" -ForegroundColor Yellow
    Write-Host "  INICIO_RAPIDO_V3.md" -ForegroundColor White
    Write-Host "  MEJORAS_FINALES_V3.md" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: La instalacion fallo" -ForegroundColor Red
    Write-Host "Por favor revisa los errores arriba" -ForegroundColor Red
    exit 1
}
