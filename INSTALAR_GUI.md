# 🖥️ INSTALAR APLICACION DE ESCRITORIO

## ⚡ INSTALACION RAPIDA (5 MINUTOS)

### Paso 1: Activar Entorno Virtual

```bash
cd c:\xampp\htdocs\Trading\Trading
venv\Scripts\activate
```

### Paso 2: Instalar Dependencias GUI

```bash
pip install PyQt6 PyQt6-WebEngine pyqtgraph qdarkstyle fastapi uvicorn pydantic
```

**Tiempo:** 2-3 minutos

### Paso 3: Verificar Instalación

```bash
python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6 OK')"
python -c "import fastapi; print('FastAPI OK')"
```

Debe mostrar:
```
PyQt6 OK
FastAPI OK
```

### Paso 4: Iniciar Aplicación

```bash
start_trading_app.bat
```

**¡LISTO!** La aplicación debe abrirse.

---

## 🔧 INSTALACION DETALLADA

### Windows

**1. Instalar PyQt6:**
```bash
pip install PyQt6==6.6.0
```

**2. Instalar PyQt6-WebEngine:**
```bash
pip install PyQt6-WebEngine==6.6.0
```

**3. Instalar pyqtgraph:**
```bash
pip install pyqtgraph==0.13.3
```

**4. Instalar qdarkstyle:**
```bash
pip install qdarkstyle==3.2.0
```

**5. Instalar FastAPI:**
```bash
pip install fastapi==0.104.0
pip install uvicorn==0.24.0
pip install pydantic==2.5.0
```

**6. Verificar:**
```bash
pip list | findstr PyQt6
pip list | findstr fastapi
```

### Linux

```bash
# Instalar dependencias del sistema
sudo apt-get update
sudo apt-get install python3-pyqt6 python3-pyqt6.qtwebengine

# Instalar paquetes Python
pip install PyQt6 PyQt6-WebEngine pyqtgraph qdarkstyle
pip install fastapi uvicorn pydantic
```

### macOS

```bash
# Instalar con Homebrew
brew install pyqt6

# Instalar paquetes Python
pip install PyQt6 PyQt6-WebEngine pyqtgraph qdarkstyle
pip install fastapi uvicorn pydantic
```

---

## 🐛 SOLUCION DE PROBLEMAS

### Error: "No module named 'PyQt6'"

**Solución:**
```bash
pip uninstall PyQt6
pip install PyQt6==6.6.0
```

### Error: "DLL load failed"

**Solución Windows:**
1. Instalar Visual C++ Redistributable:
   - https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Reiniciar
3. Reinstalar PyQt6

### Error: "qt.qpa.plugin: Could not load the Qt platform plugin"

**Solución:**
```bash
set QT_QPA_PLATFORM_PLUGIN_PATH=%VIRTUAL_ENV%\Lib\site-packages\PyQt6\Qt6\plugins\platforms
python desktop_app.py
```

### Error: "ImportError: cannot import name 'QApplication'"

**Solución:**
```bash
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip
pip install PyQt6
```

### Aplicación se ve mal (sin tema oscuro)

**Solución:**
```bash
pip install qdarkstyle
```

---

## ✅ VERIFICACION COMPLETA

### Script de Verificación

Crear archivo `test_gui.py`:

```python
import sys

print("Verificando instalación de GUI...")

# Test PyQt6
try:
    from PyQt6.QtWidgets import QApplication
    print("✓ PyQt6 OK")
except ImportError as e:
    print(f"✗ PyQt6 ERROR: {e}")
    sys.exit(1)

# Test PyQt6-WebEngine
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    print("✓ PyQt6-WebEngine OK")
except ImportError as e:
    print(f"✗ PyQt6-WebEngine ERROR: {e}")

# Test pyqtgraph
try:
    import pyqtgraph as pg
    print("✓ pyqtgraph OK")
except ImportError as e:
    print(f"✗ pyqtgraph ERROR: {e}")
    sys.exit(1)

# Test qdarkstyle
try:
    import qdarkstyle
    print("✓ qdarkstyle OK")
except ImportError as e:
    print(f"✗ qdarkstyle ERROR: {e}")
    sys.exit(1)

# Test FastAPI
try:
    from fastapi import FastAPI
    print("✓ FastAPI OK")
except ImportError as e:
    print(f"✗ FastAPI ERROR: {e}")
    sys.exit(1)

# Test uvicorn
try:
    import uvicorn
    print("✓ uvicorn OK")
except ImportError as e:
    print(f"✗ uvicorn ERROR: {e}")
    sys.exit(1)

print("\n✅ TODAS LAS DEPENDENCIAS GUI INSTALADAS CORRECTAMENTE")
```

Ejecutar:
```bash
python test_gui.py
```

---

## 📦 DEPENDENCIAS COMPLETAS

### requirements_gui.txt

```
# GUI Desktop
PyQt6>=6.6.0
PyQt6-WebEngine>=6.6.0
pyqtgraph>=0.13.3
qdarkstyle>=3.2.0

# API REST
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
websockets>=12.0

# Utilidades
requests>=2.31.0
python-dotenv>=1.0.0
```

Instalar todo:
```bash
pip install -r requirements_gui.txt
```

---

## 🚀 INICIAR APLICACION

### Método 1: Script Automático

```bash
start_trading_app.bat
```

### Método 2: Manual

**Terminal 1 - API:**
```bash
cd c:\xampp\htdocs\Trading\Trading
venv\Scripts\activate
python run_api.py
```

**Terminal 2 - App:**
```bash
cd c:\xampp\htdocs\Trading\Trading
venv\Scripts\activate
python desktop_app.py
```

### Método 3: Python directo

```bash
cd c:\xampp\htdocs\Trading\Trading
venv\Scripts\activate
python -m src.gui.main_window
```

---

## 📊 VERIFICAR QUE FUNCIONA

### Checklist:

1. **API corriendo:**
   - Abrir: http://127.0.0.1:8000/docs
   - Debe mostrar documentación Swagger

2. **Aplicación abierta:**
   - Ventana con tema oscuro
   - Dashboard visible
   - Panel de trading visible
   - Gráfico visible

3. **Conectar broker:**
   - Click "Conectar Broker"
   - Seleccionar Quotex
   - Debe conectar sin errores

4. **Iniciar sistema:**
   - Click "Iniciar"
   - Estado debe cambiar a "Ejecutando"
   - Dashboard debe actualizarse

5. **Ejecutar operación:**
   - Panel de Trading
   - Click "Actualizar Precio"
   - Click "COMPRAR"
   - Debe aparecer en "Posiciones"

---

## 💡 TIPS

### Rendimiento

**Si la app va lenta:**
```bash
# Reducir frecuencia de actualización
# En main_window.py, línea ~XXX:
self.update_timer.start(5000)  # 5 segundos en vez de 2
```

### Tema

**Cambiar tema:**
```python
# En desktop_app.py:
# Comentar línea del tema oscuro
# app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
```

### Tamaño de Ventana

**Ajustar tamaño inicial:**
```python
# En main_window.py, línea ~XX:
self.setGeometry(100, 100, 1920, 1080)  # Pantalla completa
```

---

## 🆘 SOPORTE

### Si nada funciona:

1. **Desinstalar todo:**
```bash
pip uninstall PyQt6 PyQt6-WebEngine pyqtgraph qdarkstyle fastapi uvicorn -y
```

2. **Limpiar cache:**
```bash
pip cache purge
```

3. **Reinstalar:**
```bash
pip install --no-cache-dir PyQt6 PyQt6-WebEngine pyqtgraph qdarkstyle fastapi uvicorn
```

4. **Verificar Python:**
```bash
python --version
# Debe ser 3.10 o superior
```

5. **Crear nuevo entorno virtual:**
```bash
cd c:\xampp\htdocs\Trading\Trading
python -m venv venv_new
venv_new\Scripts\activate
pip install -r requirements.txt
```

---

## ✅ LISTO

Si todo funciona, deberías ver:

```
======================================================================
🚀 INICIANDO API DE TRADING
======================================================================
📡 URL: http://127.0.0.1:8000
📚 Docs: http://127.0.0.1:8000/docs
======================================================================
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Y la aplicación de escritorio abierta con tema oscuro.

**¡A OPERAR!** 🚀📈
