"""
Launcher Principal - TradePro
Inicia la aplicación con splash screen
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from src.gui.splash_screen import SplashScreen
from src.gui.modern_trading_app import ModernTradingApp
from loguru import logger


def main():
    """Lanzar aplicación"""
    
    # Configurar logger
    logger.add("logs/tradepro_{time}.log", rotation="1 day")
    logger.info("Iniciando TradePro...")
    
    # Crear aplicación
    app = QApplication(sys.argv)
    app.setApplicationName("TradePro")
    app.setApplicationVersion("4.0.0")
    app.setOrganizationName("TradePro Team")
    
    # Mostrar splash screen
    splash = SplashScreen()
    splash.show()
    
    # Crear ventana principal (oculta)
    main_window = ModernTradingApp()
    
    # Cuando splash termine, mostrar ventana principal
    def show_main_window():
        splash.close()
        main_window.show()
        logger.info("TradePro iniciado exitosamente")
    
    # Esperar 3 segundos (o hasta que splash termine)
    QTimer.singleShot(3000, show_main_window)
    
    # Ejecutar
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
