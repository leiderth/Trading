"""
Script para conectar automáticamente a Binance
Configura las credenciales y prueba la conexión
"""

import asyncio
from binance.client import Client
from loguru import logger

# TUS CREDENCIALES DE BINANCE
API_KEY = "AsJ3UTzFTux4wnzWQiMvYuThjgo05FlZpd6sYRKdihHZtAC4pAy1gL7O3QyiFMTC"
API_SECRET = "tbFovnluEo5BBSG8l91hXbC7hF72bSxcnbiud0xoCrQS1pOjqvTrBsScznNjNJ8N"

def test_binance_connection(testnet=False):
    """Prueba conexión a Binance"""
    try:
        logger.info("=" * 60)
        logger.info("🔌 PROBANDO CONEXIÓN A BINANCE")
        logger.info("=" * 60)
        
        mode = "TESTNET" if testnet else "MAINNET (REAL)"
        logger.info(f"Modo: {mode}")
        logger.info(f"API Key: {API_KEY[:8]}...")
        
        # Crear cliente
        if testnet:
            client = Client(API_KEY, API_SECRET, testnet=True)
            logger.info("🔗 Conectando a Binance TESTNET...")
        else:
            client = Client(API_KEY, API_SECRET)
            logger.info("🔗 Conectando a Binance MAINNET (REAL)...")
        
        # Obtener información de cuenta
        logger.info("📊 Obteniendo información de cuenta...")
        account = client.get_account()
        
        # Mostrar información
        logger.success("✅ CONEXIÓN EXITOSA!")
        logger.info("-" * 60)
        logger.info(f"Can Trade: {account['canTrade']}")
        logger.info(f"Can Withdraw: {account['canWithdraw']}")
        logger.info(f"Can Deposit: {account['canDeposit']}")
        logger.info(f"Account Type: {account['accountType']}")
        
        # Mostrar balances
        logger.info("-" * 60)
        logger.info("💰 BALANCES:")
        balances = [b for b in account['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
        
        if balances:
            for balance in balances[:10]:  # Mostrar primeros 10
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                logger.info(f"  {asset}: {total:.8f} (Free: {free:.8f}, Locked: {locked:.8f})")
        else:
            logger.warning("  No hay balances disponibles")
        
        logger.info("-" * 60)
        
        # Probar obtener precio
        logger.info("📈 Probando obtener precio de BTCUSDT...")
        ticker = client.get_symbol_ticker(symbol="BTCUSDT")
        logger.info(f"  Precio actual BTC: ${float(ticker['price']):,.2f}")
        
        logger.success("=" * 60)
        logger.success("✅ TODAS LAS PRUEBAS EXITOSAS")
        logger.success("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error("=" * 60)
        logger.error("❌ ERROR EN LA CONEXIÓN")
        logger.error("=" * 60)
        logger.error(f"Error: {str(e)}")
        logger.error("-" * 60)
        
        # Diagnóstico
        if "Invalid API-key" in str(e):
            logger.error("🔍 DIAGNÓSTICO: API Key inválida")
            logger.error("   Verifica que la API Key esté activa en Binance")
        elif "Signature" in str(e):
            logger.error("🔍 DIAGNÓSTICO: API Secret incorrecta")
            logger.error("   Verifica que el Secret esté correcto")
        elif "IP" in str(e):
            logger.error("🔍 DIAGNÓSTICO: IP no autorizada")
            logger.error("   Agrega tu IP en Binance o quita la restricción")
        elif "permission" in str(e).lower():
            logger.error("🔍 DIAGNÓSTICO: Sin permisos de trading")
            logger.error("   Habilita 'Enable Spot & Margin Trading' en Binance")
        else:
            logger.error("🔍 DIAGNÓSTICO: Error desconocido")
            logger.error(f"   Mensaje completo: {e}")
        
        logger.error("=" * 60)
        return False

def save_to_database():
    """Guarda las credenciales en la base de datos"""
    try:
        from src.database import get_database
        
        logger.info("💾 Guardando credenciales en base de datos...")
        
        db = get_database()
        
        # Actualizar configuración del usuario
        db.update_user_settings(1, {  # user_id = 1 (trader_pro)
            'broker': 'binance',
            'api_key': API_KEY,
            'api_secret': API_SECRET,
            'testnet': False  # MAINNET (real)
        })
        
        logger.success("✅ Credenciales guardadas en base de datos")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error guardando en DB: {e}")
        return False

if __name__ == "__main__":
    print("\n")
    logger.info("🚀 CONFIGURACIÓN AUTOMÁTICA DE BINANCE")
    print("\n")
    
    # Preguntar modo
    print("Selecciona el modo:")
    print("1. TESTNET (Pruebas - Dinero ficticio)")
    print("2. MAINNET (REAL - Tu dinero real)")
    print()
    
    choice = input("Opción (1 o 2): ").strip()
    
    testnet = choice == "1"
    
    if not testnet:
        print("\n⚠️  ADVERTENCIA: Vas a usar DINERO REAL")
        confirm = input("¿Estás seguro? (si/no): ").strip().lower()
        if confirm != "si":
            logger.warning("Operación cancelada")
            exit()
    
    print("\n")
    
    # Probar conexión
    success = test_binance_connection(testnet=testnet)
    
    if success:
        print("\n")
        # Guardar en DB
        save_to_database()
        
        print("\n")
        logger.success("=" * 60)
        logger.success("🎉 CONFIGURACIÓN COMPLETA")
        logger.success("=" * 60)
        logger.info("Ahora puedes:")
        logger.info("1. Ejecutar: .\\start_binance_real.bat")
        logger.info("2. Ir a Settings en TradePro")
        logger.info("3. Las credenciales ya están guardadas")
        logger.info("4. Click 'Conectar Broker'")
        logger.success("=" * 60)
    else:
        print("\n")
        logger.error("❌ Configuración fallida - Revisa los errores arriba")
        logger.info("💡 Soluciones:")
        logger.info("1. Verifica la API Key en Binance.com")
        logger.info("2. Verifica que tenga permisos de trading")
        logger.info("3. Verifica que esté activa (no suspendida)")
