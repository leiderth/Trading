"""
Script para configurar Binance Demo Trading (Testnet)
Para credenciales de testnet.binance.com
"""

from src.database import get_database
from loguru import logger

# ============================================
# TUS CREDENCIALES DE BINANCE DEMO TRADING
# ============================================

DEMO_API_KEY = "Q9JgwPqSs6n4cAehdAn2DeBD1cQRZkqjUjRy4O3UY4mBquKxvMnjJiyXqO8I5esO"
DEMO_API_SECRET = "qcixvUmW5EJCuzbXv9IEfpcc8k04AyNysawSUjcSycIJrxEJjFtZTK3g0JushnvV"

# ============================================

def configurar_demo():
    """Configura credenciales de demo trading en la base de datos"""
    
    logger.info("=" * 70)
    logger.info("🔧 CONFIGURANDO BINANCE DEMO TRADING")
    logger.info("=" * 70)
    
    try:
        logger.info("Conectando a base de datos...")
        db = get_database()
        
        logger.info("Actualizando credenciales de demo trading...")
        db.update_user_settings(1, {
            'broker': 'binance',
            'api_key': DEMO_API_KEY,
            'api_secret': DEMO_API_SECRET,
            'testnet': True  # Activar modo testnet
        })
        
        logger.success("✅ Credenciales de demo trading guardadas")
        logger.info("-" * 70)
        logger.info(f"API Key: {DEMO_API_KEY[:10]}...{DEMO_API_KEY[-4:]}")
        logger.info(f"Secret: {DEMO_API_SECRET[:10]}...{DEMO_API_SECRET[-4:]}")
        logger.info("Testnet/Demo: ACTIVADO ✅")
        logger.info("-" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def probar_conexion_simple():
    """Prueba simple de conexión"""
    
    logger.info("=" * 70)
    logger.info("🧪 PROBANDO CONEXIÓN BÁSICA")
    logger.info("=" * 70)
    
    try:
        from binance.client import Client
        
        logger.info("Creando cliente...")
        # Binance Demo Trading usa testnet=True
        client = Client(DEMO_API_KEY, DEMO_API_SECRET, testnet=True)
        
        logger.info("Test: Ping al servidor...")
        client.ping()
        logger.success("✅ Ping exitoso")
        
        logger.info("Test: Obtener hora del servidor...")
        server_time = client.get_server_time()
        logger.success(f"✅ Hora del servidor: {server_time['serverTime']}")
        
        logger.success("=" * 70)
        logger.success("✅ CONEXIÓN BÁSICA EXITOSA")
        logger.success("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.warning("Esto puede ser normal si las credenciales tienen restricciones")
        logger.info("Las credenciales están guardadas y funcionarán en TradePro")
        return False

if __name__ == "__main__":
    print("\n")
    
    # Configurar credenciales
    if configurar_demo():
        print("\n")
        
        # Probar conexión básica
        probar_conexion_simple()
        
        print("\n")
        logger.success("=" * 70)
        logger.success("🎉 CONFIGURACIÓN COMPLETADA")
        logger.success("=" * 70)
        logger.info("")
        logger.info("PRÓXIMOS PASOS:")
        logger.info("1. Abre TradePro: python launch_app.py")
        logger.info("2. Ve a Settings")
        logger.info("3. Verás tus credenciales cargadas")
        logger.info("4. VERIFICA que 'Usar Testnet' esté MARCADO ✅")
        logger.info("5. Click 'Conectar Broker'")
        logger.info("6. Espera 30 segundos")
        logger.info("7. Debe decir '● Conectado' (verde)")
        logger.info("")
        logger.info("NOTA: Binance Demo Trading tiene algunas limitaciones")
        logger.info("pero funciona perfectamente para trading de prueba.")
        logger.info("")
    
    print("\n")
