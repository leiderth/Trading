"""
Sistema de Trading Algorítmico con IA
Punto de entrada principal
"""

import asyncio
import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config.settings import settings, logger
from src.core.trading_system import TradingSystem


async def main():
    """Función principal"""
    
    # Crear sistema de trading
    trading_system = TradingSystem(config={
        'broker': 'quotex',  # quotex, binance, oanda, etc.
        'symbol': 'EUR/USD',
        'timeframe': '5m',
        'auto_trading': settings.auto_trading,
        'close_positions_on_stop': True
    })
    
    try:
        # Inicializar sistema
        logger.info("🔧 Inicializando sistema...")
        initialized = await trading_system.initialize()
        
        if not initialized:
            logger.error("✗ No se pudo inicializar el sistema")
            return
        
        # Iniciar trading
        logger.info("▶️  Iniciando sistema de trading...")
        await trading_system.start()
        
    except KeyboardInterrupt:
        logger.info("\n⏸️  Interrupción detectada (Ctrl+C)")
    except Exception as e:
        logger.error(f"✗ Error fatal: {e}")
    finally:
        # Detener sistema
        logger.info("🛑 Deteniendo sistema...")
        await trading_system.stop()
        logger.success("✓ Sistema detenido correctamente")


if __name__ == "__main__":
    """
    Ejecutar con:
    python main.py
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n👋 Adiós!")
    except Exception as e:
        logger.error(f"✗ Error ejecutando sistema: {e}")
        sys.exit(1)
