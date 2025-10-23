@echo off
echo ======================================================================
echo INICIANDO TRADING SYSTEM PRO
echo ======================================================================
echo.

cd /d %~dp0

echo [1/3] Activando entorno virtual...
call venv\Scripts\activate

echo [2/3] Iniciando API REST...
start "Trading API" cmd /k "venv\Scripts\activate && python run_api.py"

echo [3/3] Esperando 5 segundos...
timeout /t 5 /nobreak > nul

echo [4/4] Iniciando aplicacion de escritorio...
start "Trading App" cmd /k "venv\Scripts\activate && python desktop_app.py"

echo.
echo ======================================================================
echo SISTEMA INICIADO
echo ======================================================================
echo API: http://127.0.0.1:8000
echo Docs: http://127.0.0.1:8000/docs
echo ======================================================================
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause > nul
