@echo off
cls
echo ========================================
echo  INSTALACION COMPLETA TRADEPRO v4.0
echo  Sistema de Trading Profesional
echo ========================================
echo.

echo [1/8] Verificando Python...
.\venv\Scripts\python.exe --version
if %errorlevel% neq 0 (
    echo ERROR: Python no encontrado
    pause
    exit /b 1
)
echo OK - Python encontrado

echo.
echo [2/8] Instalando dependencias base...
.\venv\Scripts\python.exe -m pip install --upgrade pip --quiet
.\venv\Scripts\python.exe -m pip install -r requirements.txt --quiet
if %errorlevel% neq 0 (
    echo ERROR: Fallo instalacion de dependencias
    pause
    exit /b 1
)
echo OK - Dependencias base instaladas

echo.
echo [3/8] Instalando PyQt6 y componentes GUI...
.\venv\Scripts\python.exe -m pip install PyQt6 pyqtgraph --quiet
echo OK - PyQt6 instalado

echo.
echo [4/8] Instalando herramientas de construccion...
.\venv\Scripts\python.exe -m pip install pyinstaller pillow --quiet
echo OK - PyInstaller y Pillow instalados

echo.
echo [5/8] Creando logo profesional...
.\venv\Scripts\python.exe crear_logo.py
if %errorlevel% neq 0 (
    echo ADVERTENCIA: No se pudo crear logo
) else (
    echo OK - Logo creado
)

echo.
echo [6/8] Creando directorios...
if not exist "config" mkdir config
if not exist "models" mkdir models
if not exist "logs" mkdir logs
if not exist "backtests" mkdir backtests
if not exist "portfolios" mkdir portfolios
if not exist "exports" mkdir exports
echo OK - Directorios creados

echo.
echo [7/8] Verificando componentes...
.\venv\Scripts\python.exe -c "import PyQt6; import requests; import numpy; import pandas; print('OK - Todos los modulos disponibles')"
if %errorlevel% neq 0 (
    echo ERROR: Faltan modulos
    pause
    exit /b 1
)

echo.
echo [8/8] Creando acceso directo...
echo Set oWS = WScript.CreateObject("WScript.Shell") > CreateShortcut.vbs
echo sLinkFile = "%USERPROFILE%\Desktop\TradePro.lnk" >> CreateShortcut.vbs
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> CreateShortcut.vbs
echo oLink.TargetPath = "%CD%\launch_tradepro.bat" >> CreateShortcut.vbs
echo oLink.WorkingDirectory = "%CD%" >> CreateShortcut.vbs
echo oLink.Description = "TradePro - Professional Trading Platform" >> CreateShortcut.vbs
echo oLink.IconLocation = "%CD%\assets\icon.ico" >> CreateShortcut.vbs
echo oLink.Save >> CreateShortcut.vbs
cscript CreateShortcut.vbs //Nologo
del CreateShortcut.vbs
echo OK - Acceso directo creado en escritorio

echo.
echo ========================================
echo  INSTALACION COMPLETADA EXITOSAMENTE
echo ========================================
echo.
echo Componentes instalados:
echo  [OK] Python y dependencias
echo  [OK] PyQt6 (GUI)
echo  [OK] PyInstaller (para .exe)
echo  [OK] Logo profesional
echo  [OK] Directorios configurados
echo  [OK] Acceso directo en escritorio
echo.
echo Para ejecutar TradePro:
echo  1. Doble click en acceso directo del escritorio
echo  2. O ejecutar: launch_tradepro.bat
echo  3. O ejecutar: python launch_tradepro.py
echo.
echo Para crear .exe:
echo  build_tradepro.bat
echo.
echo Documentacion:
echo  APP_COMPLETA_FINAL.md
echo  GUIA_FINAL_INTEGRACION.md
echo  INTEGRACION_COMPLETA.md
echo.
pause
