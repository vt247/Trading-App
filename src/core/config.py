"""
Configuration Management for Wolf Market Analyzer
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""

    # Project paths
    BASE_DIR = Path(__file__).parent.parent.parent
    CHARTS_DIR = BASE_DIR / "charts"
    DATA_DIR = BASE_DIR / "data"

    # Exchange API
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET", "")

    # Anthropic Claude API
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # Telegram Bot
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

    # Trading Settings
    ACCOUNT_SIZE = float(os.getenv("ACCOUNT_SIZE", "10000"))
    RISK_PER_TRADE_PERCENT = float(os.getenv("RISK_PER_TRADE_PERCENT", "1.0"))
    DEFAULT_TIMEFRAME = os.getenv("DEFAULT_TIMEFRAME", "4h")

    # Watchlist
    @staticmethod
    def get_watchlist() -> List[str]:
        """Get trading watchlist from environment"""
        watchlist_str = os.getenv("WATCHLIST", "BTC/USDT,ETH/USDT,SOL/USDT")
        return [asset.strip() for asset in watchlist_str.split(",")]

    # App Settings
    TIMEZONE = os.getenv("TIMEZONE", "Europe/Helsinki")
    DAILY_BRIEF_TIME = os.getenv("DAILY_BRIEF_TIME", "07:00")
    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/wolf_analyzer.db")

    # Server
    PORT = int(os.getenv("PORT", "8080"))
    HOST = os.getenv("HOST", "0.0.0.0")

    # Pattern Recognition Settings
    PATTERN_CONFIDENCE_THRESHOLD = 0.65  # Minimum 65% confidence
    MIN_RISK_REWARD_RATIO = 2.0  # Minimum 2:1 R:R

    # Historical Analysis
    HISTORICAL_LOOKBACK_DAYS = 180  # 6 months of historical data
    SIMILAR_PATTERN_THRESHOLD = 0.75  # 75% similarity for historical matches

    @classmethod
    def validate(cls) -> bool:
        """Validate that required configuration is present"""
        required_keys = []

        # Check API keys based on usage
        if not cls.BINANCE_API_KEY:
            print("⚠️  Warning: BINANCE_API_KEY not set. Market data will be limited.")

        if not cls.ANTHROPIC_API_KEY:
            print("⚠️  Warning: ANTHROPIC_API_KEY not set. AI analysis will be disabled.")

        # Create required directories
        cls.CHARTS_DIR.mkdir(exist_ok=True)
        cls.DATA_DIR.mkdir(exist_ok=True)

        return True

    @classmethod
    def display(cls):
        """Display current configuration (safe - no secrets)"""
        print("🐺 Wolf Market Analyzer Configuration")
        print("=" * 50)
        print(f"Account Size: ${cls.ACCOUNT_SIZE:,.2f}")
        print(f"Risk per Trade: {cls.RISK_PER_TRADE_PERCENT}%")
        print(f"Default Timeframe: {cls.DEFAULT_TIMEFRAME}")
        print(f"Watchlist: {', '.join(cls.get_watchlist())}")
        print(f"Timezone: {cls.TIMEZONE}")
        print(f"Daily Brief Time: {cls.DAILY_BRIEF_TIME}")
        print(f"Debug Mode: {cls.DEBUG_MODE}")
        print(f"Database: {cls.DATABASE_URL}")
        print(f"Binance API: {'✓ Connected' if cls.BINANCE_API_KEY else '✗ Not configured'}")
        print(f"Claude AI: {'✓ Connected' if cls.ANTHROPIC_API_KEY else '✗ Not configured'}")
        print(f"Telegram: {'✓ Connected' if cls.TELEGRAM_BOT_TOKEN else '✗ Not configured'}")
        print("=" * 50)


# Validate configuration on import
Config.validate()
