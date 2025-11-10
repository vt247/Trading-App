# 🐺 Wolf Market Analyzer

**AI-Powered Daily Trading Companion** - Learn to read markets like an institutional trader using the FOOS4 methodology.

## Overview

Wolf Market Analyzer is not a trading bot. It's an educational tool that teaches you to recognize institutional patterns, understand market psychology, and trade with discipline. The app analyzes charts in real-time, identifies critical patterns, and guides you from reactive trading (sheep) to anticipatory trading (wolf).

## Features

- 📊 **Real-time Pattern Recognition** - FOOS4 methodology (triangles, support/resistance, volume analysis)
- 🧠 **AI-Powered Analysis** - Claude AI interprets patterns and provides context
- 📈 **Historical Context** - "What happened last time we saw this pattern?"
- 🎯 **Entry/Exit Framework** - Precise levels with risk:reward calculations
- 📝 **Trade Journaling** - AI coaching feedback on your decisions
- 📱 **Telegram Alerts** - Daily briefings and setup notifications
- 🌐 **Web Dashboard** - Visual interface for analysis

## Installation

### Prerequisites
- Python 3.9 or higher
- Binance account (for market data API)
- Anthropic API key (for Claude AI)
- Telegram bot token (optional, for notifications)

### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Trading-App
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and settings
```

5. **Initialize database**
```bash
python -m src.database.init_db
```

6. **Run the application**
```bash
python main.py
```

## Quick Start

### Daily Routine (10 minutes)

**Morning (7:00 AM)**
```bash
python main.py --brief
```
Get your pre-market briefing and watchlist status.

**During Day**
```bash
python main.py --scan
```
Scan for active setups and alerts.

**Evening**
```bash
python main.py --journal
```
Log your trades and get AI coaching feedback.

## Configuration

Edit `.env` file to customize:

```bash
# Your watchlist
WATCHLIST=BTC/USDT,ETH/USDT,SOL/USDT,AVAX/USDT

# Trading parameters
ACCOUNT_SIZE=10000
RISK_PER_TRADE_PERCENT=1.0

# Your timezone
TIMEZONE=Europe/Helsinki
DAILY_BRIEF_TIME=07:00
```

## Project Structure

```
Trading-App/
├── src/
│   ├── core/              # Core application logic
│   ├── data/              # Market data handling
│   ├── analysis/          # Pattern recognition & analysis
│   ├── ai/                # Claude AI integration
│   ├── notifications/     # Telegram bot
│   ├── journal/           # Trade journaling
│   ├── database/          # Database models
│   └── web/               # Web dashboard
├── tests/                 # Unit tests
├── charts/                # Generated charts
├── main.py                # Application entry point
├── requirements.txt       # Dependencies
└── README.md
```

## Usage Examples

### Analyze a specific asset
```bash
python main.py --analyze BTC/USDT --timeframe 4h
```

### Get pattern analysis
```bash
python main.py --patterns --asset ETH/USDT
```

### Start web dashboard
```bash
python main.py --web
```

### Enable Telegram notifications
```bash
python main.py --telegram --daemon
```

## Learning Path

### Phase 1: Learning (Weeks 1-4)
- Paper trading only
- Learn to recognize patterns
- Understand institutional behavior
- Goal: 70%+ pattern recognition accuracy

### Phase 2: Validation (Weeks 5-8)
- Small real trades ($200-500)
- Test your understanding
- Build confidence
- Maintain 2:1 risk:reward minimum

### Phase 3: Scale (Month 3+)
- Proper position sizing
- Consistent profitability
- Adapt to market conditions

## Safety & Disclaimers

⚠️ **IMPORTANT**
- This is an educational tool, not financial advice
- Past performance does not guarantee future results
- Never risk more than 1-2% of your account per trade
- Markets can be unpredictable - always use stop losses
- Start with paper trading before using real money

## API Keys & Security

### Binance API
1. Go to Binance API Management
2. Create new API key
3. Enable "Read" permissions only (no trading permissions needed for MVP)
4. Whitelist your IP address
5. Add to `.env` file

### Anthropic API
1. Sign up at console.anthropic.com
2. Generate API key
3. Add to `.env` file

### Telegram Bot
1. Message @BotFather on Telegram
2. Create new bot with /newbot
3. Copy token to `.env` file
4. Get your chat ID from @userinfobot

## Development

### Run tests
```bash
pytest tests/
```

### Code formatting
```bash
black src/
flake8 src/
```

## Deployment

### Railway.app
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

## Roadmap

- [x] Phase 1: Core architecture
- [ ] Phase 1: Market data connector
- [ ] Phase 1: Pattern recognition
- [ ] Phase 1: Basic CLI
- [ ] Phase 2: Claude AI integration
- [ ] Phase 2: Historical analysis
- [ ] Phase 2: Trade journal
- [ ] Phase 3: Telegram bot
- [ ] Phase 3: Web dashboard
- [ ] Phase 4: Railway deployment

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: [Wiki section]

## License

MIT License - See LICENSE file for details

## Acknowledgments

Built with:
- CCXT for exchange connectivity
- Anthropic Claude for AI analysis
- FOOS4 methodology by Cameron Fous

---

**Remember:** Survival > Profit. Understanding > Speed.

*Learn to see the battle between institutions and retail. Trade like a wolf, not a sheep.* 🐺
