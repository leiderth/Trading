"""
Script para entrenar el agente de Reinforcement Learning
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.config.settings import settings, logger
from src.models.rl_agent import RLAgent, TrainingCallback


def main():
    """Entrena el agente RL"""
    
    logger.info("=" * 70)
    logger.info("🎓 ENTRENAMIENTO DEL AGENTE RL (PPO)")
    logger.info("=" * 70)
    
    # 1. Crear agente
    logger.info("🤖 Creando agente RL...")
    
    rl_config = settings.get('ai.rl')
    agent = RLAgent(config=rl_config)
    
    # 2. Construir modelo
    agent.build_model()
    
    # 3. Entrenar
    logger.info("\n🎓 Iniciando entrenamiento...")
    logger.info("  Total timesteps: 100,000")
    logger.info("  (Esto puede tomar 30-60 minutos...)")
    
    callback = TrainingCallback(verbose=1)
    
    agent.train(
        total_timesteps=100000,
        callback=callback
    )
    
    # 4. Guardar modelo
    logger.info("\n💾 Guardando modelo...")
    
    model_dir = Path(__file__).parent.parent / "models"
    model_dir.mkdir(exist_ok=True)
    
    agent.save(model_dir / "best_rl_model.zip")
    
    # 5. Resumen
    logger.info("\n" + "=" * 70)
    logger.success("✓ ENTRENAMIENTO RL COMPLETADO")
    logger.info("=" * 70)
    logger.info("💡 El agente ha sido entrenado en un environment simulado")
    logger.info("💡 Se recomienda hacer backtesting antes de usar en producción")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
