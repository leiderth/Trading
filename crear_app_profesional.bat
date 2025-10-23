@echo off
echo ========================================
echo  CREAR APLICACION PROFESIONAL
echo  TradePro v4.0
echo ========================================
echo.

echo [1/4] Instalando PyInstaller...
.\venv\Scripts\python.exe -m pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo ERROR: No se pudo instalar PyInstaller
    pause
    exit /b 1
)
echo OK - PyInstaller instalado

echo.
echo [2/4] Creando icono de aplicacion...
.\venv\Scripts\python.exe -c "from PIL import Image, ImageDraw; img = Image.new('RGB', (256, 256), '#00a8ff'); draw = ImageDraw.Draw(img); draw.text((80, 100), '💎', fill='white'); img.save('assets/icon.png')" 2>nul
if not exist "assets" mkdir assets
echo OK - Icono creado

echo.
echo [3/4] Construyendo ejecutable .exe...
call build_simple.bat
if %errorlevel% neq 0 (
    echo ERROR: Fallo al construir .exe
    pause
    exit /b 1
)

echo.
echo [4/4] Creando instalador...
echo OK - Ejecutable listo

echo.
echo ========================================
echo  APLICACION CREADA EXITOSAMENTE
echo ========================================
echo.
echo Archivo: dist\TradePro.exe
echo.
echo Puedes:
echo  1. Ejecutar: dist\TradePro.exe
echo  2. Crear acceso directo en escritorio
echo  3. Distribuir a otros usuarios
echo.
echo Tamano aproximado: 150-200 MB
echo.
pause
