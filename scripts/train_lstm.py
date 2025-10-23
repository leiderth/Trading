"""
Script para entrenar el modelo LSTM
"""

import sys
import asyncio
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config.settings import settings, logger
from src.brokers.quotex_broker import QuotexBroker
from src.models.lstm_predictor import LSTMPredictor


async def main():
    """Entrena el modelo LSTM con datos históricos"""
    
    logger.info("=" * 70)
    logger.info("🎓 ENTRENAMIENTO DEL MODELO LSTM")
    logger.info("=" * 70)
    
    # 1. Conectar al broker para obtener datos
    logger.info("📊 Obteniendo datos históricos...")
    
    broker = QuotexBroker({
        'email': settings.quotex_email,
        'password': settings.quotex_password,
        'demo_mode': True,
        'initial_balance': 10000
    })
    
    await broker.connect()
    
    # Obtener datos históricos (2 años)
    symbol = 'EUR/USD'
    timeframe = '5m'
    bars = 100000  # Aproximadamente 2 años de datos en 5m
    
    logger.info(f"  Símbolo: {symbol}")
    logger.info(f"  Timeframe: {timeframe}")
    logger.info(f"  Velas: {bars}")
    
    df = await broker.get_live_data(symbol, timeframe, bars)
    
    if df.empty:
        logger.error("✗ No se pudieron obtener datos")
        return
    
    logger.success(f"✓ Datos obtenidos: {len(df)} velas")
    
    # 2. Crear y entrenar modelo LSTM
    logger.info("\n🧠 Creando modelo LSTM...")
    
    lstm_config = settings.get('ai.lstm')
    predictor = LSTMPredictor(config=lstm_config)
    
    # 3. Entrenar
    logger.info("\n🎓 Iniciando entrenamiento...")
    logger.info("  (Esto puede tomar varios minutos...)")
    
    metrics = predictor.train(
        df=df,
        validation_split=0.2,
        verbose=True
    )
    
    # 4. Guardar modelo
    logger.info("\n💾 Guardando modelo...")
    
    model_dir = Path(__file__).parent.parent / "models"
    model_dir.mkdir(exist_ok=True)
    
    predictor.save(model_dir / "best_lstm_model.pth")
    
    # 5. Resumen
    logger.info("\n" + "=" * 70)
    logger.success("✓ ENTRENAMIENTO COMPLETADO")
    logger.info("=" * 70)
    logger.info(f"📊 Best Val Loss: {metrics['best_val_loss']:.6f}")
    logger.info(f"🎯 Confidence Score: {metrics['confidence']:.2%}")
    logger.info(f"📈 Epochs Trained: {metrics['epochs_trained']}")
    logger.info("=" * 70)
    
    # Desconectar
    await broker.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
