@echo off
echo ========================================
echo  CONSTRUYENDO TRADEPRO.EXE
echo ========================================
echo.

echo Limpiando builds anteriores...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist TradePro.spec del TradePro.spec

echo.
echo Construyendo ejecutable...
.\venv\Scripts\python.exe -m PyInstaller ^
    --name TradePro ^
    --onefile ^
    --windowed ^
    --clean ^
    --optimize 2 ^
    src\gui\modern_trading_app.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Fallo al construir .exe
    pause
    exit /b 1
)

echo.
echo ========================================
echo  EXITO - TradePro.exe CREADO
echo ========================================
echo.
echo Ubicacion: dist\TradePro.exe
echo.
echo Puedes ejecutar: dist\TradePro.exe
echo.
pause
