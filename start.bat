@echo off
cls
echo ========================================
echo  TRADEPRO - INICIO COMPLETO
echo ========================================
echo.
echo Este script iniciara:
echo 1. API Backend (puerto 8001)
echo 2. TradePro GUI
echo.
echo IMPORTANTE:
echo - Se abriran 2 ventanas
echo - NO cierres la ventana de la API
echo - Espera 10 segundos antes de conectar
echo.
pause
cls

echo.
echo [1/2] Iniciando API Backend...
echo.
start "TradePro API - NO CERRAR" cmd /k "cd /d %~dp0 && .\venv\Scripts\python.exe -m uvicorn src.api.trading_api:app --reload --port 8001"

echo Esperando a que API inicie...
timeout /t 10 /nobreak >nul

echo.
echo [2/2] Iniciando TradePro GUI...
echo.
start "TradePro" cmd /k "cd /d %~dp0 && .\venv\Scripts\python.exe launch_app.py"

echo.
echo ========================================
echo  SISTEMA INICIADO
echo ========================================
echo.
echo Ventana 1: API Backend (NO CERRAR)
echo Ventana 2: TradePro GUI
echo.
echo PASOS SIGUIENTES:
echo 1. Espera 10 segundos
echo 2. En TradePro, ve a Settings
echo 3. Credenciales ya estan cargadas
echo 4. Click "Conectar Broker"
echo 5. Espera 30 segundos
echo 6. Debe decir "Conectado" en verde
echo.
echo API: http://127.0.0.1:8001
echo Docs: http://127.0.0.1:8001/docs
echo Health: http://127.0.0.1:8001/health
echo.
echo Presiona cualquier tecla para cerrar este mensaje...
pause >nul
