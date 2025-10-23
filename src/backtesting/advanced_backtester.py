"""
Advanced Backtesting Framework
Walk-forward, Monte Carlo, Parameter Optimization, Overfitting Detection
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from concurrent.futures import ProcessPoolExecutor
from loguru import logger
import warnings
warnings.filterwarnings('ignore')


@dataclass
class BacktestResult:
    """Resultado de un backtest"""
    total_return: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    num_trades: int
    avg_trade_duration: float
    trades: List[Dict]
    equity_curve: np.ndarray
    parameters: Dict


class AdvancedBacktester:
    """
    Framework avanzado de backtesting
    
    Características:
    - Walk-Forward Optimization
    - Monte Carlo Simulation
    - Parameter Optimization (Grid Search, Genetic Algorithm)
    - Overfitting Detection
    - Out-of-Sample Testing
    - Bootstrap Resampling
    - Multi-Objective Optimization
    """
    
    def __init__(self, initial_capital: float = 10000):
        self.initial_capital = initial_capital
        self.risk_free_rate = 0.02  # 2% anual
        
        logger.info(f"Advanced Backtester inicializado (capital: ${initial_capital:,.2f})")
    
    def backtest_strategy(
        self,
        data: pd.DataFrame,
        strategy_func: Callable,
        parameters: Dict,
        commission: float = 0.001,
        slippage: float = 0.0005
    ) -> BacktestResult:
        """
        Ejecuta backtest de una estrategia
        
        Args:
            data: DataFrame con OHLCV y features
            strategy_func: Función de estrategia que retorna señales
            parameters: Parámetros de la estrategia
            commission: Comisión por trade (0.1% = 0.001)
            slippage: Slippage estimado
        
        Returns:
            BacktestResult con métricas
        """
        # Generar señales
        signals = strategy_func(data, parameters)
        
        # Simular trades
        trades = []
        equity = self.initial_capital
        equity_curve = [equity]
        position = None
        
        for i in range(len(data)):
            signal = signals[i] if i < len(signals) else 0
            price = data.iloc[i]['close']
            
            # Abrir posición
            if signal != 0 and position is None:
                # Calcular tamaño de posición
                position_size = equity * 0.95  # 95% del capital
                shares = position_size / price
                
                # Aplicar costos
                entry_cost = position_size * (commission + slippage)
                equity -= entry_cost
                
                position = {
                    'entry_price': price,
                    'entry_time': data.index[i],
                    'shares': shares,
                    'direction': signal,  # 1 = long, -1 = short
                    'entry_cost': entry_cost
                }
            
            # Cerrar posición
            elif signal == 0 and position is not None:
                # Calcular P&L
                exit_price = price
                pnl = (exit_price - position['entry_price']) * position['shares'] * position['direction']
                
                # Aplicar costos
                exit_value = abs(position['shares'] * exit_price)
                exit_cost = exit_value * (commission + slippage)
                pnl -= exit_cost
                
                equity += pnl
                
                # Guardar trade
                trades.append({
                    'entry_time': position['entry_time'],
                    'exit_time': data.index[i],
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'return': pnl / (position['shares'] * position['entry_price']),
                    'direction': position['direction'],
                    'duration': (data.index[i] - position['entry_time']).total_seconds() / 3600
                })
                
                position = None
            
            equity_curve.append(equity)
        
        # Cerrar posición abierta al final
        if position is not None:
            exit_price = data.iloc[-1]['close']
            pnl = (exit_price - position['entry_price']) * position['shares'] * position['direction']
            exit_cost = abs(position['shares'] * exit_price) * (commission + slippage)
            pnl -= exit_cost
            equity += pnl
            
            trades.append({
                'entry_time': position['entry_time'],
                'exit_time': data.index[-1],
                'entry_price': position['entry_price'],
                'exit_price': exit_price,
                'pnl': pnl,
                'return': pnl / (position['shares'] * position['entry_price']),
                'direction': position['direction'],
                'duration': (data.index[-1] - position['entry_time']).total_seconds() / 3600
            })
        
        # Calcular métricas
        equity_curve = np.array(equity_curve)
        returns = np.diff(equity_curve) / equity_curve[:-1]
        
        total_return = (equity - self.initial_capital) / self.initial_capital
        sharpe_ratio = self._calculate_sharpe(returns)
        sortino_ratio = self._calculate_sortino(returns)
        max_drawdown = self._calculate_max_drawdown(equity_curve)
        
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] < 0]
        
        win_rate = len(winning_trades) / len(trades) if trades else 0
        
        avg_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t['pnl'] for t in losing_trades])) if losing_trades else 1
        profit_factor = (avg_win * len(winning_trades)) / (avg_loss * len(losing_trades)) if losing_trades else 0
        
        avg_duration = np.mean([t['duration'] for t in trades]) if trades else 0
        
        return BacktestResult(
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            profit_factor=profit_factor,
            num_trades=len(trades),
            avg_trade_duration=avg_duration,
            trades=trades,
            equity_curve=equity_curve,
            parameters=parameters
        )
    
    def walk_forward_optimization(
        self,
        data: pd.DataFrame,
        strategy_func: Callable,
        param_grid: Dict,
        train_period: int = 252,  # 1 año
        test_period: int = 63,    # 3 meses
        step: int = 21            # 1 mes
    ) -> Dict:
        """
        Walk-Forward Optimization
        
        Divide datos en ventanas de train/test que se mueven hacia adelante
        Optimiza en train, valida en test
        
        Args:
            data: DataFrame con datos
            strategy_func: Función de estrategia
            param_grid: Grid de parámetros a probar
            train_period: Días de entrenamiento
            test_period: Días de prueba
            step: Días a avanzar cada iteración
        
        Returns:
            Dict con resultados de cada ventana
        """
        logger.info(f"Walk-Forward Optimization iniciado (train: {train_period}, test: {test_period})")
        
        results = []
        start = 0
        
        while start + train_period + test_period <= len(data):
            # Dividir datos
            train_data = data.iloc[start:start + train_period]
            test_data = data.iloc[start + train_period:start + train_period + test_period]
            
            # Optimizar en train
            best_params = self._optimize_parameters(train_data, strategy_func, param_grid)
            
            # Validar en test
            test_result = self.backtest_strategy(test_data, strategy_func, best_params)
            
            results.append({
                'train_start': train_data.index[0],
                'train_end': train_data.index[-1],
                'test_start': test_data.index[0],
                'test_end': test_data.index[-1],
                'best_params': best_params,
                'test_sharpe': test_result.sharpe_ratio,
                'test_return': test_result.total_return,
                'test_drawdown': test_result.max_drawdown,
                'num_trades': test_result.num_trades
            })
            
            logger.info(f"Window {len(results)}: Sharpe={test_result.sharpe_ratio:.2f}, "
                       f"Return={test_result.total_return*100:.2f}%")
            
            start += step
        
        # Agregar resultados
        avg_sharpe = np.mean([r['test_sharpe'] for r in results])
        avg_return = np.mean([r['test_return'] for r in results])
        avg_drawdown = np.mean([r['test_drawdown'] for r in results])
        
        logger.info(f"Walk-Forward completado: {len(results)} ventanas")
        logger.info(f"  Avg Sharpe: {avg_sharpe:.2f}")
        logger.info(f"  Avg Return: {avg_return*100:.2f}%")
        logger.info(f"  Avg Drawdown: {avg_drawdown*100:.2f}%")
        
        return {
            'windows': results,
            'avg_sharpe': avg_sharpe,
            'avg_return': avg_return,
            'avg_drawdown': avg_drawdown,
            'num_windows': len(results)
        }
    
    def monte_carlo_backtest(
        self,
        trades: List[Dict],
        n_simulations: int = 10000,
        confidence_level: float = 0.95
    ) -> Dict:
        """
        Monte Carlo Simulation de trades
        
        Reordena trades aleatoriamente para estimar distribución de resultados
        
        Args:
            trades: Lista de trades históricos
            n_simulations: Número de simulaciones
            confidence_level: Nivel de confianza
        
        Returns:
            Dict con estadísticas de la simulación
        """
        logger.info(f"Monte Carlo Backtest: {n_simulations} simulaciones")
        
        if not trades:
            return {}
        
        # Extraer retornos de trades
        returns = np.array([t['return'] for t in trades])
        
        # Simulaciones
        final_returns = []
        max_drawdowns = []
        
        for _ in range(n_simulations):
            # Reordenar trades aleatoriamente
            shuffled_returns = np.random.choice(returns, size=len(returns), replace=True)
            
            # Calcular equity curve
            equity = np.cumprod(1 + shuffled_returns)
            
            # Métricas
            final_return = equity[-1] - 1
            max_dd = self._calculate_max_drawdown(equity)
            
            final_returns.append(final_return)
            max_drawdowns.append(max_dd)
        
        final_returns = np.array(final_returns)
        max_drawdowns = np.array(max_drawdowns)
        
        # Estadísticas
        mean_return = np.mean(final_returns)
        median_return = np.median(final_returns)
        std_return = np.std(final_returns)
        
        # Percentiles
        lower_percentile = (1 - confidence_level) / 2
        upper_percentile = 1 - lower_percentile
        
        ci_lower = np.percentile(final_returns, lower_percentile * 100)
        ci_upper = np.percentile(final_returns, upper_percentile * 100)
        
        # Probabilidad de profit
        prob_profit = np.sum(final_returns > 0) / n_simulations
        
        # Worst case
        worst_return = np.min(final_returns)
        worst_drawdown = np.max(max_drawdowns)
        
        logger.info(f"  Mean Return: {mean_return*100:.2f}%")
        logger.info(f"  Prob Profit: {prob_profit*100:.1f}%")
        logger.info(f"  Worst DD: {worst_drawdown*100:.2f}%")
        
        return {
            'mean_return': mean_return,
            'median_return': median_return,
            'std_return': std_return,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper,
            'prob_profit': prob_profit,
            'worst_return': worst_return,
            'worst_drawdown': worst_drawdown,
            'simulations': final_returns
        }
    
    def detect_overfitting(
        self,
        train_result: BacktestResult,
        test_result: BacktestResult,
        threshold: float = 0.3
    ) -> Dict:
        """
        Detecta overfitting comparando train vs test
        
        Args:
            train_result: Resultado en training set
            test_result: Resultado en test set
            threshold: Threshold de degradación aceptable
        
        Returns:
            Dict con análisis de overfitting
        """
        # Calcular degradación
        sharpe_degradation = (train_result.sharpe_ratio - test_result.sharpe_ratio) / train_result.sharpe_ratio if train_result.sharpe_ratio != 0 else 0
        return_degradation = (train_result.total_return - test_result.total_return) / train_result.total_return if train_result.total_return != 0 else 0
        
        # Detectar overfitting
        is_overfit = sharpe_degradation > threshold or return_degradation > threshold
        
        # Clasificar nivel
        if sharpe_degradation > 0.5:
            level = "SEVERE"
        elif sharpe_degradation > 0.3:
            level = "MODERATE"
        elif sharpe_degradation > 0.1:
            level = "MILD"
        else:
            level = "NONE"
        
        result = {
            'is_overfit': is_overfit,
            'level': level,
            'sharpe_degradation': sharpe_degradation,
            'return_degradation': return_degradation,
            'train_sharpe': train_result.sharpe_ratio,
            'test_sharpe': test_result.sharpe_ratio,
            'train_return': train_result.total_return,
            'test_return': test_result.total_return
        }
        
        if is_overfit:
            logger.warning(f"⚠️ OVERFITTING DETECTADO ({level})")
            logger.warning(f"  Sharpe degradation: {sharpe_degradation*100:.1f}%")
            logger.warning(f"  Return degradation: {return_degradation*100:.1f}%")
        else:
            logger.info(f"✅ No overfitting detectado")
        
        return result
    
    def _optimize_parameters(
        self,
        data: pd.DataFrame,
        strategy_func: Callable,
        param_grid: Dict,
        metric: str = 'sharpe_ratio'
    ) -> Dict:
        """
        Optimiza parámetros usando Grid Search
        
        Args:
            data: DataFrame con datos
            strategy_func: Función de estrategia
            param_grid: Grid de parámetros
            metric: Métrica a optimizar
        
        Returns:
            Mejores parámetros
        """
        # Generar todas las combinaciones
        param_combinations = self._generate_param_combinations(param_grid)
        
        best_score = -np.inf
        best_params = None
        
        for params in param_combinations:
            try:
                result = self.backtest_strategy(data, strategy_func, params)
                score = getattr(result, metric)
                
                if score > best_score:
                    best_score = score
                    best_params = params
            except:
                continue
        
        return best_params if best_params else param_combinations[0]
    
    def _generate_param_combinations(self, param_grid: Dict) -> List[Dict]:
        """Genera todas las combinaciones de parámetros"""
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        
        combinations = []
        
        def recurse(index, current):
            if index == len(keys):
                combinations.append(current.copy())
                return
            
            for value in values[index]:
                current[keys[index]] = value
                recurse(index + 1, current)
        
        recurse(0, {})
        return combinations
    
    def _calculate_sharpe(self, returns: np.ndarray) -> float:
        """Calcula Sharpe Ratio"""
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - self.risk_free_rate / 252
        return np.mean(excess_returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0.0
    
    def _calculate_sortino(self, returns: np.ndarray) -> float:
        """Calcula Sortino Ratio"""
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - self.risk_free_rate / 252
        downside_returns = returns[returns < 0]
        downside_std = np.std(downside_returns) if len(downside_returns) > 0 else np.std(returns)
        
        return np.mean(excess_returns) / downside_std * np.sqrt(252) if downside_std > 0 else 0.0
    
    def _calculate_max_drawdown(self, equity_curve: np.ndarray) -> float:
        """Calcula Maximum Drawdown"""
        running_max = np.maximum.accumulate(equity_curve)
        drawdown = (equity_curve - running_max) / running_max
        return np.min(drawdown)
