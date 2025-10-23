"""
Test completo del sistema
Verifica API, Broker y conexión end-to-end
"""

import asyncio
import requests
from loguru import logger

# Credenciales de Demo Trading
DEMO_API_KEY = "Q9JgwPqSs6n4cAehdAn2DeBD1cQRZkqjUjRy4O3UY4mBquKxvMnjJiyXqO8I5esO"
DEMO_API_SECRET = "qcixvUmW5EJCuzbXv9IEfpcc8k04AyNysawSUjcSycIJrxEJjFtZTK3g0JushnvV"

API_URL = "http://127.0.0.1:8001"

def test_1_api_health():
    """Test 1: Verificar que la API esté corriendo"""
    logger.info("=" * 70)
    logger.info("TEST 1: API Health Check")
    logger.info("=" * 70)
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            logger.success("✅ API está corriendo")
            logger.info(f"   Status: {data.get('status')}")
            logger.info(f"   Timestamp: {data.get('timestamp')}")
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

def test_2_broker_direct():
    """Test 2: Probar BinanceBroker directamente"""
    logger.info("=" * 70)
    logger.info("TEST 2: BinanceBroker Directo")
    logger.info("=" * 70)
    
    try:
        from src.brokers.binance_broker import BinanceBroker
        
        config = {
            'api_key': DEMO_API_KEY,
            'api_secret': DEMO_API_SECRET,
            'testnet': True
        }
        
        logger.info("Creando instancia de BinanceBroker...")
        broker = BinanceBroker(config)
        
        logger.info("Intentando conectar...")
        result = asyncio.run(broker.connect())
        
        if result:
            logger.success("✅ BinanceBroker conectado exitosamente")
            return True
        else:
            logger.error("❌ BinanceBroker no pudo conectar")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_3_api_endpoint():
    """Test 3: Probar endpoint /api/broker/connect"""
    logger.info("=" * 70)
    logger.info("TEST 3: API Endpoint /api/broker/connect")
    logger.info("=" * 70)
    
    try:
        payload = {
            "broker_type": "binance",
            "credentials": {
                "api_key": DEMO_API_KEY,
                "api_secret": DEMO_API_SECRET,
                "testnet": True
            },
            "demo_mode": True
        }
        
        logger.info(f"Enviando POST a {API_URL}/api/broker/connect")
        logger.info(f"Broker: binance")
        logger.info(f"Testnet: True")
        logger.info(f"API Key: {DEMO_API_KEY[:10]}...")
        
        response = requests.post(
            f"{API_URL}/api/broker/connect",
            json=payload,
            timeout=60  # 60 segundos de timeout
        )
        
        logger.info(f"Status Code: {response.status_code}")
        logger.info(f"Respuesta: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') or data.get('status') == 'success':
                logger.success("✅ Endpoint conectó exitosamente")
                logger.info(f"   Mensaje: {data.get('message')}")
                return True
            else:
                logger.error(f"❌ Endpoint retornó error: {data}")
                return False
        else:
            logger.error(f"❌ Error HTTP {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"   Detalle: {error_data.get('detail')}")
            except:
                logger.error(f"   Respuesta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        logger.error("❌ Timeout - La API no respondió en 60 segundos")
        logger.error("   Revisa los logs de la API para ver qué está pasando")
        return False
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n")
    logger.info("🧪 TEST COMPLETO DEL SISTEMA")
    print("\n")
    
    results = []
    
    # Test 1: API Health
    results.append(("API Health", test_1_api_health()))
    print("\n")
    
    if not results[0][1]:
        logger.error("❌ La API no está corriendo. No se pueden ejecutar más tests.")
        logger.info("Inicia la API con:")
        logger.info("  uvicorn src.api.trading_api:app --reload --port 8001")
        return
    
    # Test 2: Broker Directo
    results.append(("Broker Directo", test_2_broker_direct()))
    print("\n")
    
    # Test 3: API Endpoint
    results.append(("API Endpoint", test_3_api_endpoint()))
    print("\n")
    
    # Resumen
    logger.info("=" * 70)
    logger.info("📊 RESUMEN DE TESTS")
    logger.info("=" * 70)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {name}")
    
    print("\n")
    
    if all(r[1] for r in results):
        logger.success("=" * 70)
        logger.success("🎉 TODOS LOS TESTS PASARON")
        logger.success("=" * 70)
        logger.info("")
        logger.info("El sistema está funcionando correctamente.")
        logger.info("Ahora puedes usar TradePro:")
        logger.info("  python launch_app.py")
        logger.info("")
    else:
        logger.error("=" * 70)
        logger.error("❌ ALGUNOS TESTS FALLARON")
        logger.error("=" * 70)
        logger.info("")
        logger.info("Revisa los errores arriba para más detalles.")
        logger.info("")
    
    print("\n")

if __name__ == "__main__":
    main()
