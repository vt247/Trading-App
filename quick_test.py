#!/usr/bin/env python3
"""Quick analysis test with more detailed output"""
import sys
sys.path.insert(0, '/home/user/Trading-App')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from wolf_analyzer.analysis.pattern_recognition import PatternRecognition
from wolf_analyzer.analysis.technical_indicators import TechnicalIndicators

print("=" * 70)
print("🧪 QUICK TEST: Detailed Analysis")
print("=" * 70)

# Generate realistic descending triangle data
dates = pd.date_range(start=datetime.now() - timedelta(hours=400), periods=100, freq='4H')
np.random.seed(123)

prices = []
support = 42000  # Flat support
for i in range(100):
    # Descending resistance
    resistance = 45000 - (i * 25)
    # Price between support and resistance
    price = np.random.uniform(support * 1.005, resistance * 0.995)
    prices.append(price)

df = pd.DataFrame({
    'open': [p - np.random.uniform(0, 100) for p in prices],
    'high': [p + np.random.uniform(50, 200) for p in prices],
    'low': [p - np.random.uniform(50, 200) for p in prices],
    'close': prices,
    'volume': [1e8 * (1 + i/100) + np.random.uniform(-1e7, 1e7) for i in range(100)]
}, index=dates)

print("\n📊 Generated BTC/USDT data (Descending Triangle)")
print(f"  Candles: {len(df)}")
print(f"  Period: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
print(f"  Price range: ${df['low'].min():,.0f} - ${df['high'].max():,.0f}")
print(f"  Current price: ${df['close'].iloc[-1]:,.2f}")
print(f"  24h change: {((df['close'].iloc[-1] / df['close'].iloc[-6] - 1) * 100):.2f}%")

# Technical Indicators
print("\n📈 Technical Indicators:")
print("-" * 70)
indicators = TechnicalIndicators()

# Support/Resistance
support_levels, resistance_levels = indicators.calculate_support_resistance(df)
print(f"Support levels: {', '.join([f'${s:,.0f}' for s in support_levels])}")
print(f"Resistance levels: {', '.join([f'${r:,.0f}' for r in resistance_levels])}")

# RSI
rsi = indicators.calculate_rsi(df)
rsi_current = rsi.iloc[-1]
rsi_signal = "OVERSOLD 🟢" if rsi_current < 30 else "OVERBOUGHT 🔴" if rsi_current > 70 else "NEUTRAL ⚪"
print(f"\nRSI (14): {rsi_current:.2f} - {rsi_signal}")

# MACD
macd, signal, histogram = indicators.calculate_macd(df)
macd_signal = "BULLISH 🟢" if histogram.iloc[-1] > 0 else "BEARISH 🔴"
print(f"MACD: {macd.iloc[-1]:.2f} | Signal: {signal.iloc[-1]:.2f} | {macd_signal}")

# Trend
trend = indicators.identify_trend(df)
trend_emoji = "📈" if trend == "bullish" else "📉" if trend == "bearish" else "➡️"
print(f"Trend: {trend.upper()} {trend_emoji}")

# Volume
vol_increasing = indicators.is_volume_increasing(df)
print(f"Volume: {'Increasing 📊' if vol_increasing else 'Decreasing 📉'}")

# ATR (volatility)
atr = indicators.calculate_atr(df)
print(f"ATR (14): ${atr.iloc[-1]:,.2f} (volatility)")

# Pattern Recognition
print("\n🎯 Pattern Recognition:")
print("-" * 70)
recognizer = PatternRecognition(min_confidence=0.50)
patterns = recognizer.analyze_chart(df, "BTC/USDT")

if patterns:
    for i, pattern in enumerate(patterns, 1):
        print(f"\n✓ PATTERN #{i}: {pattern.pattern_type}")
        print(f"  Confidence: {pattern.confidence:.1%}")
        print(f"  Risk:Reward: {pattern.risk_reward:.2f}:1")
        print(f"  Entry: ${pattern.entry_zone[0]:,.2f} - ${pattern.entry_zone[1]:,.2f}")
        print(f"  Stop Loss: ${pattern.stop_loss:,.2f}")
        print(f"  Targets: {', '.join([f'${t:,.2f}' for t in pattern.targets])}")
        print(f"  Volume confirmed: {'✓' if pattern.volume_confirmation else '✗'}")
        print(f"  Institutional signal: {'✓' if pattern.institutional_signal else '✗'}")
else:
    print("  No patterns detected with current criteria")
    print("  (This is normal - not all market conditions show clear patterns)")

print("\n" + "=" * 70)
print("✅ Test completed successfully!")
print("=" * 70)
