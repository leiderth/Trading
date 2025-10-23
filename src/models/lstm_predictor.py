"""
Modelo LSTM para predicción de precios
Predice movimientos futuros del mercado
"""

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from typing import Tuple, Optional, Dict
from pathlib import Path
from loguru import logger


class PriceDataset(Dataset):
    """Dataset para entrenamiento del LSTM"""
    
    def __init__(self, sequences: np.ndarray, targets: np.ndarray):
        self.sequences = torch.FloatTensor(sequences)
        self.targets = torch.FloatTensor(targets)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.targets[idx]


class LSTMModel(nn.Module):
    """Arquitectura LSTM para predicción de precios"""
    
    def __init__(
        self,
        input_size: int,
        hidden_units: list = [128, 64],
        dropout: float = 0.2,
        forecast_horizon: int = 10
    ):
        super(LSTMModel, self).__init__()
        
        self.input_size = input_size
        self.hidden_units = hidden_units
        self.forecast_horizon = forecast_horizon
        
        # Primera capa LSTM
        self.lstm1 = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_units[0],
            batch_first=True,
            dropout=dropout if len(hidden_units) > 1 else 0
        )
        
        # Segunda capa LSTM
        self.lstm2 = nn.LSTM(
            input_size=hidden_units[0],
            hidden_size=hidden_units[1],
            batch_first=True
        )
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        # Capas densas
        self.fc1 = nn.Linear(hidden_units[1], 32)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(32, forecast_horizon)
    
    def forward(self, x):
        # x shape: (batch, sequence_length, input_size)
        
        # LSTM layers
        lstm_out1, _ = self.lstm1(x)
        lstm_out1 = self.dropout(lstm_out1)
        
        lstm_out2, _ = self.lstm2(lstm_out1)
        
        # Tomar última salida temporal
        last_output = lstm_out2[:, -1, :]
        
        # Dense layers
        out = self.fc1(last_output)
        out = self.relu(out)
        out = self.dropout(out)
        out = self.fc2(out)
        
        return out


class LSTMPredictor:
    """
    Predictor LSTM para precios de mercado
    """
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
        # Hiperparámetros
        self.lookback_period = self.config.get('lookback_period', 100)
        self.forecast_horizon = self.config.get('forecast_horizon', 10)
        self.hidden_units = self.config.get('hidden_units', [128, 64])
        self.dropout = self.config.get('dropout', 0.2)
        self.learning_rate = self.config.get('learning_rate', 0.001)
        self.batch_size = self.config.get('batch_size', 32)
        self.epochs = self.config.get('epochs', 100)
        
        # Modelo
        self.model: Optional[LSTMModel] = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Normalización
        self.price_mean = 0.0
        self.price_std = 1.0
        
        # Métricas
        self.training_history = []
        self.confidence_score = 0.0
        
        logger.info(f"🧠 LSTMPredictor inicializado (device: {self.device})")
    
    def build_model(self, input_size: int):
        """Construye la arquitectura del modelo"""
        self.model = LSTMModel(
            input_size=input_size,
            hidden_units=self.hidden_units,
            dropout=self.dropout,
            forecast_horizon=self.forecast_horizon
        ).to(self.device)
        
        logger.info(f"✓ Modelo LSTM construido")
        logger.info(f"  Input size: {input_size}")
        logger.info(f"  Hidden units: {self.hidden_units}")
        logger.info(f"  Forecast horizon: {self.forecast_horizon}")
        logger.info(f"  Total parameters: {sum(p.numel() for p in self.model.parameters()):,}")
    
    def prepare_sequences(
        self, 
        prices: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepara secuencias para entrenamiento
        
        Args:
            prices: Array de precios (close prices)
            
        Returns:
            Tupla (sequences, targets)
        """
        # Normalizar precios
        self.price_mean = np.mean(prices)
        self.price_std = np.std(prices)
        normalized_prices = (prices - self.price_mean) / (self.price_std + 1e-8)
        
        sequences = []
        targets = []
        
        for i in range(len(normalized_prices) - self.lookback_period - self.forecast_horizon):
            # Secuencia de entrada
            seq = normalized_prices[i:i + self.lookback_period]
            
            # Target: próximos N precios
            target = normalized_prices[
                i + self.lookback_period:i + self.lookback_period + self.forecast_horizon
            ]
            
            sequences.append(seq)
            targets.append(target)
        
        sequences = np.array(sequences).reshape(-1, self.lookback_period, 1)
        targets = np.array(targets)
        
        logger.debug(f"✓ Secuencias preparadas: {sequences.shape}, targets: {targets.shape}")
        
        return sequences, targets
    
    def train(
        self, 
        df: pd.DataFrame,
        validation_split: float = 0.2,
        verbose: bool = True
    ) -> Dict:
        """
        Entrena el modelo LSTM
        
        Args:
            df: DataFrame con columna 'close'
            validation_split: Porcentaje para validación
            verbose: Mostrar progreso
            
        Returns:
            Diccionario con métricas de entrenamiento
        """
        if 'close' not in df.columns:
            raise ValueError("DataFrame debe contener columna 'close'")
        
        prices = df['close'].values
        
        if len(prices) < self.lookback_period + self.forecast_horizon + 100:
            raise ValueError(f"Datos insuficientes. Mínimo: {self.lookback_period + self.forecast_horizon + 100}")
        
        # Preparar datos
        sequences, targets = self.prepare_sequences(prices)
        
        # Split train/validation
        split_idx = int(len(sequences) * (1 - validation_split))
        train_sequences = sequences[:split_idx]
        train_targets = targets[:split_idx]
        val_sequences = sequences[split_idx:]
        val_targets = targets[split_idx:]
        
        # Crear datasets
        train_dataset = PriceDataset(train_sequences, train_targets)
        val_dataset = PriceDataset(val_sequences, val_targets)
        
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)
        
        # Construir modelo si no existe
        if self.model is None:
            self.build_model(input_size=1)
        
        # Optimizer y loss
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        criterion = nn.MSELoss()
        
        # Entrenamiento
        logger.info(f"🎓 Iniciando entrenamiento LSTM...")
        logger.info(f"  Train samples: {len(train_dataset)}")
        logger.info(f"  Val samples: {len(val_dataset)}")
        logger.info(f"  Epochs: {self.epochs}")
        
        best_val_loss = float('inf')
        patience = 10
        patience_counter = 0
        
        for epoch in range(self.epochs):
            # Training
            self.model.train()
            train_loss = 0.0
            
            for sequences_batch, targets_batch in train_loader:
                sequences_batch = sequences_batch.to(self.device)
                targets_batch = targets_batch.to(self.device)
                
                optimizer.zero_grad()
                outputs = self.model(sequences_batch)
                loss = criterion(outputs, targets_batch)
                loss.backward()
                optimizer.step()
                
                train_loss += loss.item()
            
            train_loss /= len(train_loader)
            
            # Validation
            self.model.eval()
            val_loss = 0.0
            
            with torch.no_grad():
                for sequences_batch, targets_batch in val_loader:
                    sequences_batch = sequences_batch.to(self.device)
                    targets_batch = targets_batch.to(self.device)
                    
                    outputs = self.model(sequences_batch)
                    loss = criterion(outputs, targets_batch)
                    val_loss += loss.item()
            
            val_loss /= len(val_loader)
            
            # Guardar historial
            self.training_history.append({
                'epoch': epoch + 1,
                'train_loss': train_loss,
                'val_loss': val_loss
            })
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Guardar mejor modelo
                self._save_checkpoint('best_lstm_model.pth')
            else:
                patience_counter += 1
            
            if verbose and (epoch + 1) % 10 == 0:
                logger.info(
                    f"  Epoch {epoch+1}/{self.epochs} | "
                    f"Train Loss: {train_loss:.6f} | "
                    f"Val Loss: {val_loss:.6f}"
                )
            
            if patience_counter >= patience:
                logger.info(f"⚠️  Early stopping en epoch {epoch+1}")
                break
        
        # Calcular confianza basada en val loss
        self.confidence_score = self._calculate_confidence(best_val_loss)
        
        logger.success(f"✓ Entrenamiento completado")
        logger.info(f"  Best Val Loss: {best_val_loss:.6f}")
        logger.info(f"  Confidence Score: {self.confidence_score:.2%}")
        
        return {
            'best_val_loss': best_val_loss,
            'confidence': self.confidence_score,
            'epochs_trained': len(self.training_history)
        }
    
    def predict(self, df: pd.DataFrame) -> Tuple[np.ndarray, float, float]:
        """
        Predice precios futuros
        
        Args:
            df: DataFrame con últimas N velas (mínimo lookback_period)
            
        Returns:
            Tupla (predicted_prices, direction_confidence, price_change_percent)
        """
        if self.model is None:
            raise ValueError("Modelo no entrenado. Llamar a train() primero.")
        
        if len(df) < self.lookback_period:
            raise ValueError(f"Se requieren al menos {self.lookback_period} velas")
        
        # Obtener últimos precios
        prices = df['close'].tail(self.lookback_period).values
        
        # Normalizar
        normalized_prices = (prices - self.price_mean) / (self.price_std + 1e-8)
        
        # Preparar input
        sequence = torch.FloatTensor(normalized_prices).reshape(1, self.lookback_period, 1)
        sequence = sequence.to(self.device)
        
        # Predicción
        self.model.eval()
        with torch.no_grad():
            prediction = self.model(sequence)
            prediction = prediction.cpu().numpy()[0]
        
        # Desnormalizar
        predicted_prices = prediction * self.price_std + self.price_mean
        
        # Calcular dirección y confianza
        current_price = prices[-1]
        future_price = predicted_prices[-1]  # Último precio predicho
        price_change_percent = ((future_price - current_price) / current_price) * 100
        
        # Dirección esperada
        direction = "UP" if future_price > current_price else "DOWN"
        
        # Confianza basada en magnitud del cambio y confidence score del modelo
        magnitude_confidence = min(abs(price_change_percent) / 2.0, 1.0)  # Max 2% = 100% confianza
        direction_confidence = self.confidence_score * magnitude_confidence
        
        logger.debug(f"📈 Predicción: {direction} | Cambio: {price_change_percent:+.2f}% | Confianza: {direction_confidence:.2%}")
        
        return predicted_prices, direction_confidence, price_change_percent
    
    def get_confidence(self) -> float:
        """Retorna el score de confianza del modelo"""
        return self.confidence_score
    
    def _calculate_confidence(self, val_loss: float) -> float:
        """
        Calcula score de confianza basado en validation loss
        
        Args:
            val_loss: Validation loss del modelo
            
        Returns:
            Score de confianza entre 0 y 1
        """
        # Mapear val_loss a confianza
        # Loss bajo = alta confianza
        # Asumiendo que loss < 0.01 es excelente
        if val_loss < 0.001:
            return 0.95
        elif val_loss < 0.005:
            return 0.85
        elif val_loss < 0.01:
            return 0.75
        elif val_loss < 0.02:
            return 0.65
        elif val_loss < 0.05:
            return 0.55
        else:
            return 0.45
    
    def save(self, filepath: str):
        """Guarda el modelo entrenado"""
        if self.model is None:
            logger.warning("⚠️  No hay modelo para guardar")
            return
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        checkpoint = {
            'model_state_dict': self.model.state_dict(),
            'config': self.config,
            'lookback_period': self.lookback_period,
            'forecast_horizon': self.forecast_horizon,
            'hidden_units': self.hidden_units,
            'price_mean': self.price_mean,
            'price_std': self.price_std,
            'confidence_score': self.confidence_score,
            'training_history': self.training_history
        }
        
        torch.save(checkpoint, filepath)
        logger.success(f"✓ Modelo guardado: {filepath}")
    
    def load(self, filepath: str):
        """Carga un modelo guardado"""
        filepath = Path(filepath)
        
        if not filepath.exists():
            logger.error(f"✗ Archivo no encontrado: {filepath}")
            return False
        
        try:
            checkpoint = torch.load(filepath, map_location=self.device)
            
            # Restaurar configuración
            self.lookback_period = checkpoint['lookback_period']
            self.forecast_horizon = checkpoint['forecast_horizon']
            self.hidden_units = checkpoint['hidden_units']
            self.price_mean = checkpoint['price_mean']
            self.price_std = checkpoint['price_std']
            self.confidence_score = checkpoint['confidence_score']
            self.training_history = checkpoint.get('training_history', [])
            
            # Construir y cargar modelo
            self.build_model(input_size=1)
            self.model.load_state_dict(checkpoint['model_state_dict'])
            self.model.eval()
            
            logger.success(f"✓ Modelo cargado: {filepath}")
            logger.info(f"  Confidence: {self.confidence_score:.2%}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Error cargando modelo: {e}")
            return False
    
    def _save_checkpoint(self, filename: str):
        """Guarda checkpoint durante entrenamiento"""
        checkpoint_dir = Path(__file__).parent.parent.parent / "models" / "checkpoints"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.save(checkpoint_dir / filename)
