"""
Test de conexión a la API REST
Simula lo que hace la GUI
"""

import requests
import json
from loguru import logger

# Configuración
API_URL = "http://127.0.0.1:8001"
API_KEY = "AsJ3UTzFTux4wnzWQiMvYuThjgo05FlZpd6sYRKdihHZtAC4pAy1gL7O3QyiFMTC"
API_SECRET = "tbFovnluEo5BBSG8l91hXbC7hF72bSxcnbiud0xoCrQS1pOjqvTrBsScznNjNJ8N"

def test_health():
    """Test 1: Verificar que la API esté corriendo"""
    logger.info("=" * 70)
    logger.info("TEST 1: Verificar API corriendo")
    logger.info("=" * 70)
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            logger.success("✅ API está corriendo")
            logger.info(f"Respuesta: {response.json()}")
            return True
        else:
            logger.error(f"❌ API respondió con código {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("❌ No se puede conectar a la API")
        logger.error("   Asegúrate de que esté corriendo:")
        logger.error("   uvicorn src.api.trading_api:app --reload --port 8001")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

def test_broker_connection():
    """Test 2: Conectar al broker"""
    logger.info("=" * 70)
    logger.info("TEST 2: Conectar a Binance")
    logger.info("=" * 70)
    
    try:
        # Preparar payload (igual que la GUI)
        payload = {
            "broker_type": "binance",
            "credentials": {
                "api_key": API_KEY,
                "api_secret": API_SECRET,
                "testnet": False
            },
            "demo_mode": False
        }
        
        logger.info(f"Enviando POST a {API_URL}/api/broker/connect")
        logger.info(f"Broker: binance")
        logger.info(f"Testnet: False")
        logger.info(f"API Key: {API_KEY[:10]}...")
        
        # Hacer request
        response = requests.post(
            f"{API_URL}/api/broker/connect",
            json=payload,
            timeout=30
        )
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Respuesta: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            logger.success("✅ CONEXIÓN EXITOSA")
            logger.info(f"Mensaje: {data.get('message')}")
            logger.info(f"Broker: {data.get('broker')}")
            return True
        else:
            logger.error(f"❌ Error {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"Detalle: {error_data.get('detail')}")
            except:
                logger.error(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout - La API no respondió en 30 segundos")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n")
    logger.info("🧪 TEST DE CONEXIÓN API → BINANCE")
    print("\n")
    
    # Test 1: API corriendo
    if not test_health():
        logger.error("❌ La API no está corriendo. Inicia la API primero.")
        return
    
    print("\n")
    
    # Test 2: Conectar broker
    if test_broker_connection():
        print("\n")
        logger.success("=" * 70)
        logger.success("🎉 TODOS LOS TESTS EXITOSOS")
        logger.success("=" * 70)
        logger.info("La GUI debería poder conectarse sin problemas")
    else:
        print("\n")
        logger.error("=" * 70)
        logger.error("❌ TEST FALLÓ")
        logger.error("=" * 70)
        logger.info("Revisa los logs de la API para más detalles")
    
    print("\n")

if __name__ == "__main__":
    main()
