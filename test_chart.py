#!/usr/bin/env python3
"""Quick chart generation test"""
import sys
sys.path.insert(0, '/home/user/Trading-App')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.analysis.chart_generator import ChartGenerator
from src.analysis.pattern_recognition import Pattern

# Generate sample data
dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='4H')
np.random.seed(42)

prices = []
base = 42000
for i in range(len(dates)):
    price = base + (i * 10) + np.random.uniform(-200, 200)
    prices.append(price)

df = pd.DataFrame({
    'open': [p - np.random.uniform(0, 100) for p in prices],
    'high': [p + np.random.uniform(0, 150) for p in prices],
    'low': [p - np.random.uniform(0, 150) for p in prices],
    'close': prices,
    'volume': [np.random.uniform(5e7, 1e8) for _ in prices]
}, index=dates)

# Create a sample pattern
pattern = Pattern(
    pattern_type="Ascending Triangle",
    confidence=0.78,
    entry_zone=(42250, 42350),
    stop_loss=41800,
    targets=[42850, 43450, 44100],
    risk_reward=2.85,
    formation_time=72,
    description="Bullish continuation pattern with flat resistance and rising support",
    key_levels={'resistance': 43000, 'support': 42000, 'current_price': 42300},
    volume_confirmation=True,
    institutional_signal=True
)

# Generate chart
print("🎨 Generating chart with pattern annotations...")
generator = ChartGenerator()
chart_path = generator.create_pattern_chart(df, "BTC/USDT (TEST)", pattern, save=True)
print(f"✓ Chart saved to: {chart_path}")
print("\n📊 Chart includes:")
print("  • Candlestick price action")
print("  • Entry zone (green lines)")
print("  • Stop loss (red line)")
print("  • Three targets (blue lines)")
print("  • Volume bars")
print("  • Pattern info box")
