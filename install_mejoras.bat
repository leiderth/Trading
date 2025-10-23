@echo off
echo ========================================
echo  INSTALACION DE MEJORAS V3.0
echo  Trading System Pro
echo ========================================
echo.

echo [1/4] Instalando dependencias de Binance Futures...
.\venv\Scripts\python.exe -m pip install python-binance --quiet
if %errorlevel% neq 0 (
    echo ERROR: No se pudo instalar python-binance
    pause
    exit /b 1
)
echo OK - python-binance instalado

echo.
echo [2/4] Verificando dependencias de IA...
.\venv\Scripts\python.exe -m pip install torch scipy scikit-learn --quiet
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar dependencias de IA
    pause
    exit /b 1
)
echo OK - Dependencias de IA verificadas

echo.
echo [3/4] Creando directorios necesarios...
if not exist "assets" mkdir assets
if not exist "models" mkdir models
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups
echo OK - Directorios creados

echo.
echo [4/4] Verificando instalacion...
.\venv\Scripts\python.exe -c "import binance; import torch; import scipy; print('Todas las dependencias instaladas correctamente')"
if %errorlevel% neq 0 (
    echo ERROR: Verificacion fallida
    pause
    exit /b 1
)

echo.
echo ========================================
echo  INSTALACION COMPLETADA
echo ========================================
echo.
echo Mejoras instaladas:
echo  - Binance Futures (Apalancamiento)
echo  - IA Avanzada (5 modelos)
echo  - 130+ Indicadores tecnicos
echo  - Aprendizaje continuo
echo  - Interfaz moderna
echo.
echo Para iniciar la aplicacion:
echo   start_trading_app.bat
echo.
echo Documentacion:
echo   MEJORAS_FINALES_V3.md
echo.
pause
