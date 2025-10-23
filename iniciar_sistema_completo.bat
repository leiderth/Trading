@echo off
cls
echo ========================================
echo  INICIANDO TRADEPRO CON BINANCE REAL
echo ========================================
echo.
echo Tus credenciales ya estan configuradas
echo Conectando a Binance MAINNET (REAL)
echo.
echo IMPORTANTE: Se abriran 2 ventanas
echo 1. API Backend (NO CERRAR)
echo 2. Aplicacion TradePro
echo.
pause
echo.

echo [1/2] Iniciando API Backend en puerto 8001...
start "TradePro API" cmd /k "cd /d %~dp0 && .\venv\Scripts\python.exe -m uvicorn src.api.trading_api:app --reload --port 8001"

echo Esperando a que API inicie...
timeout /t 8 /nobreak >nul

echo.
echo [2/2] Iniciando TradePro GUI...
start "TradePro GUI" cmd /k "cd /d %~dp0 && .\venv\Scripts\python.exe launch_app.py"

echo.
echo ========================================
echo  SISTEMA INICIADO
echo ========================================
echo.
echo API: http://127.0.0.1:8001
echo Docs: http://127.0.0.1:8001/docs
echo.
echo PASOS EN LA APP:
echo 1. Ve a Settings
echo 2. Tus credenciales ya estan guardadas
echo 3. DESMARCA "Usar Testnet"
echo 4. Click "Conectar Broker"
echo 5. Espera 20 segundos
echo 6. Debe decir "Conectado" en verde
echo.
echo Para cerrar: Cierra ambas ventanas
echo.
pause
