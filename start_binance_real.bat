@echo off
cls
echo ========================================
echo  TRADEPRO - TRADING REAL CON BINANCE
echo  MODO PRODUCCION
echo ========================================
echo.
echo ADVERTENCIA: Este modo usa tu API Key REAL de Binance
echo Los trades seran REALES y usaran tu dinero real
echo.
echo Asegurate de:
echo  1. Tener tu API Key de Binance lista
echo  2. API Key tiene permisos de trading
echo  3. Tienes fondos en tu cuenta
echo.
pause
echo.

echo [1/2] Iniciando API Backend (Puerto 8001)...
start "TradePro API - REAL" cmd /k ".\venv\Scripts\python.exe -m uvicorn src.api.trading_api:app --reload --port 8001"

echo Esperando a que API inicie...
timeout /t 5 /nobreak >nul

echo.
echo [2/2] Iniciando GUI...
start "TradePro GUI - REAL" .\venv\Scripts\python.exe launch_app.py

echo.
echo ========================================
echo  SISTEMA INICIADO - MODO REAL
echo ========================================
echo.
echo API REST: http://127.0.0.1:8001
echo API Docs: http://127.0.0.1:8001/docs
echo.
echo PASOS SIGUIENTES:
echo 1. En la GUI, ve a Settings
echo 2. Ingresa tu API Key de Binance REAL
echo 3. Ingresa tu API Secret
echo 4. DESMARCA "Usar Testnet" (IMPORTANTE)
echo 5. Click "Conectar Broker"
echo 6. Ve a Trading y ejecuta trades REALES
echo.
echo IMPORTANTE: Los trades seran REALES
echo.
pause
