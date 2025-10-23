@echo off
echo ========================================
echo  INICIANDO TRADEPRO COMPLETO
echo  Sistema de Trading Profesional
echo ========================================
echo.

echo [1/3] Iniciando API Backend...
start "TradePro API" cmd /k ".\venv\Scripts\python.exe -m uvicorn src.api.trading_api:app --reload --port 8001"

echo Esperando a que API inicie...
timeout /t 5 /nobreak >nul

echo.
echo [2/3] Iniciando GUI Moderna...
start "TradePro GUI" .\venv\Scripts\python.exe launch_app.py

echo.
echo [3/3] Sistema iniciado exitosamente
echo.
echo ========================================
echo  TRADEPRO EJECUTANDOSE
echo ========================================
echo.
echo API REST: http://127.0.0.1:8000
echo API Docs: http://127.0.0.1:8000/docs
echo GUI: Ventana abierta
echo.
echo Presiona cualquier tecla para cerrar todo el sistema...
pause >nul

echo.
echo Cerrando sistema...
taskkill /FI "WINDOWTITLE eq TradePro*" /F >nul 2>&1

echo Sistema cerrado.
timeout /t 2 /nobreak >nul
