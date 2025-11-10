#!/usr/bin/env python3
"""
Wolf Market Analyzer - Web Dashboard Runner
Easy launcher for the web interface
"""

import sys
import argparse

# Add src to path
sys.path.insert(0, '/home/user/Trading-App')

from src.web.app import run_dashboard
from src.core.config import Config


def main():
    parser = argparse.ArgumentParser(
        description="🐺 Wolf Market Analyzer - Web Dashboard"
    )

    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )

    parser.add_argument(
        '--port',
        type=int,
        default=Config.PORT,
        help=f'Port to bind to (default: {Config.PORT})'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )

    args = parser.parse_args()

    print("\n" + "🐺" * 30)
    print("   WOLF MARKET ANALYZER - WEB DASHBOARD")
    print("🐺" * 30 + "\n")

    # Display configuration
    print("Configuration:")
    print(f"  Watchlist: {', '.join(Config.get_watchlist())}")
    print(f"  Account Size: ${Config.ACCOUNT_SIZE:,.2f}")
    print(f"  Risk per Trade: {Config.RISK_PER_TRADE_PERCENT}%")
    print()

    # Run dashboard
    run_dashboard(
        host=args.host,
        port=args.port,
        debug=args.debug or Config.DEBUG_MODE
    )


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down web dashboard...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if Config.DEBUG_MODE:
            raise
        sys.exit(1)
