"""
Rastreador de Performance
Calcula y almacena métricas de rendimiento del sistema
"""

import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
from collections import deque
from loguru import logger


class PerformanceTracker:
    """
    Rastrea y calcula métricas de performance del trading
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.current_equity = initial_capital
        self.peak_equity = initial_capital
        
        # Historial
        self.equity_history = [initial_capital]
        self.balance_history = [initial_capital]
        self.timestamp_history = [datetime.now()]
        
        # Trades
        self.trades: List[Dict] = []
        self.open_trades: Dict[str, Dict] = {}
        
        # Métricas diarias
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.last_reset_date = datetime.now().date()
        
        # Estadísticas
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        self.total_commission = 0.0
        
        # Drawdown
        self.max_drawdown = 0.0
        self.current_drawdown = 0.0
        self.drawdown_duration = 0
        
        logger.info(f"📊 PerformanceTracker inicializado (Capital: ${initial_capital:,.2f})")
    
    def update(
        self,
        equity: float,
        balance: float,
        unrealized_pnl: float = 0.0
    ):
        """
        Actualiza estado actual
        
        Args:
            equity: Equity actual (balance + unrealized P&L)
            balance: Balance actual
            unrealized_pnl: P&L no realizado
        """
        self.current_equity = equity
        
        # Agregar a historial
        self.equity_history.append(equity)
        self.balance_history.append(balance)
        self.timestamp_history.append(datetime.now())
        
        # Limitar tamaño del historial (últimos 10,000 puntos)
        if len(self.equity_history) > 10000:
            self.equity_history = self.equity_history[-10000:]
            self.balance_history = self.balance_history[-10000:]
            self.timestamp_history = self.timestamp_history[-10000:]
        
        # Actualizar peak equity
        if equity > self.peak_equity:
            self.peak_equity = equity
            self.drawdown_duration = 0
        else:
            self.drawdown_duration += 1
        
        # Calcular drawdown actual
        if self.peak_equity > 0:
            self.current_drawdown = (self.peak_equity - equity) / self.peak_equity
            
            if self.current_drawdown > self.max_drawdown:
                self.max_drawdown = self.current_drawdown
        
        # Resetear estadísticas diarias si cambió el día
        current_date = datetime.now().date()
        if current_date != self.last_reset_date:
            self.reset_daily_stats()
            self.last_reset_date = current_date
    
    def register_trade_opened(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        quantity: float,
        stop_loss: Optional[float] = None,
        take_profit: Optional[float] = None,
        trade_id: Optional[str] = None
    ):
        """Registra apertura de un trade"""
        if trade_id is None:
            trade_id = f"trade_{len(self.trades) + 1}"
        
        trade_data = {
            'id': trade_id,
            'symbol': symbol,
            'side': side,
            'entry_price': entry_price,
            'quantity': quantity,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'opened_at': datetime.now(),
            'status': 'open'
        }
        
        self.open_trades[trade_id] = trade_data
        logger.debug(f"📝 Trade registrado: {trade_id}")
    
    def register_trade_closed(
        self,
        trade_id: str,
        exit_price: float,
        pnl: float,
        commission: float = 0.0,
        exit_reason: str = "manual"
    ):
        """Registra cierre de un trade"""
        if trade_id not in self.open_trades:
            logger.warning(f"⚠️  Trade {trade_id} no encontrado en trades abiertos")
            return
        
        trade_data = self.open_trades[trade_id]
        trade_data.update({
            'exit_price': exit_price,
            'pnl': pnl,
            'commission': commission,
            'closed_at': datetime.now(),
            'exit_reason': exit_reason,
            'status': 'closed',
            'duration': (datetime.now() - trade_data['opened_at']).total_seconds()
        })
        
        # Calcular P&L porcentual
        entry_value = trade_data['entry_price'] * trade_data['quantity']
        if entry_value > 0:
            trade_data['pnl_percent'] = (pnl / entry_value) * 100
        else:
            trade_data['pnl_percent'] = 0.0
        
        # Agregar a historial
        self.trades.append(trade_data)
        del self.open_trades[trade_id]
        
        # Actualizar estadísticas
        self.total_trades += 1
        self.daily_trades += 1
        self.total_pnl += pnl
        self.daily_pnl += pnl
        self.total_commission += commission
        
        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        logger.info(f"✓ Trade cerrado: {trade_id} | P&L: ${pnl:.2f} ({trade_data['pnl_percent']:+.2f}%)")
    
    def calculate_metrics(self) -> Dict:
        """
        Calcula todas las métricas de performance
        
        Returns:
            Diccionario con métricas
        """
        if len(self.trades) == 0:
            return self._empty_metrics()
        
        # Convertir trades a DataFrame
        df = pd.DataFrame(self.trades)
        
        # Métricas básicas
        total_return = ((self.current_equity - self.initial_capital) / self.initial_capital) * 100
        win_rate = (self.winning_trades / self.total_trades) * 100 if self.total_trades > 0 else 0
        
        # Profit Factor
        gross_profit = df[df['pnl'] > 0]['pnl'].sum() if len(df[df['pnl'] > 0]) > 0 else 0
        gross_loss = abs(df[df['pnl'] < 0]['pnl'].sum()) if len(df[df['pnl'] < 0]) > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0
        
        # Average Win/Loss
        avg_win = df[df['pnl'] > 0]['pnl'].mean() if len(df[df['pnl'] > 0]) > 0 else 0
        avg_loss = df[df['pnl'] < 0]['pnl'].mean() if len(df[df['pnl'] < 0]) > 0 else 0
        
        # Expectancy
        expectancy = (win_rate / 100 * avg_win) + ((1 - win_rate / 100) * avg_loss)
        
        # Sharpe Ratio
        sharpe_ratio = self._calculate_sharpe_ratio()
        
        # Sortino Ratio
        sortino_ratio = self._calculate_sortino_ratio()
        
        # Calmar Ratio
        calmar_ratio = (total_return / 100) / self.max_drawdown if self.max_drawdown > 0 else 0
        
        # Consecutive wins/losses
        max_consecutive_wins = self._calculate_max_consecutive(df, True)
        max_consecutive_losses = self._calculate_max_consecutive(df, False)
        
        # Average trade duration
        avg_duration = df['duration'].mean() / 60  # en minutos
        
        metrics = {
            # Rentabilidad
            'total_return': total_return,
            'total_pnl': self.total_pnl,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'net_profit': self.total_pnl - self.total_commission,
            
            # Trades
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            
            # Ratios
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            
            # Promedios
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'avg_trade': self.total_pnl / self.total_trades if self.total_trades > 0 else 0,
            'expectancy': expectancy,
            
            # Drawdown
            'max_drawdown': self.max_drawdown * 100,
            'current_drawdown': self.current_drawdown * 100,
            'drawdown_duration': self.drawdown_duration,
            
            # Rachas
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            
            # Otros
            'avg_trade_duration_minutes': avg_duration,
            'total_commission': self.total_commission,
            
            # Capital
            'initial_capital': self.initial_capital,
            'current_equity': self.current_equity,
            'peak_equity': self.peak_equity,
            
            # Diario
            'daily_pnl': self.daily_pnl,
            'daily_trades': self.daily_trades
        }
        
        return metrics
    
    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """Calcula Sharpe Ratio"""
        if len(self.equity_history) < 2:
            return 0.0
        
        # Calcular returns
        equity_array = np.array(self.equity_history)
        returns = np.diff(equity_array) / equity_array[:-1]
        
        if len(returns) == 0 or np.std(returns) == 0:
            return 0.0
        
        # Sharpe = (mean_return - risk_free_rate) / std_return
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        sharpe = (mean_return - risk_free_rate) / std_return
        
        # Anualizar (asumiendo 252 días de trading)
        sharpe_annualized = sharpe * np.sqrt(252)
        
        return sharpe_annualized
    
    def _calculate_sortino_ratio(self, risk_free_rate: float = 0.0) -> float:
        """Calcula Sortino Ratio (solo considera volatilidad negativa)"""
        if len(self.equity_history) < 2:
            return 0.0
        
        equity_array = np.array(self.equity_history)
        returns = np.diff(equity_array) / equity_array[:-1]
        
        if len(returns) == 0:
            return 0.0
        
        # Solo returns negativos
        negative_returns = returns[returns < 0]
        
        if len(negative_returns) == 0:
            return float('inf')  # No hay pérdidas
        
        downside_std = np.std(negative_returns)
        
        if downside_std == 0:
            return 0.0
        
        mean_return = np.mean(returns)
        sortino = (mean_return - risk_free_rate) / downside_std
        
        # Anualizar
        sortino_annualized = sortino * np.sqrt(252)
        
        return sortino_annualized
    
    def _calculate_max_consecutive(self, df: pd.DataFrame, wins: bool) -> int:
        """Calcula máxima racha de ganancias o pérdidas consecutivas"""
        if len(df) == 0:
            return 0
        
        max_streak = 0
        current_streak = 0
        
        for pnl in df['pnl']:
            if (wins and pnl > 0) or (not wins and pnl < 0):
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        return max_streak
    
    def _empty_metrics(self) -> Dict:
        """Retorna métricas vacías"""
        return {
            'total_return': 0.0,
            'total_pnl': 0.0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'sharpe_ratio': 0.0,
            'sortino_ratio': 0.0,
            'max_drawdown': 0.0,
            'current_drawdown': 0.0
        }
    
    def reset_daily_stats(self):
        """Resetea estadísticas diarias"""
        self.daily_pnl = 0.0
        self.daily_trades = 0
        logger.debug("📊 Estadísticas diarias reseteadas")
    
    def get_equity_curve(self) -> pd.DataFrame:
        """Retorna curva de equity como DataFrame"""
        return pd.DataFrame({
            'timestamp': self.timestamp_history,
            'equity': self.equity_history,
            'balance': self.balance_history
        })
    
    def get_trades_dataframe(self) -> pd.DataFrame:
        """Retorna trades como DataFrame"""
        if len(self.trades) == 0:
            return pd.DataFrame()
        return pd.DataFrame(self.trades)
    
    def print_summary(self):
        """Imprime resumen de performance"""
        metrics = self.calculate_metrics()
        
        logger.info("=" * 70)
        logger.info("📊 RESUMEN DE PERFORMANCE")
        logger.info("=" * 70)
        logger.info(f"💰 Capital Inicial: ${metrics['initial_capital']:,.2f}")
        logger.info(f"💰 Equity Actual: ${metrics['current_equity']:,.2f}")
        logger.info(f"📈 Retorno Total: {metrics['total_return']:+.2f}%")
        logger.info(f"💵 P&L Total: ${metrics['total_pnl']:+,.2f}")
        logger.info("")
        logger.info(f"📊 Total Trades: {metrics['total_trades']}")
        logger.info(f"🟢 Ganadores: {metrics['winning_trades']} ({metrics['win_rate']:.1f}%)")
        logger.info(f"🔴 Perdedores: {metrics['losing_trades']}")
        logger.info("")
        logger.info(f"📊 Profit Factor: {metrics['profit_factor']:.2f}")
        logger.info(f"📊 Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        logger.info(f"📊 Sortino Ratio: {metrics['sortino_ratio']:.2f}")
        logger.info("")
        logger.info(f"📉 Max Drawdown: {metrics['max_drawdown']:.2f}%")
        logger.info(f"📉 Drawdown Actual: {metrics['current_drawdown']:.2f}%")
        logger.info("=" * 70)
