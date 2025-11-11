"""
FOOS Pattern Recognition System
Implements Cameron Fous' 4-pattern triangle breakout methodology
"""

import pandas as pd
import numpy as np
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
from datetime import datetime

from wolf_analyzer.analysis.technical_indicators import TechnicalIndicators

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class FOOSPattern:
    """FOOS Pattern detection result"""
    pattern_type: str  # FORCE, SURVIVAL, REVIVAL, GOLD
    confidence: float  # 0.0 - 1.0
    detected_at: datetime

    # Phase timestamps (indices in dataframe)
    phase_1_start: int
    phase_2_start: int
    phase_3_breakout: int

    # Key price levels
    neckline_price: float
    neckline_touches: int
    trendline_slope: float
    entry_low: float
    entry_high: float
    stop_loss: float
    target_1: float
    target_2: float
    target_3: float
    risk_reward: float

    # Pattern characteristics
    lead_in_trend: str  # 'bullish', 'neutral', 'bearish'
    consolidation_days: int
    volume_spike_confirmed: bool
    ema_13_position: str  # 'above', 'below'

    # Trendline points for drawing
    neckline_start_idx: int
    neckline_end_idx: int
    trendline_start_idx: int
    trendline_end_idx: int

    description: str
    notes: str


class FOOSPatternDetector:
    """
    Detects FOOS patterns in historical price data
    Currently implements: FORCE pattern
    TODO: SURVIVAL, REVIVAL, GOLD patterns
    """

    def __init__(self, min_confidence: float = 0.65, relaxed_mode: bool = False):
        """
        Initialize FOOS pattern detector

        Args:
            min_confidence: Minimum confidence threshold (0.0-1.0)
            relaxed_mode: If True, uses more lenient detection criteria for testing
        """
        self.min_confidence = min_confidence
        self.relaxed_mode = relaxed_mode
        self.indicators = TechnicalIndicators()

        if relaxed_mode:
            logger.info("🔓 RELAXED MODE: Using lenient detection criteria for testing")

    def detect_patterns(self, df: pd.DataFrame, symbol: str) -> List[FOOSPattern]:
        """
        Detect all FOOS patterns in the dataset

        Args:
            df: DataFrame with OHLCV data (needs at least 100 candles)
            symbol: Trading pair symbol

        Returns:
            List of detected patterns sorted by confidence
        """
        patterns = []

        if len(df) < 100:
            logger.warning(f"⚠️  {symbol}: Need at least 100 candles for pattern detection (got {len(df)})")
            return patterns

        logger.info(f"🔍 Scanning {symbol} for FOOS patterns ({len(df)} candles)...")

        # Detect FORCE patterns
        force_patterns = self._detect_force(df)
        patterns.extend(force_patterns)

        # TODO: Add other pattern types
        # patterns.extend(self._detect_survival(df))
        # patterns.extend(self._detect_revival(df))
        # patterns.extend(self._detect_gold(df))

        # Show all patterns before filtering
        if force_patterns:
            logger.info(f"  Found {len(force_patterns)} FORCE candidate(s) before confidence filter")
            for p in force_patterns:
                logger.info(f"    - {p.pattern_type}: {p.confidence:.1%} confidence (threshold: {self.min_confidence:.1%})")

        # Filter by confidence
        patterns = [p for p in patterns if p.confidence >= self.min_confidence]

        # Sort by confidence (highest first)
        patterns.sort(key=lambda x: x.confidence, reverse=True)

        if patterns:
            logger.info(f"✓ {symbol}: Detected {len(patterns)} high-confidence FOOS pattern(s)")
        else:
            logger.info(f"  {symbol}: No patterns above {self.min_confidence:.0%} confidence threshold")

        return patterns

    def _detect_force(self, df: pd.DataFrame) -> List[FOOSPattern]:
        """
        Detect FORCE pattern (most reliable)

        FORCE Pattern Characteristics:
        - Lead-in: Bullish or Neutral trend
        - Phase 1: Price + Volume increase (initial bullish move)
        - Phase 2: Consolidation forming triangle
          - Neckline: Flat resistance (2+ touches)
          - Trendline: Rising support (2+ higher lows)
          - Volume: Decreasing during consolidation
        - Phase 3: Breakout above neckline with volume spike

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of detected FORCE patterns
        """
        patterns = []

        # Need sufficient data
        if len(df) < 100:
            logger.warning(f"      ⚠️  Insufficient data for FORCE detection: {len(df)} candles (need 100+)")
            return patterns

        logger.info(f"      📊 FORCE detection starting with {len(df)} candles")
        logger.info(f"      📊 Scanning range: index 50 to {len(df) - 20} ({len(df) - 70} windows)")

        if self.relaxed_mode:
            logger.info(f"      🔓 RELAXED criteria: wider neckline (2%), accept flat trendlines, no convergence check, 1.0:1 R:R")

        # Calculate indicators
        ema_13 = self.indicators.calculate_ema_13(df)

        # Debug counters
        checked = 0
        failed_lead_in = 0
        failed_neckline = 0
        failed_trendline = 0
        failed_convergence = 0
        failed_breakout = 0
        failed_risk_reward = 0

        # Scan through data looking for potential patterns
        # Start from index 50 to have enough history for lead-in trend
        # End 20 candles before current to see if breakout confirmed
        for i in range(50, len(df) - 20):
            checked += 1
            # Look at a window of 30-50 candles for consolidation
            window_start = i
            window_end = min(i + 50, len(df) - 10)
            window = df.iloc[window_start:window_end]

            if len(window) < 30:
                continue

            # Step 1: Check lead-in trend (20 candles before consolidation)
            lead_in = df.iloc[max(0, window_start - 20):window_start]
            lead_in_trend = self._classify_trend(lead_in)

            # FORCE requires bullish or neutral lead-in (relaxed: allow bearish)
            if not self.relaxed_mode and lead_in_trend not in ['bullish', 'neutral']:
                failed_lead_in += 1
                continue
            elif self.relaxed_mode and lead_in_trend == 'bearish':
                # In relaxed mode, still count bearish but don't skip
                pass

            # Step 2: Identify potential neckline (resistance)
            neckline_result = self._find_neckline(window)
            if not neckline_result:
                failed_neckline += 1
                continue

            neckline_price, neckline_touches, neckline_indices = neckline_result

            # Need at least 2 touches to confirm neckline (relaxed: 1 touch OK)
            min_touches = 1 if self.relaxed_mode else 2
            if neckline_touches < min_touches:
                failed_neckline += 1
                continue

            # Step 3: Identify ascending trendline (support)
            trendline_result = self._find_ascending_trendline(window)
            if not trendline_result:
                failed_trendline += 1
                continue

            trendline_slope, trendline_indices = trendline_result

            # Slope must be positive (ascending) - Relaxed: accept flat/slightly descending
            min_slope = -0.0001 if self.relaxed_mode else 0
            if trendline_slope <= min_slope:
                failed_trendline += 1
                continue

            # Step 4: Check for triangle convergence (skip in relaxed mode)
            # Lines should be getting closer (consolidation narrowing)
            if not self.relaxed_mode:
                if not self._check_triangle_convergence(window, neckline_price, trendline_indices):
                    failed_convergence += 1
                    continue

            # Step 5: Check volume pattern (decreasing during consolidation)
            volume_decreasing = self._is_volume_decreasing(window)

            # Step 6: Look for breakout after consolidation
            breakout_result = self._find_breakout(
                df, window_end, neckline_price, volume_decreasing
            )

            if not breakout_result:
                failed_breakout += 1
                continue

            breakout_idx, breakout_confirmed, volume_spike = breakout_result

            # Calculate confidence score
            confidence = self._calculate_force_confidence(
                neckline_touches=neckline_touches,
                trendline_slope=trendline_slope,
                volume_decreasing=volume_decreasing,
                volume_spike=volume_spike,
                lead_in_trend=lead_in_trend,
                consolidation_length=len(window)
            )

            # Calculate entry/exit levels
            current_price = df.iloc[breakout_idx]['close']
            entry_low = neckline_price * 0.998  # Just below neckline
            entry_high = neckline_price * 1.002  # Just above neckline

            # Stop loss: Below lowest low in consolidation
            consolidation_lows = window['low']
            stop_loss = consolidation_lows.min() * 0.995

            # Targets based on triangle height
            triangle_height = neckline_price - consolidation_lows.min()
            target_1 = neckline_price + (triangle_height * 0.5)
            target_2 = neckline_price + (triangle_height * 1.0)
            target_3 = neckline_price + (triangle_height * 1.5)

            # Risk:Reward calculation
            risk = entry_high - stop_loss
            reward = target_2 - entry_high
            risk_reward = reward / risk if risk > 0 else 0

            # Only consider if R:R >= 2:1 (relaxed: 1.0:1)
            min_risk_reward = 1.0 if self.relaxed_mode else 2.0
            if risk_reward < min_risk_reward:
                failed_risk_reward += 1
                continue

            # Check EMA 13 position
            ema_13_val = ema_13.iloc[breakout_idx]
            ema_13_position = 'above' if current_price > ema_13_val else 'below'

            # Create pattern object
            pattern = FOOSPattern(
                pattern_type='FORCE',
                confidence=confidence,
                detected_at=df.index[breakout_idx],
                phase_1_start=window_start - 10,  # Approximate start of initial move
                phase_2_start=window_start,
                phase_3_breakout=breakout_idx,
                neckline_price=neckline_price,
                neckline_touches=neckline_touches,
                trendline_slope=trendline_slope,
                entry_low=entry_low,
                entry_high=entry_high,
                stop_loss=stop_loss,
                target_1=target_1,
                target_2=target_2,
                target_3=target_3,
                risk_reward=risk_reward,
                lead_in_trend=lead_in_trend,
                consolidation_days=len(window),
                volume_spike_confirmed=volume_spike,
                ema_13_position=ema_13_position,
                neckline_start_idx=window_start + neckline_indices[0],
                neckline_end_idx=window_start + neckline_indices[-1],
                trendline_start_idx=window_start + trendline_indices[0],
                trendline_end_idx=window_start + trendline_indices[-1],
                description=f"FORCE pattern: {lead_in_trend.title()} lead-in → Triangle consolidation → Breakout",
                notes=f"Neckline: ${neckline_price:.2f}, R:R {risk_reward:.2f}:1"
            )

            patterns.append(pattern)

            # Skip ahead to avoid overlapping patterns
            i = breakout_idx + 10

        # Print debug summary - ALWAYS print this
        logger.info(f"      📊 FORCE scan summary:")
        logger.info(f"         Windows checked: {checked}")
        logger.info(f"         Patterns found: {len(patterns)}")

        if checked > 0:
            total_failed = failed_lead_in + failed_neckline + failed_trendline + failed_convergence + failed_breakout + failed_risk_reward
            logger.info(f"         Total failed: {total_failed}")

            min_rr = "1.0:1" if self.relaxed_mode else "2:1"
            min_touches = "1+" if self.relaxed_mode else "2+"
            trendline_desc = "flat/ascending" if self.relaxed_mode else "ascending"

            if failed_lead_in > 0:
                logger.info(f"         ↳ {failed_lead_in} ({failed_lead_in/checked*100:.1f}%) failed: bearish lead-in trend")
            if failed_neckline > 0:
                logger.info(f"         ↳ {failed_neckline} ({failed_neckline/checked*100:.1f}%) failed: no clear neckline resistance (need {min_touches} touches)")
            if failed_trendline > 0:
                logger.info(f"         ↳ {failed_trendline} ({failed_trendline/checked*100:.1f}%) failed: no {trendline_desc} support trendline")
            if failed_convergence > 0:
                logger.info(f"         ↳ {failed_convergence} ({failed_convergence/checked*100:.1f}%) failed: triangle not converging")
            if failed_breakout > 0:
                logger.info(f"         ↳ {failed_breakout} ({failed_breakout/checked*100:.1f}%) failed: no breakout above neckline")
            if failed_risk_reward > 0:
                logger.info(f"         ↳ {failed_risk_reward} ({failed_risk_reward/checked*100:.1f}%) failed: risk/reward < {min_rr}")
        else:
            logger.warning(f"         ⚠️  No windows were checked!")

        return patterns

    def _classify_trend(self, df: pd.DataFrame) -> str:
        """
        Classify trend as bullish, neutral, or bearish

        Args:
            df: DataFrame with OHLCV data

        Returns:
            'bullish', 'neutral', or 'bearish'
        """
        if len(df) < 5:
            return 'neutral'

        # Calculate price slope
        prices = df['close'].values
        x = np.arange(len(prices))
        slope = np.polyfit(x, prices, 1)[0]

        # Normalize slope by average price
        avg_price = prices.mean()
        norm_slope = slope / avg_price

        # Classify
        if norm_slope > 0.001:  # More than 0.1% per candle
            return 'bullish'
        elif norm_slope < -0.001:
            return 'bearish'
        else:
            return 'neutral'

    def _find_neckline(self, df: pd.DataFrame) -> Optional[Tuple[float, int, List[int]]]:
        """
        Find horizontal neckline (resistance) in consolidation

        Returns:
            (neckline_price, touch_count, touch_indices) or None
        """
        highs = df['high'].values

        # Find the highest point in the range
        max_high = highs.max()

        # Count touches within threshold of max_high (relaxed: 2%, strict: 0.5%)
        threshold_pct = 0.02 if self.relaxed_mode else 0.005
        threshold = max_high * threshold_pct
        touches = []

        for i, high in enumerate(highs):
            if abs(high - max_high) <= threshold:
                touches.append(i)

        if len(touches) >= 2:
            return (max_high, len(touches), touches)

        return None

    def _find_ascending_trendline(self, df: pd.DataFrame) -> Optional[Tuple[float, List[int]]]:
        """
        Find ascending trendline (rising support) in consolidation

        Returns:
            (slope, low_indices) or None
        """
        lows = df['low'].values

        # Find local lows (points where price touched support)
        local_lows = []
        for i in range(1, len(lows) - 1):
            if lows[i] <= lows[i-1] and lows[i] <= lows[i+1]:
                local_lows.append(i)

        if len(local_lows) < 2:
            return None

        # Calculate slope through local lows
        x = np.array(local_lows)
        y = lows[local_lows]

        if len(x) < 2:
            return None

        slope = np.polyfit(x, y, 1)[0]

        return (slope, local_lows)

    def _check_triangle_convergence(
        self,
        df: pd.DataFrame,
        neckline: float,
        trendline_indices: List[int]
    ) -> bool:
        """Check if triangle is converging (getting narrower)"""
        if len(trendline_indices) < 2:
            return False

        lows = df['low'].values

        # Distance from trendline to neckline should decrease
        start_distance = neckline - lows[trendline_indices[0]]
        end_distance = neckline - lows[trendline_indices[-1]]

        # End distance should be smaller (converging)
        return end_distance < start_distance * 0.8

    def _is_volume_decreasing(self, df: pd.DataFrame) -> bool:
        """Check if volume is decreasing during consolidation"""
        if len(df) < 10:
            return False

        first_half_vol = df['volume'].iloc[:len(df)//2].mean()
        second_half_vol = df['volume'].iloc[len(df)//2:].mean()

        return second_half_vol < first_half_vol * 0.9

    def _find_breakout(
        self,
        df: pd.DataFrame,
        consolidation_end: int,
        neckline: float,
        volume_was_decreasing: bool
    ) -> Optional[Tuple[int, bool, bool]]:
        """
        Look for breakout after consolidation ends

        Returns:
            (breakout_index, confirmed, volume_spike) or None
        """
        # Look at next 20 candles for breakout
        search_end = min(consolidation_end + 20, len(df))

        for i in range(consolidation_end, search_end):
            candle = df.iloc[i]

            # Check if price broke above neckline (relaxed: 0.1%, strict: 0.2%)
            breakout_pct = 1.001 if self.relaxed_mode else 1.002
            if candle['close'] > neckline * breakout_pct:
                # Check for volume spike
                avg_volume = df['volume'].iloc[max(0, i-20):i].mean()
                current_volume = candle['volume']
                volume_spike = current_volume > avg_volume * 1.3

                # Breakout confirmed if:
                # 1. Close above neckline
                # 2. (Ideally) volume spike present
                confirmed = volume_spike or (not volume_was_decreasing)

                return (i, confirmed, volume_spike)

        return None

    def _calculate_force_confidence(
        self,
        neckline_touches: int,
        trendline_slope: float,
        volume_decreasing: bool,
        volume_spike: bool,
        lead_in_trend: str,
        consolidation_length: int
    ) -> float:
        """
        Calculate confidence score for FORCE pattern

        Returns:
            Confidence score (0.0 - 1.0)
        """
        confidence = 0.5  # Base confidence

        # More neckline touches = stronger resistance = higher confidence
        confidence += min(neckline_touches * 0.08, 0.20)

        # Positive slope on trendline = ascending triangle
        if trendline_slope > 0:
            confidence += min(trendline_slope * 100, 0.15)

        # Volume decreasing during consolidation
        if volume_decreasing:
            confidence += 0.10

        # Volume spike on breakout
        if volume_spike:
            confidence += 0.15

        # Bullish lead-in is ideal for FORCE
        if lead_in_trend == 'bullish':
            confidence += 0.10
        elif lead_in_trend == 'neutral':
            confidence += 0.05

        # Consolidation length (sweet spot: 15-40 candles for 4h timeframe)
        if 15 <= consolidation_length <= 40:
            confidence += 0.05

        return min(confidence, 0.99)  # Cap at 99%
