"""
Advanced Risk Management System
Nivel institucional: VaR, CVaR, Monte Carlo, Stress Testing, Kelly Criterion
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy import stats
from scipy.optimize import minimize
from loguru import logger
import warnings
warnings.filterwarnings('ignore')


class AdvancedRiskManager:
    """
    Sistema de gestión de riesgo institucional
    
    Características:
    - Value at Risk (VaR)
    - Conditional Value at Risk (CVaR)
    - Monte Carlo Simulation
    - Stress Testing
    - Kelly Criterion
    - Dynamic Position Sizing
    - Portfolio Risk Metrics
    """
    
    def __init__(self, confidence_levels: List[float] = [0.95, 0.99, 0.999]):
        self.confidence_levels = confidence_levels
        self.historical_returns = []
        self.portfolio_history = []
        
        logger.info("Advanced Risk Manager inicializado")
    
    def calculate_var(
        self,
        returns: np.ndarray,
        confidence_level: float = 0.95,
        method: str = 'historical'
    ) -> float:
        """
        Calculate Value at Risk (VaR)
        
        VaR responde: "¿Cuál es la pérdida máxima esperada con X% de confianza?"
        
        Args:
            returns: Array de retornos históricos
            confidence_level: Nivel de confianza (0.95 = 95%)
            method: 'historical', 'parametric', 'monte_carlo'
        
        Returns:
            VaR como porcentaje (ej: -0.05 = -5%)
        """
        if len(returns) == 0:
            return 0.0
        
        if method == 'historical':
            # Historical VaR: percentil de la distribución empírica
            var = np.percentile(returns, (1 - confidence_level) * 100)
            
        elif method == 'parametric':
            # Parametric VaR: asume distribución normal
            mean = np.mean(returns)
            std = np.std(returns)
            z_score = stats.norm.ppf(1 - confidence_level)
            var = mean + z_score * std
            
        elif method == 'monte_carlo':
            # Monte Carlo VaR: simulación
            simulated_returns = self._monte_carlo_simulation(returns, n_simulations=10000)
            var = np.percentile(simulated_returns, (1 - confidence_level) * 100)
        
        else:
            raise ValueError(f"Método desconocido: {method}")
        
        logger.debug(f"VaR ({confidence_level*100}%, {method}): {var*100:.2f}%")
        return var
    
    def calculate_cvar(
        self,
        returns: np.ndarray,
        confidence_level: float = 0.95,
        method: str = 'historical'
    ) -> float:
        """
        Calculate Conditional Value at Risk (CVaR) / Expected Shortfall
        
        CVaR responde: "Si las cosas van mal (peor que VaR), ¿cuánto perderé en promedio?"
        
        CVaR es más conservador que VaR y considera la cola de la distribución.
        
        Args:
            returns: Array de retornos históricos
            confidence_level: Nivel de confianza
            method: 'historical', 'parametric'
        
        Returns:
            CVaR como porcentaje
        """
        if len(returns) == 0:
            return 0.0
        
        # Primero calcular VaR
        var = self.calculate_var(returns, confidence_level, method)
        
        if method == 'historical':
            # CVaR histórico: promedio de pérdidas peores que VaR
            tail_losses = returns[returns <= var]
            cvar = np.mean(tail_losses) if len(tail_losses) > 0 else var
            
        elif method == 'parametric':
            # CVaR paramétrico: fórmula cerrada para distribución normal
            mean = np.mean(returns)
            std = np.std(returns)
            z_score = stats.norm.ppf(1 - confidence_level)
            cvar = mean - std * stats.norm.pdf(z_score) / (1 - confidence_level)
        
        else:
            cvar = var
        
        logger.debug(f"CVaR ({confidence_level*100}%, {method}): {cvar*100:.2f}%")
        return cvar
    
    def monte_carlo_simulation(
        self,
        current_price: float,
        returns: np.ndarray,
        n_simulations: int = 10000,
        n_days: int = 30,
        confidence_level: float = 0.95
    ) -> Dict:
        """
        Monte Carlo Simulation para proyección de precios
        
        Simula 10,000+ escenarios posibles del precio futuro
        
        Args:
            current_price: Precio actual
            returns: Retornos históricos
            n_simulations: Número de simulaciones
            n_days: Días a proyectar
            confidence_level: Nivel de confianza
        
        Returns:
            Dict con estadísticas de la simulación
        """
        if len(returns) == 0:
            return {}
        
        # Parámetros de la distribución
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        # Matriz de simulaciones (n_simulations x n_days)
        simulations = np.zeros((n_simulations, n_days))
        simulations[:, 0] = current_price
        
        # Generar caminos aleatorios
        for day in range(1, n_days):
            # Generar retornos aleatorios
            random_returns = np.random.normal(mean_return, std_return, n_simulations)
            # Aplicar retornos
            simulations[:, day] = simulations[:, day - 1] * (1 + random_returns)
        
        # Precios finales
        final_prices = simulations[:, -1]
        
        # Estadísticas
        mean_price = np.mean(final_prices)
        median_price = np.median(final_prices)
        std_price = np.std(final_prices)
        
        # Percentiles
        percentile_5 = np.percentile(final_prices, 5)
        percentile_25 = np.percentile(final_prices, 25)
        percentile_75 = np.percentile(final_prices, 75)
        percentile_95 = np.percentile(final_prices, 95)
        
        # VaR y CVaR de la simulación
        final_returns = (final_prices - current_price) / current_price
        var = np.percentile(final_returns, (1 - confidence_level) * 100)
        cvar = np.mean(final_returns[final_returns <= var])
        
        # Probabilidad de profit
        prob_profit = np.sum(final_prices > current_price) / n_simulations
        
        results = {
            'current_price': current_price,
            'mean_price': mean_price,
            'median_price': median_price,
            'std_price': std_price,
            'percentile_5': percentile_5,
            'percentile_25': percentile_25,
            'percentile_75': percentile_75,
            'percentile_95': percentile_95,
            'var': var,
            'cvar': cvar,
            'prob_profit': prob_profit,
            'simulations': simulations,
            'final_prices': final_prices
        }
        
        logger.info(f"Monte Carlo: {n_simulations} simulaciones, {n_days} días")
        logger.info(f"  Precio esperado: ${mean_price:.2f}")
        logger.info(f"  Probabilidad de profit: {prob_profit*100:.1f}%")
        logger.info(f"  VaR ({confidence_level*100}%): {var*100:.2f}%")
        
        return results
    
    def stress_test(
        self,
        returns: np.ndarray,
        scenarios: Dict[str, Dict] = None
    ) -> Dict:
        """
        Stress Testing con escenarios históricos extremos
        
        Simula cómo se comportaría el portfolio en crisis históricas
        
        Args:
            returns: Retornos del portfolio
            scenarios: Escenarios personalizados
        
        Returns:
            Dict con resultados de cada escenario
        """
        if scenarios is None:
            # Escenarios históricos predefinidos
            scenarios = {
                'dot_com_crash_2000': {
                    'description': 'Dot-com Crash (2000-2002)',
                    'market_drop': -0.49,  # -49%
                    'volatility_spike': 3.0,  # 3x volatilidad normal
                    'duration_days': 900
                },
                'financial_crisis_2008': {
                    'description': 'Financial Crisis (2008)',
                    'market_drop': -0.57,  # -57%
                    'volatility_spike': 4.0,
                    'duration_days': 500
                },
                'flash_crash_2010': {
                    'description': 'Flash Crash (May 2010)',
                    'market_drop': -0.09,  # -9% en minutos
                    'volatility_spike': 10.0,
                    'duration_days': 1
                },
                'covid_crash_2020': {
                    'description': 'COVID-19 Crash (March 2020)',
                    'market_drop': -0.34,  # -34%
                    'volatility_spike': 5.0,
                    'duration_days': 30
                },
                'crypto_winter_2022': {
                    'description': 'Crypto Winter (2022)',
                    'market_drop': -0.75,  # -75%
                    'volatility_spike': 6.0,
                    'duration_days': 365
                }
            }
        
        results = {}
        
        for scenario_name, scenario in scenarios.items():
            # Simular el escenario
            market_drop = scenario['market_drop']
            vol_spike = scenario['volatility_spike']
            
            # Aplicar shock al portfolio
            shocked_returns = returns * vol_spike
            portfolio_impact = np.sum(shocked_returns) + market_drop
            
            # Calcular métricas bajo estrés
            stressed_var = self.calculate_var(shocked_returns, 0.95)
            stressed_cvar = self.calculate_cvar(shocked_returns, 0.95)
            max_drawdown = self._calculate_max_drawdown(shocked_returns)
            
            results[scenario_name] = {
                'description': scenario['description'],
                'portfolio_impact': portfolio_impact,
                'stressed_var_95': stressed_var,
                'stressed_cvar_95': stressed_cvar,
                'max_drawdown': max_drawdown,
                'survival_probability': 1.0 if portfolio_impact > -1.0 else 0.0
            }
            
            logger.info(f"Stress Test: {scenario['description']}")
            logger.info(f"  Impact: {portfolio_impact*100:.2f}%")
            logger.info(f"  Max Drawdown: {max_drawdown*100:.2f}%")
        
        return results
    
    def kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        max_kelly: float = 0.25
    ) -> float:
        """
        Kelly Criterion para position sizing óptimo
        
        Fórmula: f* = (p*b - q) / b
        donde:
        - p = probabilidad de ganar
        - q = probabilidad de perder (1-p)
        - b = ratio win/loss
        
        Args:
            win_rate: Tasa de éxito (0-1)
            avg_win: Ganancia promedio
            avg_loss: Pérdida promedio (positivo)
            max_kelly: Kelly máximo (para ser conservador)
        
        Returns:
            Fracción óptima del capital a arriesgar (0-1)
        """
        if win_rate <= 0 or win_rate >= 1:
            return 0.0
        
        if avg_loss <= 0:
            return 0.0
        
        # Probabilidades
        p = win_rate
        q = 1 - win_rate
        
        # Ratio win/loss
        b = avg_win / avg_loss
        
        # Kelly Criterion
        kelly = (p * b - q) / b
        
        # Limitar Kelly (ser conservador)
        kelly = max(0, min(kelly, max_kelly))
        
        logger.info(f"Kelly Criterion: {kelly*100:.2f}%")
        logger.info(f"  Win Rate: {win_rate*100:.1f}%")
        logger.info(f"  Win/Loss Ratio: {b:.2f}")
        
        return kelly
    
    def dynamic_position_sizing(
        self,
        capital: float,
        current_volatility: float,
        historical_volatility: float,
        kelly_fraction: float,
        max_position_size: float = 0.10
    ) -> float:
        """
        Dynamic Position Sizing basado en volatilidad y Kelly
        
        Ajusta el tamaño de posición según:
        - Volatilidad actual vs histórica
        - Kelly Criterion
        - Límites de riesgo
        
        Args:
            capital: Capital disponible
            current_volatility: Volatilidad actual
            historical_volatility: Volatilidad histórica promedio
            kelly_fraction: Fracción de Kelly
            max_position_size: Tamaño máximo de posición (% del capital)
        
        Returns:
            Tamaño de posición en unidades de capital
        """
        # Ajuste por volatilidad
        vol_ratio = historical_volatility / current_volatility if current_volatility > 0 else 1.0
        vol_adjusted_kelly = kelly_fraction * vol_ratio
        
        # Aplicar límites
        position_fraction = min(vol_adjusted_kelly, max_position_size)
        position_fraction = max(0, position_fraction)
        
        # Calcular tamaño de posición
        position_size = capital * position_fraction
        
        logger.debug(f"Position Size: ${position_size:.2f} ({position_fraction*100:.2f}% del capital)")
        logger.debug(f"  Vol Ratio: {vol_ratio:.2f}")
        logger.debug(f"  Kelly: {kelly_fraction*100:.2f}%")
        
        return position_size
    
    def portfolio_risk_metrics(
        self,
        returns: np.ndarray,
        risk_free_rate: float = 0.02
    ) -> Dict:
        """
        Calcula métricas de riesgo del portfolio
        
        Returns:
            Dict con todas las métricas de riesgo
        """
        if len(returns) == 0:
            return {}
        
        # Retorno anualizado
        annual_return = np.mean(returns) * 252
        
        # Volatilidad anualizada
        annual_volatility = np.std(returns) * np.sqrt(252)
        
        # Sharpe Ratio
        sharpe = (annual_return - risk_free_rate) / annual_volatility if annual_volatility > 0 else 0
        
        # Sortino Ratio (solo considera downside volatility)
        downside_returns = returns[returns < 0]
        downside_std = np.std(downside_returns) * np.sqrt(252) if len(downside_returns) > 0 else annual_volatility
        sortino = (annual_return - risk_free_rate) / downside_std if downside_std > 0 else 0
        
        # Max Drawdown
        max_dd = self._calculate_max_drawdown(returns)
        
        # Calmar Ratio
        calmar = annual_return / abs(max_dd) if max_dd != 0 else 0
        
        # VaR y CVaR
        var_95 = self.calculate_var(returns, 0.95, 'historical')
        cvar_95 = self.calculate_cvar(returns, 0.95, 'historical')
        var_99 = self.calculate_var(returns, 0.99, 'historical')
        cvar_99 = self.calculate_cvar(returns, 0.99, 'historical')
        
        # Skewness y Kurtosis
        skewness = stats.skew(returns)
        kurtosis = stats.kurtosis(returns)
        
        metrics = {
            'annual_return': annual_return,
            'annual_volatility': annual_volatility,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown': max_dd,
            'calmar_ratio': calmar,
            'var_95': var_95,
            'cvar_95': cvar_95,
            'var_99': var_99,
            'cvar_99': cvar_99,
            'skewness': skewness,
            'kurtosis': kurtosis
        }
        
        logger.info("Portfolio Risk Metrics:")
        logger.info(f"  Annual Return: {annual_return*100:.2f}%")
        logger.info(f"  Annual Volatility: {annual_volatility*100:.2f}%")
        logger.info(f"  Sharpe Ratio: {sharpe:.2f}")
        logger.info(f"  Sortino Ratio: {sortino:.2f}")
        logger.info(f"  Max Drawdown: {max_dd*100:.2f}%")
        logger.info(f"  Calmar Ratio: {calmar:.2f}")
        logger.info(f"  VaR (95%): {var_95*100:.2f}%")
        logger.info(f"  CVaR (95%): {cvar_95*100:.2f}%")
        
        return metrics
    
    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Calcula el máximo drawdown"""
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_dd = np.min(drawdown)
        return max_dd
    
    def _monte_carlo_simulation(self, returns: np.ndarray, n_simulations: int) -> np.ndarray:
        """Simulación Monte Carlo simple"""
        mean = np.mean(returns)
        std = np.std(returns)
        simulated = np.random.normal(mean, std, n_simulations)
        return simulated
    
    def circuit_breaker_check(
        self,
        current_drawdown: float,
        max_drawdown_limit: float = 0.15,
        daily_loss: float = 0.0,
        daily_loss_limit: float = 0.05
    ) -> Dict:
        """
        Circuit Breaker: Detiene trading si se superan límites
        
        Args:
            current_drawdown: Drawdown actual
            max_drawdown_limit: Límite de drawdown (default 15%)
            daily_loss: Pérdida del día
            daily_loss_limit: Límite de pérdida diaria (default 5%)
        
        Returns:
            Dict con decisión y razón
        """
        should_stop = False
        reasons = []
        
        # Check drawdown
        if abs(current_drawdown) > max_drawdown_limit:
            should_stop = True
            reasons.append(f"Drawdown {abs(current_drawdown)*100:.1f}% > límite {max_drawdown_limit*100:.1f}%")
        
        # Check daily loss
        if abs(daily_loss) > daily_loss_limit:
            should_stop = True
            reasons.append(f"Pérdida diaria {abs(daily_loss)*100:.1f}% > límite {daily_loss_limit*100:.1f}%")
        
        if should_stop:
            logger.warning(f"🚨 CIRCUIT BREAKER ACTIVADO: {', '.join(reasons)}")
        
        return {
            'should_stop': should_stop,
            'reasons': reasons,
            'current_drawdown': current_drawdown,
            'daily_loss': daily_loss
        }
