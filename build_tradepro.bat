@echo off
cls
echo ========================================
echo  CONSTRUYENDO TRADEPRO.EXE
echo  Ejecutable Profesional
echo ========================================
echo.

echo Limpiando builds anteriores...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist *.spec del *.spec

echo.
echo Construyendo ejecutable optimizado...
echo (Esto puede tardar 3-5 minutos)
echo.

.\venv\Scripts\python.exe -m PyInstaller ^
    --name TradePro ^
    --onefile ^
    --windowed ^
    --clean ^
    --optimize 2 ^
    --icon assets\icon.ico ^
    --add-data "assets;assets" ^
    --hidden-import sklearn.utils._cython_blas ^
    --hidden-import sklearn.neighbors.typedefs ^
    --hidden-import sklearn.neighbors.quad_tree ^
    --hidden-import sklearn.tree._utils ^
    --hidden-import PyQt6.sip ^
    launch_app.py

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Fallo al construir .exe
    echo.
    echo Verifica que:
    echo  1. PyInstaller este instalado
    echo  2. No haya errores en el codigo
    echo  3. Todos los modulos esten disponibles
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  EXITO - TradePro.exe CREADO
echo ========================================
echo.

REM Obtener tamaño del archivo
for %%A in (dist\TradePro.exe) do set size=%%~zA
set /a sizeMB=%size% / 1048576

echo Ubicacion: dist\TradePro.exe
echo Tamano: %sizeMB% MB
echo.
echo El ejecutable es completamente independiente.
echo Puede distribuirse sin necesidad de Python.
echo.
echo Para probar:
echo  dist\TradePro.exe
echo.
echo Para distribuir:
echo  1. Copiar dist\TradePro.exe
echo  2. Compartir con otros usuarios
echo  3. Crear instalador con Inno Setup (opcional)
echo.
pause
