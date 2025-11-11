"""
FOOS4 Pattern Recognition System
Identifies institutional trading patterns based on FOOS4 methodology
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from wolf_analyzer.analysis.technical_indicators import TechnicalIndicators


@dataclass
class Pattern:
    """Pattern detection result"""
    pattern_type: str
    confidence: float
    entry_zone: Tuple[float, float]
    stop_loss: float
    targets: List[float]
    risk_reward: float
    formation_time: int  # hours
    description: str
    key_levels: Dict[str, float]
    volume_confirmation: bool
    institutional_signal: bool


class PatternRecognition:
    """
    FOOS4 Pattern Recognition Engine
    Identifies key trading patterns used by institutional traders
    """

    def __init__(self, min_confidence: float = 0.65):
        """
        Initialize pattern recognition

        Args:
            min_confidence: Minimum confidence threshold (0.0-1.0)
        """
        self.min_confidence = min_confidence
        self.indicators = TechnicalIndicators()

    def analyze_chart(self, df: pd.DataFrame, symbol: str) -> List[Pattern]:
        """
        Analyze chart and identify all patterns

        Args:
            df: DataFrame with OHLCV data
            symbol: Trading pair symbol

        Returns:
            List of detected patterns
        """
        patterns = []

        # Check for each pattern type
        patterns.extend(self._detect_ascending_triangle(df))
        patterns.extend(self._detect_descending_triangle(df))
        patterns.extend(self._detect_support_break(df))
        patterns.extend(self._detect_resistance_break(df))
        patterns.extend(self._detect_falling_wedge(df))
        patterns.extend(self._detect_rising_wedge(df))

        # Filter by confidence
        patterns = [p for p in patterns if p.confidence >= self.min_confidence]

        # Sort by confidence
        patterns.sort(key=lambda x: x.confidence, reverse=True)

        return patterns

    def _detect_ascending_triangle(self, df: pd.DataFrame) -> List[Pattern]:
        """
        Detect ascending triangle pattern (bullish)

        Characteristics:
        - Flat upper resistance
        - Rising lower support
        - Decreasing volume into apex
        - Bullish breakout expected
        """
        patterns = []

        if len(df) < 50:
            return patterns

        # Get recent data (last 50 candles)
        recent = df.tail(50)

        # Identify resistance level (flat top)
        resistance_highs = recent['high'].tail(20)
        resistance_level = resistance_highs.max()
        resistance_touches = len(resistance_highs[resistance_highs >= resistance_level * 0.995])

        # Identify support (rising lows)
        support_lows = recent['low'].tail(20)
        support_slope = self._calculate_trendline_slope(support_lows)

        # Check for ascending triangle conditions
        if resistance_touches >= 2 and support_slope > 0:
            # Calculate confidence
            confidence = self._calculate_pattern_confidence(
                resistance_touches=resistance_touches,
                support_slope=support_slope,
                volume_decreasing=self._is_volume_decreasing(recent),
                time_in_pattern=len(recent)
            )

            # Calculate entry/exit levels
            current_price = df['close'].iloc[-1]
            entry_low = current_price * 0.998
            entry_high = resistance_level * 0.999

            stop_loss = support_lows.min() * 0.995

            # Targets based on triangle height
            pattern_height = resistance_level - support_lows.min()
            target1 = resistance_level + (pattern_height * 0.5)
            target2 = resistance_level + (pattern_height * 1.0)
            target3 = resistance_level + (pattern_height * 1.5)

            # Risk:Reward
            risk = entry_high - stop_loss
            reward = target2 - entry_high
            risk_reward = reward / risk if risk > 0 else 0

            if risk_reward >= 2.0:  # Minimum 2:1 R:R
                # Calculate trendline points for rising support
                support_start = support_lows.iloc[0]
                support_end = support_lows.iloc[-1]

                pattern = Pattern(
                    pattern_type="Ascending Triangle",
                    confidence=confidence,
                    entry_zone=(entry_low, entry_high),
                    stop_loss=stop_loss,
                    targets=[target1, target2, target3],
                    risk_reward=risk_reward,
                    formation_time=len(recent) * 4,  # assuming 4h candles
                    description="Bullish continuation pattern with flat resistance and rising support",
                    key_levels={
                        'resistance': resistance_level,
                        'support': support_lows.min(),
                        'support_start': support_start,
                        'support_end': support_end,
                        'current_price': current_price
                    },
                    volume_confirmation=self._is_volume_decreasing(recent),
                    institutional_signal=True
                )
                patterns.append(pattern)

        return patterns

    def _detect_descending_triangle(self, df: pd.DataFrame) -> List[Pattern]:
        """
        Detect descending triangle pattern (bearish)

        Characteristics:
        - Flat lower support
        - Descending upper resistance
        - Decreasing volume into apex
        - Bearish breakdown expected
        """
        patterns = []

        if len(df) < 50:
            return patterns

        recent = df.tail(50)

        # Identify support level (flat bottom)
        support_lows = recent['low'].tail(20)
        support_level = support_lows.min()
        support_touches = len(support_lows[support_lows <= support_level * 1.005])

        # Identify resistance (descending highs)
        resistance_highs = recent['high'].tail(20)
        resistance_slope = self._calculate_trendline_slope(resistance_highs)

        # Check for descending triangle conditions
        if support_touches >= 2 and resistance_slope < 0:
            confidence = self._calculate_pattern_confidence(
                resistance_touches=support_touches,
                support_slope=abs(resistance_slope),
                volume_decreasing=self._is_volume_decreasing(recent),
                time_in_pattern=len(recent)
            )

            current_price = df['close'].iloc[-1]
            entry_low = support_level * 1.001
            entry_high = current_price * 1.002

            stop_loss = resistance_highs.max() * 1.005

            # Targets based on triangle height
            pattern_height = resistance_highs.max() - support_level
            target1 = support_level - (pattern_height * 0.5)
            target2 = support_level - (pattern_height * 1.0)
            target3 = support_level - (pattern_height * 1.5)

            risk = stop_loss - entry_low
            reward = entry_low - target2
            risk_reward = reward / risk if risk > 0 else 0

            if risk_reward >= 2.0:
                # Calculate trendline points for falling resistance
                resistance_start = resistance_highs.iloc[0]
                resistance_end = resistance_highs.iloc[-1]

                pattern = Pattern(
                    pattern_type="Descending Triangle",
                    confidence=confidence,
                    entry_zone=(entry_low, entry_high),
                    stop_loss=stop_loss,
                    targets=[target1, target2, target3],
                    risk_reward=risk_reward,
                    formation_time=len(recent) * 4,
                    description="Bearish continuation pattern with flat support and descending resistance",
                    key_levels={
                        'support': support_level,
                        'resistance': resistance_highs.max(),
                        'resistance_start': resistance_start,
                        'resistance_end': resistance_end,
                        'current_price': current_price
                    },
                    volume_confirmation=self._is_volume_decreasing(recent),
                    institutional_signal=True
                )
                patterns.append(pattern)

        return patterns

    def _detect_support_break(self, df: pd.DataFrame) -> List[Pattern]:
        """Detect support level breaks (bearish)"""
        patterns = []

        if len(df) < 30:
            return patterns

        # Identify support levels
        support_levels, _ = self.indicators.calculate_support_resistance(df, window=20, num_levels=3)

        if not support_levels:
            return patterns

        current_price = df['close'].iloc[-1]
        recent_low = df['low'].tail(5).min()

        # Check if price is breaking support
        for support in support_levels:
            if recent_low <= support * 1.01 and current_price < support:
                # Potential support break
                confidence = 0.7  # Base confidence

                # Increase confidence with volume
                if self.indicators.is_volume_increasing(df):
                    confidence += 0.15

                pattern = Pattern(
                    pattern_type="Support Break",
                    confidence=confidence,
                    entry_zone=(support * 0.995, support * 1.0),
                    stop_loss=support * 1.02,
                    targets=[support * 0.97, support * 0.94, support * 0.90],
                    risk_reward=2.5,
                    formation_time=10,
                    description="Price breaking key support level with volume",
                    key_levels={'support': support, 'current_price': current_price},
                    volume_confirmation=self.indicators.is_volume_increasing(df),
                    institutional_signal=True
                )
                patterns.append(pattern)
                break  # Only detect closest support

        return patterns

    def _detect_resistance_break(self, df: pd.DataFrame) -> List[Pattern]:
        """Detect resistance level breaks (bullish)"""
        patterns = []

        if len(df) < 30:
            return patterns

        # Identify resistance levels
        _, resistance_levels = self.indicators.calculate_support_resistance(df, window=20, num_levels=3)

        if not resistance_levels:
            return patterns

        current_price = df['close'].iloc[-1]
        recent_high = df['high'].tail(5).max()

        # Check if price is breaking resistance
        for resistance in resistance_levels:
            if recent_high >= resistance * 0.99 and current_price > resistance:
                confidence = 0.7

                if self.indicators.is_volume_increasing(df):
                    confidence += 0.15

                pattern = Pattern(
                    pattern_type="Resistance Break",
                    confidence=confidence,
                    entry_zone=(resistance * 1.0, resistance * 1.005),
                    stop_loss=resistance * 0.98,
                    targets=[resistance * 1.03, resistance * 1.06, resistance * 1.10],
                    risk_reward=2.5,
                    formation_time=10,
                    description="Price breaking key resistance level with volume",
                    key_levels={'resistance': resistance, 'current_price': current_price},
                    volume_confirmation=self.indicators.is_volume_increasing(df),
                    institutional_signal=True
                )
                patterns.append(pattern)
                break

        return patterns

    def _detect_falling_wedge(self, df: pd.DataFrame) -> List[Pattern]:
        """Detect falling wedge pattern (bullish reversal)"""
        patterns = []
        # Implementation similar to triangles
        return patterns

    def _detect_rising_wedge(self, df: pd.DataFrame) -> List[Pattern]:
        """Detect rising wedge pattern (bearish reversal)"""
        patterns = []
        # Implementation similar to triangles
        return patterns

    @staticmethod
    def _calculate_trendline_slope(series: pd.Series) -> float:
        """Calculate slope of trendline through price points"""
        if len(series) < 2:
            return 0

        x = np.arange(len(series))
        y = series.values

        # Linear regression
        slope = np.polyfit(x, y, 1)[0]
        return slope

    @staticmethod
    def _is_volume_decreasing(df: pd.DataFrame, window: int = 10) -> bool:
        """Check if volume is decreasing (typical in triangle patterns)"""
        if len(df) < window * 2:
            return False

        recent_volume = df['volume'].tail(window).mean()
        previous_volume = df['volume'].tail(window * 2).head(window).mean()

        return recent_volume < previous_volume

    @staticmethod
    def _calculate_pattern_confidence(
        resistance_touches: int,
        support_slope: float,
        volume_decreasing: bool,
        time_in_pattern: int
    ) -> float:
        """
        Calculate pattern confidence score

        Args:
            resistance_touches: Number of times resistance tested
            support_slope: Slope of support trendline
            volume_decreasing: Whether volume is decreasing
            time_in_pattern: Number of candles in pattern

        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.5  # Base confidence

        # More touches = higher confidence
        confidence += min(resistance_touches * 0.1, 0.25)

        # Strong slope = higher confidence
        if abs(support_slope) > 0.5:
            confidence += 0.1

        # Volume confirmation
        if volume_decreasing:
            confidence += 0.1

        # Time in pattern (sweet spot: 10-30 candles)
        if 10 <= time_in_pattern <= 30:
            confidence += 0.05

        return min(confidence, 0.99)  # Max 99% confidence


# Example usage
if __name__ == "__main__":
    # Test pattern recognition
    dates = pd.date_range('2024-01-01', periods=100, freq='4H')
    sample_data = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)

    recognizer = PatternRecognition()
    patterns = recognizer.analyze_chart(sample_data, "BTC/USDT")

    print(f"Detected {len(patterns)} patterns:")
    for pattern in patterns:
        print(f"\n{pattern.pattern_type} - Confidence: {pattern.confidence:.1%}")
        print(f"Entry: ${pattern.entry_zone[0]:.2f} - ${pattern.entry_zone[1]:.2f}")
        print(f"Stop: ${pattern.stop_loss:.2f}")
        print(f"Targets: {[f'${t:.2f}' for t in pattern.targets]}")
        print(f"R:R = {pattern.risk_reward:.2f}:1")
