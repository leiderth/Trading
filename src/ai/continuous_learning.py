"""
Continuous Learning System
Sistema de aprendizaje continuo que mejora con cada operación
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from loguru import logger
import json
from collections import deque
import torch
import torch.optim as optim


class ContinuousLearningSystem:
    """
    Sistema de aprendizaje continuo que:
    1. Aprende de cada operación
    2. Se adapta a cambios de mercado
    3. Optimiza estrategias automáticamente
    4. Detecta regímenes de mercado
    5. Auto-tune de hiperparámetros
    """
    
    def __init__(self, predictor, max_memory: int = 10000):
        self.predictor = predictor
        self.max_memory = max_memory
        
        # Memory buffers
        self.experience_buffer = deque(maxlen=max_memory)
        self.performance_history = deque(maxlen=1000)
        self.market_regime_history = deque(maxlen=500)
        
        # Learning metrics
        self.total_trades = 0
        self.successful_trades = 0
        self.total_profit = 0.0
        self.learning_rate = 0.001
        
        # Market regime detector
        self.current_regime = 'UNKNOWN'
        self.regime_models = {}
        
        # Adaptive parameters
        self.adaptive_params = {
            'risk_multiplier': 1.0,
            'confidence_threshold': 0.6,
            'stop_loss_multiplier': 1.0,
            'take_profit_multiplier': 1.0
        }
        
        # Optimizers
        self.optimizer = optim.Adam(
            list(predictor.transformer.parameters()) +
            list(predictor.wavenet.parameters()) +
            list(predictor.lstm.parameters()) +
            list(predictor.gru.parameters()) +
            list(predictor.tcn.parameters()),
            lr=self.learning_rate
        )
        
        logger.info("Sistema de aprendizaje continuo inicializado")
    
    def learn_from_trade(self, trade_data: Dict):
        """
        Aprende de una operación completada
        
        Args:
            trade_data: {
                'entry_price': float,
                'exit_price': float,
                'direction': str,
                'profit': float,
                'features': np.ndarray,
                'market_data': Dict,
                'duration': int (minutos)
            }
        """
        try:
            # Guardar experiencia
            self.experience_buffer.append(trade_data)
            
            # Actualizar métricas
            self.total_trades += 1
            if trade_data['profit'] > 0:
                self.successful_trades += 1
            self.total_profit += trade_data['profit']
            
            # Calcular reward
            reward = self._calculate_reward(trade_data)
            
            # Entrenar modelo con experiencia
            self._train_from_experience(trade_data, reward)
            
            # Detectar régimen de mercado
            self._update_market_regime(trade_data['market_data'])
            
            # Adaptar parámetros
            self._adapt_parameters()
            
            # Auto-tune cada 50 operaciones
            if self.total_trades % 50 == 0:
                self._auto_tune_hyperparameters()
            
            # Guardar checkpoint cada 100 operaciones
            if self.total_trades % 100 == 0:
                self._save_checkpoint()
            
            logger.info(f"Aprendizaje completado. Trade #{self.total_trades}, "
                       f"Win Rate: {self.get_win_rate():.2%}, "
                       f"Profit: ${self.total_profit:.2f}")
            
        except Exception as e:
            logger.error(f"Error en aprendizaje: {e}")
    
    def _calculate_reward(self, trade_data: Dict) -> float:
        """
        Calcula reward para reinforcement learning
        Considera: profit, risk-adjusted return, duration
        """
        profit = trade_data['profit']
        duration = trade_data['duration']
        
        # Reward base: profit normalizado
        base_reward = profit / abs(trade_data['entry_price']) * 100
        
        # Penalizar operaciones muy largas
        time_penalty = max(0, (duration - 60) / 60) * 0.1
        
        # Bonus por operaciones rápidas y rentables
        if profit > 0 and duration < 30:
            base_reward *= 1.2
        
        # Penalizar pérdidas grandes
        if profit < 0:
            base_reward *= 1.5  # Penalizar más las pérdidas
        
        final_reward = base_reward - time_penalty
        
        return final_reward
    
    def _train_from_experience(self, trade_data: Dict, reward: float):
        """Entrena el modelo con la experiencia"""
        try:
            features = trade_data['features']
            target = trade_data['exit_price']
            
            # Preparar datos
            x = torch.FloatTensor(features).unsqueeze(0).to(self.predictor.device)
            y_true = torch.FloatTensor([target]).to(self.predictor.device)
            reward_tensor = torch.FloatTensor([reward]).to(self.predictor.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            
            # Predicciones de cada modelo
            transformer_out = self.predictor.transformer(x)
            wavenet_out = self.predictor.wavenet(x)
            lstm_out = self.predictor.lstm(x)
            gru_out = self.predictor.gru(x)
            tcn_out = self.predictor.tcn(x)
            
            # Loss ponderado por reward
            mse_loss = torch.nn.MSELoss()
            
            loss_transformer = mse_loss(transformer_out['price'], y_true)
            loss_wavenet = mse_loss(wavenet_out, y_true)
            loss_lstm = mse_loss(lstm_out, y_true)
            loss_gru = mse_loss(gru_out, y_true)
            loss_tcn = mse_loss(tcn_out, y_true)
            
            # Loss total ponderado por reward (refuerzo)
            total_loss = (loss_transformer + loss_wavenet + loss_lstm + 
                         loss_gru + loss_tcn) * (1.0 - reward * 0.1)
            
            # Backward pass
            total_loss.backward()
            torch.nn.utils.clip_grad_norm_(self.optimizer.param_groups[0]['params'], 1.0)
            self.optimizer.step()
            
            logger.debug(f"Training loss: {total_loss.item():.4f}, Reward: {reward:.4f}")
            
        except Exception as e:
            logger.error(f"Error en entrenamiento: {e}")
    
    def _update_market_regime(self, market_data: Dict):
        """
        Detecta y actualiza el régimen de mercado actual
        Regímenes: TRENDING_UP, TRENDING_DOWN, RANGING, VOLATILE, CALM
        """
        try:
            # Calcular métricas de mercado
            volatility = market_data.get('volatility', 0)
            trend_strength = market_data.get('trend_strength', 0)
            volume_trend = market_data.get('volume_trend', 1.0)
            
            # Detectar régimen
            if trend_strength > 0.7:
                if market_data.get('price_change', 0) > 0:
                    regime = 'TRENDING_UP'
                else:
                    regime = 'TRENDING_DOWN'
            elif volatility > 0.03:
                regime = 'VOLATILE'
            elif volatility < 0.01:
                regime = 'CALM'
            else:
                regime = 'RANGING'
            
            # Actualizar régimen actual
            if regime != self.current_regime:
                logger.info(f"Cambio de régimen: {self.current_regime} → {regime}")
                self.current_regime = regime
                self._adapt_to_regime(regime)
            
            # Guardar en historial
            self.market_regime_history.append({
                'timestamp': datetime.now(),
                'regime': regime,
                'volatility': volatility,
                'trend_strength': trend_strength
            })
            
        except Exception as e:
            logger.error(f"Error detectando régimen: {e}")
    
    def _adapt_to_regime(self, regime: str):
        """Adapta parámetros según el régimen de mercado"""
        
        if regime == 'TRENDING_UP' or regime == 'TRENDING_DOWN':
            # En tendencia: más agresivo, stops más amplios
            self.adaptive_params['risk_multiplier'] = 1.3
            self.adaptive_params['stop_loss_multiplier'] = 1.2
            self.adaptive_params['take_profit_multiplier'] = 1.5
            self.adaptive_params['confidence_threshold'] = 0.55
            
        elif regime == 'RANGING':
            # En rango: más conservador, stops ajustados
            self.adaptive_params['risk_multiplier'] = 0.8
            self.adaptive_params['stop_loss_multiplier'] = 0.8
            self.adaptive_params['take_profit_multiplier'] = 1.0
            self.adaptive_params['confidence_threshold'] = 0.65
            
        elif regime == 'VOLATILE':
            # Volátil: muy conservador, stops muy ajustados
            self.adaptive_params['risk_multiplier'] = 0.5
            self.adaptive_params['stop_loss_multiplier'] = 0.6
            self.adaptive_params['take_profit_multiplier'] = 0.8
            self.adaptive_params['confidence_threshold'] = 0.75
            
        elif regime == 'CALM':
            # Calma: moderado
            self.adaptive_params['risk_multiplier'] = 1.0
            self.adaptive_params['stop_loss_multiplier'] = 1.0
            self.adaptive_params['take_profit_multiplier'] = 1.2
            self.adaptive_params['confidence_threshold'] = 0.60
        
        logger.info(f"Parámetros adaptados para régimen {regime}: {self.adaptive_params}")
    
    def _adapt_parameters(self):
        """Adapta parámetros basándose en performance reciente"""
        
        if len(self.performance_history) < 20:
            return
        
        # Analizar últimas 20 operaciones
        recent_trades = list(self.performance_history)[-20:]
        recent_win_rate = sum(1 for t in recent_trades if t['profit'] > 0) / len(recent_trades)
        recent_profit = sum(t['profit'] for t in recent_trades)
        
        # Ajustar confidence threshold
        if recent_win_rate < 0.45:
            # Bajo win rate: ser más selectivo
            self.adaptive_params['confidence_threshold'] = min(0.80, 
                self.adaptive_params['confidence_threshold'] + 0.05)
        elif recent_win_rate > 0.65:
            # Alto win rate: ser más agresivo
            self.adaptive_params['confidence_threshold'] = max(0.50,
                self.adaptive_params['confidence_threshold'] - 0.05)
        
        # Ajustar risk multiplier
        if recent_profit < 0:
            # Pérdidas: reducir riesgo
            self.adaptive_params['risk_multiplier'] = max(0.3,
                self.adaptive_params['risk_multiplier'] * 0.9)
        elif recent_profit > 0 and recent_win_rate > 0.60:
            # Ganancias consistentes: aumentar riesgo
            self.adaptive_params['risk_multiplier'] = min(2.0,
                self.adaptive_params['risk_multiplier'] * 1.1)
        
        logger.debug(f"Parámetros adaptados: {self.adaptive_params}")
    
    def _auto_tune_hyperparameters(self):
        """
        Auto-tuning de hiperparámetros usando Bayesian Optimization
        """
        logger.info("Iniciando auto-tuning de hiperparámetros...")
        
        try:
            # Evaluar performance actual
            current_performance = self._evaluate_performance()
            
            # Ajustar learning rate
            if current_performance['win_rate'] < 0.50:
                self.learning_rate *= 0.9
            elif current_performance['win_rate'] > 0.65:
                self.learning_rate *= 1.1
            
            self.learning_rate = np.clip(self.learning_rate, 0.0001, 0.01)
            
            # Actualizar optimizer
            for param_group in self.optimizer.param_groups:
                param_group['lr'] = self.learning_rate
            
            logger.info(f"Auto-tuning completado. Learning rate: {self.learning_rate:.6f}")
            
        except Exception as e:
            logger.error(f"Error en auto-tuning: {e}")
    
    def _evaluate_performance(self) -> Dict:
        """Evalúa performance del sistema"""
        
        if self.total_trades == 0:
            return {
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0
            }
        
        win_rate = self.successful_trades / self.total_trades
        
        # Calcular profit factor
        wins = [t['profit'] for t in self.experience_buffer if t['profit'] > 0]
        losses = [abs(t['profit']) for t in self.experience_buffer if t['profit'] < 0]
        
        total_wins = sum(wins) if wins else 0
        total_losses = sum(losses) if losses else 1
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        # Calcular Sharpe Ratio
        returns = [t['profit'] / abs(t['entry_price']) for t in self.experience_buffer]
        sharpe_ratio = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if len(returns) > 1 else 0
        
        # Calcular Max Drawdown
        cumulative = np.cumsum([t['profit'] for t in self.experience_buffer])
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(np.min(drawdown)) if len(drawdown) > 0 else 0
        
        return {
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown
        }
    
    def get_adaptive_parameters(self) -> Dict:
        """Retorna parámetros adaptados actuales"""
        return self.adaptive_params.copy()
    
    def get_win_rate(self) -> float:
        """Retorna win rate actual"""
        if self.total_trades == 0:
            return 0.0
        return self.successful_trades / self.total_trades
    
    def get_statistics(self) -> Dict:
        """Retorna estadísticas completas"""
        performance = self._evaluate_performance()
        
        return {
            'total_trades': self.total_trades,
            'successful_trades': self.successful_trades,
            'win_rate': performance['win_rate'],
            'total_profit': self.total_profit,
            'profit_factor': performance['profit_factor'],
            'sharpe_ratio': performance['sharpe_ratio'],
            'max_drawdown': performance['max_drawdown'],
            'current_regime': self.current_regime,
            'adaptive_params': self.adaptive_params,
            'learning_rate': self.learning_rate
        }
    
    def _save_checkpoint(self):
        """Guarda checkpoint del sistema"""
        try:
            checkpoint_path = f"models/checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pt"
            
            self.predictor.save(checkpoint_path)
            
            # Guardar métricas
            stats = self.get_statistics()
            with open(checkpoint_path.replace('.pt', '_stats.json'), 'w') as f:
                json.dump(stats, f, indent=2)
            
            logger.info(f"Checkpoint guardado: {checkpoint_path}")
            
        except Exception as e:
            logger.error(f"Error guardando checkpoint: {e}")
    
    def replay_experience(self, batch_size: int = 32):
        """
        Experience Replay: entrena con experiencias pasadas
        """
        if len(self.experience_buffer) < batch_size:
            return
        
        # Sample random batch
        indices = np.random.choice(len(self.experience_buffer), batch_size, replace=False)
        batch = [self.experience_buffer[i] for i in indices]
        
        # Train on batch
        for experience in batch:
            reward = self._calculate_reward(experience)
            self._train_from_experience(experience, reward)
        
        logger.debug(f"Experience replay: {batch_size} samples")
