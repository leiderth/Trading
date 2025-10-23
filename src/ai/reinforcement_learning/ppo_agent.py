"""
Proximal Policy Optimization (PPO) Agent
Estado del arte en Reinforcement Learning para trading
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from typing import Dict, List, Tuple
from collections import deque
import random
from loguru import logger


class ActorCritic(nn.Module):
    """
    Red neuronal Actor-Critic para PPO
    Actor: Decide qué acción tomar
    Critic: Evalúa qué tan buena es la acción
    """
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dim: int = 256):
        super().__init__()
        
        # Shared feature extractor
        self.shared = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
        # Actor head (policy)
        self.actor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, action_dim),
            nn.Softmax(dim=-1)
        )
        
        # Critic head (value function)
        self.critic = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )
    
    def forward(self, state):
        features = self.shared(state)
        action_probs = self.actor(features)
        state_value = self.critic(features)
        return action_probs, state_value


class PPOAgent:
    """
    Proximal Policy Optimization Agent
    
    Características:
    - Clipped surrogate objective
    - Generalized Advantage Estimation (GAE)
    - Multiple epochs per update
    - Entropy bonus para exploración
    """
    
    def __init__(
        self,
        state_dim: int,
        action_dim: int,
        lr: float = 3e-4,
        gamma: float = 0.99,
        gae_lambda: float = 0.95,
        clip_epsilon: float = 0.2,
        c1: float = 0.5,  # Value loss coefficient
        c2: float = 0.01,  # Entropy coefficient
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    ):
        self.device = device
        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_epsilon = clip_epsilon
        self.c1 = c1
        self.c2 = c2
        
        # Actor-Critic network
        self.policy = ActorCritic(state_dim, action_dim).to(device)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=lr)
        
        # Memory
        self.memory = {
            'states': [],
            'actions': [],
            'rewards': [],
            'values': [],
            'log_probs': [],
            'dones': []
        }
        
        # Statistics
        self.episode_rewards = []
        self.episode_lengths = []
        
        logger.info(f"PPO Agent inicializado en {device}")
    
    def select_action(self, state: np.ndarray, deterministic: bool = False) -> Tuple[int, float, float]:
        """
        Selecciona acción usando la política actual
        
        Returns:
            action: Acción seleccionada
            log_prob: Log probabilidad de la acción
            value: Valor estimado del estado
        """
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            action_probs, value = self.policy(state_tensor)
        
        if deterministic:
            action = torch.argmax(action_probs, dim=1).item()
        else:
            dist = torch.distributions.Categorical(action_probs)
            action = dist.sample().item()
        
        log_prob = torch.log(action_probs[0, action] + 1e-10).item()
        
        return action, log_prob, value.item()
    
    def store_transition(self, state, action, reward, value, log_prob, done):
        """Almacena transición en memoria"""
        self.memory['states'].append(state)
        self.memory['actions'].append(action)
        self.memory['rewards'].append(reward)
        self.memory['values'].append(value)
        self.memory['log_probs'].append(log_prob)
        self.memory['dones'].append(done)
    
    def compute_gae(self, next_value: float) -> Tuple[List[float], List[float]]:
        """
        Compute Generalized Advantage Estimation (GAE)
        
        GAE reduce variance mientras mantiene bajo bias
        """
        rewards = self.memory['rewards']
        values = self.memory['values'] + [next_value]
        dones = self.memory['dones']
        
        advantages = []
        gae = 0
        
        # Compute advantages backwards
        for t in reversed(range(len(rewards))):
            delta = rewards[t] + self.gamma * values[t + 1] * (1 - dones[t]) - values[t]
            gae = delta + self.gamma * self.gae_lambda * (1 - dones[t]) * gae
            advantages.insert(0, gae)
        
        # Compute returns (advantages + values)
        returns = [adv + val for adv, val in zip(advantages, values[:-1])]
        
        return advantages, returns
    
    def update(self, next_state: np.ndarray, epochs: int = 10, batch_size: int = 64):
        """
        Actualiza la política usando PPO
        
        Args:
            next_state: Siguiente estado para bootstrap
            epochs: Número de epochs de optimización
            batch_size: Tamaño del batch
        """
        if len(self.memory['states']) == 0:
            return
        
        # Compute next value for GAE
        next_state_tensor = torch.FloatTensor(next_state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            _, next_value = self.policy(next_state_tensor)
            next_value = next_value.item()
        
        # Compute advantages and returns
        advantages, returns = self.compute_gae(next_value)
        
        # Convert to tensors
        states = torch.FloatTensor(np.array(self.memory['states'])).to(self.device)
        actions = torch.LongTensor(self.memory['actions']).to(self.device)
        old_log_probs = torch.FloatTensor(self.memory['log_probs']).to(self.device)
        advantages = torch.FloatTensor(advantages).to(self.device)
        returns = torch.FloatTensor(returns).to(self.device)
        
        # Normalize advantages
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # PPO update for multiple epochs
        dataset_size = len(states)
        
        for epoch in range(epochs):
            # Shuffle data
            indices = torch.randperm(dataset_size)
            
            for start_idx in range(0, dataset_size, batch_size):
                end_idx = min(start_idx + batch_size, dataset_size)
                batch_indices = indices[start_idx:end_idx]
                
                # Get batch
                batch_states = states[batch_indices]
                batch_actions = actions[batch_indices]
                batch_old_log_probs = old_log_probs[batch_indices]
                batch_advantages = advantages[batch_indices]
                batch_returns = returns[batch_indices]
                
                # Forward pass
                action_probs, values = self.policy(batch_states)
                
                # Compute new log probs
                dist = torch.distributions.Categorical(action_probs)
                new_log_probs = dist.log_prob(batch_actions)
                entropy = dist.entropy().mean()
                
                # Compute ratio
                ratio = torch.exp(new_log_probs - batch_old_log_probs)
                
                # Clipped surrogate objective
                surr1 = ratio * batch_advantages
                surr2 = torch.clamp(ratio, 1 - self.clip_epsilon, 1 + self.clip_epsilon) * batch_advantages
                actor_loss = -torch.min(surr1, surr2).mean()
                
                # Value loss
                value_loss = nn.MSELoss()(values.squeeze(), batch_returns)
                
                # Total loss
                loss = actor_loss + self.c1 * value_loss - self.c2 * entropy
                
                # Optimize
                self.optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(self.policy.parameters(), 0.5)
                self.optimizer.step()
        
        # Clear memory
        self.clear_memory()
        
        logger.debug(f"PPO update completed. Loss: {loss.item():.4f}")
    
    def clear_memory(self):
        """Limpia la memoria"""
        for key in self.memory:
            self.memory[key] = []
    
    def save(self, path: str):
        """Guarda el modelo"""
        torch.save({
            'policy_state_dict': self.policy.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'episode_rewards': self.episode_rewards,
            'episode_lengths': self.episode_lengths
        }, path)
        logger.info(f"PPO Agent guardado en {path}")
    
    def load(self, path: str):
        """Carga el modelo"""
        checkpoint = torch.load(path, map_location=self.device)
        self.policy.load_state_dict(checkpoint['policy_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.episode_rewards = checkpoint.get('episode_rewards', [])
        self.episode_lengths = checkpoint.get('episode_lengths', [])
        logger.info(f"PPO Agent cargado desde {path}")


class TradingEnvironment:
    """
    Environment para trading con RL
    Compatible con Gym interface
    """
    
    def __init__(self, data: np.ndarray, initial_balance: float = 10000):
        self.data = data
        self.initial_balance = initial_balance
        self.reset()
    
    def reset(self):
        """Reset environment"""
        self.current_step = 0
        self.balance = self.initial_balance
        self.position = 0  # 0: no position, 1: long, -1: short
        self.entry_price = 0
        self.total_reward = 0
        
        return self._get_state()
    
    def _get_state(self):
        """Get current state"""
        if self.current_step >= len(self.data):
            return np.zeros(self.data.shape[1] + 3)
        
        market_state = self.data[self.current_step]
        position_state = np.array([
            self.position,
            self.balance / self.initial_balance,
            (self.balance - self.initial_balance) / self.initial_balance
        ])
        
        return np.concatenate([market_state, position_state])
    
    def step(self, action: int):
        """
        Execute action
        
        Actions:
        0: Hold
        1: Buy/Long
        2: Sell/Short
        3: Close position
        """
        current_price = self.data[self.current_step, 0]  # Assuming first column is price
        reward = 0
        done = False
        
        # Execute action
        if action == 1 and self.position == 0:  # Buy
            self.position = 1
            self.entry_price = current_price
        
        elif action == 2 and self.position == 0:  # Sell
            self.position = -1
            self.entry_price = current_price
        
        elif action == 3 and self.position != 0:  # Close
            pnl = (current_price - self.entry_price) * self.position
            self.balance += pnl
            reward = pnl / self.entry_price  # Normalized reward
            self.position = 0
            self.entry_price = 0
        
        # Move to next step
        self.current_step += 1
        
        # Check if done
        if self.current_step >= len(self.data) - 1:
            done = True
            # Close any open position
            if self.position != 0:
                pnl = (current_price - self.entry_price) * self.position
                self.balance += pnl
                reward += pnl / self.entry_price
        
        self.total_reward += reward
        
        next_state = self._get_state()
        
        return next_state, reward, done, {}
