"""
Technical analysis module for stock price indicators.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict


class TechnicalAnalyzer:
    """Performs technical analysis on stock data."""
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize technical analyzer.
        
        Args:
            data: DataFrame with historical price data (OHLCV)
        """
        self.data = data
        self.score = 0.0
    
    def calculate_sma(self, window: int) -> pd.Series:
        """Calculate Simple Moving Average."""
        return self.data['Close'].rolling(window=window).mean()
    
    def calculate_ema(self, window: int) -> pd.Series:
        """Calculate Exponential Moving Average."""
        return self.data['Close'].ewm(span=window, adjust=False).mean()
    
    def calculate_rsi(self, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index.
        
        Args:
            period: RSI period (default 14)
            
        Returns:
            Series with RSI values
        """
        delta = self.data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Avoid division by zero
        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_macd(self) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate MACD and Signal line.
        
        Returns:
            Tuple of (MACD line, Signal line)
        """
        ema_12 = self.calculate_ema(12)
        ema_26 = self.calculate_ema(26)
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()
        
        return macd, signal
    
    def calculate_bollinger_bands(self, window: int = 20, num_std: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.
        
        Args:
            window: Moving average window
            num_std: Number of standard deviations
            
        Returns:
            Tuple of (upper band, middle band, lower band)
        """
        sma = self.calculate_sma(window)
        std = self.data['Close'].rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return upper_band, sma, lower_band
    
    def analyze_trend(self) -> Tuple[List[Tuple[str, float, str]], float]:
        """
        Analyze price trend using moving averages.
        
        Returns:
            Tuple of (signals list, score)
        """
        signals = []
        score = 0.0
        
        try:
            sma_50 = self.calculate_sma(50)
            sma_200 = self.calculate_sma(200)
            
            if len(sma_50.dropna()) < 1 or len(sma_200.dropna()) < 1:
                signals.append(("Données insuffisantes pour l'analyse de tendance", 0, "Neutre"))
                return signals, score
            
            current_price = self.data['Close'].iloc[-1]
            current_sma_50 = sma_50.iloc[-1]
            current_sma_200 = sma_200.iloc[-1]
            
            # Golden Cross / Death Cross
            if current_sma_50 > current_sma_200:
                signals.append(("Golden Cross détecté (SMA50 > SMA200)", 2, "Haussier"))
                score += 2
            else:
                signals.append(("Death Cross détecté (SMA50 < SMA200)", -2, "Baissier"))
                score -= 2
            
            # Price position relative to moving averages
            if current_price > current_sma_50 > current_sma_200:
                signals.append(("Prix au-dessus des 2 moyennes mobiles", 1, "Haussier"))
                score += 1
            elif current_price < current_sma_50 < current_sma_200:
                signals.append(("Prix en-dessous des 2 moyennes mobiles", -1, "Baissier"))
                score -= 1
            
        except Exception as e:
            signals.append((f"Erreur analyse tendance: {str(e)[:50]}", 0, "Neutre"))
        
        return signals, score
    
    def analyze_momentum(self) -> Tuple[List[Tuple[str, float, str]], float]:
        """
        Analyze momentum using RSI.
        
        Returns:
            Tuple of (signals list, score)
        """
        signals = []
        score = 0.0
        
        try:
            rsi = self.calculate_rsi()
            
            if len(rsi.dropna()) < 1:
                signals.append(("Données insuffisantes pour le RSI", 0, "Neutre"))
                return signals, score
            
            current_rsi = rsi.iloc[-1]
            
            if pd.isna(current_rsi):
                signals.append(("RSI non calculable", 0, "Neutre"))
                return signals, score
            
            if current_rsi < 30:
                signals.append((f"RSI à {current_rsi:.2f} - Survente", 2, "Haussier"))
                score += 2
            elif current_rsi > 70:
                signals.append((f"RSI à {current_rsi:.2f} - Surachat", -2, "Baissier"))
                score -= 2
            elif 40 <= current_rsi <= 60:
                signals.append((f"RSI à {current_rsi:.2f} - Neutre", 0, "Neutre"))
            else:
                signals.append((f"RSI à {current_rsi:.2f}", 0, "Neutre"))
            
        except Exception as e:
            signals.append((f"Erreur analyse RSI: {str(e)[:50]}", 0, "Neutre"))
        
        return signals, score
    
    def analyze_macd_signal(self) -> Tuple[List[Tuple[str, float, str]], float]:
        """
        Analyze MACD signals.
        
        Returns:
            Tuple of (signals list, score)
        """
        signals = []
        score = 0.0
        
        try:
            macd, signal_line = self.calculate_macd()
            
            if len(macd.dropna()) < 2 or len(signal_line.dropna()) < 2:
                signals.append(("Données insuffisantes pour le MACD", 0, "Neutre"))
                return signals, score
            
            current_macd = macd.iloc[-1]
            current_signal = signal_line.iloc[-1]
            prev_macd = macd.iloc[-2]
            prev_signal = signal_line.iloc[-2]
            
            if any(pd.isna([current_macd, current_signal, prev_macd, prev_signal])):
                signals.append(("MACD non calculable", 0, "Neutre"))
                return signals, score
            
            # Bullish crossover
            if prev_macd < prev_signal and current_macd > current_signal:
                signals.append(("MACD croisement haussier", 2, "Haussier"))
                score += 2
            # Bearish crossover
            elif prev_macd > prev_signal and current_macd < current_signal:
                signals.append(("MACD croisement baissier", -2, "Baissier"))
                score -= 2
            elif current_macd > current_signal:
                signals.append(("MACD au-dessus du signal", 1, "Haussier"))
                score += 1
            else:
                signals.append(("MACD en-dessous du signal", -1, "Baissier"))
                score -= 1
            
        except Exception as e:
            signals.append((f"Erreur analyse MACD: {str(e)[:50]}", 0, "Neutre"))
        
        return signals, score
    
    def analyze_bollinger(self) -> Tuple[List[Tuple[str, float, str]], float]:
        """
        Analyze Bollinger Bands.
        
        Returns:
            Tuple of (signals list, score)
        """
        signals = []
        score = 0.0
        
        try:
            upper, middle, lower = self.calculate_bollinger_bands()
            
            if len(upper.dropna()) < 1:
                signals.append(("Données insuffisantes pour Bollinger", 0, "Neutre"))
                return signals, score
            
            current_price = self.data['Close'].iloc[-1]
            current_upper = upper.iloc[-1]
            current_lower = lower.iloc[-1]
            
            if any(pd.isna([current_upper, current_lower])):
                signals.append(("Bandes de Bollinger non calculables", 0, "Neutre"))
                return signals, score
            
            if current_price <= current_lower:
                signals.append(("Prix touche la bande inférieure", 1, "Haussier"))
                score += 1
            elif current_price >= current_upper:
                signals.append(("Prix touche la bande supérieure", -1, "Baissier"))
                score -= 1
            else:
                signals.append(("Prix dans les bandes normales", 0, "Neutre"))
            
        except Exception as e:
            signals.append((f"Erreur analyse Bollinger: {str(e)[:50]}", 0, "Neutre"))
        
        return signals, score
    
    def analyze_volume(self) -> Tuple[List[Tuple[str, float, str]], float]:
        """
        Analyze trading volume.
        
        Returns:
            Tuple of (signals list, score)
        """
        signals = []
        score = 0.0
        
        try:
            if 'Volume' not in self.data.columns or len(self.data) < 20:
                signals.append(("Données de volume insuffisantes", 0, "Neutre"))
                return signals, score
            
            avg_volume = self.data['Volume'].tail(20).mean()
            recent_volume = self.data['Volume'].iloc[-1]
            
            if pd.isna(avg_volume) or pd.isna(recent_volume) or avg_volume == 0:
                signals.append(("Volume non disponible", 0, "Neutre"))
                return signals, score
            
            if recent_volume > avg_volume * 1.5:
                signals.append(("Volume anormalement élevé", 1, "Attention"))
                score += 0.5
            elif recent_volume < avg_volume * 0.5:
                signals.append(("Volume anormalement faible", 0, "Prudence"))
            else:
                signals.append(("Volume normal", 0, "Neutre"))
            
        except Exception as e:
            signals.append((f"Erreur analyse volume: {str(e)[:50]}", 0, "Neutre"))
        
        return signals, score
    
    def full_technical_analysis(self) -> Tuple[List[Tuple[str, float, str]], float]:
        """
        Perform complete technical analysis.
        
        Returns:
            Tuple of (all signals, total score)
        """
        all_signals = []
        total_score = 0.0
        
        # Trend analysis
        trend_signals, trend_score = self.analyze_trend()
        all_signals.extend(trend_signals)
        total_score += trend_score
        
        # Momentum analysis
        momentum_signals, momentum_score = self.analyze_momentum()
        all_signals.extend(momentum_signals)
        total_score += momentum_score
        
        # MACD analysis
        macd_signals, macd_score = self.analyze_macd_signal()
        all_signals.extend(macd_signals)
        total_score += macd_score
        
        # Bollinger analysis
        bollinger_signals, bollinger_score = self.analyze_bollinger()
        all_signals.extend(bollinger_signals)
        total_score += bollinger_score
        
        # Volume analysis
        volume_signals, volume_score = self.analyze_volume()
        all_signals.extend(volume_signals)
        total_score += volume_score
        
        return all_signals, total_score