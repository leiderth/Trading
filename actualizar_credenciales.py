"""
Script para actualizar credenciales de Binance
Ejecuta esto después de crear una nueva API Key
"""

from src.database import get_database
from loguru import logger

# PEGA AQUÍ TUS NUEVAS CREDENCIALES
API_KEY = "PEGA_TU_NUEVA_API_KEY_AQUI"
API_SECRET = "PEGA_TU_NUEVO_API_SECRET_AQUI"

def update_credentials():
    """Actualiza credenciales en la base de datos"""
    
    if "PEGA_TU" in API_KEY or "PEGA_TU" in API_SECRET:
        logger.error("❌ Debes editar este archivo y pegar tus credenciales")
        logger.info("1. Abre: actualizar_credenciales.py")
        logger.info("2. Reemplaza API_KEY y API_SECRET")
        logger.info("3. Guarda el archivo")
        logger.info("4. Ejecuta de nuevo")
        return False
    
    try:
        logger.info("Actualizando credenciales en base de datos...")
        
        db = get_database()
        db.update_user_settings(1, {
            'broker': 'binance',
            'api_key': API_KEY,
            'api_secret': API_SECRET,
            'testnet': False
        })
        
        logger.success("✅ Credenciales actualizadas")
        logger.info(f"API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n")
    logger.info("🔄 ACTUALIZANDO CREDENCIALES")
    print("\n")
    
    if update_credentials():
        print("\n")
        logger.success("✅ Listo!")
        logger.info("Ahora ejecuta: .\\venv\\Scripts\\python.exe test_binance_auto.py")
        print("\n")
