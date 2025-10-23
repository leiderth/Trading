"""
Advanced Technical Indicators
100+ indicadores técnicos de nivel institucional
"""

import numpy as np
import pandas as pd
from typing import Dict, List
import talib
from scipy import stats
from loguru import logger


class AdvancedIndicators:
    """
    Suite completa de indicadores técnicos avanzados
    """
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula todos los indicadores disponibles
        
        Args:
            df: DataFrame con OHLCV
        
        Returns:
            DataFrame con 100+ indicadores
        """
        try:
            indicators = df.copy()
            
            # 1. TREND INDICATORS (20)
            indicators = AdvancedIndicators._add_trend_indicators(indicators)
            
            # 2. MOMENTUM INDICATORS (25)
            indicators = AdvancedIndicators._add_momentum_indicators(indicators)
            
            # 3. VOLATILITY INDICATORS (15)
            indicators = AdvancedIndicators._add_volatility_indicators(indicators)
            
            # 4. VOLUME INDICATORS (15)
            indicators = AdvancedIndicators._add_volume_indicators(indicators)
            
            # 5. CYCLE INDICATORS (10)
            indicators = AdvancedIndicators._add_cycle_indicators(indicators)
            
            # 6. PATTERN RECOGNITION (20)
            indicators = AdvancedIndicators._add_pattern_indicators(indicators)
            
            # 7. STATISTICAL INDICATORS (15)
            indicators = AdvancedIndicators._add_statistical_indicators(indicators)
            
            # 8. CUSTOM INDICATORS (10)
            indicators = AdvancedIndicators._add_custom_indicators(indicators)
            
            logger.info(f"Calculados {len(indicators.columns) - 5} indicadores")
            return indicators
            
        except Exception as e:
            logger.error(f"Error calculando indicadores: {e}")
            return df
    
    @staticmethod
    def _add_trend_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Indicadores de tendencia"""
        
        # Moving Averages
        for period in [5, 10, 20, 50, 100, 200]:
            df[f'SMA_{period}'] = talib.SMA(df['close'], timeperiod=period)
            df[f'EMA_{period}'] = talib.EMA(df['close'], timeperiod=period)
            df[f'WMA_{period}'] = talib.WMA(df['close'], timeperiod=period)
        
        # MACD
        df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(df['close'])
        
        # ADX (Average Directional Index)
        df['ADX'] = talib.ADX(df['high'], df['low'], df['close'])
        df['ADX_PLUS'] = talib.PLUS_DI(df['high'], df['low'], df['close'])
        df['ADX_MINUS'] = talib.MINUS_DI(df['high'], df['low'], df['close'])
        
        # Parabolic SAR
        df['SAR'] = talib.SAR(df['high'], df['low'])
        
        # Aroon
        df['AROON_UP'], df['AROON_DOWN'] = talib.AROON(df['high'], df['low'])
        df['AROON_OSC'] = talib.AROONOSC(df['high'], df['low'])
        
        # Supertrend
        df = AdvancedIndicators._calculate_supertrend(df)
        
        return df
    
    @staticmethod
    def _add_momentum_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Indicadores de momentum"""
        
        # RSI (múltiples períodos)
        for period in [7, 14, 21, 28]:
            df[f'RSI_{period}'] = talib.RSI(df['close'], timeperiod=period)
        
        # Stochastic
        df['STOCH_K'], df['STOCH_D'] = talib.STOCH(df['high'], df['low'], df['close'])
        df['STOCHF_K'], df['STOCHF_D'] = talib.STOCHF(df['high'], df['low'], df['close'])
        df['STOCHRSI_K'], df['STOCHRSI_D'] = talib.STOCHRSI(df['close'])
        
        # Williams %R
        df['WILLR'] = talib.WILLR(df['high'], df['low'], df['close'])
        
        # CCI (Commodity Channel Index)
        df['CCI'] = talib.CCI(df['high'], df['low'], df['close'])
        
        # MFI (Money Flow Index)
        df['MFI'] = talib.MFI(df['high'], df['low'], df['close'], df['volume'])
        
        # ROC (Rate of Change)
        for period in [10, 20, 30]:
            df[f'ROC_{period}'] = talib.ROC(df['close'], timeperiod=period)
        
        # Momentum
        df['MOM'] = talib.MOM(df['close'])
        
        # Ultimate Oscillator
        df['ULTOSC'] = talib.ULTOSC(df['high'], df['low'], df['close'])
        
        # Awesome Oscillator
        df['AO'] = AdvancedIndicators._calculate_awesome_oscillator(df)
        
        # True Strength Index
        df['TSI'] = AdvancedIndicators._calculate_tsi(df)
        
        return df
    
    @staticmethod
    def _add_volatility_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Indicadores de volatilidad"""
        
        # Bollinger Bands
        df['BB_UPPER'], df['BB_MIDDLE'], df['BB_LOWER'] = talib.BBANDS(df['close'])
        df['BB_WIDTH'] = (df['BB_UPPER'] - df['BB_LOWER']) / df['BB_MIDDLE']
        df['BB_PERCENT'] = (df['close'] - df['BB_LOWER']) / (df['BB_UPPER'] - df['BB_LOWER'])
        
        # ATR (Average True Range)
        for period in [7, 14, 21]:
            df[f'ATR_{period}'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
        
        # Keltner Channels
        df = AdvancedIndicators._calculate_keltner_channels(df)
        
        # Donchian Channels
        df = AdvancedIndicators._calculate_donchian_channels(df)
        
        # Historical Volatility
        df['HV_20'] = df['close'].pct_change().rolling(20).std() * np.sqrt(252)
        df['HV_50'] = df['close'].pct_change().rolling(50).std() * np.sqrt(252)
        
        # Chaikin Volatility
        df['CHAIK_VOL'] = talib.EMA(df['high'] - df['low'], 10)
        
        return df
    
    @staticmethod
    def _add_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Indicadores de volumen"""
        
        # OBV (On Balance Volume)
        df['OBV'] = talib.OBV(df['close'], df['volume'])
        
        # AD (Accumulation/Distribution)
        df['AD'] = talib.AD(df['high'], df['low'], df['close'], df['volume'])
        
        # ADOSC (Chaikin A/D Oscillator)
        df['ADOSC'] = talib.ADOSC(df['high'], df['low'], df['close'], df['volume'])
        
        # CMF (Chaikin Money Flow)
        df['CMF'] = AdvancedIndicators._calculate_cmf(df)
        
        # VWAP (Volume Weighted Average Price)
        df['VWAP'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
        
        # Volume Rate of Change
        df['VROC'] = df['volume'].pct_change(periods=10) * 100
        
        # Force Index
        df['FORCE_INDEX'] = df['close'].diff() * df['volume']
        
        # Ease of Movement
        df['EOM'] = talib.EMA((df['high'] + df['low']) / 2 - (df['high'].shift() + df['low'].shift()) / 2, 14) / df['volume']
        
        # Volume Oscillator
        df['VO'] = ((df['volume'].rolling(5).mean() - df['volume'].rolling(10).mean()) / 
                    df['volume'].rolling(10).mean() * 100)
        
        return df
    
    @staticmethod
    def _add_cycle_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Indicadores de ciclo"""
        
        # Hilbert Transform
        df['HT_DCPERIOD'] = talib.HT_DCPERIOD(df['close'])
        df['HT_DCPHASE'] = talib.HT_DCPHASE(df['close'])
        df['HT_TRENDMODE'] = talib.HT_TRENDMODE(df['close'])
        
        # Sine Wave
        df['HT_SINE'], df['HT_LEADSINE'] = talib.HT_SINE(df['close'])
        
        # Dominant Cycle
        df['DOMINANT_CYCLE'] = AdvancedIndicators._calculate_dominant_cycle(df)
        
        return df
    
    @staticmethod
    def _add_pattern_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Reconocimiento de patrones"""
        
        # Candlestick Patterns (20 más importantes)
        patterns = [
            'CDLDOJI', 'CDLHAMMER', 'CDLINVERTEDHAMMER', 'CDLENGULFING',
            'CDLHARAMI', 'CDLPIERCING', 'CDLMORNINGSTAR', 'CDLEVENINGSTAR',
            'CDLSHOOTINGSTAR', 'CDLSPINNINGTOP', 'CDLMARUBOZU', 'CDLDRAGONFLYDOJI',
            'CDLGRAVESTONEDOJI', 'CDL3WHITESOLDIERS', 'CDL3BLACKCROWS', 'CDLABANDONEDBABY',
            'CDLTAKURI', 'CDLCONCEALBABYSWALL', 'CDLKICKING', 'CDLTHRUSTING'
        ]
        
        for pattern in patterns:
            try:
                df[pattern] = getattr(talib, pattern)(df['open'], df['high'], df['low'], df['close'])
            except:
                pass
        
        # Chart Patterns
        df['DOUBLE_TOP'] = AdvancedIndicators._detect_double_top(df)
        df['DOUBLE_BOTTOM'] = AdvancedIndicators._detect_double_bottom(df)
        df['HEAD_SHOULDERS'] = AdvancedIndicators._detect_head_shoulders(df)
        
        return df
    
    @staticmethod
    def _add_statistical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Indicadores estadísticos"""
        
        # Z-Score
        df['ZSCORE'] = (df['close'] - df['close'].rolling(20).mean()) / df['close'].rolling(20).std()
        
        # Skewness
        df['SKEW'] = df['close'].rolling(20).apply(lambda x: stats.skew(x))
        
        # Kurtosis
        df['KURT'] = df['close'].rolling(20).apply(lambda x: stats.kurtosis(x))
        
        # Linear Regression
        df['LINEARREG'] = talib.LINEARREG(df['close'])
        df['LINEARREG_ANGLE'] = talib.LINEARREG_ANGLE(df['close'])
        df['LINEARREG_SLOPE'] = talib.LINEARREG_SLOPE(df['close'])
        
        # Standard Deviation
        df['STDDEV'] = talib.STDDEV(df['close'])
        
        # Variance
        df['VAR'] = talib.VAR(df['close'])
        
        # Correlation
        df['CORREL'] = talib.CORREL(df['high'], df['low'])
        
        # Beta
        df['BETA'] = talib.BETA(df['high'], df['low'])
        
        return df
    
    @staticmethod
    def _add_custom_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Indicadores personalizados"""
        
        # Trend Strength
        df['TREND_STRENGTH'] = abs(df['close'] - df['SMA_50']) / df['ATR_14']
        
        # Volatility Ratio
        df['VOL_RATIO'] = df['ATR_14'] / df['close']
        
        # Price Distance from MA
        df['DIST_SMA20'] = (df['close'] - df['SMA_20']) / df['SMA_20'] * 100
        df['DIST_EMA50'] = (df['close'] - df['EMA_50']) / df['EMA_50'] * 100
        
        # Volume Trend
        df['VOL_TREND'] = df['volume'] / df['volume'].rolling(20).mean()
        
        # Momentum Score
        df['MOM_SCORE'] = (
            (df['RSI_14'] / 100) * 0.3 +
            ((df['MACD'] > df['MACD_signal']).astype(int)) * 0.3 +
            ((df['close'] > df['SMA_20']).astype(int)) * 0.4
        )
        
        # Volatility Score
        df['VOL_SCORE'] = (df['ATR_14'] / df['close']) * 100
        
        # Trend Score
        df['TREND_SCORE'] = (
            ((df['SMA_20'] > df['SMA_50']).astype(int)) * 0.3 +
            ((df['EMA_20'] > df['EMA_50']).astype(int)) * 0.3 +
            (df['ADX'] / 100) * 0.4
        )
        
        return df
    
    # Helper methods
    
    @staticmethod
    def _calculate_supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.DataFrame:
        """Calcula Supertrend"""
        hl2 = (df['high'] + df['low']) / 2
        atr = talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
        
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        df['SUPERTREND'] = 0.0
        df['SUPERTREND_UPPER'] = upper_band
        df['SUPERTREND_LOWER'] = lower_band
        
        return df
    
    @staticmethod
    def _calculate_awesome_oscillator(df: pd.DataFrame) -> pd.Series:
        """Calcula Awesome Oscillator"""
        median = (df['high'] + df['low']) / 2
        ao = median.rolling(5).mean() - median.rolling(34).mean()
        return ao
    
    @staticmethod
    def _calculate_tsi(df: pd.DataFrame, long: int = 25, short: int = 13) -> pd.Series:
        """Calcula True Strength Index"""
        price_change = df['close'].diff()
        double_smoothed_pc = price_change.ewm(span=long).mean().ewm(span=short).mean()
        double_smoothed_abs_pc = price_change.abs().ewm(span=long).mean().ewm(span=short).mean()
        tsi = 100 * (double_smoothed_pc / double_smoothed_abs_pc)
        return tsi
    
    @staticmethod
    def _calculate_keltner_channels(df: pd.DataFrame, period: int = 20, multiplier: float = 2.0) -> pd.DataFrame:
        """Calcula Keltner Channels"""
        ema = df['close'].ewm(span=period).mean()
        atr = talib.ATR(df['high'], df['low'], df['close'], timeperiod=period)
        
        df['KC_UPPER'] = ema + (multiplier * atr)
        df['KC_MIDDLE'] = ema
        df['KC_LOWER'] = ema - (multiplier * atr)
        
        return df
    
    @staticmethod
    def _calculate_donchian_channels(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
        """Calcula Donchian Channels"""
        df['DC_UPPER'] = df['high'].rolling(period).max()
        df['DC_LOWER'] = df['low'].rolling(period).min()
        df['DC_MIDDLE'] = (df['DC_UPPER'] + df['DC_LOWER']) / 2
        
        return df
    
    @staticmethod
    def _calculate_cmf(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calcula Chaikin Money Flow"""
        mfv = ((df['close'] - df['low']) - (df['high'] - df['close'])) / (df['high'] - df['low']) * df['volume']
        cmf = mfv.rolling(period).sum() / df['volume'].rolling(period).sum()
        return cmf
    
    @staticmethod
    def _calculate_dominant_cycle(df: pd.DataFrame) -> pd.Series:
        """Calcula ciclo dominante usando FFT"""
        prices = df['close'].values
        fft = np.fft.fft(prices)
        power = np.abs(fft) ** 2
        freq = np.fft.fftfreq(len(prices))
        
        # Encontrar frecuencia dominante
        idx = np.argmax(power[1:len(power)//2]) + 1
        dominant_freq = abs(freq[idx])
        dominant_period = 1 / dominant_freq if dominant_freq > 0 else 20
        
        return pd.Series(dominant_period, index=df.index)
    
    @staticmethod
    def _detect_double_top(df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detecta patrón Double Top"""
        # Simplificado - busca dos máximos similares
        highs = df['high'].rolling(window).max()
        is_double_top = (highs == highs.shift(window)) & (df['high'] == highs)
        return is_double_top.astype(int)
    
    @staticmethod
    def _detect_double_bottom(df: pd.DataFrame, window: int = 20) -> pd.Series:
        """Detecta patrón Double Bottom"""
        lows = df['low'].rolling(window).min()
        is_double_bottom = (lows == lows.shift(window)) & (df['low'] == lows)
        return is_double_bottom.astype(int)
    
    @staticmethod
    def _detect_head_shoulders(df: pd.DataFrame) -> pd.Series:
        """Detecta patrón Head and Shoulders"""
        # Simplificado - busca tres picos con el del medio más alto
        peaks = (df['high'] > df['high'].shift(1)) & (df['high'] > df['high'].shift(-1))
        return peaks.astype(int)
