"""
Sistema de Trading Automático con IA
Analiza el mercado y ejecuta operaciones automáticamente
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from loguru import logger
import pandas as pd
import numpy as np

from ..brokers.base_broker import OrderSide, OrderType
from .technical_analyzer import TechnicalAnalyzer


class AutoTrader:
    """
    Sistema de trading automático con IA
    Analiza mercado, toma decisiones y ejecuta trades
    """
    
    def __init__(self, controller, config: Dict):
        """
        Args:
            controller: Instancia de TradingController (usa API REST)
            config: Configuración del bot
        """
        self.controller = controller
        self.config = config
        
        # Estado del bot
        self.is_running = False
        self.is_paused = False
        
        # Configuración de trading
        self.symbols = config.get('symbols', ['BTCUSDT', 'ETHUSDT'])
        self.timeframe = config.get('timeframe', '5m')  # 5 minutos para day trading
        self.max_positions = config.get('max_positions', 3)
        self.risk_per_trade = config.get('risk_per_trade', 0.02)  # 2% por trade
        self.max_daily_loss = config.get('max_daily_loss', 0.05)  # 5% pérdida máxima diaria
        
        # Money management
        self.initial_balance = 0
        self.current_balance = 0
        self.daily_pnl = 0
        self.daily_trades = 0
        self.max_daily_trades = config.get('max_daily_trades', 20)
        
        # Analizador técnico
        self.analyzer = TechnicalAnalyzer()
        
        # Posiciones activas
        self.active_positions = {}
        
        # Historial
        self.trade_history = []
        self.signals_history = []
        
        # Callbacks
        self.on_trade_callback = None
        self.on_signal_callback = None
        self.on_error_callback = None
        
        logger.info("🤖 AutoTrader inicializado")
        logger.info(f"   Símbolos: {self.symbols}")
        logger.info(f"   Timeframe: {self.timeframe}")
        logger.info(f"   Max posiciones: {self.max_positions}")
        logger.info(f"   Riesgo por trade: {self.risk_per_trade * 100}%")
    
    async def start(self):
        """Inicia el bot de trading automático"""
        if self.is_running:
            logger.warning("⚠️ El bot ya está corriendo")
            return
        
        logger.success("🚀 Iniciando AutoTrader...")
        self.is_running = True
        self.is_paused = False
        
        # Obtener balance inicial vía API
        balance_data = self.controller.get_balance() or {}
        self.initial_balance = float(balance_data.get('balance', 0) or 0)
        self.current_balance = self.initial_balance
        
        logger.info(f"💰 Balance inicial: ${self.initial_balance:,.2f}")
        
        # Loop principal
        await self._main_loop()
    
    async def stop(self):
        """Detiene el bot"""
        logger.warning("🛑 Deteniendo AutoTrader...")
        self.is_running = False
        
        # Cerrar todas las posiciones abiertas
        if self.config.get('close_on_stop', True):
            await self._close_all_positions()
        
        logger.success("✅ AutoTrader detenido")
    
    async def pause(self):
        """Pausa el bot (no ejecuta nuevos trades pero mantiene posiciones)"""
        self.is_paused = True
        logger.info("⏸️ AutoTrader pausado")
    
    async def resume(self):
        """Reanuda el bot"""
        self.is_paused = False
        logger.info("▶️ AutoTrader reanudado")
    
    async def _main_loop(self):
        """Loop principal del bot"""
        logger.info("🔄 Iniciando loop principal...")
        
        while self.is_running:
            try:
                # Verificar si está pausado
                if self.is_paused:
                    await asyncio.sleep(5)
                    continue
                
                # Verificar límites de riesgo
                if not await self._check_risk_limits():
                    logger.warning("⚠️ Límites de riesgo alcanzados. Pausando...")
                    await self.pause()
                    await asyncio.sleep(60)
                    continue
                
                # Actualizar balance
                await self._update_balance()
                
                # Analizar cada símbolo
                for symbol in self.symbols:
                    try:
                        await self._analyze_and_trade(symbol)
                    except Exception as e:
                        logger.error(f"❌ Error analizando {symbol}: {e}")
                        if self.on_error_callback:
                            self.on_error_callback(symbol, str(e))
                
                # Gestionar posiciones abiertas
                await self._manage_positions()
                
                # Esperar antes del siguiente ciclo
                await asyncio.sleep(self._get_sleep_time())
                
            except Exception as e:
                logger.error(f"❌ Error en main loop: {e}")
                logger.exception("Traceback:")
                await asyncio.sleep(10)
        
        logger.info("🏁 Loop principal terminado")
    
    async def _analyze_and_trade(self, symbol: str):
        """
        Analiza un símbolo y ejecuta trade si hay señal
        
        Args:
            symbol: Par de trading (ej: BTCUSDT)
        """
        # Verificar si ya tenemos posición en este símbolo
        if symbol in self.active_positions:
            return
        
        # Verificar si podemos abrir más posiciones
        if len(self.active_positions) >= self.max_positions:
            return
        
        # Verificar límite de trades diarios
        if self.daily_trades >= self.max_daily_trades:
            return
        
        # Obtener datos de mercado
        market_data = await self._get_market_data(symbol)
        if market_data is None:
            return
        
        # Analizar con IA
        signal = await self._analyze_with_ai(symbol, market_data)
        
        if signal['action'] != 'HOLD':
            logger.info(f"📊 Señal detectada para {symbol}: {signal['action']}")
            logger.info(f"   Confianza: {signal['confidence']:.2%}")
            logger.info(f"   Razón: {signal['reason']}")
            
            # Guardar señal
            self.signals_history.append({
                'timestamp': datetime.now(),
                'symbol': symbol,
                'signal': signal
            })
            
            if self.on_signal_callback:
                self.on_signal_callback(symbol, signal)
            
            # Ejecutar trade si la confianza es suficiente
            if signal['confidence'] >= self.config.get('min_confidence', 0.65):
                await self._execute_trade(symbol, signal)
    
    async def _analyze_with_ai(self, symbol: str, market_data: pd.DataFrame) -> Dict:
        """
        Analiza el mercado usando indicadores técnicos
        
        Returns:
            Dict con: action, confidence, reason, entry_price, stop_loss, take_profit
        """
        try:
            # Analizar con indicadores técnicos
            signal = self.analyzer.analyze(market_data)
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Error en análisis: {e}")
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': f'Error: {str(e)}',
                'entry_price': market_data['close'].iloc[-1],
                'stop_loss': None,
                'take_profit': None
            }
    
    
    async def _execute_trade(self, symbol: str, signal: Dict):
        """Ejecuta un trade basado en la señal"""
        try:
            # Calcular tamaño de posición
            position_size = self._calculate_position_size(
                signal['entry_price'],
                signal['stop_loss']
            )
            
            if position_size <= 0:
                logger.warning(f"⚠️ Tamaño de posición inválido para {symbol}")
                return
            
            logger.info(f"📈 Ejecutando {signal['action']} en {symbol}")
            logger.info(f"   Cantidad: {position_size}")
            logger.info(f"   Precio entrada: ${signal['entry_price']:.2f}")
            logger.info(f"   Stop Loss: ${signal['stop_loss']:.2f}")
            logger.info(f"   Take Profit: ${signal['take_profit']:.2f}")
            
            # Ejecutar orden vía API Controller
            side_text = 'buy' if signal['action'] == 'BUY' else 'sell'
            result = self.controller.execute_trade(
                symbol=symbol,
                side=side_text,
                amount=position_size,
                stop_loss=signal.get('stop_loss'),
                take_profit=signal.get('take_profit')
            )
            order = result if result and result.get('success') else None
            
            if order:
                # Guardar posición
                self.active_positions[symbol] = {
                    'order': order,
                    'signal': signal,
                    'entry_time': datetime.now(),
                    'entry_price': signal['entry_price'],
                    'stop_loss': signal['stop_loss'],
                    'take_profit': signal['take_profit'],
                    'quantity': position_size
                }
                
                self.daily_trades += 1
                
                # Guardar en historial
                self.trade_history.append({
                    'timestamp': datetime.now(),
                    'symbol': symbol,
                    'action': signal['action'],
                    'quantity': position_size,
                    'entry_price': signal['entry_price'],
                    'confidence': signal['confidence']
                })
                
                logger.success(f"✅ Trade ejecutado: {signal['action']} {position_size} {symbol}")
                
                if self.on_trade_callback:
                    self.on_trade_callback(symbol, order, signal)
            else:
                logger.error(f"❌ Error ejecutando orden en {symbol}")
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando trade: {e}")
            logger.exception("Traceback:")
    
    def _calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """Calcula el tamaño de la posición basado en riesgo"""
        # Riesgo en dólares
        risk_amount = self.current_balance * self.risk_per_trade
        
        # Distancia al stop loss
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit == 0:
            return 0
        
        # Tamaño de posición
        position_size = risk_amount / risk_per_unit
        
        # Limitar a máximo 10% del balance
        max_position_value = self.current_balance * 0.1
        max_position_size = max_position_value / entry_price
        
        return min(position_size, max_position_size)
    
    async def _manage_positions(self):
        """Gestiona posiciones abiertas (stop loss, take profit, trailing stop)"""
        for symbol in list(self.active_positions.keys()):
            try:
                position = self.active_positions[symbol]
                
                # Obtener precio actual desde mercado (fallback: último cierre)
                md = self.controller.get_market_data(symbol) or {}
                current_price = None
                if isinstance(md, dict):
                    current_price = md.get('last') or md.get('price')
                    candles = md.get('candles') or md.get('klines') or md.get('data')
                    if current_price is None and candles:
                        try:
                            last = candles[-1]
                            if isinstance(last, dict):
                                current_price = float(last.get('close'))
                            elif isinstance(last, (list, tuple)) and len(last) >= 5:
                                current_price = float(last[4])  # close index típico
                        except Exception:
                            pass
                if current_price is None:
                    logger.warning(f"No se pudo obtener precio actual para {symbol}; skip gestión")
                    continue
                
                # Verificar stop loss
                if self._check_stop_loss(position, current_price):
                    await self._close_position(symbol, "Stop Loss")
                    continue
                
                # Verificar take profit
                if self._check_take_profit(position, current_price):
                    await self._close_position(symbol, "Take Profit")
                    continue
                
                # Trailing stop (opcional)
                if self.config.get('use_trailing_stop', True):
                    self._update_trailing_stop(position, current_price)
                
            except Exception as e:
                logger.error(f"❌ Error gestionando posición {symbol}: {e}")
    
    def _check_stop_loss(self, position: Dict, current_price: float) -> bool:
        """Verifica si se alcanzó el stop loss"""
        signal = position['signal']
        
        if signal['action'] == 'BUY':
            return current_price <= position['stop_loss']
        else:  # SELL
            return current_price >= position['stop_loss']
    
    def _check_take_profit(self, position: Dict, current_price: float) -> bool:
        """Verifica si se alcanzó el take profit"""
        signal = position['signal']
        
        if signal['action'] == 'BUY':
            return current_price >= position['take_profit']
        else:  # SELL
            return current_price <= position['take_profit']
    
    def _update_trailing_stop(self, position: Dict, current_price: float):
        """Actualiza trailing stop"""
        signal = position['signal']
        trailing_percent = self.config.get('trailing_stop_percent', 0.02)  # 2%
        
        if signal['action'] == 'BUY':
            # Para compras, subir el stop loss si el precio sube
            new_stop = current_price * (1 - trailing_percent)
            if new_stop > position['stop_loss']:
                position['stop_loss'] = new_stop
                logger.info(f"📈 Trailing stop actualizado para {position['order'].symbol}: ${new_stop:.2f}")
        else:  # SELL
            # Para ventas, bajar el stop loss si el precio baja
            new_stop = current_price * (1 + trailing_percent)
            if new_stop < position['stop_loss']:
                position['stop_loss'] = new_stop
                logger.info(f"📉 Trailing stop actualizado para {position['order'].symbol}: ${new_stop:.2f}")
    
    async def _close_position(self, symbol: str, reason: str):
        """Cierra una posición"""
        try:
            position = self.active_positions[symbol]
            signal = position['signal']
            
            logger.info(f"🔒 Cerrando posición {symbol} - Razón: {reason}")
            
            # Ejecutar orden de cierre vía API (opuesta a la entrada)
            close_side = 'sell' if signal['action'] == 'BUY' else 'buy'
            order = self.controller.execute_trade(
                symbol=symbol,
                side=close_side,
                amount=position['quantity']
            )
            
            if order:
                # Calcular P&L con mercado actual
                md = self.controller.get_market_data(symbol) or {}
                exit_price = md.get('last') or md.get('price')
                if exit_price is None:
                    candles = md.get('candles') or md.get('klines') or md.get('data')
                    if candles:
                        last = candles[-1]
                        if isinstance(last, dict):
                            exit_price = float(last.get('close', 0))
                        elif isinstance(last, (list, tuple)) and len(last) >= 5:
                            exit_price = float(last[4])
                if exit_price is None:
                    exit_price = position['entry_price']
                
                if signal['action'] == 'BUY':
                    pnl = (exit_price - position['entry_price']) * position['quantity']
                else:
                    pnl = (position['entry_price'] - exit_price) * position['quantity']
                
                self.daily_pnl += pnl
                
                logger.success(f"✅ Posición cerrada: {symbol}")
                logger.info(f"   P&L: ${pnl:+,.2f}")
                logger.info(f"   Entrada: ${position['entry_price']:.2f}")
                logger.info(f"   Salida: ${exit_price:.2f}")
                
                # Remover de posiciones activas
                del self.active_positions[symbol]
                
        except Exception as e:
            logger.error(f"❌ Error cerrando posición {symbol}: {e}")
    
    async def _close_all_positions(self):
        """Cierra todas las posiciones abiertas"""
        logger.info("🔒 Cerrando todas las posiciones...")
        
        for symbol in list(self.active_positions.keys()):
            await self._close_position(symbol, "Bot detenido")
        
        logger.success("✅ Todas las posiciones cerradas")
    
    async def _check_risk_limits(self) -> bool:
        """Verifica si se han alcanzado los límites de riesgo"""
        # Verificar pérdida diaria máxima
        daily_loss_percent = abs(self.daily_pnl / self.initial_balance)
        
        if self.daily_pnl < 0 and daily_loss_percent >= self.max_daily_loss:
            logger.error(f"🚨 Pérdida diaria máxima alcanzada: {daily_loss_percent:.2%}")
            return False
        
        return True
    
    async def _update_balance(self):
        """Actualiza el balance actual"""
        try:
            balance_data = self.controller.get_balance() or {}
            self.current_balance = float(balance_data.get('balance', self.current_balance))
        except Exception as e:
            logger.error(f"❌ Error actualizando balance: {e}")
    
    async def _get_market_data(self, symbol: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Obtiene datos históricos del mercado"""
        try:
            md = self.controller.get_market_data(symbol) or {}
            candles = md.get('candles') or md.get('klines') or md.get('data') or md.get('history')
            
            if not candles:
                return None
            
            # Normalizar diferentes formatos
            if isinstance(candles[0], dict):
                df = pd.DataFrame(candles)
            else:
                # Asumir formato kline [openTime, open, high, low, close, volume, ...]
                cols = ['open_time','open','high','low','close','volume']
                df = pd.DataFrame(candles, columns=cols + list(range(max(0, len(candles[0]) - len(cols)))))
            # Convertir a floats
            for col in ['open','high','low','close','volume']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            return df
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo datos de {symbol}: {e}")
            return None
    
    def _get_sleep_time(self) -> int:
        """Calcula tiempo de espera entre ciclos basado en timeframe"""
        timeframe_map = {
            '1m': 60,
            '5m': 300,
            '15m': 900,
            '1h': 3600
        }
        return timeframe_map.get(self.timeframe, 300)
    
    def get_status(self) -> Dict:
        """Obtiene el estado actual del bot"""
        return {
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'balance': self.current_balance,
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades,
            'active_positions': len(self.active_positions),
            'symbols': self.symbols,
            'timeframe': self.timeframe
        }
