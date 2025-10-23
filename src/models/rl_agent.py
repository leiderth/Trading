"""
Agente de Reinforcement Learning (PPO)
Toma decisiones de trading basadas en el estado del mercado
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from collections import deque
from loguru import logger

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import BaseCallback
import gymnasium as gym
from gymnasium import spaces


class TradingEnvironment(gym.Env):
    """
    Environment de trading para Reinforcement Learning
    Compatible con Gymnasium/OpenAI Gym
    """
    
    def __init__(
        self,
        state_dim: int = 80,
        initial_balance: float = 10000.0,
        max_position_size: float = 1.0,
        transaction_cost: float = 0.0002
    ):
        super(TradingEnvironment, self).__init__()
        
        self.state_dim = state_dim
        self.initial_balance = initial_balance
        self.max_position_size = max_position_size
        self.transaction_cost = transaction_cost
        
        # Espacios de acción y observación
        # Acciones: 0=HOLD, 1-4=BUY(25%,50%,75%,100%), 5-8=SELL, 9=CLOSE
        self.action_space = spaces.Discrete(10)
        
        # Estado: features normalizados
        self.observation_space = spaces.Box(
            low=-np.inf,
            high=np.inf,
            shape=(state_dim,),
            dtype=np.float32
        )
        
        # Estado interno
        self.balance = initial_balance
        self.equity = initial_balance
        self.position = 0.0  # Posición actual (-1 a 1)
        self.entry_price = 0.0
        self.current_price = 0.0
        self.unrealized_pnl = 0.0
        self.realized_pnl = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.max_drawdown = 0.0
        self.peak_equity = initial_balance
        
        # Historial
        self.equity_history = []
        self.action_history = []
        
        # Datos de mercado (se actualizan externamente)
        self.market_data = None
        self.current_step = 0
        
        logger.debug("🎮 TradingEnvironment inicializado")
    
    def reset(self, seed=None, options=None):
        """Resetea el environment"""
        super().reset(seed=seed)
        
        self.balance = self.initial_balance
        self.equity = self.initial_balance
        self.position = 0.0
        self.entry_price = 0.0
        self.current_price = 0.0
        self.unrealized_pnl = 0.0
        self.realized_pnl = 0.0
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.max_drawdown = 0.0
        self.peak_equity = self.initial_balance
        
        self.equity_history = [self.initial_balance]
        self.action_history = []
        self.current_step = 0
        
        # Estado inicial (zeros si no hay datos)
        initial_state = np.zeros(self.state_dim, dtype=np.float32)
        
        return initial_state, {}
    
    def step(self, action: int):
        """
        Ejecuta una acción en el environment
        
        Args:
            action: Acción a ejecutar (0-9)
            
        Returns:
            Tupla (observation, reward, terminated, truncated, info)
        """
        # Decodificar acción
        action_type, position_size = self._decode_action(action)
        
        # Ejecutar acción
        reward = self._execute_action(action_type, position_size)
        
        # Actualizar estado
        self._update_state()
        
        # Verificar si terminó el episodio
        terminated = self.equity <= self.initial_balance * 0.5  # Stop si pierde 50%
        truncated = False
        
        # Información adicional
        info = {
            'balance': self.balance,
            'equity': self.equity,
            'position': self.position,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'total_trades': self.total_trades,
            'win_rate': self.winning_trades / max(self.total_trades, 1),
            'max_drawdown': self.max_drawdown
        }
        
        # Próximo estado (se actualiza externamente con datos reales)
        next_state = np.zeros(self.state_dim, dtype=np.float32)
        
        self.current_step += 1
        
        return next_state, reward, terminated, truncated, info
    
    def _decode_action(self, action: int) -> Tuple[str, float]:
        """
        Decodifica acción numérica
        
        Returns:
            Tupla (tipo_accion, tamaño_posicion)
        """
        if action == 0:
            return "HOLD", 0.0
        elif action in [1, 2, 3, 4]:
            # BUY con diferentes tamaños
            sizes = [0.25, 0.50, 0.75, 1.0]
            return "BUY", sizes[action - 1]
        elif action in [5, 6, 7, 8]:
            # SELL con diferentes tamaños
            sizes = [0.25, 0.50, 0.75, 1.0]
            return "SELL", sizes[action - 5]
        elif action == 9:
            return "CLOSE", 1.0
        else:
            return "HOLD", 0.0
    
    def _execute_action(self, action_type: str, position_size: float) -> float:
        """
        Ejecuta la acción y calcula recompensa
        
        Returns:
            Recompensa de la acción
        """
        reward = 0.0
        
        if action_type == "HOLD":
            # Pequeña penalización por no hacer nada
            reward = -0.01
        
        elif action_type == "BUY":
            if self.position <= 0:  # Solo si no hay posición long
                # Abrir posición long
                self.position = position_size * self.max_position_size
                self.entry_price = self.current_price
                
                # Costo de transacción
                cost = self.entry_price * abs(self.position) * self.transaction_cost
                self.balance -= cost
                reward = -cost  # Penalización por costo
        
        elif action_type == "SELL":
            if self.position >= 0:  # Solo si no hay posición short
                # Abrir posición short
                self.position = -position_size * self.max_position_size
                self.entry_price = self.current_price
                
                # Costo de transacción
                cost = self.entry_price * abs(self.position) * self.transaction_cost
                self.balance -= cost
                reward = -cost
        
        elif action_type == "CLOSE":
            if self.position != 0:
                # Cerrar posición
                pnl = self._calculate_pnl()
                
                # Costo de transacción
                cost = self.current_price * abs(self.position) * self.transaction_cost
                pnl -= cost
                
                # Actualizar balance
                self.balance += pnl
                self.realized_pnl += pnl
                
                # Actualizar estadísticas
                self.total_trades += 1
                if pnl > 0:
                    self.winning_trades += 1
                else:
                    self.losing_trades += 1
                
                # Calcular recompensa
                reward = self._calculate_reward(pnl)
                
                # Resetear posición
                self.position = 0.0
                self.entry_price = 0.0
                self.unrealized_pnl = 0.0
        
        self.action_history.append(action_type)
        
        return reward
    
    def _calculate_pnl(self) -> float:
        """Calcula P&L de la posición actual"""
        if self.position == 0:
            return 0.0
        
        if self.position > 0:  # Long
            pnl = (self.current_price - self.entry_price) * abs(self.position) * self.balance
        else:  # Short
            pnl = (self.entry_price - self.current_price) * abs(self.position) * self.balance
        
        return pnl
    
    def _calculate_reward(self, pnl: float) -> float:
        """
        Calcula recompensa basada en P&L y otros factores
        
        Función de recompensa:
        Reward = (Profit * 10) - (Loss * 15) - (DrawdownPenalty * 5) + (SharpeBonus * 3)
        """
        reward = 0.0
        
        # Componente de profit/loss
        pnl_percent = (pnl / self.initial_balance) * 100
        
        if pnl > 0:
            reward += pnl_percent * 10  # Bonus por ganancia
        else:
            reward += pnl_percent * 15  # Penalización más fuerte por pérdida
        
        # Penalización por drawdown
        current_drawdown = (self.peak_equity - self.equity) / self.peak_equity
        if current_drawdown > 0.10:  # Más de 10% drawdown
            reward -= current_drawdown * 5
        
        # Bonus por Sharpe ratio (simplificado)
        if len(self.equity_history) > 10:
            returns = np.diff(self.equity_history[-10:]) / self.equity_history[-11:-1]
            if len(returns) > 0 and np.std(returns) > 0:
                sharpe = np.mean(returns) / np.std(returns)
                reward += sharpe * 3
        
        return reward
    
    def _update_state(self):
        """Actualiza el estado interno"""
        # Calcular P&L no realizado
        if self.position != 0:
            self.unrealized_pnl = self._calculate_pnl()
        else:
            self.unrealized_pnl = 0.0
        
        # Actualizar equity
        self.equity = self.balance + self.unrealized_pnl
        self.equity_history.append(self.equity)
        
        # Actualizar peak equity y drawdown
        if self.equity > self.peak_equity:
            self.peak_equity = self.equity
        
        current_drawdown = (self.peak_equity - self.equity) / self.peak_equity
        if current_drawdown > self.max_drawdown:
            self.max_drawdown = current_drawdown
    
    def set_market_data(self, price: float):
        """Actualiza el precio actual del mercado"""
        self.current_price = price
    
    def render(self):
        """Renderiza el estado actual (para debugging)"""
        print(f"Step: {self.current_step} | Equity: ${self.equity:.2f} | "
              f"Position: {self.position:.2f} | P&L: ${self.realized_pnl:.2f}")


class RLAgent:
    """
    Agente de Reinforcement Learning usando PPO
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Hiperparámetros
        self.state_dim = self.config.get('state_dim', 80)
        self.learning_rate = self.config.get('learning_rate', 0.0003)
        self.gamma = self.config.get('gamma', 0.99)
        self.n_steps = self.config.get('n_steps', 2048)
        self.batch_size = self.config.get('batch_size', 64)
        self.n_epochs = self.config.get('n_epochs', 10)
        
        # Environment
        self.env = TradingEnvironment(state_dim=self.state_dim)
        self.vec_env = DummyVecEnv([lambda: self.env])
        
        # Modelo PPO
        self.model: Optional[PPO] = None
        self.is_trained = False
        
        # Métricas
        self.training_history = []
        
        logger.info("🤖 RLAgent inicializado (PPO)")
    
    def build_model(self):
        """Construye el modelo PPO"""
        self.model = PPO(
            policy="MlpPolicy",
            env=self.vec_env,
            learning_rate=self.learning_rate,
            n_steps=self.n_steps,
            batch_size=self.batch_size,
            n_epochs=self.n_epochs,
            gamma=self.gamma,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.01,
            vf_coef=0.5,
            max_grad_norm=0.5,
            verbose=0,
            device='auto'
        )
        
        logger.success("✓ Modelo PPO construido")
        logger.info(f"  Learning rate: {self.learning_rate}")
        logger.info(f"  Gamma: {self.gamma}")
        logger.info(f"  N steps: {self.n_steps}")
    
    def train(self, total_timesteps: int = 100000, callback=None):
        """
        Entrena el agente
        
        Args:
            total_timesteps: Número total de pasos de entrenamiento
            callback: Callback personalizado
        """
        if self.model is None:
            self.build_model()
        
        logger.info(f"🎓 Iniciando entrenamiento RL...")
        logger.info(f"  Total timesteps: {total_timesteps:,}")
        
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=callback,
            progress_bar=True
        )
        
        self.is_trained = True
        logger.success("✓ Entrenamiento RL completado")
    
    def select_action(
        self, 
        state: np.ndarray,
        deterministic: bool = False
    ) -> Tuple[int, np.ndarray]:
        """
        Selecciona una acción basada en el estado
        
        Args:
            state: Estado actual del mercado
            deterministic: Si True, selecciona acción con mayor probabilidad
            
        Returns:
            Tupla (acción, probabilidades)
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado. Llamar a train() primero.")
        
        # Asegurar que state tenga la forma correcta
        if len(state.shape) == 1:
            state = state.reshape(1, -1)
        
        # Predecir acción
        action, _states = self.model.predict(state, deterministic=deterministic)
        
        # Obtener probabilidades de acción
        obs_tensor = torch.FloatTensor(state).to(self.model.device)
        with torch.no_grad():
            distribution = self.model.policy.get_distribution(obs_tensor)
            probs = torch.softmax(distribution.distribution.logits, dim=-1)
            probs = probs.cpu().numpy()[0]
        
        return int(action[0]), probs
    
    def get_action_name(self, action: int) -> str:
        """Convierte acción numérica a nombre"""
        action_names = {
            0: "HOLD",
            1: "BUY_25%",
            2: "BUY_50%",
            3: "BUY_75%",
            4: "BUY_100%",
            5: "SELL_25%",
            6: "SELL_50%",
            7: "SELL_75%",
            8: "SELL_100%",
            9: "CLOSE"
        }
        return action_names.get(action, "UNKNOWN")
    
    def save(self, filepath: str):
        """Guarda el modelo entrenado"""
        if self.model is None:
            logger.warning("⚠️  No hay modelo para guardar")
            return
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        self.model.save(filepath)
        logger.success(f"✓ Modelo RL guardado: {filepath}")
    
    def load(self, filepath: str):
        """Carga un modelo guardado"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"✗ Archivo no encontrado: {filepath}")
            return False
        
        try:
            self.model = PPO.load(filepath, env=self.vec_env)
            self.is_trained = True
            logger.success(f"✓ Modelo RL cargado: {filepath}")
            return True
        except Exception as e:
            logger.error(f"✗ Error cargando modelo: {e}")
            return False


class TrainingCallback(BaseCallback):
    """Callback personalizado para monitorear entrenamiento"""
    
    def __init__(self, verbose=0):
        super(TrainingCallback, self).__init__(verbose)
        self.episode_rewards = []
        self.episode_lengths = []
    
    def _on_step(self) -> bool:
        # Registrar recompensas
        if len(self.locals.get('rewards', [])) > 0:
            self.episode_rewards.append(self.locals['rewards'][0])
        
        # Log cada 1000 pasos
        if self.n_calls % 1000 == 0:
            if len(self.episode_rewards) > 0:
                mean_reward = np.mean(self.episode_rewards[-100:])
                logger.info(f"  Step {self.n_calls} | Mean Reward (last 100): {mean_reward:.2f}")
        
        return True
