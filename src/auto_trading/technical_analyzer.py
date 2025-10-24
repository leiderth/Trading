"""
Analizador Técnico Simple
Usa solo indicadores técnicos sin modelos de IA pesados
"""

import pandas as pd
import numpy as np
from loguru import logger
from typing import Dict


class TechnicalAnalyzer:
    """
    Analizador basado en indicadores técnicos
    No requiere PyTorch ni modelos de IA pesados
    """
    
    def __init__(self):
        logger.info("📊 TechnicalAnalyzer inicializado")
    
    def analyze(self, market_data: pd.DataFrame) -> Dict:
        """
        Analiza el mercado usando indicadores técnicos
        
        Args:
            market_data: DataFrame con OHLCV
            
        Returns:
            Dict con: action, confidence, reason, entry_price, stop_loss, take_profit
        """
        try:
            # Calcular indicadores
            df = self._calculate_indicators(market_data)
            
            # Obtener valores actuales
            current = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Analizar señales
            signal = self._generate_signal(current, prev, df)
            
            return signal
            
        except Exception as e:
            logger.error(f"❌ Error en análisis técnico: {e}")
            return {
                'action': 'HOLD',
                'confidence': 0.0,
                'reason': f'Error: {str(e)}',
                'entry_price': market_data['close'].iloc[-1],
                'stop_loss': None,
                'take_profit': None
            }
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calcula todos los indicadores técnicos"""
        df = df.copy()
        
        # RSI (Relative Strength Index)
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['signal_line']
        
        # Bollinger Bands
        df['bb_middle'] = df['close'].rolling(window=20).mean()
        bb_std = df['close'].rolling(window=20).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
        
        # Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        df['ema_12'] = df['close'].ewm(span=12, adjust=False).mean()
        df['ema_26'] = df['close'].ewm(span=26, adjust=False).mean()
        
        # ATR (Average True Range)
        df['h-l'] = df['high'] - df['low']
        df['h-pc'] = abs(df['high'] - df['close'].shift(1))
        df['l-pc'] = abs(df['low'] - df['close'].shift(1))
        df['tr'] = df[['h-l', 'h-pc', 'l-pc']].max(axis=1)
        df['atr'] = df['tr'].rolling(window=14).mean()
        
        # Volume
        df['volume_sma'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Price changes
        df['price_change_1'] = df['close'].pct_change(1)
        df['price_change_5'] = df['close'].pct_change(5)
        
        # Momentum
        df['momentum'] = df['close'] - df['close'].shift(10)
        
        return df
    
    def _generate_signal(self, current: pd.Series, prev: pd.Series, df: pd.DataFrame) -> Dict:
        """Genera señal de trading basada en indicadores"""
        
        # Valores actuales
        price = current['close']
        rsi = current['rsi']
        macd = current['macd']
        signal_line = current['signal_line']
        macd_hist = current['macd_histogram']
        bb_upper = current['bb_upper']
        bb_lower = current['bb_lower']
        bb_middle = current['bb_middle']
        sma_20 = current['sma_20']
        sma_50 = current['sma_50']
        volume_ratio = current['volume_ratio']
        atr = current['atr']
        
        # Valores anteriores
        prev_macd_hist = prev['macd_histogram']
        
        # Contadores de señales
        buy_signals = 0
        sell_signals = 0
        total_signals = 0
        reasons = []
        
        # === SEÑALES DE COMPRA ===
        
        # 1. RSI Sobreventa
        if rsi < 30:
            buy_signals += 2  # Peso mayor
            total_signals += 2
            reasons.append("RSI sobreventa (<30)")
        elif rsi < 40:
            buy_signals += 1
            total_signals += 2
            reasons.append("RSI bajo (<40)")
        else:
            total_signals += 2
        
        # 2. MACD Cruce Alcista
        if macd > signal_line and prev_macd_hist < 0 and macd_hist > 0:
            buy_signals += 2
            total_signals += 2
            reasons.append("MACD cruce alcista")
        elif macd > signal_line:
            buy_signals += 1
            total_signals += 2
            reasons.append("MACD positivo")
        else:
            total_signals += 2
        
        # 3. Bollinger Bands
        if price < bb_lower:
            buy_signals += 2
            total_signals += 2
            reasons.append("Precio bajo Bollinger inferior")
        elif price < bb_middle:
            buy_signals += 1
            total_signals += 2
            reasons.append("Precio bajo media Bollinger")
        else:
            total_signals += 2
        
        # 4. Moving Averages
        if price > sma_20 and sma_20 > sma_50:
            buy_signals += 2
            total_signals += 2
            reasons.append("Tendencia alcista (MA)")
        elif price > sma_20:
            buy_signals += 1
            total_signals += 2
            reasons.append("Precio sobre SMA20")
        else:
            total_signals += 2
        
        # 5. Volumen
        if volume_ratio > 1.5:
            buy_signals += 1
            total_signals += 1
            reasons.append("Volumen alto")
        else:
            total_signals += 1
        
        # === SEÑALES DE VENTA ===
        
        # 1. RSI Sobrecompra
        if rsi > 70:
            sell_signals += 2
            reasons.append("RSI sobrecompra (>70)")
        elif rsi > 60:
            sell_signals += 1
            reasons.append("RSI alto (>60)")
        
        # 2. MACD Cruce Bajista
        if macd < signal_line and prev_macd_hist > 0 and macd_hist < 0:
            sell_signals += 2
            reasons.append("MACD cruce bajista")
        elif macd < signal_line:
            sell_signals += 1
            reasons.append("MACD negativo")
        
        # 3. Bollinger Bands
        if price > bb_upper:
            sell_signals += 2
            reasons.append("Precio sobre Bollinger superior")
        elif price > bb_middle:
            sell_signals += 1
            reasons.append("Precio sobre media Bollinger")
        
        # 4. Moving Averages
        if price < sma_20 and sma_20 < sma_50:
            sell_signals += 2
            reasons.append("Tendencia bajista (MA)")
        elif price < sma_20:
            sell_signals += 1
            reasons.append("Precio bajo SMA20")
        
        # === DECISIÓN FINAL ===
        
        # Calcular confianza
        if buy_signals > sell_signals:
            action = 'BUY'
            confidence = buy_signals / total_signals
            reason = "Señal de COMPRA: " + ", ".join(reasons[:3])
        elif sell_signals > buy_signals:
            action = 'SELL'
            confidence = sell_signals / total_signals
            reason = "Señal de VENTA: " + ", ".join(reasons[:3])
        else:
            action = 'HOLD'
            confidence = 0.0
            reason = "Sin señal clara, condiciones mixtas"
        
        # Calcular Stop Loss y Take Profit
        if action == 'BUY':
            stop_loss = price - (atr * 2)
            take_profit = price + (atr * 3)
        elif action == 'SELL':
            stop_loss = price + (atr * 2)
            take_profit = price - (atr * 3)
        else:
            stop_loss = None
            take_profit = None
        
        return {
            'action': action,
            'confidence': confidence,
            'reason': reason,
            'entry_price': price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'atr': atr,
            'indicators': {
                'rsi': rsi,
                'macd': macd,
                'price_vs_bb': 'lower' if price < bb_lower else 'upper' if price > bb_upper else 'middle',
                'trend': 'up' if sma_20 > sma_50 else 'down',
                'volume': 'high' if volume_ratio > 1.5 else 'normal'
            }
        }
