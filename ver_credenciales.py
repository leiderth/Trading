"""
Script para ver las credenciales guardadas en la base de datos
"""

from src.database import get_database
from loguru import logger

def ver_credenciales():
    """Ver credenciales guardadas"""
    
    logger.info("=" * 70)
    logger.info("🔍 VERIFICANDO CREDENCIALES GUARDADAS")
    logger.info("=" * 70)
    
    try:
        db = get_database()
        
        # Obtener usuario
        user = db.get_user_by_username("trader_pro")
        if not user:
            logger.error("❌ Usuario 'trader_pro' no encontrado")
            return
        
        user_id = user['id']
        logger.info(f"Usuario: {user['username']} (ID: {user_id})")
        logger.info(f"Balance: ${user['current_balance']:,.2f}")
        logger.info("-" * 70)
        
        # Obtener configuración
        settings = db.get_user_settings(user_id)
        
        if settings:
            logger.success("✅ CONFIGURACIÓN ENCONTRADA")
            logger.info("-" * 70)
            logger.info(f"Broker: {settings.get('broker', 'No configurado')}")
            logger.info(f"API Key: {settings.get('api_key', 'No configurada')}")
            logger.info(f"API Secret: {settings.get('api_secret', 'No configurada')}")
            logger.info(f"Testnet: {settings.get('testnet', 'No configurado')}")
            logger.info("-" * 70)
            
            # Verificar que las credenciales sean las correctas
            expected_key = "AsJ3UTzFTux4wnzWQiMvYuThjgo05FlZpd6sYRKdihHZtAC4pAy1gL7O3QyiFMTC"
            expected_secret = "tbFovnluEo5BBSG8l91hXbC7hF72bSxcnbiud0xoCrQS1pOjqvTrBsScznNjNJ8N"
            
            if settings.get('api_key') == expected_key:
                logger.success("✅ API Key correcta")
            else:
                logger.error("❌ API Key NO coincide")
                logger.info(f"Esperada: {expected_key[:20]}...")
                logger.info(f"Guardada: {settings.get('api_key', '')[:20]}...")
            
            if settings.get('api_secret') == expected_secret:
                logger.success("✅ API Secret correcta")
            else:
                logger.error("❌ API Secret NO coincide")
                logger.info(f"Esperada: {expected_secret[:20]}...")
                logger.info(f"Guardada: {settings.get('api_secret', '')[:20]}...")
            
        else:
            logger.error("❌ NO SE ENCONTRÓ CONFIGURACIÓN")
            logger.info("Ejecuta: python test_binance_auto.py")
            logger.info("Esto guardará las credenciales")
        
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n")
    ver_credenciales()
    print("\n")
