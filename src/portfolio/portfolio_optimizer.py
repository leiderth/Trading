"""
Portfolio Optimization
Markowitz, Black-Litterman, Risk Parity, Hierarchical Risk Parity
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from scipy.optimize import minimize
from scipy.cluster.hierarchy import linkage, dendrogram
from loguru import logger
import warnings
warnings.filterwarnings('ignore')


class PortfolioOptimizer:
    """
    Optimizador de Portfolio Institucional
    
    Métodos:
    - Modern Portfolio Theory (Markowitz)
    - Black-Litterman Model
    - Risk Parity
    - Hierarchical Risk Parity (HRP)
    - Maximum Sharpe Ratio
    - Minimum Variance
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        self.risk_free_rate = risk_free_rate
        logger.info("Portfolio Optimizer inicializado")
    
    def markowitz_optimization(
        self,
        returns: pd.DataFrame,
        target_return: Optional[float] = None,
        method: str = 'max_sharpe'
    ) -> Dict:
        """
        Modern Portfolio Theory (Markowitz)
        
        Args:
            returns: DataFrame con retornos de cada activo
            target_return: Retorno objetivo (opcional)
            method: 'max_sharpe', 'min_variance', 'target_return'
        
        Returns:
            Dict con pesos óptimos y métricas
        """
        logger.info(f"Markowitz Optimization ({method})")
        
        # Calcular estadísticas
        mean_returns = returns.mean() * 252  # Anualizado
        cov_matrix = returns.cov() * 252     # Anualizado
        
        n_assets = len(mean_returns)
        
        # Función objetivo
        def portfolio_stats(weights):
            portfolio_return = np.dot(weights, mean_returns)
            portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
            sharpe = (portfolio_return - self.risk_free_rate) / portfolio_std
            return portfolio_return, portfolio_std, sharpe
        
        # Restricciones
        constraints = [
            {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Suma = 1
        ]
        
        if target_return is not None:
            constraints.append({
                'type': 'eq',
                'fun': lambda x: np.dot(x, mean_returns) - target_return
            })
        
        # Límites (0 a 1 para cada activo)
        bounds = tuple((0, 1) for _ in range(n_assets))
        
        # Pesos iniciales
        init_weights = np.array([1/n_assets] * n_assets)
        
        # Optimizar
        if method == 'max_sharpe':
            # Maximizar Sharpe Ratio
            def neg_sharpe(weights):
                _, _, sharpe = portfolio_stats(weights)
                return -sharpe
            
            result = minimize(
                neg_sharpe,
                init_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
        
        elif method == 'min_variance':
            # Minimizar varianza
            def portfolio_variance(weights):
                return np.dot(weights.T, np.dot(cov_matrix, weights))
            
            result = minimize(
                portfolio_variance,
                init_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints
            )
        
        else:
            raise ValueError(f"Método desconocido: {method}")
        
        # Pesos óptimos
        optimal_weights = result.x
        
        # Métricas del portfolio óptimo
        port_return, port_std, port_sharpe = portfolio_stats(optimal_weights)
        
        # Crear dict de pesos
        weights_dict = {
            returns.columns[i]: optimal_weights[i]
            for i in range(n_assets)
            if optimal_weights[i] > 0.01  # Solo mostrar > 1%
        }
        
        logger.info(f"  Expected Return: {port_return*100:.2f}%")
        logger.info(f"  Volatility: {port_std*100:.2f}%")
        logger.info(f"  Sharpe Ratio: {port_sharpe:.2f}")
        
        return {
            'weights': weights_dict,
            'weights_array': optimal_weights,
            'expected_return': port_return,
            'volatility': port_std,
            'sharpe_ratio': port_sharpe,
            'method': method
        }
    
    def black_litterman(
        self,
        returns: pd.DataFrame,
        market_caps: Dict[str, float],
        views: Dict[str, float],
        view_confidence: float = 0.5
    ) -> Dict:
        """
        Black-Litterman Model
        
        Combina equilibrio de mercado con views del inversor
        
        Args:
            returns: DataFrame con retornos históricos
            market_caps: Dict con market caps de cada activo
            views: Dict con views del inversor (ej: {'BTC': 0.15} = espero 15% return)
            view_confidence: Confianza en las views (0-1)
        
        Returns:
            Dict con pesos óptimos
        """
        logger.info("Black-Litterman Optimization")
        
        # Calcular estadísticas
        cov_matrix = returns.cov() * 252
        
        # Pesos de mercado (basados en market cap)
        total_market_cap = sum(market_caps.values())
        market_weights = np.array([
            market_caps.get(asset, 0) / total_market_cap
            for asset in returns.columns
        ])
        
        # Retornos implícitos del mercado (reverse optimization)
        risk_aversion = 2.5  # Típico
        implied_returns = risk_aversion * np.dot(cov_matrix, market_weights)
        
        # Matriz P (views)
        n_assets = len(returns.columns)
        n_views = len(views)
        
        P = np.zeros((n_views, n_assets))
        Q = np.zeros(n_views)
        
        for i, (asset, view_return) in enumerate(views.items()):
            if asset in returns.columns:
                asset_idx = returns.columns.get_loc(asset)
                P[i, asset_idx] = 1
                Q[i] = view_return
        
        # Matriz Omega (incertidumbre de views)
        tau = 0.025  # Parámetro de escala
        Omega = np.dot(np.dot(P, tau * cov_matrix), P.T) * (1 / view_confidence)
        
        # Retornos posteriores (Black-Litterman)
        M_inverse = np.linalg.inv(tau * cov_matrix)
        
        posterior_returns = np.linalg.inv(
            M_inverse + np.dot(np.dot(P.T, np.linalg.inv(Omega)), P)
        ).dot(
            np.dot(M_inverse, implied_returns) + np.dot(np.dot(P.T, np.linalg.inv(Omega)), Q)
        )
        
        # Optimizar con retornos posteriores
        def portfolio_variance(weights):
            return np.dot(weights.T, np.dot(cov_matrix, weights))
        
        def portfolio_return(weights):
            return np.dot(weights, posterior_returns)
        
        # Maximizar Sharpe con retornos posteriores
        def neg_sharpe(weights):
            ret = portfolio_return(weights)
            std = np.sqrt(portfolio_variance(weights))
            return -(ret - self.risk_free_rate) / std
        
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = tuple((0, 1) for _ in range(n_assets))
        init_weights = market_weights
        
        result = minimize(
            neg_sharpe,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        
        # Métricas
        port_return = portfolio_return(optimal_weights)
        port_std = np.sqrt(portfolio_variance(optimal_weights))
        port_sharpe = (port_return - self.risk_free_rate) / port_std
        
        weights_dict = {
            returns.columns[i]: optimal_weights[i]
            for i in range(n_assets)
            if optimal_weights[i] > 0.01
        }
        
        logger.info(f"  Expected Return: {port_return*100:.2f}%")
        logger.info(f"  Sharpe Ratio: {port_sharpe:.2f}")
        
        return {
            'weights': weights_dict,
            'weights_array': optimal_weights,
            'expected_return': port_return,
            'volatility': port_std,
            'sharpe_ratio': port_sharpe,
            'method': 'black_litterman'
        }
    
    def risk_parity(self, returns: pd.DataFrame) -> Dict:
        """
        Risk Parity Portfolio
        
        Cada activo contribuye igual riesgo al portfolio
        
        Args:
            returns: DataFrame con retornos
        
        Returns:
            Dict con pesos óptimos
        """
        logger.info("Risk Parity Optimization")
        
        # Calcular covarianza
        cov_matrix = returns.cov() * 252
        n_assets = len(returns.columns)
        
        # Función objetivo: minimizar diferencia en contribución de riesgo
        def risk_contribution(weights):
            portfolio_var = np.dot(weights.T, np.dot(cov_matrix, weights))
            marginal_contrib = np.dot(cov_matrix, weights)
            risk_contrib = weights * marginal_contrib / np.sqrt(portfolio_var)
            
            # Queremos que todas las contribuciones sean iguales
            target_contrib = 1 / n_assets
            return np.sum((risk_contrib - target_contrib) ** 2)
        
        # Restricciones
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bounds = tuple((0.001, 1) for _ in range(n_assets))
        init_weights = np.array([1/n_assets] * n_assets)
        
        result = minimize(
            risk_contribution,
            init_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        optimal_weights = result.x
        
        # Métricas
        mean_returns = returns.mean() * 252
        port_return = np.dot(optimal_weights, mean_returns)
        port_std = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
        port_sharpe = (port_return - self.risk_free_rate) / port_std
        
        weights_dict = {
            returns.columns[i]: optimal_weights[i]
            for i in range(n_assets)
            if optimal_weights[i] > 0.01
        }
        
        logger.info(f"  Expected Return: {port_return*100:.2f}%")
        logger.info(f"  Sharpe Ratio: {port_sharpe:.2f}")
        
        return {
            'weights': weights_dict,
            'weights_array': optimal_weights,
            'expected_return': port_return,
            'volatility': port_std,
            'sharpe_ratio': port_sharpe,
            'method': 'risk_parity'
        }
    
    def hierarchical_risk_parity(self, returns: pd.DataFrame) -> Dict:
        """
        Hierarchical Risk Parity (HRP)
        
        Usa clustering jerárquico para construir portfolio
        Más robusto que Markowitz
        
        Args:
            returns: DataFrame con retornos
        
        Returns:
            Dict con pesos óptimos
        """
        logger.info("Hierarchical Risk Parity Optimization")
        
        # Calcular matriz de correlación
        corr_matrix = returns.corr()
        
        # Convertir a matriz de distancia
        dist_matrix = np.sqrt((1 - corr_matrix) / 2)
        
        # Clustering jerárquico
        link = linkage(dist_matrix, method='single')
        
        # Ordenar activos según clustering
        sorted_indices = self._get_quasi_diag(link)
        sorted_corr = corr_matrix.iloc[sorted_indices, sorted_indices]
        
        # Calcular pesos usando bisección recursiva
        weights = self._recursive_bisection(sorted_corr, returns.iloc[:, sorted_indices].cov() * 252)
        
        # Reordenar pesos al orden original
        optimal_weights = np.zeros(len(returns.columns))
        for i, idx in enumerate(sorted_indices):
            optimal_weights[idx] = weights[i]
        
        # Métricas
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        
        port_return = np.dot(optimal_weights, mean_returns)
        port_std = np.sqrt(np.dot(optimal_weights.T, np.dot(cov_matrix, optimal_weights)))
        port_sharpe = (port_return - self.risk_free_rate) / port_std
        
        weights_dict = {
            returns.columns[i]: optimal_weights[i]
            for i in range(len(returns.columns))
            if optimal_weights[i] > 0.01
        }
        
        logger.info(f"  Expected Return: {port_return*100:.2f}%")
        logger.info(f"  Sharpe Ratio: {port_sharpe:.2f}")
        
        return {
            'weights': weights_dict,
            'weights_array': optimal_weights,
            'expected_return': port_return,
            'volatility': port_std,
            'sharpe_ratio': port_sharpe,
            'method': 'hrp'
        }
    
    def efficient_frontier(
        self,
        returns: pd.DataFrame,
        n_points: int = 100
    ) -> Dict:
        """
        Calcula la frontera eficiente
        
        Args:
            returns: DataFrame con retornos
            n_points: Número de puntos en la frontera
        
        Returns:
            Dict con puntos de la frontera
        """
        logger.info(f"Calculando Efficient Frontier ({n_points} puntos)")
        
        mean_returns = returns.mean() * 252
        cov_matrix = returns.cov() * 252
        
        # Rango de retornos
        min_return = mean_returns.min()
        max_return = mean_returns.max()
        target_returns = np.linspace(min_return, max_return, n_points)
        
        frontier_volatilities = []
        frontier_weights = []
        
        for target_return in target_returns:
            try:
                result = self.markowitz_optimization(
                    returns,
                    target_return=target_return,
                    method='min_variance'
                )
                frontier_volatilities.append(result['volatility'])
                frontier_weights.append(result['weights_array'])
            except:
                continue
        
        return {
            'returns': target_returns[:len(frontier_volatilities)],
            'volatilities': np.array(frontier_volatilities),
            'weights': frontier_weights
        }
    
    def _get_quasi_diag(self, link):
        """Obtiene orden quasi-diagonal del clustering"""
        link = link.astype(int)
        sorted_items = []
        
        def recurse(node):
            if node < len(link) + 1:
                sorted_items.append(node)
            else:
                left = int(link[node - len(link) - 1, 0])
                right = int(link[node - len(link) - 1, 1])
                recurse(left)
                recurse(right)
        
        recurse(len(link) * 2)
        return sorted_items
    
    def _recursive_bisection(self, corr_matrix, cov_matrix):
        """Bisección recursiva para HRP"""
        weights = np.ones(len(corr_matrix))
        
        def bisect(items):
            if len(items) == 1:
                return
            
            # Dividir en dos clusters
            mid = len(items) // 2
            left = items[:mid]
            right = items[mid:]
            
            # Calcular varianza de cada cluster
            left_var = self._cluster_var(cov_matrix, left)
            right_var = self._cluster_var(cov_matrix, right)
            
            # Asignar pesos inversamente proporcional a varianza
            alpha = 1 - left_var / (left_var + right_var)
            
            weights[left] *= alpha
            weights[right] *= (1 - alpha)
            
            # Recursión
            bisect(left)
            bisect(right)
        
        bisect(list(range(len(corr_matrix))))
        
        # Normalizar
        return weights / weights.sum()
    
    def _cluster_var(self, cov_matrix, items):
        """Calcula varianza de un cluster"""
        cov_slice = cov_matrix[np.ix_(items, items)]
        w = np.ones(len(items)) / len(items)
        return np.dot(w.T, np.dot(cov_slice, w))
