"""
Sistema Principal de Trading
Orquesta todos los componentes: brokers, IA, risk management, etc.
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from loguru import logger

from ..config.settings import settings
from ..brokers.base_broker import BaseBroker, OrderSide, PositionSide
from ..brokers.quotex_broker import QuotexBroker
from ..brokers.binance_broker import BinanceBroker
from ..data.feature_engineering import FeatureEngineering
from ..models.lstm_predictor import LSTMPredictor
from ..models.rl_agent import RLAgent
from ..risk.risk_manager import RiskManager
from ..utils.performance_tracker import PerformanceTracker
from ..utils.telegram_notifier import TelegramNotifier


class TradingSystem:
    """
    Sistema principal de trading algorítmico con IA
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Estado del sistema
        self.is_running = False
        self.is_initialized = False
        
        # Componentes principales
        self.broker: Optional[BaseBroker] = None
        self.feature_engineer: Optional[FeatureEngineering] = None
        self.lstm_predictor: Optional[LSTMPredictor] = None
        self.rl_agent: Optional[RLAgent] = None
        self.risk_manager: Optional[RiskManager] = None
        self.performance_tracker: Optional[PerformanceTracker] = None
        self.notifier: Optional[TelegramNotifier] = None
        
        # Configuración
        self.symbol = self.config.get('symbol', 'EUR/USD')
        self.timeframe = self.config.get('timeframe', '5m')
        self.auto_trading = self.config.get('auto_trading', False)
        
        # Datos de mercado
        self.market_data: Optional[pd.DataFrame] = None
        self.last_update = None
        
        # Estadísticas
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        logger.info("=" * 70)
        logger.info("🚀 SISTEMA DE TRADING ALGORÍTMICO CON IA")
        logger.info("=" * 70)
    
    async def initialize(self):
        """Inicializa todos los componentes del sistema"""
        try:
            logger.info("🔧 Inicializando componentes del sistema...")
            
            # 1. Inicializar broker
            await self._initialize_broker()
            
            # 2. Inicializar feature engineering
            self.feature_engineer = FeatureEngineering(
                config=settings.get('technical_indicators')
            )
            logger.success("✓ Feature Engineering inicializado")
            
            # 3. Inicializar LSTM Predictor
            self.lstm_predictor = LSTMPredictor(
                config=settings.get('ai.lstm')
            )
            
            # Cargar modelo pre-entrenado si existe
            model_path = "models/best_lstm_model.pth"
            if not self.lstm_predictor.load(model_path):
                logger.warning("⚠️  No se encontró modelo LSTM pre-entrenado")
                logger.info("💡 Se entrenará con datos históricos en el primer uso")
            
            # 4. Inicializar RL Agent
            self.rl_agent = RLAgent(
                config=settings.get('ai.rl')
            )
            
            # Cargar modelo pre-entrenado si existe
            rl_model_path = "models/best_rl_model.zip"
            if not self.rl_agent.load(rl_model_path):
                logger.warning("⚠️  No se encontró modelo RL pre-entrenado")
                logger.info("💡 Se entrenará con simulaciones en el primer uso")
            
            # 5. Inicializar Risk Manager
            self.risk_manager = RiskManager(
                config=settings.get('trading.risk_management')
            )
            logger.success("✓ Risk Manager inicializado")
            
            # 6. Inicializar Performance Tracker
            self.performance_tracker = PerformanceTracker(
                initial_capital=settings.initial_capital
            )
            logger.success("✓ Performance Tracker inicializado")
            
            # 7. Inicializar notificador de Telegram
            if settings.telegram_bot_token and settings.telegram_chat_id:
                self.notifier = TelegramNotifier(
                    bot_token=settings.telegram_bot_token,
                    chat_id=settings.telegram_chat_id
                )
                await self.notifier.send_message("🚀 Sistema de Trading Inicializado")
                logger.success("✓ Telegram Notifier inicializado")
            
            self.is_initialized = True
            logger.success("=" * 70)
            logger.success("✓ SISTEMA COMPLETAMENTE INICIALIZADO")
            logger.success("=" * 70)
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Error inicializando sistema: {e}")
            return False
    
    async def _initialize_broker(self):
        """Inicializa conexión con el broker"""
        broker_type = self.config.get('broker', 'quotex')
        
        if broker_type == 'quotex':
            self.broker = QuotexBroker({
                'email': settings.quotex_email,
                'password': settings.quotex_password,
                'demo_mode': settings.quotex_demo_mode,
                'initial_balance': settings.initial_capital
            })
        elif broker_type == 'binance':
            self.broker = BinanceBroker({
                'api_key': settings.binance_api_key,
                'api_secret': settings.binance_api_secret,
                'testnet': settings.binance_testnet,
                'demo_mode': settings.binance_testnet
            })
        else:
            raise ValueError(f"Broker no soportado: {broker_type}")
        
        # Conectar
        connected = await self.broker.connect()
        if not connected:
            raise ConnectionError("No se pudo conectar al broker")
        
        logger.success(f"✓ Conectado a {broker_type.upper()}")
    
    async def start(self):
        """Inicia el sistema de trading"""
        if not self.is_initialized:
            logger.error("✗ Sistema no inicializado. Llamar a initialize() primero")
            return
        
        self.is_running = True
        logger.info("=" * 70)
        logger.info("▶️  SISTEMA DE TRADING INICIADO")
        logger.info(f"📊 Símbolo: {self.symbol}")
        logger.info(f"⏱️  Timeframe: {self.timeframe}")
        logger.info(f"🤖 Trading Automático: {'✓' if self.auto_trading else '✗'}")
        logger.info("=" * 70)
        
        # Enviar notificación
        if self.notifier:
            await self.notifier.send_message(
                f"▶️ Trading iniciado\n"
                f"📊 {self.symbol} | {self.timeframe}\n"
                f"🤖 Auto: {'Sí' if self.auto_trading else 'No'}"
            )
        
        # Loop principal
        await self._main_loop()
    
    async def stop(self):
        """Detiene el sistema de trading"""
        self.is_running = False
        logger.info("⏸️  Deteniendo sistema...")
        
        # Cerrar todas las posiciones si está configurado
        if self.config.get('close_positions_on_stop', False):
            await self._close_all_positions()
        
        # Desconectar broker
        if self.broker:
            await self.broker.disconnect()
        
        # Enviar notificación
        if self.notifier:
            await self.notifier.send_message("⏸️ Sistema de Trading Detenido")
        
        logger.success("✓ Sistema detenido")
    
    async def _main_loop(self):
        """Loop principal del sistema"""
        
        while self.is_running:
            try:
                # 1. Obtener datos del mercado
                await self._update_market_data()
                
                # 2. Calcular features
                if self.market_data is not None and len(self.market_data) > 0:
                    self.market_data = self.feature_engineer.calculate_all_features(
                        self.market_data
                    )
                
                # 3. Actualizar estado del risk manager
                await self._update_risk_manager()
                
                # 4. Monitorear posiciones abiertas
                await self._monitor_positions()
                
                # 5. Generar señal de trading (si auto trading está activo)
                if self.auto_trading:
                    await self._generate_and_execute_signal()
                
                # 6. Actualizar performance tracker
                await self._update_performance()
                
                # 7. Esperar hasta la próxima vela
                await self._wait_next_candle()
                
            except Exception as e:
                logger.error(f"✗ Error en main loop: {e}")
                await asyncio.sleep(5)  # Esperar antes de reintentar
        
        logger.info("🛑 Main loop terminado")
    
    async def _update_market_data(self):
        """Actualiza datos del mercado"""
        try:
            # Obtener datos históricos
            df = await self.broker.get_live_data(
                symbol=self.symbol,
                timeframe=self.timeframe,
                bars=200  # Suficiente para indicadores
            )
            
            if df is not None and not df.empty:
                self.market_data = df
                self.last_update = datetime.now()
                logger.debug(f"📊 Datos actualizados: {len(df)} velas")
            else:
                logger.warning("⚠️  No se pudieron obtener datos del mercado")
                
        except Exception as e:
            logger.error(f"✗ Error actualizando datos: {e}")
    
    async def _update_risk_manager(self):
        """Actualiza estado del risk manager"""
        try:
            # Obtener info de cuenta
            account_info = await self.broker.get_account_info()
            
            # Obtener posiciones abiertas
            open_positions = await self.broker.get_open_positions()
            
            # Actualizar risk manager
            self.risk_manager.update_state(
                current_equity=account_info.equity,
                peak_equity=self.performance_tracker.peak_equity,
                open_positions=len(open_positions),
                daily_pnl=self.performance_tracker.daily_pnl
            )
            
        except Exception as e:
            logger.error(f"✗ Error actualizando risk manager: {e}")
    
    async def _monitor_positions(self):
        """Monitorea y actualiza posiciones abiertas"""
        try:
            positions = await self.broker.get_open_positions()
            
            for position in positions:
                # Actualizar trailing stop si está configurado
                if settings.get('trading.stop_loss.trailing_enabled', True):
                    await self._update_trailing_stop(position)
                
                # Log de estado
                pnl_emoji = "🟢" if position.unrealized_pnl > 0 else "🔴"
                logger.debug(
                    f"{pnl_emoji} Posición {position.id}: "
                    f"{position.side.value} {position.symbol} | "
                    f"P&L: ${position.unrealized_pnl:.2f} ({position.unrealized_pnl_percent:+.2f}%)"
                )
                
        except Exception as e:
            logger.error(f"✗ Error monitoreando posiciones: {e}")
    
    async def _update_trailing_stop(self, position):
        """Actualiza trailing stop de una posición"""
        try:
            # Calcular ATR
            atr = self.feature_engineer.calculate_atr(self.market_data)
            
            # Calcular nuevo trailing stop
            new_stop = self.risk_manager.calculate_trailing_stop(
                entry_price=position.entry_price,
                current_price=position.current_price,
                side=position.side.value,
                atr=atr,
                atr_multiplier=settings.get('trading.stop_loss.trailing_atr_multiplier', 1.5)
            )
            
            # Actualizar si es necesario
            if new_stop and new_stop != position.stop_loss:
                order_id = position.metadata.get('order_id')
                if order_id:
                    await self.broker.modify_order(
                        order_id=order_id,
                        stop_loss=new_stop
                    )
                    logger.info(f"📈 Trailing stop actualizado: {position.id} → {new_stop:.5f}")
                    
        except Exception as e:
            logger.error(f"✗ Error actualizando trailing stop: {e}")
    
    async def _generate_and_execute_signal(self):
        """Genera señal de trading y ejecuta si es válida"""
        try:
            # Verificar si se puede operar
            can_trade, reason = self.risk_manager.can_trade()
            if not can_trade:
                logger.debug(f"⏸️  No se puede operar: {reason}")
                return
            
            # 1. PREDICCIÓN LSTM
            predicted_prices, lstm_confidence, price_change = self.lstm_predictor.predict(
                self.market_data
            )
            
            direction_lstm = "UP" if price_change > 0 else "DOWN"
            
            logger.info(f"🧠 LSTM Predicción: {direction_lstm} | "
                       f"Cambio: {price_change:+.2f}% | "
                       f"Confianza: {lstm_confidence:.2%}")
            
            # 2. DECISIÓN RL AGENT
            # Preparar estado
            state = self.feature_engineer.get_feature_vector(
                self.market_data,
                lookback=1
            )
            
            # Obtener acción
            action, action_probs = self.rl_agent.select_action(state, deterministic=True)
            action_name = self.rl_agent.get_action_name(action)
            rl_confidence = float(action_probs[action])
            
            logger.info(f"🤖 RL Acción: {action_name} | Confianza: {rl_confidence:.2%}")
            
            # 3. COMBINAR PREDICCIONES
            # Verificar alineación
            action_direction = "UP" if action in [1, 2, 3, 4] else "DOWN" if action in [5, 6, 7, 8] else "NEUTRAL"
            
            if action_direction == "NEUTRAL" or action == 0:  # HOLD
                logger.debug("⏸️  Acción HOLD - No operar")
                return
            
            # Verificar alineación entre LSTM y RL
            if action_direction != direction_lstm:
                logger.warning("⚠️  LSTM y RL no están alineados - No operar")
                return
            
            # Calcular confianza combinada
            lstm_weight = settings.get('ai.confidence.lstm_weight', 0.4)
            rl_weight = settings.get('ai.confidence.rl_weight', 0.6)
            combined_confidence = lstm_confidence * lstm_weight + rl_confidence * rl_weight
            
            # Verificar umbral de confianza
            min_confidence = settings.confidence_threshold
            if combined_confidence < min_confidence:
                logger.info(f"⏸️  Confianza insuficiente: {combined_confidence:.2%} < {min_confidence:.2%}")
                return
            
            logger.success(f"✓ SEÑAL VÁLIDA: {action_direction} | Confianza: {combined_confidence:.2%}")
            
            # 4. EJECUTAR TRADE
            await self._execute_trade(
                direction=action_direction,
                confidence=combined_confidence,
                action=action
            )
            
        except Exception as e:
            logger.error(f"✗ Error generando señal: {e}")
    
    async def _execute_trade(self, direction: str, confidence: float, action: int):
        """Ejecuta un trade"""
        try:
            # Obtener precio actual
            bid, ask = await self.broker.get_current_price(self.symbol)
            current_price = ask if direction == "UP" else bid
            
            # Calcular ATR para stop loss
            atr = self.feature_engineer.calculate_atr(self.market_data)
            
            # Calcular stop loss
            side = "long" if direction == "UP" else "short"
            stop_loss = self.risk_manager.calculate_stop_loss(
                entry_price=current_price,
                side=side,
                atr=atr,
                method=settings.get('trading.stop_loss.method', 'atr'),
                atr_multiplier=settings.get('trading.stop_loss.atr_multiplier', 1.5)
            )
            
            # Calcular take profit
            take_profit = self.risk_manager.calculate_take_profit(
                entry_price=current_price,
                stop_loss=stop_loss,
                side=side,
                risk_reward_ratio=settings.get('trading.take_profit.risk_reward_ratio', 2.0)
            )
            
            # Validar parámetros
            is_valid, validation_msg = self.risk_manager.validate_trade_parameters(
                entry_price=current_price,
                stop_loss=stop_loss,
                take_profit=take_profit,
                side=side
            )
            
            if not is_valid:
                logger.warning(f"⚠️  Trade inválido: {validation_msg}")
                return
            
            # Obtener balance
            account_info = await self.broker.get_account_info()
            
            # Calcular tamaño de posición
            position_size = self.risk_manager.calculate_position_size(
                balance=account_info.balance,
                entry_price=current_price,
                stop_loss_price=stop_loss,
                confidence=confidence,
                method=settings.get('trading.risk_management.position_sizing_method', 'kelly_modified')
            )
            
            if position_size <= 0:
                logger.warning("⚠️  Tamaño de posición = 0")
                return
            
            # Ejecutar orden
            logger.info("=" * 70)
            logger.info("📤 EJECUTANDO TRADE")
            logger.info(f"  Dirección: {direction}")
            logger.info(f"  Precio: {current_price:.5f}")
            logger.info(f"  Tamaño: {position_size:.4f}")
            logger.info(f"  Stop Loss: {stop_loss:.5f}")
            logger.info(f"  Take Profit: {take_profit:.5f}")
            logger.info(f"  Confianza: {confidence:.2%}")
            logger.info("=" * 70)
            
            order_side = OrderSide.BUY if direction == "UP" else OrderSide.SELL
            
            order = await self.broker.place_market_order(
                symbol=self.symbol,
                side=order_side,
                quantity=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            # Registrar trade
            self.total_trades += 1
            self.performance_tracker.register_trade_opened(
                symbol=self.symbol,
                side=side,
                entry_price=current_price,
                quantity=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit
            )
            
            # Enviar notificación
            if self.notifier:
                await self.notifier.send_message(
                    f"📤 TRADE ABIERTO\n"
                    f"{'🟢 LONG' if direction == 'UP' else '🔴 SHORT'} {self.symbol}\n"
                    f"💰 Precio: {current_price:.5f}\n"
                    f"📊 Tamaño: {position_size:.4f}\n"
                    f"🛑 SL: {stop_loss:.5f}\n"
                    f"🎯 TP: {take_profit:.5f}\n"
                    f"🎲 Confianza: {confidence:.1%}"
                )
            
            logger.success("✓ Trade ejecutado exitosamente")
            
        except Exception as e:
            logger.error(f"✗ Error ejecutando trade: {e}")
    
    async def _update_performance(self):
        """Actualiza métricas de performance"""
        try:
            # Obtener info de cuenta
            account_info = await self.broker.get_account_info()
            
            # Actualizar tracker
            self.performance_tracker.update(
                equity=account_info.equity,
                balance=account_info.balance,
                unrealized_pnl=account_info.unrealized_pnl
            )
            
        except Exception as e:
            logger.error(f"✗ Error actualizando performance: {e}")
    
    async def _wait_next_candle(self):
        """Espera hasta la próxima vela"""
        # Calcular tiempo hasta próxima vela
        timeframe_minutes = self._parse_timeframe(self.timeframe)
        now = datetime.now()
        
        # Calcular próxima vela
        minutes_elapsed = now.minute % timeframe_minutes
        seconds_elapsed = now.second
        
        wait_seconds = (timeframe_minutes - minutes_elapsed) * 60 - seconds_elapsed
        
        if wait_seconds > 0:
            logger.debug(f"⏳ Esperando {wait_seconds}s hasta próxima vela...")
            await asyncio.sleep(wait_seconds)
        else:
            await asyncio.sleep(5)  # Espera mínima
    
    async def _close_all_positions(self):
        """Cierra todas las posiciones abiertas"""
        try:
            positions = await self.broker.get_open_positions()
            
            for position in positions:
                logger.info(f"🔒 Cerrando posición: {position.id}")
                await self.broker.close_position(position.id)
            
            logger.success(f"✓ {len(positions)} posiciones cerradas")
            
        except Exception as e:
            logger.error(f"✗ Error cerrando posiciones: {e}")
    
    def _parse_timeframe(self, timeframe: str) -> int:
        """Convierte timeframe a minutos"""
        mapping = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440, '1D': 1440
        }
        return mapping.get(timeframe, 5)
    
    def get_status(self) -> Dict:
        """Retorna estado actual del sistema"""
        return {
            'is_running': self.is_running,
            'is_initialized': self.is_initialized,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'auto_trading': self.auto_trading,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'last_update': self.last_update.isoformat() if self.last_update else None
        }
