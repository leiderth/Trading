"""
Módulo de Gestión de Riesgo Profesional
Implementa estrategias avanzadas de risk management
"""

import numpy as np
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from loguru import logger


@dataclass
class RiskLimits:
    """Límites de riesgo configurables"""
    max_risk_per_trade: float = 0.02  # 2%
    max_drawdown: float = 0.15  # 15%
    max_positions: int = 3
    max_daily_loss: float = 0.05  # 5%
    max_consecutive_losses: int = 3
    min_risk_reward_ratio: float = 2.0


class RiskManager:
    """
    Gestor de riesgo profesional
    Calcula tamaños de posición, stop loss, take profit, etc.
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Límites de riesgo
        self.limits = RiskLimits(
            max_risk_per_trade=self.config.get('max_risk_per_trade', 0.02),
            max_drawdown=self.config.get('max_drawdown', 0.15),
            max_positions=self.config.get('max_positions', 3),
            max_daily_loss=self.config.get('max_daily_loss', 0.05),
            max_consecutive_losses=self.config.get('max_consecutive_losses', 3),
            min_risk_reward_ratio=self.config.get('min_risk_reward_ratio', 2.0)
        )
        
        # Estado actual
        self.current_drawdown = 0.0
        self.peak_equity = 0.0
        self.consecutive_losses = 0
        self.daily_pnl = 0.0
        self.open_positions_count = 0
        
        # Modo de reducción de riesgo
        self.risk_reduction_active = False
        self.risk_reduction_factor = 1.0
        
        # Pausa de trading
        self.trading_paused = False
        self.pause_reason = ""
        
        logger.info("🛡️  RiskManager inicializado")
        logger.info(f"  Max risk per trade: {self.limits.max_risk_per_trade:.1%}")
        logger.info(f"  Max drawdown: {self.limits.max_drawdown:.1%}")
        logger.info(f"  Max positions: {self.limits.max_positions}")
    
    def update_state(
        self,
        current_equity: float,
        peak_equity: float,
        open_positions: int,
        daily_pnl: float = 0.0
    ):
        """
        Actualiza el estado del risk manager
        
        Args:
            current_equity: Equity actual
            peak_equity: Máximo equity histórico
            open_positions: Número de posiciones abiertas
            daily_pnl: P&L del día actual
        """
        self.peak_equity = peak_equity
        self.open_positions_count = open_positions
        self.daily_pnl = daily_pnl
        
        # Calcular drawdown
        if peak_equity > 0:
            self.current_drawdown = (peak_equity - current_equity) / peak_equity
        
        # Verificar límites críticos
        self._check_critical_limits()
    
    def can_trade(self) -> Tuple[bool, str]:
        """
        Verifica si se puede operar
        
        Returns:
            Tupla (puede_operar, razón)
        """
        if self.trading_paused:
            return False, self.pause_reason
        
        # Verificar drawdown máximo
        if self.current_drawdown >= self.limits.max_drawdown:
            return False, f"Drawdown máximo alcanzado ({self.current_drawdown:.1%})"
        
        # Verificar pérdida diaria máxima
        if self.daily_pnl < -self.limits.max_daily_loss:
            return False, f"Pérdida diaria máxima alcanzada ({self.daily_pnl:.1%})"
        
        # Verificar número máximo de posiciones
        if self.open_positions_count >= self.limits.max_positions:
            return False, f"Máximo de posiciones abiertas ({self.open_positions_count})"
        
        return True, "OK"
    
    def calculate_position_size(
        self,
        balance: float,
        entry_price: float,
        stop_loss_price: float,
        confidence: float = 1.0,
        method: str = "fixed"
    ) -> float:
        """
        Calcula el tamaño óptimo de la posición
        
        Args:
            balance: Balance disponible
            entry_price: Precio de entrada
            stop_loss_price: Precio de stop loss
            confidence: Nivel de confianza (0-1)
            method: Método de cálculo ("fixed", "kelly", "kelly_modified")
            
        Returns:
            Tamaño de posición en unidades
        """
        if balance <= 0 or entry_price <= 0:
            return 0.0
        
        # Calcular distancia al stop loss
        stop_distance = abs(entry_price - stop_loss_price)
        if stop_distance == 0:
            logger.warning("⚠️  Stop loss distance es 0")
            return 0.0
        
        # Riesgo máximo en dinero
        max_risk_amount = balance * self.limits.max_risk_per_trade
        
        # Aplicar factor de reducción si está activo
        if self.risk_reduction_active:
            max_risk_amount *= self.risk_reduction_factor
            logger.debug(f"🔻 Riesgo reducido a {self.risk_reduction_factor:.0%}")
        
        # Ajustar por confianza
        adjusted_risk = max_risk_amount * confidence
        
        # Calcular tamaño según método
        if method == "fixed":
            position_size = adjusted_risk / stop_distance
        
        elif method == "kelly":
            # Kelly Criterion: f = (bp - q) / b
            # Simplificado: asumiendo win_rate = confidence, b = risk_reward_ratio
            win_rate = confidence
            loss_rate = 1 - win_rate
            risk_reward = self.limits.min_risk_reward_ratio
            
            kelly_fraction = (win_rate * risk_reward - loss_rate) / risk_reward
            kelly_fraction = max(0, min(kelly_fraction, 0.25))  # Cap al 25%
            
            position_size = (balance * kelly_fraction) / entry_price
        
        elif method == "kelly_modified":
            # Kelly modificado (más conservador)
            win_rate = confidence
            loss_rate = 1 - win_rate
            risk_reward = self.limits.min_risk_reward_ratio
            
            kelly_fraction = (win_rate * risk_reward - loss_rate) / risk_reward
            kelly_fraction = max(0, min(kelly_fraction, 0.25))
            
            # Usar solo 50% del Kelly
            modified_kelly = kelly_fraction * 0.5
            
            position_size = (balance * modified_kelly) / entry_price
        
        else:
            position_size = adjusted_risk / stop_distance
        
        # Limitar tamaño máximo (no más del 30% del balance)
        max_position_value = balance * 0.30
        max_position_size = max_position_value / entry_price
        position_size = min(position_size, max_position_size)
        
        logger.debug(f"💰 Position size calculado: {position_size:.4f} unidades")
        logger.debug(f"  Método: {method} | Confianza: {confidence:.0%}")
        logger.debug(f"  Riesgo: ${adjusted_risk:.2f} ({adjusted_risk/balance:.2%})")
        
        return position_size
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        side: str,
        atr: float,
        method: str = "atr",
        atr_multiplier: float = 1.5,
        fixed_percent: float = 0.02
    ) -> float:
        """
        Calcula el precio de stop loss
        
        Args:
            entry_price: Precio de entrada
            side: "long" o "short"
            atr: Average True Range
            method: "atr", "fixed", "percentage"
            atr_multiplier: Multiplicador de ATR
            fixed_percent: Porcentaje fijo
            
        Returns:
            Precio de stop loss
        """
        if method == "atr":
            stop_distance = atr * atr_multiplier
        elif method == "fixed":
            stop_distance = entry_price * fixed_percent
        elif method == "percentage":
            stop_distance = entry_price * fixed_percent
        else:
            stop_distance = atr * atr_multiplier
        
        if side.lower() == "long":
            stop_loss = entry_price - stop_distance
        else:  # short
            stop_loss = entry_price + stop_distance
        
        logger.debug(f"🛑 Stop Loss: {stop_loss:.5f} (distancia: {stop_distance:.5f})")
        
        return stop_loss
    
    def calculate_take_profit(
        self,
        entry_price: float,
        stop_loss: float,
        side: str,
        risk_reward_ratio: Optional[float] = None
    ) -> float:
        """
        Calcula el precio de take profit
        
        Args:
            entry_price: Precio de entrada
            stop_loss: Precio de stop loss
            side: "long" o "short"
            risk_reward_ratio: Ratio riesgo/recompensa (default: 2.0)
            
        Returns:
            Precio de take profit
        """
        if risk_reward_ratio is None:
            risk_reward_ratio = self.limits.min_risk_reward_ratio
        
        # Calcular distancia al stop loss
        stop_distance = abs(entry_price - stop_loss)
        
        # Take profit a N veces la distancia
        tp_distance = stop_distance * risk_reward_ratio
        
        if side.lower() == "long":
            take_profit = entry_price + tp_distance
        else:  # short
            take_profit = entry_price - tp_distance
        
        logger.debug(f"🎯 Take Profit: {take_profit:.5f} (R:R = {risk_reward_ratio}:1)")
        
        return take_profit
    
    def calculate_trailing_stop(
        self,
        entry_price: float,
        current_price: float,
        side: str,
        atr: float,
        atr_multiplier: float = 1.5
    ) -> Optional[float]:
        """
        Calcula trailing stop loss
        
        Args:
            entry_price: Precio de entrada
            current_price: Precio actual
            side: "long" o "short"
            atr: Average True Range
            atr_multiplier: Multiplicador de ATR
            
        Returns:
            Nuevo stop loss o None si no se debe mover
        """
        trailing_distance = atr * atr_multiplier
        
        if side.lower() == "long":
            # Solo mover stop loss hacia arriba
            new_stop = current_price - trailing_distance
            if new_stop > entry_price:
                return new_stop
        else:  # short
            # Solo mover stop loss hacia abajo
            new_stop = current_price + trailing_distance
            if new_stop < entry_price:
                return new_stop
        
        return None
    
    def update_after_trade(self, pnl: float, was_win: bool):
        """
        Actualiza estado después de un trade
        
        Args:
            pnl: P&L del trade
            was_win: Si fue ganancia o pérdida
        """
        self.daily_pnl += pnl
        
        if was_win:
            self.consecutive_losses = 0
            
            # Desactivar reducción de riesgo si estaba activa
            if self.risk_reduction_active:
                self.risk_reduction_active = False
                self.risk_reduction_factor = 1.0
                logger.info("✓ Reducción de riesgo desactivada")
        else:
            self.consecutive_losses += 1
            
            # Activar reducción de riesgo si hay pérdidas consecutivas
            if self.consecutive_losses >= self.limits.max_consecutive_losses:
                self.risk_reduction_active = True
                self.risk_reduction_factor = 0.5
                logger.warning(f"⚠️  {self.consecutive_losses} pérdidas consecutivas")
                logger.warning(f"🔻 Reduciendo tamaño de posición a {self.risk_reduction_factor:.0%}")
    
    def pause_trading(self, reason: str):
        """Pausa el trading automático"""
        self.trading_paused = True
        self.pause_reason = reason
        logger.error(f"🚨 TRADING PAUSADO: {reason}")
    
    def resume_trading(self):
        """Reanuda el trading"""
        self.trading_paused = False
        self.pause_reason = ""
        logger.success("✓ Trading reanudado")
    
    def _check_critical_limits(self):
        """Verifica límites críticos y toma acciones"""
        
        # Drawdown crítico
        if self.current_drawdown >= self.limits.max_drawdown:
            self.pause_trading(
                f"Drawdown crítico alcanzado: {self.current_drawdown:.1%}"
            )
        
        # Pérdida diaria máxima
        if self.daily_pnl <= -self.limits.max_daily_loss:
            self.pause_trading(
                f"Pérdida diaria máxima alcanzada: {self.daily_pnl:.1%}"
            )
        
        # Advertencia de drawdown
        if 0.10 <= self.current_drawdown < self.limits.max_drawdown:
            logger.warning(f"⚠️  Drawdown actual: {self.current_drawdown:.1%}")
    
    def get_status(self) -> Dict:
        """Retorna estado actual del risk manager"""
        return {
            'can_trade': not self.trading_paused,
            'pause_reason': self.pause_reason,
            'current_drawdown': self.current_drawdown,
            'consecutive_losses': self.consecutive_losses,
            'daily_pnl': self.daily_pnl,
            'open_positions': self.open_positions_count,
            'risk_reduction_active': self.risk_reduction_active,
            'risk_reduction_factor': self.risk_reduction_factor,
            'limits': {
                'max_risk_per_trade': self.limits.max_risk_per_trade,
                'max_drawdown': self.limits.max_drawdown,
                'max_positions': self.limits.max_positions,
                'max_daily_loss': self.limits.max_daily_loss,
                'max_consecutive_losses': self.limits.max_consecutive_losses
            }
        }
    
    def reset_daily_stats(self):
        """Resetea estadísticas diarias"""
        self.daily_pnl = 0.0
        logger.debug("📊 Estadísticas diarias reseteadas")
    
    def calculate_kelly_fraction(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Calcula Kelly Criterion
        
        Args:
            win_rate: Tasa de ganancia (0-1)
            avg_win: Ganancia promedio
            avg_loss: Pérdida promedio (valor positivo)
            
        Returns:
            Fracción de Kelly
        """
        if avg_loss == 0:
            return 0.0
        
        b = avg_win / avg_loss  # Ratio win/loss
        p = win_rate
        q = 1 - win_rate
        
        kelly = (b * p - q) / b
        
        # Limitar entre 0 y 0.25 (25% máximo)
        kelly = max(0, min(kelly, 0.25))
        
        return kelly
    
    def validate_trade_parameters(
        self,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        side: str
    ) -> Tuple[bool, str]:
        """
        Valida parámetros de un trade
        
        Returns:
            Tupla (es_valido, mensaje)
        """
        # Verificar que los precios sean positivos
        if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
            return False, "Precios deben ser positivos"
        
        # Verificar que SL y TP estén en el lado correcto
        if side.lower() == "long":
            if stop_loss >= entry_price:
                return False, "Stop loss debe estar por debajo del precio de entrada (LONG)"
            if take_profit <= entry_price:
                return False, "Take profit debe estar por encima del precio de entrada (LONG)"
        else:  # short
            if stop_loss <= entry_price:
                return False, "Stop loss debe estar por encima del precio de entrada (SHORT)"
            if take_profit >= entry_price:
                return False, "Take profit debe estar por debajo del precio de entrada (SHORT)"
        
        # Verificar ratio riesgo/recompensa
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        if risk == 0:
            return False, "Riesgo no puede ser 0"
        
        risk_reward_ratio = reward / risk
        
        if risk_reward_ratio < self.limits.min_risk_reward_ratio:
            return False, f"Ratio R:R insuficiente ({risk_reward_ratio:.2f} < {self.limits.min_risk_reward_ratio})"
        
        return True, "OK"
