"""
Script para crear ejecutable .exe de la aplicación
Genera instalador profesional
"""

import PyInstaller.__main__
import os
import shutil

# Configuración
APP_NAME = "TradePro"
VERSION = "4.0.0"
AUTHOR = "TradePro Team"
ICON_PATH = "assets/icon.ico"  # Crear icono

def build_exe():
    """Construir ejecutable"""
    
    print("=" * 60)
    print(f"  CONSTRUYENDO {APP_NAME} v{VERSION}")
    print("=" * 60)
    print()
    
    # Limpiar builds anteriores
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    
    # Crear directorios si no existen
    os.makedirs('config', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Argumentos de PyInstaller
    args = [
        'src/gui/modern_trading_app.py',  # Script principal
        '--name', APP_NAME,
        '--onefile',  # Un solo archivo .exe
        '--windowed',  # Sin consola
        '--clean',
        
        # Icono (opcional)
        # '--icon', ICON_PATH,
        
        # Ocultar imports
        '--hidden-import', 'sklearn.utils._cython_blas',
        '--hidden-import', 'sklearn.neighbors.typedefs',
        '--hidden-import', 'sklearn.neighbors.quad_tree',
        '--hidden-import', 'sklearn.tree._utils',
        
        # Optimizaciones
        '--optimize', '2',
    ]
    
    print("Ejecutando PyInstaller...")
    print()
    
    PyInstaller.__main__.run(args)
    
    print()
    print("=" * 60)
    print(f"  ✅ {APP_NAME}.exe CREADO EXITOSAMENTE")
    print("=" * 60)
    print()
    print(f"Ubicación: dist/{APP_NAME}.exe")
    print(f"Tamaño: ~{os.path.getsize(f'dist/{APP_NAME}.exe') / (1024*1024):.1f} MB")
    print()
    print("Puedes distribuir este archivo .exe")
    print()


if __name__ == "__main__":
    build_exe()
