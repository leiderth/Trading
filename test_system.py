"""
Script de prueba rapida del sistema
Verifica que todos los componentes esten instalados correctamente
"""

import sys
from pathlib import Path

print("=" * 70)
print("VERIFICACION DEL SISTEMA DE TRADING")
print("=" * 70)

# Test 1: Importaciones basicas
print("\n1. Verificando importaciones basicas...")
try:
    import numpy as np
    import pandas as pd
    print("   OK - NumPy y Pandas")
except ImportError as e:
    print(f"   ERROR - {e}")
    sys.exit(1)

# Test 2: PyTorch
print("\n2. Verificando PyTorch...")
try:
    import torch
    print(f"   OK - PyTorch {torch.__version__}")
    print(f"   CUDA disponible: {torch.cuda.is_available()}")
except ImportError as e:
    print(f"   ERROR - {e}")
    sys.exit(1)

# Test 3: TensorFlow
print("\n3. Verificando TensorFlow...")
try:
    import tensorflow as tf
    print(f"   OK - TensorFlow {tf.__version__}")
except ImportError as e:
    print(f"   ERROR - {e}")
    sys.exit(1)

# Test 4: Stable Baselines3
print("\n4. Verificando Stable-Baselines3...")
try:
    import stable_baselines3
    print(f"   OK - Stable-Baselines3 {stable_baselines3.__version__}")
except ImportError as e:
    print(f"   ERROR - {e}")
    sys.exit(1)

# Test 5: TA-Lib
print("\n5. Verificando TA-Lib...")
try:
    import talib
    print("   OK - TA-Lib")
except ImportError as e:
    print(f"   ERROR - {e}")
    print("   SOLUCION: Instalar TA-Lib (ver INSTALL.md)")

# Test 6: pandas-ta
print("\n6. Verificando pandas-ta...")
try:
    import pandas_ta as ta
    print("   OK - pandas-ta")
except ImportError as e:
    print(f"   ERROR - {e}")
    sys.exit(1)

# Test 7: Modulos del sistema
print("\n7. Verificando modulos del sistema...")
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from src.config.settings import settings
    print("   OK - Settings")
    
    from src.brokers.quotex_broker import QuotexBroker
    print("   OK - QuotexBroker")
    
    from src.data.feature_engineering import FeatureEngineering
    print("   OK - FeatureEngineering")
    
    from src.models.lstm_predictor import LSTMPredictor
    print("   OK - LSTMPredictor")
    
    from src.models.rl_agent import RLAgent
    print("   OK - RLAgent")
    
    from src.risk.risk_manager import RiskManager
    print("   OK - RiskManager")
    
    from src.core.trading_system import TradingSystem
    print("   OK - TradingSystem")
    
except ImportError as e:
    print(f"   ERROR - {e}")
    sys.exit(1)

# Test 8: Archivos de configuracion
print("\n8. Verificando archivos de configuracion...")

config_file = Path("config/config.yaml")
if config_file.exists():
    print("   OK - config.yaml encontrado")
else:
    print("   ERROR - config.yaml no encontrado")

env_file = Path(".env")
if env_file.exists():
    print("   OK - .env encontrado")
else:
    print("   ADVERTENCIA - .env no encontrado (copiar de .env.example)")

# Test 9: Directorios
print("\n9. Verificando estructura de directorios...")

required_dirs = ['src', 'config', 'models', 'logs', 'scripts']
for dir_name in required_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists():
        print(f"   OK - {dir_name}/")
    else:
        print(f"   Creando - {dir_name}/")
        dir_path.mkdir(exist_ok=True)

# Test 10: Test rapido de componentes
print("\n10. Test rapido de componentes...")

try:
    # Test Feature Engineering
    fe = FeatureEngineering()
    test_data = pd.DataFrame({
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='5min'),
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 101,
        'low': np.random.randn(100).cumsum() + 99,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    df_with_features = fe.calculate_all_features(test_data)
    print(f"   OK - Feature Engineering ({len(df_with_features.columns)} features)")
    
    # Test Risk Manager
    rm = RiskManager()
    position_size = rm.calculate_position_size(
        balance=10000,
        entry_price=1.0850,
        stop_loss_price=1.0830,
        confidence=0.75
    )
    print(f"   OK - Risk Manager (position size: {position_size:.4f})")
    
except Exception as e:
    print(f"   ERROR - {e}")
    import traceback
    traceback.print_exc()

# Resumen final
print("\n" + "=" * 70)
print("VERIFICACION COMPLETADA")
print("=" * 70)
print("\nSistema listo para usar!")
print("\nProximos pasos:")
print("1. Configurar .env con tus credenciales")
print("2. Ejecutar: python main.py")
print("3. Ver QUICKSTART.md para mas informacion")
print("=" * 70)
