#!/usr/bin/env python3
"""
Wolf Market Analyzer - Main Application
AI-Powered Daily Trading Companion
"""

import sys
import argparse
from datetime import datetime
from typing import List, Dict

from wolf_analyzer.core.config import Config
from wolf_analyzer.data.market_data import MarketDataConnector
from wolf_analyzer.analysis.pattern_recognition import PatternRecognition, Pattern
from wolf_analyzer.analysis.chart_generator import ChartGenerator
from wolf_analyzer.ai.claude_analyzer import ClaudeAnalyzer


class WolfAnalyzer:
    """Main application class"""

    def __init__(self):
        """Initialize Wolf Market Analyzer"""
        print("🐺 Wolf Market Analyzer")
        print("=" * 50)

        self.config = Config
        self.market_data = MarketDataConnector()
        self.pattern_recognition = PatternRecognition()
        self.chart_generator = ChartGenerator()
        self.ai_analyzer = ClaudeAnalyzer()

    def show_config(self):
        """Display current configuration"""
        self.config.display()

    def get_daily_brief(self):
        """Generate and display daily market briefing"""
        print("\n📊 Generating Daily Market Brief...")
        print("=" * 50)

        # Get watchlist data
        watchlist = Config.get_watchlist()
        watchlist_data = {}
        all_patterns = {}

        for symbol in watchlist:
            print(f"\nAnalyzing {symbol}...", end=" ")

            # Fetch data
            df = self.market_data.get_ohlcv(symbol, timeframe="4h", limit=100)
            if df.empty:
                print("✗ Failed")
                continue

            # Get current info
            ticker = self.market_data.get_ticker_info(symbol)
            watchlist_data[symbol] = ticker

            # Detect patterns
            patterns = self.pattern_recognition.analyze_chart(df, symbol)
            all_patterns[symbol] = patterns

            print(f"✓ {len(patterns)} patterns")

        # Generate AI briefing
        if self.ai_analyzer.client:
            briefing = self.ai_analyzer.generate_daily_brief(watchlist_data, all_patterns)
            print("\n" + briefing)
        else:
            # Fallback: manual briefing
            self._display_manual_briefing(watchlist_data, all_patterns)

    def analyze_symbol(self, symbol: str, timeframe: str = "4h", generate_chart: bool = True):
        """
        Analyze a specific symbol

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Timeframe for analysis
            generate_chart: Whether to generate visual chart
        """
        print(f"\n🔍 Analyzing {symbol} ({timeframe})")
        print("=" * 50)

        # Fetch data
        print("Fetching market data...", end=" ")
        df = self.market_data.get_ohlcv(symbol, timeframe=timeframe, limit=200)
        if df.empty:
            print("✗ Failed to fetch data")
            return

        print(f"✓ {len(df)} candles")

        # Current price info
        ticker = self.market_data.get_ticker_info(symbol)
        print(f"\nCurrent Price: ${ticker['price']:,.2f}")
        print(f"24h Change: {ticker['change_24h']:+.2f}%")
        print(f"24h Volume: ${ticker['volume_24h']:,.0f}")

        # Detect patterns
        print("\nDetecting patterns...", end=" ")
        patterns = self.pattern_recognition.analyze_chart(df, symbol)
        print(f"✓ {len(patterns)} patterns found")

        # Display patterns
        if patterns:
            self._display_patterns(patterns, symbol)

            # Generate chart for best pattern
            if generate_chart:
                print("\nGenerating chart...", end=" ")
                chart_path = self.chart_generator.create_pattern_chart(
                    df, symbol, patterns[0]
                )
                print(f"✓ Saved to {chart_path}")

            # AI analysis for best pattern
            if self.ai_analyzer.client and patterns:
                print("\n🤖 AI Analysis")
                print("-" * 50)
                market_context = {
                    'current_price': ticker['price'],
                    'change_24h': ticker['change_24h'],
                    'volume_24h': ticker['volume_24h'],
                    'timeframe': timeframe
                }
                analysis = self.ai_analyzer.analyze_pattern(
                    patterns[0], symbol, market_context
                )
                print(analysis)
        else:
            print("\n⚠️  No high-confidence patterns detected")
            print("Consider checking again later or adjusting timeframe")

    def scan_watchlist(self):
        """Scan entire watchlist for setups"""
        print("\n🔎 Scanning Watchlist for Setups")
        print("=" * 50)

        watchlist = Config.get_watchlist()
        all_setups = []

        for symbol in watchlist:
            print(f"\n{symbol}...", end=" ")

            df = self.market_data.get_ohlcv(symbol, timeframe="4h", limit=100)
            if df.empty:
                print("✗")
                continue

            patterns = self.pattern_recognition.analyze_chart(df, symbol)

            if patterns:
                print(f"✓ {len(patterns)} patterns")
                for pattern in patterns:
                    all_setups.append({
                        'symbol': symbol,
                        'pattern': pattern
                    })
            else:
                print("○ No patterns")

        # Display summary
        print("\n" + "=" * 50)
        print(f"FOUND {len(all_setups)} TOTAL SETUPS")
        print("=" * 50)

        if all_setups:
            # Sort by confidence
            all_setups.sort(key=lambda x: x['pattern'].confidence, reverse=True)

            for i, setup in enumerate(all_setups[:5], 1):  # Top 5
                pattern = setup['pattern']
                print(f"\n{i}. {setup['symbol']} - {pattern.pattern_type}")
                print(f"   Confidence: {pattern.confidence:.1%}")
                print(f"   R:R = {pattern.risk_reward:.2f}:1")
                print(f"   Entry: ${pattern.entry_zone[0]:.2f}-${pattern.entry_zone[1]:.2f}")
                print(f"   Stop: ${pattern.stop_loss:.2f}")
                print(f"   Target: ${pattern.targets[0]:.2f}")

    def _display_patterns(self, patterns: List[Pattern], symbol: str):
        """Display detected patterns"""
        for i, pattern in enumerate(patterns, 1):
            print(f"\n{'='*50}")
            print(f"PATTERN #{i}: {pattern.pattern_type}")
            print(f"{'='*50}")
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

    def _display_manual_briefing(self, watchlist_data: Dict, patterns: Dict):
        """Display manual briefing when AI unavailable"""
        print("\n🐺 DAILY MARKET BRIEF")
        print("=" * 50)

        for symbol, ticker in watchlist_data.items():
            symbol_patterns = patterns.get(symbol, [])
            status = "🔥" if symbol_patterns else "○"

            print(f"\n{status} {symbol}")
            print(f"   Price: ${ticker['price']:,.2f} ({ticker['change_24h']:+.2f}%)")
            print(f"   Volume: ${ticker['volume_24h']:,.0f}")

            if symbol_patterns:
                print(f"   Patterns: {len(symbol_patterns)}")
                for p in symbol_patterns[:1]:  # Show top pattern
                    print(f"   → {p.pattern_type} ({p.confidence:.0%} confidence)")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="🐺 Wolf Market Analyzer - AI-Powered Trading Companion"
    )

    parser.add_argument(
        "--config",
        action="store_true",
        help="Show current configuration"
    )

    parser.add_argument(
        "--brief",
        action="store_true",
        help="Generate daily market briefing"
    )

    parser.add_argument(
        "--analyze",
        type=str,
        metavar="SYMBOL",
        help="Analyze specific symbol (e.g., BTC/USDT)"
    )

    parser.add_argument(
        "--timeframe",
        type=str,
        default="4h",
        help="Timeframe for analysis (default: 4h)"
    )

    parser.add_argument(
        "--scan",
        action="store_true",
        help="Scan watchlist for setups"
    )

    parser.add_argument(
        "--no-chart",
        action="store_true",
        help="Skip chart generation"
    )

    args = parser.parse_args()

    # Initialize application
    app = WolfAnalyzer()

    # Execute commands
    if args.config:
        app.show_config()

    elif args.brief:
        app.get_daily_brief()

    elif args.analyze:
        app.analyze_symbol(
            args.analyze,
            timeframe=args.timeframe,
            generate_chart=not args.no_chart
        )

    elif args.scan:
        app.scan_watchlist()

    else:
        # Default: show help
        parser.print_help()
        print("\n" + "=" * 50)
        print("QUICK START EXAMPLES:")
        print("=" * 50)
        print("python main.py --config              # Show configuration")
        print("python main.py --brief               # Daily market briefing")
        print("python main.py --analyze BTC/USDT    # Analyze Bitcoin")
        print("python main.py --scan                # Scan watchlist")
        print("=" * 50)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Exiting Wolf Market Analyzer...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if Config.DEBUG_MODE:
            raise
        sys.exit(1)
