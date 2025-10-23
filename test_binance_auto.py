"""
Test automático de conexión a Binance
Prueba las credenciales sin interacción del usuario
"""

from binance.client import Client
from loguru import logger
import sys

# TUS CREDENCIALES
API_KEY = "AsJ3UTzFTux4wnzWQiMvYuThjgo05FlZpd6sYRKdihHZtAC4pAy1gL7O3QyiFMTC"
API_SECRET = "tbFovnluEo5BBSG8l91hXbC7hF72bSxcnbiud0xoCrQS1pOjqvTrBsScznNjNJ8N"

def test_connection():
    """Prueba conexión automáticamente"""
    
    logger.info("=" * 70)
    logger.info("🔌 PROBANDO CONEXIÓN A BINANCE MAINNET (REAL)")
    logger.info("=" * 70)
    
    try:
        # Crear cliente
        logger.info(f"API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
        logger.info("Conectando...")
        
        client = Client(API_KEY, API_SECRET)
        
        # Test 1: Ping
        logger.info("Test 1: Ping al servidor...")
        client.ping()
        logger.success("  ✅ Ping exitoso")
        
        # Test 2: Server time
        logger.info("Test 2: Obtener hora del servidor...")
        server_time = client.get_server_time()
        logger.success(f"  ✅ Hora del servidor: {server_time['serverTime']}")
        
        # Test 3: Account info
        logger.info("Test 3: Obtener información de cuenta...")
        account = client.get_account()
        logger.success("  ✅ Información de cuenta obtenida")
        
        # Mostrar info
        logger.info("-" * 70)
        logger.info("📊 INFORMACIÓN DE CUENTA:")
        logger.info(f"  Can Trade: {account['canTrade']}")
        logger.info(f"  Can Withdraw: {account['canWithdraw']}")
        logger.info(f"  Can Deposit: {account['canDeposit']}")
        logger.info(f"  Account Type: {account['accountType']}")
        
        # Test 4: Balances
        logger.info("-" * 70)
        logger.info("💰 BALANCES:")
        balances = [b for b in account['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
        
        if balances:
            total_usdt = 0
            for balance in balances:
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                logger.info(f"  {asset}: {total:.8f} (Free: {free:.8f})")
                
                # Estimar valor en USDT
                if asset == 'USDT':
                    total_usdt += total
                elif asset in ['BTC', 'ETH', 'BNB']:
                    try:
                        ticker = client.get_symbol_ticker(symbol=f"{asset}USDT")
                        price = float(ticker['price'])
                        value_usdt = total * price
                        total_usdt += value_usdt
                        logger.info(f"    → Valor: ${value_usdt:,.2f} USDT")
                    except:
                        pass
            
            logger.info("-" * 70)
            logger.info(f"💵 VALOR ESTIMADO TOTAL: ${total_usdt:,.2f} USDT")
        else:
            logger.warning("  ⚠️  No hay balances disponibles")
        
        # Test 5: Precio BTC
        logger.info("-" * 70)
        logger.info("Test 4: Obtener precio de BTCUSDT...")
        ticker = client.get_symbol_ticker(symbol="BTCUSDT")
        btc_price = float(ticker['price'])
        logger.success(f"  ✅ Precio BTC: ${btc_price:,.2f}")
        
        # Test 6: Verificar permisos de trading
        logger.info("-" * 70)
        logger.info("Test 5: Verificar permisos de trading...")
        if account['canTrade']:
            logger.success("  ✅ PERMISOS DE TRADING HABILITADOS")
        else:
            logger.error("  ❌ PERMISOS DE TRADING DESHABILITADOS")
            logger.error("     Ve a Binance → API Management → Habilita 'Enable Spot & Margin Trading'")
            return False
        
        # Resumen final
        logger.info("=" * 70)
        logger.success("✅ TODAS LAS PRUEBAS EXITOSAS")
        logger.success("=" * 70)
        logger.info("Tu API Key funciona correctamente")
        logger.info("Puedes conectarte desde TradePro")
        logger.info("=" * 70)
        
        return True
        
    except Exception as e:
        logger.error("=" * 70)
        logger.error("❌ ERROR EN LA CONEXIÓN")
        logger.error("=" * 70)
        logger.error(f"Error: {str(e)}")
        logger.error("-" * 70)
        
        # Diagnóstico detallado
        error_str = str(e).lower()
        
        if "invalid api-key" in error_str or "api-key" in error_str:
            logger.error("🔍 PROBLEMA: API Key inválida o incorrecta")
            logger.error("")
            logger.error("SOLUCIONES:")
            logger.error("1. Ve a Binance.com → Perfil → API Management")
            logger.error("2. Verifica que la API Key esté ACTIVA (no suspendida)")
            logger.error("3. Copia la API Key de nuevo (sin espacios)")
            logger.error("4. Si es necesario, crea una nueva API Key")
            
        elif "signature" in error_str:
            logger.error("🔍 PROBLEMA: API Secret incorrecta")
            logger.error("")
            logger.error("SOLUCIONES:")
            logger.error("1. Verifica que el Secret esté correcto")
            logger.error("2. El Secret solo se muestra UNA VEZ al crear la API Key")
            logger.error("3. Si lo perdiste, debes crear una nueva API Key")
            
        elif "ip" in error_str or "whitelist" in error_str:
            logger.error("🔍 PROBLEMA: Tu IP no está autorizada")
            logger.error("")
            logger.error("SOLUCIONES:")
            logger.error("1. Ve a Binance.com → API Management")
            logger.error("2. Click en tu API Key → Edit restrictions")
            logger.error("3. Opción A: Quita la restricción de IP (menos seguro)")
            logger.error("4. Opción B: Agrega tu IP actual a la whitelist")
            
        elif "permission" in error_str or "not authorized" in error_str:
            logger.error("🔍 PROBLEMA: Sin permisos suficientes")
            logger.error("")
            logger.error("SOLUCIONES:")
            logger.error("1. Ve a Binance.com → API Management")
            logger.error("2. Click en tu API Key → Edit")
            logger.error("3. Habilita: 'Enable Reading'")
            logger.error("4. Habilita: 'Enable Spot & Margin Trading'")
            logger.error("5. NO habilites: 'Enable Withdrawals' (seguridad)")
            
        else:
            logger.error("🔍 PROBLEMA: Error desconocido")
            logger.error("")
            logger.error("INFORMACIÓN DEL ERROR:")
            logger.error(f"  {e}")
            logger.error("")
            logger.error("SOLUCIONES GENERALES:")
            logger.error("1. Verifica tu conexión a internet")
            logger.error("2. Verifica que Binance.com esté accesible")
            logger.error("3. Intenta crear una nueva API Key")
        
        logger.error("=" * 70)
        return False

if __name__ == "__main__":
    print("\n")
    success = test_connection()
    print("\n")
    
    if success:
        # Guardar en base de datos
        try:
            from src.database import get_database
            
            logger.info("💾 Guardando credenciales en base de datos...")
            db = get_database()
            db.update_user_settings(1, {
                'broker': 'binance',
                'api_key': API_KEY,
                'api_secret': API_SECRET,
                'testnet': False
            })
            logger.success("✅ Credenciales guardadas")
            
            print("\n")
            logger.info("🚀 PRÓXIMOS PASOS:")
            logger.info("1. Ejecuta: .\\start_binance_real.bat")
            logger.info("2. En TradePro → Settings → Conectar Broker")
            logger.info("3. ¡Listo para operar!")
            print("\n")
            
        except Exception as e:
            logger.warning(f"No se pudo guardar en DB: {e}")
            logger.info("Puedes ingresar las credenciales manualmente en Settings")
    
    sys.exit(0 if success else 1)
