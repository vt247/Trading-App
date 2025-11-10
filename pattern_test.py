#!/usr/bin/env python3
"""Test pattern detection with clear patterns"""
import sys
sys.path.insert(0, '/home/user/Trading-App')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from wolf_analyzer.analysis.pattern_recognition import PatternRecognition

print("=" * 70)
print("🎯 PATTERN DETECTION TEST")
print("=" * 70)

# Test 1: Ascending Triangle (very clear pattern)
print("\n📊 Test 1: Ascending Triangle Pattern")
print("-" * 70)

dates = pd.date_range(start=datetime.now() - timedelta(hours=200), periods=50, freq='4H')
np.random.seed(42)

resistance = 43000  # Flat top
prices = []
volumes = []

for i in range(50):
    # Rising support
    support = 42000 + (i * 15)
    # Price oscillating between support and resistance
    price = np.random.uniform(support + 50, resistance - 50)
    prices.append(price)
    # Decreasing volume (typical for triangle)
    volume = 100000000 * (1 - i/100) + np.random.uniform(-5000000, 5000000)
    volumes.append(max(volume, 50000000))

df = pd.DataFrame({
    'open': [p - np.random.uniform(10, 50) for p in prices],
    'high': [min(p + np.random.uniform(20, 100), resistance + 50) for p in prices],
    'low': [max(p - np.random.uniform(20, 100), support - 50) for p, support in zip(prices, [42000 + i*15 for i in range(50)])],
    'close': prices,
    'volume': volumes
}, index=dates)

print(f"Data: {len(df)} candles, ${df['low'].min():,.0f} - ${df['high'].max():,.0f}")

recognizer = PatternRecognition(min_confidence=0.50)
patterns = recognizer.analyze_chart(df, "BTC/USDT")

if patterns:
    for pattern in patterns:
        print(f"\n✓ FOUND: {pattern.pattern_type}")
        print(f"  Confidence: {pattern.confidence:.1%} 🎯")
        print(f"  Risk:Reward: {pattern.risk_reward:.2f}:1")
        print(f"  Entry Zone: ${pattern.entry_zone[0]:,.2f} - ${pattern.entry_zone[1]:,.2f}")
        print(f"  Stop Loss: ${pattern.stop_loss:,.2f}")
        print(f"  Targets:")
        for j, target in enumerate(pattern.targets, 1):
            profit = ((target - pattern.entry_zone[1]) / pattern.entry_zone[1] * 100)
            print(f"    T{j}: ${target:,.2f} (+{profit:.2f}%)")
        print(f"  📊 Volume confirmed: {'✓ YES' if pattern.volume_confirmation else '✗ NO'}")
        print(f"  🏦 Institutional: {'✓ YES' if pattern.institutional_signal else '✗ NO'}")
        
        # Calculate potential profit
        risk = pattern.entry_zone[1] - pattern.stop_loss
        reward = pattern.targets[1] - pattern.entry_zone[1] if len(pattern.targets) > 1 else pattern.targets[0] - pattern.entry_zone[1]
        print(f"\n  💰 If $1,000 position:")
        print(f"     Risk: ${risk/pattern.entry_zone[1]*1000:.2f}")
        print(f"     Reward: ${reward/pattern.entry_zone[1]*1000:.2f}")
else:
    print("  ✗ No clear patterns (adjusting data...)")

# Test 2: Support Break Pattern
print("\n\n📊 Test 2: Support Break Pattern")
print("-" * 70)

dates2 = pd.date_range(start=datetime.now() - timedelta(hours=80), periods=20, freq='4H')
support_level = 42000

prices2 = []
for i in range(20):
    if i < 15:
        # Price hovering around support
        price = support_level + np.random.uniform(-100, 200)
    else:
        # Breaking support
        price = support_level - (i - 14) * 80 - np.random.uniform(0, 100)
    prices2.append(price)

df2 = pd.DataFrame({
    'open': [p + np.random.uniform(-50, 50) for p in prices2],
    'high': [p + np.random.uniform(50, 150) for p in prices2],
    'low': [p - np.random.uniform(50, 150) for p in prices2],
    'close': prices2,
    'volume': [100000000 + np.random.uniform(-20000000, 20000000) for _ in range(20)]
}, index=dates2)

print(f"Data: {len(df2)} candles, Support at ${support_level:,.0f}")

patterns2 = recognizer.analyze_chart(df2, "ETH/USDT")

if patterns2:
    for pattern in patterns2:
        print(f"\n✓ FOUND: {pattern.pattern_type}")
        print(f"  Confidence: {pattern.confidence:.1%} 🎯")
        print(f"  This is a SHORT opportunity (bearish)")
        print(f"  Entry: ${pattern.entry_zone[0]:,.2f} - ${pattern.entry_zone[1]:,.2f}")
        print(f"  Stop: ${pattern.stop_loss:,.2f}")
        print(f"  Target: ${pattern.targets[0]:,.2f}")
else:
    print("  ✗ No patterns detected")

print("\n" + "=" * 70)
print("✅ Pattern Detection Tests Completed!")
print("=" * 70)
