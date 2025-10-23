# Guia de Instalacion Completa

## Requisitos Previos

### Sistema Operativo
- Windows 10/11 (64-bit)
- Linux (Ubuntu 20.04+)
- macOS (10.15+)

### Software Requerido
- Python 3.10 o superior
- Git
- Visual Studio Build Tools (Windows)

## Instalacion Paso a Paso

### 1. Verificar Python

```bash
python --version
```

### 2. Navegar al Directorio

```bash
cd c:\xampp\htdocs\Trading\Trading
```

### 3. Crear Entorno Virtual

```bash
python -m venv venv
```

### 4. Activar Entorno Virtual

Windows:
```bash
venv\Scripts\activate
```

Linux/macOS:
```bash
source venv/bin/activate
```

### 5. Actualizar pip

```bash
python -m pip install --upgrade pip
```

### 6. Instalar TA-Lib

Windows:
1. Descargar wheel desde: https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
2. Instalar: pip install TA_Lib-0.4.28-cp310-cp310-win_amd64.whl

Linux:
```bash
sudo apt-get install ta-lib
pip install TA-Lib
```

macOS:
```bash
brew install ta-lib
pip install TA-Lib
```

### 7. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 8. Configurar Variables de Entorno

```bash
copy .env.example .env
notepad .env
```

Editar con tus credenciales.

### 9. Verificar Instalacion

```bash
python -c "import torch; import tensorflow; import pandas; print('OK')"
```

### 10. Ejecutar Sistema

```bash
python main.py
```

## Problemas Comunes

### Error: ModuleNotFoundError
Solucion: Activar entorno virtual

### Error: TA-Lib no se instala
Solucion: Usar wheel pre-compilado

### Error: CUDA not available
Solucion: Instalar PyTorch con soporte CUDA o usar CPU

## Soporte

- GitHub Issues
- Email: soporte@tradingsystem.com
