"""
Configuración centralizada del sistema
Carga variables de entorno y configuración YAML
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from loguru import logger

# Cargar variables de entorno
load_dotenv()

class Settings:
    """Clase singleton para gestionar configuración del sistema"""
    
    _instance: Optional['Settings'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Carga configuración desde archivo YAML"""
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)
            logger.info(f"✓ Configuración cargada desde {config_path}")
        except Exception as e:
            logger.error(f"✗ Error cargando configuración: {e}")
            self._config = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene valor de configuración usando notación de punto
        Ejemplo: settings.get('trading.risk_management.max_risk_per_trade')
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
    
    # === BROKER CONFIGURATION ===
    @property
    def quotex_email(self) -> str:
        return os.getenv('QUOTEX_EMAIL', '')
    
    @property
    def quotex_password(self) -> str:
        return os.getenv('QUOTEX_PASSWORD', '')
    
    @property
    def quotex_demo_mode(self) -> bool:
        return os.getenv('QUOTEX_DEMO_MODE', 'true').lower() == 'true'
    
    @property
    def binance_api_key(self) -> str:
        return os.getenv('BINANCE_API_KEY', '')
    
    @property
    def binance_api_secret(self) -> str:
        return os.getenv('BINANCE_API_SECRET', '')
    
    @property
    def binance_testnet(self) -> bool:
        return os.getenv('BINANCE_TESTNET', 'true').lower() == 'true'
    
    # === TRADING CONFIGURATION ===
    @property
    def max_risk_per_trade(self) -> float:
        return float(os.getenv('MAX_RISK_PER_TRADE', 
                               self.get('trading.risk_management.max_risk_per_trade', 0.02)))
    
    @property
    def max_drawdown(self) -> float:
        return float(os.getenv('MAX_DRAWDOWN', 
                               self.get('trading.safety_limits.max_drawdown', 0.15)))
    
    @property
    def max_positions(self) -> int:
        return int(os.getenv('MAX_POSITIONS', 
                            self.get('trading.risk_management.max_positions', 3)))
    
    @property
    def initial_capital(self) -> float:
        return float(os.getenv('INITIAL_CAPITAL', 10000))
    
    # === AI CONFIGURATION ===
    @property
    def rl_learning_rate(self) -> float:
        return float(os.getenv('RL_LEARNING_RATE', 
                               self.get('ai.rl.learning_rate', 0.0003)))
    
    @property
    def confidence_threshold(self) -> float:
        return float(os.getenv('CONFIDENCE_THRESHOLD', 
                               self.get('ai.confidence.min_threshold', 0.70)))
    
    @property
    def lstm_lookback(self) -> int:
        return int(os.getenv('LSTM_LOOKBACK', 
                            self.get('ai.lstm.lookback_period', 100)))
    
    # === DATABASE CONFIGURATION ===
    @property
    def postgres_url(self) -> str:
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        db = os.getenv('POSTGRES_DB', 'trading_db')
        user = os.getenv('POSTGRES_USER', 'trading_user')
        password = os.getenv('POSTGRES_PASSWORD', 'password')
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"
    
    @property
    def redis_url(self) -> str:
        host = os.getenv('REDIS_HOST', 'localhost')
        port = os.getenv('REDIS_PORT', '6379')
        password = os.getenv('REDIS_PASSWORD', '')
        if password:
            return f"redis://:{password}@{host}:{port}/0"
        return f"redis://{host}:{port}/0"
    
    # === TELEGRAM CONFIGURATION ===
    @property
    def telegram_bot_token(self) -> str:
        return os.getenv('TELEGRAM_BOT_TOKEN', '')
    
    @property
    def telegram_chat_id(self) -> str:
        return os.getenv('TELEGRAM_CHAT_ID', '')
    
    # === TRADING MODE ===
    @property
    def trading_mode(self) -> str:
        return os.getenv('TRADING_MODE', 'demo')
    
    @property
    def auto_trading(self) -> bool:
        return os.getenv('AUTO_TRADING', 'false').lower() == 'true'
    
    @property
    def enable_rl_training(self) -> bool:
        return os.getenv('ENABLE_RL_TRAINING', 'true').lower() == 'true'
    
    # === LOGGING ===
    @property
    def log_level(self) -> str:
        return os.getenv('LOG_LEVEL', 'INFO')
    
    # === TIMEFRAMES & SYMBOLS ===
    @property
    def primary_timeframe(self) -> str:
        return os.getenv('PRIMARY_TIMEFRAME', 
                        self.get('timeframes.primary', '5m'))
    
    @property
    def trading_symbols(self) -> list:
        symbols_str = os.getenv('TRADING_SYMBOLS', 'EUR/USD,GBP/USD')
        return [s.strip() for s in symbols_str.split(',')]
    
    def __repr__(self) -> str:
        return f"<Settings(mode={self.trading_mode}, auto={self.auto_trading})>"


# Instancia global
settings = Settings()


# Configuración de Logger
def setup_logger():
    """Configura el sistema de logging"""
    log_level = settings.log_level
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Remover handlers por defecto
    logger.remove()
    
    # Console handler
    if os.getenv('LOG_TO_CONSOLE', 'true').lower() == 'true':
        logger.add(
            sink=lambda msg: print(msg, end=''),
            format=log_format,
            level=log_level,
            colorize=True
        )
    
    # File handler
    if os.getenv('LOG_TO_FILE', 'true').lower() == 'true':
        log_dir = Path(__file__).parent.parent.parent / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logger.add(
            sink=log_dir / "trading_{time:YYYY-MM-DD}.log",
            format=log_format,
            level=log_level,
            rotation="00:00",
            retention="30 days",
            compression="zip"
        )
    
    logger.info("=" * 60)
    logger.info("🚀 SISTEMA DE TRADING ALGORÍTMICO CON IA")
    logger.info(f"📊 Modo: {settings.trading_mode.upper()}")
    logger.info(f"🤖 Trading Automático: {'✓' if settings.auto_trading else '✗'}")
    logger.info(f"🧠 Entrenamiento RL: {'✓' if settings.enable_rl_training else '✗'}")
    logger.info("=" * 60)


# Inicializar logger al importar
setup_logger()
