"""
Advanced AI Predictor - Transformer + Ensemble Learning
Sistema de predicción de última generación con múltiples modelos
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple
import pandas as pd
from loguru import logger
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime


class TransformerPredictor(nn.Module):
    """
    Transformer para series temporales financieras
    Arquitectura: Multi-head attention + Feed Forward
    """
    
    def __init__(self, input_dim: int = 50, d_model: int = 128, nhead: int = 8, 
                 num_layers: int = 4, dropout: float = 0.1):
        super().__init__()
        
        self.input_projection = nn.Linear(input_dim, d_model)
        self.positional_encoding = PositionalEncoding(d_model, dropout)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            activation='gelu',
            batch_first=True
        )
        
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        
        # Multi-task heads
        self.price_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, 1)
        )
        
        self.direction_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, 3)  # Up, Down, Neutral
        )
        
        self.volatility_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, 1)
        )
        
        self.confidence_head = nn.Sequential(
            nn.Linear(d_model, d_model // 2),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(d_model // 2, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        # x shape: (batch, seq_len, input_dim)
        x = self.input_projection(x)
        x = self.positional_encoding(x)
        x = self.transformer_encoder(x)
        
        # Use last timestep
        x = x[:, -1, :]
        
        price = self.price_head(x)
        direction = self.direction_head(x)
        volatility = self.volatility_head(x)
        confidence = self.confidence_head(x)
        
        return {
            'price': price,
            'direction': direction,
            'volatility': volatility,
            'confidence': confidence
        }


class PositionalEncoding(nn.Module):
    """Positional encoding para Transformer"""
    
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe = torch.zeros(max_len, 1, d_model)
        pe[:, 0, 0::2] = torch.sin(position * div_term)
        pe[:, 0, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        x = x + self.pe[:x.size(1)].transpose(0, 1)
        return self.dropout(x)


class WaveNetPredictor(nn.Module):
    """
    WaveNet para capturar patrones temporales complejos
    """
    
    def __init__(self, input_dim: int = 50, residual_channels: int = 64, 
                 skip_channels: int = 128, num_layers: int = 10):
        super().__init__()
        
        self.input_conv = nn.Conv1d(input_dim, residual_channels, kernel_size=1)
        
        self.dilated_convs = nn.ModuleList()
        self.residual_convs = nn.ModuleList()
        self.skip_convs = nn.ModuleList()
        
        for i in range(num_layers):
            dilation = 2 ** i
            self.dilated_convs.append(
                nn.Conv1d(residual_channels, residual_channels * 2, 
                         kernel_size=2, dilation=dilation, padding=dilation)
            )
            self.residual_convs.append(
                nn.Conv1d(residual_channels, residual_channels, kernel_size=1)
            )
            self.skip_convs.append(
                nn.Conv1d(residual_channels, skip_channels, kernel_size=1)
            )
        
        self.output = nn.Sequential(
            nn.ReLU(),
            nn.Conv1d(skip_channels, skip_channels, kernel_size=1),
            nn.ReLU(),
            nn.Conv1d(skip_channels, 1, kernel_size=1)
        )
    
    def forward(self, x):
        # x shape: (batch, seq_len, input_dim)
        x = x.transpose(1, 2)  # (batch, input_dim, seq_len)
        x = self.input_conv(x)
        
        skip_connections = []
        
        for dilated_conv, residual_conv, skip_conv in zip(
            self.dilated_convs, self.residual_convs, self.skip_convs
        ):
            residual = x
            x = dilated_conv(x)
            
            # Gated activation
            gate, filter = x.chunk(2, dim=1)
            x = torch.tanh(filter) * torch.sigmoid(gate)
            
            # Skip connection
            skip = skip_conv(x)
            skip_connections.append(skip)
            
            # Residual connection
            x = residual_conv(x)
            x = x + residual
        
        # Sum skip connections
        x = torch.stack(skip_connections).sum(dim=0)
        x = self.output(x)
        
        return x[:, :, -1]  # Last timestep


class EnsemblePredictor:
    """
    Ensemble de múltiples modelos para predicciones robustas
    Combina: Transformer, WaveNet, LSTM, GRU, TCN
    """
    
    def __init__(self, input_dim: int = 50, device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.input_dim = input_dim
        
        # Modelos del ensemble
        self.transformer = TransformerPredictor(input_dim).to(device)
        self.wavenet = WaveNetPredictor(input_dim).to(device)
        self.lstm = LSTMPredictor(input_dim).to(device)
        self.gru = GRUPredictor(input_dim).to(device)
        self.tcn = TCNPredictor(input_dim).to(device)
        
        # Pesos del ensemble (aprendidos)
        self.ensemble_weights = nn.Parameter(torch.ones(5) / 5).to(device)
        
        # Meta-learner
        self.meta_learner = nn.Sequential(
            nn.Linear(5, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1)
        ).to(device)
        
        self.scaler = StandardScaler()
        self.is_trained = False
        
        logger.info(f"Ensemble Predictor inicializado en {device}")
    
    def predict(self, features: np.ndarray) -> Dict:
        """
        Predicción con ensemble
        
        Returns:
            Dict con: price, direction, confidence, volatility
        """
        if not self.is_trained:
            logger.warning("Modelo no entrenado, usando predicción base")
            return self._base_prediction(features)
        
        try:
            # Preparar datos
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            x = torch.FloatTensor(features_scaled).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                # Predicciones de cada modelo
                transformer_out = self.transformer(x)
                wavenet_out = self.wavenet(x)
                lstm_out = self.lstm(x)
                gru_out = self.gru(x)
                tcn_out = self.tcn(x)
                
                # Ensemble ponderado
                predictions = torch.stack([
                    transformer_out['price'].squeeze(),
                    wavenet_out.squeeze(),
                    lstm_out.squeeze(),
                    gru_out.squeeze(),
                    tcn_out.squeeze()
                ])
                
                # Normalizar pesos
                weights = torch.softmax(self.ensemble_weights, dim=0)
                
                # Predicción final
                final_price = (predictions * weights).sum()
                
                # Confianza basada en consenso
                std = predictions.std()
                confidence = 1.0 / (1.0 + std.item())
                
                # Dirección (mayoría de votos)
                direction_probs = torch.softmax(transformer_out['direction'], dim=1)
                direction = torch.argmax(direction_probs).item()
                
                # Volatilidad esperada
                volatility = transformer_out['volatility'].item()
                
                return {
                    'price': final_price.item(),
                    'direction': ['DOWN', 'NEUTRAL', 'UP'][direction],
                    'confidence': confidence,
                    'volatility': abs(volatility),
                    'individual_predictions': predictions.cpu().numpy().tolist(),
                    'ensemble_weights': weights.cpu().numpy().tolist()
                }
        
        except Exception as e:
            logger.error(f"Error en predicción: {e}")
            return self._base_prediction(features)
    
    def train_step(self, features: np.ndarray, target: float, market_data: Dict):
        """
        Paso de entrenamiento online
        Actualiza modelos con nuevos datos
        """
        try:
            # Preparar datos
            if not self.is_trained:
                self.scaler.fit(features.reshape(1, -1))
                self.is_trained = True
            
            features_scaled = self.scaler.transform(features.reshape(1, -1))
            x = torch.FloatTensor(features_scaled).unsqueeze(0).to(self.device)
            y = torch.FloatTensor([target]).to(self.device)
            
            # Entrenar cada modelo
            self._train_transformer(x, y, market_data)
            self._train_wavenet(x, y)
            self._train_lstm(x, y)
            self._train_gru(x, y)
            self._train_tcn(x, y)
            
            # Actualizar pesos del ensemble
            self._update_ensemble_weights(x, y)
            
            logger.debug("Entrenamiento online completado")
            
        except Exception as e:
            logger.error(f"Error en entrenamiento: {e}")
    
    def _base_prediction(self, features: np.ndarray) -> Dict:
        """Predicción base cuando no hay modelo entrenado"""
        return {
            'price': features[-1] if len(features) > 0 else 0.0,
            'direction': 'NEUTRAL',
            'confidence': 0.5,
            'volatility': 0.01
        }
    
    def save(self, path: str):
        """Guardar modelos"""
        torch.save({
            'transformer': self.transformer.state_dict(),
            'wavenet': self.wavenet.state_dict(),
            'lstm': self.lstm.state_dict(),
            'gru': self.gru.state_dict(),
            'tcn': self.tcn.state_dict(),
            'ensemble_weights': self.ensemble_weights,
            'meta_learner': self.meta_learner.state_dict(),
            'scaler': self.scaler
        }, path)
        logger.info(f"Modelos guardados en {path}")
    
    def load(self, path: str):
        """Cargar modelos"""
        checkpoint = torch.load(path, map_location=self.device)
        self.transformer.load_state_dict(checkpoint['transformer'])
        self.wavenet.load_state_dict(checkpoint['wavenet'])
        self.lstm.load_state_dict(checkpoint['lstm'])
        self.gru.load_state_dict(checkpoint['gru'])
        self.tcn.load_state_dict(checkpoint['tcn'])
        self.ensemble_weights = checkpoint['ensemble_weights']
        self.meta_learner.load_state_dict(checkpoint['meta_learner'])
        self.scaler = checkpoint['scaler']
        self.is_trained = True
        logger.info(f"Modelos cargados desde {path}")


class LSTMPredictor(nn.Module):
    """LSTM mejorado con attention"""
    
    def __init__(self, input_dim: int = 50):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, 128, num_layers=3, batch_first=True, dropout=0.2)
        self.attention = nn.MultiheadAttention(128, num_heads=4, batch_first=True)
        self.output = nn.Linear(128, 1)
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        attn_out, _ = self.attention(lstm_out, lstm_out, lstm_out)
        return self.output(attn_out[:, -1, :])


class GRUPredictor(nn.Module):
    """GRU mejorado"""
    
    def __init__(self, input_dim: int = 50):
        super().__init__()
        self.gru = nn.GRU(input_dim, 128, num_layers=3, batch_first=True, dropout=0.2)
        self.output = nn.Linear(128, 1)
    
    def forward(self, x):
        gru_out, _ = self.gru(x)
        return self.output(gru_out[:, -1, :])


class TCNPredictor(nn.Module):
    """Temporal Convolutional Network"""
    
    def __init__(self, input_dim: int = 50):
        super().__init__()
        self.tcn = nn.Sequential(
            nn.Conv1d(input_dim, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(64, 128, kernel_size=3, padding=2, dilation=2),
            nn.ReLU(),
            nn.Conv1d(128, 128, kernel_size=3, padding=4, dilation=4),
            nn.ReLU()
        )
        self.output = nn.Linear(128, 1)
    
    def forward(self, x):
        x = x.transpose(1, 2)
        tcn_out = self.tcn(x)
        return self.output(tcn_out[:, :, -1])
