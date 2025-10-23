"""
Script de prueba rápida para verificar conexiones
"""

import sys
import requests
from loguru import logger

def test_api_connection():
    """Probar conexión a la API"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=2)
        if response.status_code == 200:
            logger.info("✅ API está corriendo y responde")
            return True
        else:
            logger.error(f"❌ API responde pero con código: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ No se puede conectar a la API - No está corriendo")
        logger.info("💡 Ejecuta: uvicorn src.api.trading_api:app --reload")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

def test_database():
    """Probar conexión a la base de datos"""
    try:
        from src.database import get_database
        db = get_database()
        user = db.get_user_by_username("trader_pro")
        if user:
            logger.info(f"✅ Base de datos funciona - Usuario: {user['username']}, Balance: ${user['current_balance']:,.2f}")
            return True
        else:
            logger.warning("⚠️ Base de datos funciona pero usuario no encontrado")
            return True
    except Exception as e:
        logger.error(f"❌ Error con base de datos: {e}")
        return False

def test_trading_controller():
    """Probar TradingController"""
    try:
        from src.gui.trading_controller import TradingController
        controller = TradingController()
        
        # Verificar si puede conectar a API
        if controller.check_api_connection():
            logger.info("✅ TradingController puede conectar a API")
            return True
        else:
            logger.warning("⚠️ TradingController creado pero API no disponible")
            return False
    except Exception as e:
        logger.error(f"❌ Error con TradingController: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== PRUEBA DE CONEXIONES ===\n")
    
    # Test 1: API
    logger.info("1. Probando API...")
    api_ok = test_api_connection()
    print()
    
    # Test 2: Database
    logger.info("2. Probando Base de Datos...")
    db_ok = test_database()
    print()
    
    # Test 3: TradingController
    logger.info("3. Probando TradingController...")
    controller_ok = test_trading_controller()
    print()
    
    # Resumen
    logger.info("=== RESUMEN ===")
    logger.info(f"API: {'✅ OK' if api_ok else '❌ FALLO'}")
    logger.info(f"Database: {'✅ OK' if db_ok else '❌ FALLO'}")
    logger.info(f"TradingController: {'✅ OK' if controller_ok else '❌ FALLO'}")
    
    if not api_ok:
        print("\n💡 SOLUCIÓN:")
        print("Ejecuta en otra terminal:")
        print("  .\\venv\\Scripts\\python.exe -m uvicorn src.api.trading_api:app --reload")
    
    if db_ok and not api_ok:
        print("\n✅ Puedes usar la app en MODO DEMO (sin API)")
        print("Los trades se guardarán en la base de datos pero no se conectarán a brokers reales")
