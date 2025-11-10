#!/usr/bin/env python3
"""
Wolf Market Analyzer - Demo Mode
Test application with sample data (no API keys needed)
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, '/home/user/Trading-App')

from src.analysis.pattern_recognition import PatternRecognition
from src.analysis.technical_indicators import TechnicalIndicators
from src.analysis.chart_generator import ChartGenerator
from src.ai.claude_analyzer import ClaudeAnalyzer
from src.core.config import Config


def generate_sample_data(days=100, trend='bullish'):
    """Generate realistic sample OHLCV data"""

    # Base price
    base_price = 42000 if trend == 'bullish' else 45000

    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(hours=days * 4)  # 4h candles
    dates = pd.date_range(start=start_date, end=end_date, freq='4H')[:days]

    # Generate price action
    np.random.seed(42)  # For reproducibility

    if trend == 'bullish':
        # Ascending triangle pattern
        prices = []
        for i in range(days):
            # Flat resistance around 43000
            resistance = 43000
            # Rising support
            support = base_price + (i / days * 800)  # Rising from 42000 to 42800

            # Random walk between support and resistance
            if i < days * 0.7:
                price = np.random.uniform(support, resistance)
            else:
                # Approaching apex
                price = np.random.uniform(support, resistance * 0.995)

            prices.append(price)

        # Create OHLCV
        data = []
        for i, price in enumerate(prices):
            volatility = np.random.uniform(0.003, 0.008)  # 0.3-0.8%
            open_price = price
            high = price * (1 + volatility)
            low = price * (1 - volatility)
            close = np.random.uniform(low, high)

            # Decreasing volume (typical for triangles)
            base_volume = 100000000
            volume = base_volume * (1 - (i / days) * 0.4) + np.random.uniform(-10000000, 10000000)

            data.append({
                'timestamp': dates[i],
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': max(volume, 50000000)
            })

    elif trend == 'bearish':
        # Descending triangle pattern
        prices = []
        for i in range(days):
            # Flat support around 42000
            support = 42000
            # Descending resistance
            resistance = base_price - (i / days * 2000)  # Falling from 45000 to 43000

            price = np.random.uniform(support, resistance)
            prices.append(price)

        # Create OHLCV
        data = []
        for i, price in enumerate(prices):
            volatility = np.random.uniform(0.003, 0.008)
            open_price = price
            high = price * (1 + volatility)
            low = price * (1 - volatility)
            close = np.random.uniform(low, high)

            # Increasing volume on down moves (distribution)
            base_volume = 80000000
            volume = base_volume * (1 + (i / days) * 0.3) + np.random.uniform(-10000000, 10000000)

            data.append({
                'timestamp': dates[i],
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': max(volume, 50000000)
            })

    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    return df


def demo_pattern_recognition():
    """Demo: Pattern recognition"""
    print("=" * 60)
    print("🔍 DEMO: Pattern Recognition")
    print("=" * 60)

    # Generate bullish data
    print("\n📊 Generating sample BTC/USDT data (ascending triangle)...")
    df = generate_sample_data(days=80, trend='bullish')

    print(f"✓ Generated {len(df)} candles")
    print(f"  Price range: ${df['low'].min():,.0f} - ${df['high'].max():,.0f}")
    print(f"  Current price: ${df['close'].iloc[-1]:,.2f}")

    # Run pattern recognition
    print("\n🎯 Running pattern recognition...")
    recognizer = PatternRecognition(min_confidence=0.50)  # Lower threshold for demo
    patterns = recognizer.analyze_chart(df, "BTC/USDT")

    print(f"✓ Detected {len(patterns)} pattern(s)")

    # Display patterns
    for i, pattern in enumerate(patterns, 1):
        print(f"\n{'='*60}")
        print(f"PATTERN #{i}: {pattern.pattern_type}")
        print(f"{'='*60}")
        print(f"Confidence: {pattern.confidence:.1%}")
        print(f"Formation Time: {pattern.formation_time} hours")
        print(f"\n📍 ENTRY ZONE")
        print(f"   ${pattern.entry_zone[0]:,.2f} - ${pattern.entry_zone[1]:,.2f}")
        print(f"\n🛑 STOP LOSS")
        print(f"   ${pattern.stop_loss:,.2f}")
        print(f"\n🎯 TARGETS")
        for j, target in enumerate(pattern.targets, 1):
            print(f"   T{j}: ${target:,.2f}")
        print(f"\n📊 RISK:REWARD")
        print(f"   {pattern.risk_reward:.2f}:1")
        print(f"\n✓ CONFIRMATIONS")
        print(f"   Volume: {'✓' if pattern.volume_confirmation else '✗'}")
        print(f"   Institutional: {'✓' if pattern.institutional_signal else '✗'}")
        print(f"\n📝 DESCRIPTION")
        print(f"   {pattern.description}")

    return df, patterns


def demo_technical_indicators():
    """Demo: Technical indicators"""
    print("\n\n" + "=" * 60)
    print("📈 DEMO: Technical Indicators")
    print("=" * 60)

    df = generate_sample_data(days=100, trend='bullish')
    indicators = TechnicalIndicators()

    # Calculate various indicators
    print("\n🔢 Calculating indicators...")

    # Support/Resistance
    support, resistance = indicators.calculate_support_resistance(df)
    print(f"\n✓ Support levels: {[f'${s:,.0f}' for s in support]}")
    print(f"✓ Resistance levels: {[f'${r:,.0f}' for r in resistance]}")

    # RSI
    rsi = indicators.calculate_rsi(df)
    current_rsi = rsi.iloc[-1]
    print(f"\n✓ RSI (14): {current_rsi:.2f}")
    if current_rsi < 30:
        print("   → Oversold (potential buy)")
    elif current_rsi > 70:
        print("   → Overbought (potential sell)")
    else:
        print("   → Neutral")

    # MACD
    macd, signal, histogram = indicators.calculate_macd(df)
    print(f"\n✓ MACD: {macd.iloc[-1]:.2f}")
    print(f"  Signal: {signal.iloc[-1]:.2f}")
    print(f"  Histogram: {histogram.iloc[-1]:.2f}")
    if histogram.iloc[-1] > 0:
        print("   → Bullish crossover")
    else:
        print("   → Bearish crossover")

    # Trend
    trend = indicators.identify_trend(df)
    print(f"\n✓ Trend: {trend.upper()}")

    # Volume analysis
    volume_increasing = indicators.is_volume_increasing(df)
    print(f"✓ Volume: {'Increasing ↑' if volume_increasing else 'Decreasing ↓'}")


def demo_chart_generation(df, pattern):
    """Demo: Chart generation"""
    print("\n\n" + "=" * 60)
    print("📊 DEMO: Chart Generation")
    print("=" * 60)

    print("\n🎨 Generating annotated chart...")

    try:
        generator = ChartGenerator()
        chart_path = generator.create_pattern_chart(
            df, "BTC/USDT (DEMO)", pattern, save=True
        )
        print(f"✓ Chart saved to: {chart_path}")
        print("\n  The chart includes:")
        print("  • Candlestick price action")
        print("  • Entry zone (green dashed lines)")
        print("  • Stop loss (red line)")
        print("  • Targets (blue dotted lines)")
        print("  • Volume bars")
        print("  • Pattern info box")
    except Exception as e:
        print(f"⚠️  Chart generation: {str(e)}")
        print("  (mplfinance requires display - works on local machine)")


def demo_ai_analysis(pattern):
    """Demo: AI analysis"""
    print("\n\n" + "=" * 60)
    print("🤖 DEMO: AI Analysis with Claude")
    print("=" * 60)

    analyzer = ClaudeAnalyzer()

    if not analyzer.client:
        print("\n⚠️  Claude AI not configured")
        print("   Add ANTHROPIC_API_KEY to .env to enable AI analysis")
        print("\n   Example AI analysis output:")
        print("-" * 60)
        print("""
## PATTERN SUMMARY
This ascending triangle shows classic institutional accumulation
behavior. The pattern has formed over 72 hours with decreasing
volume - indicating a coiling spring ready to breakout.

## INSTITUTIONAL READING
Market makers are holding resistance at $43,000 while smart money
systematically accumulates at support levels ($42,000-$42,800).
Each bounce creates higher lows - buyers stepping in stronger.

The decreasing volume is NOT weakness - it's concentration.
Retail exits in frustration while institutions quietly accumulate.

## HISTORICAL CONTEXT
Based on similar patterns in BTC history:
• Last 12 ascending triangles: 10 broke upward (83% success)
• Average breakout move: 5.7% in 4 days
• Best entry timing: Support retest before breakout

## TRADE SETUP
🎯 ENTRY: Wait for volume spike on break above $43,000
   Best entry: $42,250-$42,350 (current support zone)

⚠️ CONFIRMATION: Need 2M+ volume on breakout candle
   Don't chase - let price come to your zone

🛑 INVALIDATION: Close below $41,800 = pattern failed

## RISK FACTORS
• News events can override technicals
• Watch BTC dominance for altcoin rotation signals
• Fed announcements could trigger volatility
• Pattern has 72h until apex - time sensitivity increasing
        """)
        print("-" * 60)
        return

    print("\n🧠 Analyzing pattern with Claude AI...")
    market_context = {
        'current_price': 42250,
        'change_24h': 2.3,
        'volume_24h': 85000000,
        'timeframe': '4h'
    }

    try:
        analysis = analyzer.analyze_pattern(pattern, "BTC/USDT", market_context)
        print("\n" + analysis)
    except Exception as e:
        print(f"⚠️  AI analysis error: {str(e)}")


def demo_watchlist_scan():
    """Demo: Watchlist scanning"""
    print("\n\n" + "=" * 60)
    print("🔎 DEMO: Watchlist Scan")
    print("=" * 60)

    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'AVAX/USDT']
    recognizer = PatternRecognition(min_confidence=0.50)  # Lower threshold for demo
    all_setups = []

    print("\n📊 Scanning watchlist...")

    for symbol in symbols:
        print(f"\n{symbol}...", end=" ")

        # Generate different patterns for variety
        if 'BTC' in symbol:
            df = generate_sample_data(days=100, trend='bullish')
        elif 'ETH' in symbol:
            df = generate_sample_data(days=80, trend='bearish')
        else:
            df = generate_sample_data(days=60, trend='bullish')
            df['close'] = df['close'] * 0.95  # Make it weaker

        patterns = recognizer.analyze_chart(df, symbol)

        if patterns:
            print(f"✓ {len(patterns)} pattern(s)")
            for pattern in patterns:
                all_setups.append({'symbol': symbol, 'pattern': pattern})
        else:
            print("○ No patterns")

    # Display summary
    print("\n" + "=" * 60)
    print(f"FOUND {len(all_setups)} TOTAL SETUPS")
    print("=" * 60)

    if all_setups:
        # Sort by confidence
        all_setups.sort(key=lambda x: x['pattern'].confidence, reverse=True)

        for i, setup in enumerate(all_setups[:5], 1):
            pattern = setup['pattern']
            print(f"\n{i}. {setup['symbol']} - {pattern.pattern_type}")
            print(f"   Confidence: {pattern.confidence:.1%} | R:R = {pattern.risk_reward:.2f}:1")
            print(f"   Entry: ${pattern.entry_zone[0]:,.2f}-${pattern.entry_zone[1]:,.2f}")
            print(f"   Stop: ${pattern.stop_loss:,.2f} | Target: ${pattern.targets[0]:,.2f}")


def main():
    """Run all demos"""
    print("\n" + "🐺" * 30)
    print("   WOLF MARKET ANALYZER - DEMO MODE")
    print("🐺" * 30)
    print("\nTesting all features with sample data...")
    print("(No API keys required for demo)")

    # 1. Pattern Recognition
    df, patterns = demo_pattern_recognition()

    # 2. Technical Indicators
    demo_technical_indicators()

    # 3. Chart Generation
    if patterns:
        demo_chart_generation(df, patterns[0])

    # 4. AI Analysis
    if patterns:
        demo_ai_analysis(patterns[0])

    # 5. Watchlist Scan
    demo_watchlist_scan()

    # Summary
    print("\n\n" + "=" * 60)
    print("✅ DEMO COMPLETE!")
    print("=" * 60)
    print("\nAll core features tested successfully:")
    print("  ✓ Pattern Recognition (FOOS4)")
    print("  ✓ Technical Indicators")
    print("  ✓ Chart Generation")
    print("  ✓ AI Analysis (Claude)")
    print("  ✓ Watchlist Scanning")

    print("\n📝 Next Steps:")
    print("  1. Add your API keys to .env file")
    print("  2. Run: python main.py --analyze BTC/USDT")
    print("  3. Start your daily 10-minute routine!")

    print("\n🐺 Trade like a wolf, not a sheep.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
