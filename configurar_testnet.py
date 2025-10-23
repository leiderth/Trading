"""
Script para configurar credenciales de Binance Testnet
Ejecuta esto después de obtener tus credenciales de testnet
"""

from src.database import get_database
from loguru import logger

# ============================================
# PEGA AQUÍ TUS CREDENCIALES DE TESTNET
# ============================================

TESTNET_API_KEY = "Q9JgwPqSs6n4cAehdAn2DeBD1cQRZkqjUjRy4O3UY4mBquKxvMnjJiyXqO8I5esO"
TESTNET_API_SECRET = "qcixvUmW5EJCuzbXv9IEfpcc8k04AyNysawSUjcSycIJrxEJjFtZTK3g0JushnvV"

# ============================================

def configurar_testnet():
    """Configura credenciales de testnet en la base de datos"""
    
    logger.info("=" * 70)
    logger.info("🔧 CONFIGURANDO BINANCE TESTNET")
    logger.info("=" * 70)
    
    # Validar que se hayan pegado las credenciales
    if "PEGA_TU" in TESTNET_API_KEY or "PEGA_TU" in TESTNET_API_SECRET:
        logger.error("❌ ERROR: Debes editar este archivo primero")
        logger.info("")
        logger.info("PASOS:")
        logger.info("1. Ve a: https://testnet.binance.vision/")
        logger.info("2. Login con GitHub")
        logger.info("3. Click 'Generate HMAC_SHA256 Key'")
        logger.info("4. Copia API Key y Secret Key")
        logger.info("5. Abre este archivo: configurar_testnet.py")
        logger.info("6. Pega las credenciales en las líneas 11-12")
        logger.info("7. Guarda el archivo")
        logger.info("8. Ejecuta de nuevo: python configurar_testnet.py")
        logger.info("")
        return False
    
    try:
        logger.info("Conectando a base de datos...")
        db = get_database()
        
        logger.info("Actualizando credenciales de testnet...")
        db.update_user_settings(1, {
            'broker': 'binance',
            'api_key': TESTNET_API_KEY,
            'api_secret': TESTNET_API_SECRET,
            'testnet': True  # ← IMPORTANTE: Activar testnet
        })
        
        logger.success("✅ Credenciales de testnet guardadas")
        logger.info("-" * 70)
        logger.info(f"API Key: {TESTNET_API_KEY[:10]}...{TESTNET_API_KEY[-4:]}")
        logger.info(f"Secret: {TESTNET_API_SECRET[:10]}...{TESTNET_API_SECRET[-4:]}")
        logger.info("Testnet: ACTIVADO ✅")
        logger.info("-" * 70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def probar_conexion():
    """Prueba la conexión con las credenciales de testnet"""
    
    logger.info("=" * 70)
    logger.info("🧪 PROBANDO CONEXIÓN A TESTNET")
    logger.info("=" * 70)
    
    try:
        from binance.client import Client
        
        logger.info("Creando cliente de testnet...")
        client = Client(TESTNET_API_KEY, TESTNET_API_SECRET, testnet=True)
        
        logger.info("Test 1: Ping al servidor...")
        client.ping()
        logger.success("  ✅ Ping exitoso")
        
        logger.info("Test 2: Obtener información de cuenta...")
        account = client.get_account()
        logger.success("  ✅ Cuenta obtenida")
        
        logger.info("-" * 70)
        logger.info("💰 BALANCES DE TESTNET:")
        
        total_value = 0
        for balance in account['balances']:
            free = float(balance['free'])
            locked = float(balance['locked'])
            total = free + locked
            
            if total > 0:
                logger.info(f"  {balance['asset']}: {total:,.8f} (Free: {free:,.8f})")
                
                # Estimar valor en USDT
                if balance['asset'] == 'USDT':
                    total_value += total
                elif balance['asset'] == 'BTC':
                    try:
                        ticker = client.get_symbol_ticker(symbol='BTCUSDT')
                        btc_price = float(ticker['price'])
                        total_value += total * btc_price
                    except:
                        pass
        
        logger.info("-" * 70)
        logger.info(f"💵 VALOR ESTIMADO: ~${total_value:,.2f} USDT")
        logger.info("-" * 70)
        
        logger.success("✅ CONEXIÓN A TESTNET EXITOSA")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error probando conexión: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n")
    
    # Paso 1: Configurar credenciales
    if configurar_testnet():
        print("\n")
        
        # Paso 2: Probar conexión
        if probar_conexion():
            print("\n")
            logger.success("=" * 70)
            logger.success("🎉 TESTNET CONFIGURADO EXITOSAMENTE")
            logger.success("=" * 70)
            logger.info("")
            logger.info("PRÓXIMOS PASOS:")
            logger.info("1. Abre TradePro: python launch_app.py")
            logger.info("2. Ve a Settings")
            logger.info("3. Verás tus credenciales de testnet cargadas")
            logger.info("4. VERIFICA que 'Usar Testnet' esté MARCADO ✅")
            logger.info("5. Click 'Conectar Broker'")
            logger.info("6. ¡Listo para operar con dinero ficticio!")
            logger.info("")
        else:
            logger.error("❌ Error probando conexión")
            logger.info("Verifica que las credenciales sean correctas")
    
    print("\n")
