@echo off
title TradePro - Professional Trading Platform
cls

echo ========================================
echo  TRADEPRO v4.0
echo  Professional Trading Platform
echo ========================================
echo.
echo Iniciando...
echo.

REM Verificar que venv existe
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Entorno virtual no encontrado
    echo.
    echo Por favor ejecuta primero: install_all.bat
    echo.
    pause
    exit /b 1
)

REM Iniciar API en segundo plano
echo [1/2] Iniciando API Backend...
start /B "TradePro API" venv\Scripts\python.exe -m uvicorn src.api.trading_api:app --host 127.0.0.1 --port 8000 2>nul

REM Esperar a que API inicie
timeout /t 3 /nobreak >nul

REM Iniciar GUI
echo [2/2] Iniciando GUI...
echo.
venv\Scripts\python.exe launch_app.py

REM Al cerrar GUI, matar API
echo.
echo Cerrando sistema...
taskkill /F /FI "WINDOWTITLE eq TradePro API*" >nul 2>&1

exit
