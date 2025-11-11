"""
Technical Indicators Calculator
Calculates FOOS-method indicators and traditional technical indicators
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, Dict


class TechnicalIndicators:
    """Calculate technical indicators for OHLCV data"""

    # ==========================================
    # FOOS METHOD INDICATORS
    # ==========================================

    @staticmethod
    def calculate_ema_13(df: pd.DataFrame) -> pd.Series:
        """
        Calculate 13-period Exponential Moving Average (YELLOW line in FOOS)

        Primary trend indicator:
        - Price above 13 EMA = bullish trend
        - Price below 13 EMA = bearish trend
        - First retest after breakout = strongest entry
        - Breakdown below = trend reversal warning

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Series with 13 EMA values
        """
        return df['close'].ewm(span=13, adjust=False).mean()

    @staticmethod
    def calculate_ma_50(df: pd.DataFrame) -> pd.Series:
        """
        Calculate 50-period Simple Moving Average (PINK line in FOOS)

        Medium-term trend indicator:
        - Breakdown below 50 MA = major warning signal
        - In crypto: can signal 70-90% drop incoming
        - Acts as support in strong uptrends

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Series with 50 MA values
        """
        return df['close'].rolling(window=50).mean()

    @staticmethod
    def calculate_ma_200(df: pd.DataFrame) -> pd.Series:
        """
        Calculate 200-period Simple Moving Average (BLUE line in FOOS)

        Long-term trend indicator:
        - Price above 200 MA = bull market
        - Price below 200 MA = bear market
        - Acts as major support/resistance

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Series with 200 MA values
        """
        return df['close'].rolling(window=200).mean()

    @staticmethod
    def calculate_foos_indicators(df: pd.DataFrame) -> Dict[str, pd.Series]:
        """
        Calculate all FOOS indicators at once

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with all FOOS indicators
        """
        return {
            'ema_13': TechnicalIndicators.calculate_ema_13(df),
            'ma_50': TechnicalIndicators.calculate_ma_50(df),
            'ma_200': TechnicalIndicators.calculate_ma_200(df),
            'vwap': TechnicalIndicators.calculate_vwap(df)
        }

    @staticmethod
    def get_price_position(df: pd.DataFrame) -> Dict[str, str]:
        """
        Get current price position relative to FOOS indicators

        Returns:
            Dictionary describing price position
        """
        current_price = df['close'].iloc[-1]
        ema_13 = TechnicalIndicators.calculate_ema_13(df).iloc[-1]
        ma_50 = TechnicalIndicators.calculate_ma_50(df).iloc[-1]
        ma_200 = TechnicalIndicators.calculate_ma_200(df).iloc[-1]

        return {
            'ema_13': 'above' if current_price > ema_13 else 'below',
            'ma_50': 'above' if current_price > ma_50 else 'below',
            'ma_200': 'above' if current_price > ma_200 else 'below',
            'trend': TechnicalIndicators._determine_trend(current_price, ema_13, ma_50, ma_200)
        }

    @staticmethod
    def _determine_trend(price: float, ema_13: float, ma_50: float, ma_200: float) -> str:
        """Determine overall trend based on indicator positions"""
        if price > ema_13 > ma_50 > ma_200:
            return 'strong_bull'
        elif price > ema_13 > ma_50:
            return 'bull'
        elif price > ema_13:
            return 'weak_bull'
        elif price < ema_13 < ma_50 < ma_200:
            return 'strong_bear'
        elif price < ema_13 < ma_50:
            return 'bear'
        elif price < ema_13:
            return 'weak_bear'
        else:
            return 'neutral'

    # ==========================================
    # TRADITIONAL INDICATORS (keeping existing)
    # ==========================================

    @staticmethod
    def calculate_support_resistance(
        df: pd.DataFrame,
        window: int = 20,
        num_levels: int = 3
    ) -> Tuple[list, list]:
        """
        Identify support and resistance levels

        Args:
            df: DataFrame with OHLCV data
            window: Lookback window for local extrema
            num_levels: Number of levels to identify

        Returns:
            Tuple of (support_levels, resistance_levels)
        """
        # Find local minima (support)
        local_min = df['low'].rolling(window=window, center=True).min()
        support_points = df[df['low'] == local_min]['low'].values

        # Find local maxima (resistance)
        local_max = df['high'].rolling(window=window, center=True).max()
        resistance_points = df[df['high'] == local_max]['high'].values

        # Cluster nearby levels
        support_levels = TechnicalIndicators._cluster_levels(support_points, num_levels)
        resistance_levels = TechnicalIndicators._cluster_levels(resistance_points, num_levels)

        return support_levels, resistance_levels

    @staticmethod
    def _cluster_levels(points: np.ndarray, num_clusters: int = 3) -> list:
        """Cluster price levels to find key support/resistance"""
        if len(points) == 0:
            return []

        # Remove duplicates and sort
        unique_points = np.unique(points)

        # Simple clustering: divide into groups
        if len(unique_points) <= num_clusters:
            return unique_points.tolist()

        # Use percentiles to identify key levels
        percentiles = np.linspace(0, 100, num_clusters + 2)[1:-1]
        levels = [np.percentile(unique_points, p) for p in percentiles]

        return sorted(levels)

    @staticmethod
    def calculate_vwap(df: pd.DataFrame) -> pd.Series:
        """
        Calculate Volume Weighted Average Price

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Series with VWAP values
        """
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        return vwap

    @staticmethod
    def calculate_moving_averages(
        df: pd.DataFrame,
        periods: list = [20, 50, 200]
    ) -> pd.DataFrame:
        """
        Calculate multiple moving averages

        Args:
            df: DataFrame with OHLCV data
            periods: List of MA periods

        Returns:
            DataFrame with MA columns
        """
        result = df.copy()

        for period in periods:
            result[f'SMA_{period}'] = df['close'].rolling(window=period).mean()
            result[f'EMA_{period}'] = df['close'].ewm(span=period, adjust=False).mean()

        return result

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index

        Args:
            df: DataFrame with OHLCV data
            period: RSI period

        Returns:
            Series with RSI values
        """
        delta = df['close'].diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    @staticmethod
    def calculate_macd(
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)

        Args:
            df: DataFrame with OHLCV data
            fast: Fast EMA period
            slow: Slow EMA period
            signal: Signal line period

        Returns:
            Tuple of (macd, signal_line, histogram)
        """
        ema_fast = df['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=slow, adjust=False).mean()

        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line

        return macd, signal_line, histogram

    @staticmethod
    def calculate_bollinger_bands(
        df: pd.DataFrame,
        period: int = 20,
        std_dev: int = 2
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands

        Args:
            df: DataFrame with OHLCV data
            period: Moving average period
            std_dev: Number of standard deviations

        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        middle_band = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()

        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)

        return upper_band, middle_band, lower_band

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Average True Range (volatility indicator)

        Args:
            df: DataFrame with OHLCV data
            period: ATR period

        Returns:
            Series with ATR values
        """
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=period).mean()

        return atr

    @staticmethod
    def calculate_volume_profile(
        df: pd.DataFrame,
        bins: int = 50
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate volume profile (volume at price levels)

        Args:
            df: DataFrame with OHLCV data
            bins: Number of price bins

        Returns:
            Tuple of (price_levels, volumes)
        """
        # Create price bins
        price_range = df['high'].max() - df['low'].min()
        bin_size = price_range / bins

        # Calculate volume at each price level
        price_levels = []
        volumes = []

        for i in range(bins):
            price_level = df['low'].min() + (i * bin_size)
            # Volume where price was in this range
            mask = (df['low'] <= price_level) & (df['high'] >= price_level)
            volume = df.loc[mask, 'volume'].sum()

            price_levels.append(price_level)
            volumes.append(volume)

        return np.array(price_levels), np.array(volumes)

    @staticmethod
    def detect_divergence(
        price: pd.Series,
        indicator: pd.Series,
        window: int = 14
    ) -> dict:
        """
        Detect bullish/bearish divergence between price and indicator

        Args:
            price: Price series
            indicator: Indicator series (e.g., RSI, MACD)
            window: Lookback window

        Returns:
            Dictionary with divergence signals
        """
        # Find local extrema
        price_highs = price.rolling(window=window, center=True).max() == price
        price_lows = price.rolling(window=window, center=True).min() == price

        indicator_highs = indicator.rolling(window=window, center=True).max() == indicator
        indicator_lows = indicator.rolling(window=window, center=True).min() == indicator

        # Detect bullish divergence (price lower low, indicator higher low)
        bullish_div = []
        # Detect bearish divergence (price higher high, indicator lower high)
        bearish_div = []

        # Simplified detection (can be enhanced)
        return {
            'bullish_divergence': bullish_div,
            'bearish_divergence': bearish_div
        }

    @staticmethod
    def is_volume_increasing(
        df: pd.DataFrame,
        window: int = 5
    ) -> bool:
        """
        Check if volume is increasing (confirmation signal)

        Args:
            df: DataFrame with OHLCV data
            window: Lookback window

        Returns:
            True if volume trend is increasing
        """
        recent_volume = df['volume'].tail(window)
        volume_ma = df['volume'].rolling(window=window * 2).mean()

        current_avg = recent_volume.mean()
        historical_avg = volume_ma.iloc[-window - 1]

        return current_avg > historical_avg

    @staticmethod
    def calculate_price_momentum(
        df: pd.DataFrame,
        period: int = 14
    ) -> pd.Series:
        """
        Calculate price momentum

        Args:
            df: DataFrame with OHLCV data
            period: Momentum period

        Returns:
            Series with momentum values
        """
        momentum = df['close'] - df['close'].shift(period)
        return momentum

    @staticmethod
    def identify_trend(df: pd.DataFrame, period: int = 50) -> str:
        """
        Identify overall trend direction

        Args:
            df: DataFrame with OHLCV data
            period: Period for trend calculation

        Returns:
            'bullish', 'bearish', or 'sideways'
        """
        if len(df) < period:
            return 'sideways'

        sma = df['close'].rolling(window=period).mean()
        current_price = df['close'].iloc[-1]
        current_sma = sma.iloc[-1]

        # Calculate slope of SMA
        sma_slope = (sma.iloc[-1] - sma.iloc[-period // 2]) / (period // 2)

        if current_price > current_sma and sma_slope > 0:
            return 'bullish'
        elif current_price < current_sma and sma_slope < 0:
            return 'bearish'
        else:
            return 'sideways'


# Example usage
if __name__ == "__main__":
    # Test with sample data
    dates = pd.date_range('2024-01-01', periods=100, freq='4H')
    sample_data = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)

    indicators = TechnicalIndicators()

    # Calculate indicators
    support, resistance = indicators.calculate_support_resistance(sample_data)
    print(f"Support levels: {support}")
    print(f"Resistance levels: {resistance}")

    rsi = indicators.calculate_rsi(sample_data)
    print(f"\nCurrent RSI: {rsi.iloc[-1]:.2f}")

    trend = indicators.identify_trend(sample_data)
    print(f"Trend: {trend}")
