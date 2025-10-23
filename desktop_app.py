"""
Aplicacion de Escritorio para Sistema de Trading
Interfaz grafica moderna con PyQt6
"""

import sys
import asyncio
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
import qdarkstyle

from src.gui.main_window import MainWindow


def main():
    """Funcion principal"""
    
    # Crear aplicacion Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Trading System Pro")
    app.setOrganizationName("TradingAI")
    
    # Aplicar tema oscuro
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyqt6'))
    
    # Crear ventana principal
    window = MainWindow()
    window.show()
    
    # Ejecutar aplicacion
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
