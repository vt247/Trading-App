"""
Test FOOS Pattern Detection
Quick test script to verify FORCE pattern detection works
"""

from wolf_analyzer.data.historical_manager import HistoricalDataManager
from wolf_analyzer.analysis.foos_patterns import FOOSPatternDetector

def test_force_detection():
    """Test FORCE pattern detection on BTC"""
    print("="*80)
    print("TESTING FOOS PATTERN DETECTION")
    print("="*80)

    # Initialize managers
    print("\n1. Initializing data manager...")
    hist_manager = HistoricalDataManager()

    # Get historical data (use smaller timeframe for testing)
    print("\n2. Loading historical data for BTC/USDT...")
    df = hist_manager.ensure_data('BTC/USDT', '4h', lookback_days=365)  # 1 year for faster testing

    if df.empty:
        print("❌ No data available")
        return

    print(f"✓ Loaded {len(df)} candles")
    print(f"  Date range: {df.index[0].date()} to {df.index[-1].date()}")

    # Detect patterns
    print("\n3. Detecting FORCE patterns...")
    detector = FOOSPatternDetector(min_confidence=0.65)
    patterns = detector.detect_patterns(df, 'BTC/USDT')

    # Display results
    print("\n" + "="*80)
    print(f"RESULTS: Found {len(patterns)} FORCE pattern(s)")
    print("="*80)

    for i, pattern in enumerate(patterns, 1):
        print(f"\n{'─'*80}")
        print(f"Pattern #{i}: {pattern.pattern_type}")
        print(f"{'─'*80}")
        print(f"Confidence:       {pattern.confidence:.1%}")
        print(f"Detected at:      {pattern.detected_at.date()}")
        print(f"Lead-in trend:    {pattern.lead_in_trend.title()}")
        print(f"Consolidation:    {pattern.consolidation_days} candles")
        print(f"\nKey Levels:")
        print(f"  Neckline:       ${pattern.neckline_price:,.2f} ({pattern.neckline_touches} touches)")
        print(f"  Entry zone:     ${pattern.entry_low:,.2f} - ${pattern.entry_high:,.2f}")
        print(f"  Stop loss:      ${pattern.stop_loss:,.2f}")
        print(f"  Target 1:       ${pattern.target_1:,.2f}")
        print(f"  Target 2:       ${pattern.target_2:,.2f}")
        print(f"  Target 3:       ${pattern.target_3:,.2f}")
        print(f"\nRisk:Reward:      {pattern.risk_reward:.2f}:1")
        print(f"Volume spike:     {'✓ Yes' if pattern.volume_spike_confirmed else '✗ No'}")
        print(f"EMA 13 position:  {pattern.ema_13_position.title()}")
        print(f"\n{pattern.description}")

    hist_manager.close()

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_force_detection()
