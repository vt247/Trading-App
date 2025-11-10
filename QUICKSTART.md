# 🐺 Wolf Market Analyzer - Quick Start Guide

Get started with Wolf Market Analyzer in 5 minutes.

---

## Installation

### 1. Clone Repository (if not already done)
```bash
git clone <your-repo-url>
cd Trading-App
```

### 2. Run Setup Script
```bash
bash setup.sh
```

This will:
- Create virtual environment
- Install all dependencies
- Create .env file
- Set up directories

### 3. Configure API Keys

Edit `.env` file and add your API keys:

```bash
nano .env  # or use your preferred editor
```

**Required:**
- `BINANCE_API_KEY` - Get from [Binance API Management](https://www.binance.com/en/my/settings/api-management)
- `ANTHROPIC_API_KEY` - Get from [Anthropic Console](https://console.anthropic.com)

**Optional:**
- `TELEGRAM_BOT_TOKEN` - For notifications (get from @BotFather)

**Important:** For Binance API:
- Enable "Read Info" permission only (no trading needed for MVP)
- Whitelist your IP address for security
- Save API key and secret

### 4. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 5. Initialize Database
```bash
python -m src.database.init_db
```

---

## Your First Analysis

### Check Configuration
```bash
python main.py --config
```

This shows your current settings and confirms API connections.

### Analyze Bitcoin
```bash
python main.py --analyze BTC/USDT
```

This will:
1. Fetch latest BTC data from Binance
2. Detect FOOS4 patterns
3. Generate annotated chart
4. Provide AI analysis (if Claude API configured)

### Daily Market Brief
```bash
python main.py --brief
```

Gets overview of all symbols in your watchlist.

### Scan for Setups
```bash
python main.py --scan
```

Scans entire watchlist and shows top 5 setups by confidence.

---

## Daily Workflow (10 Minutes)

### Morning Routine (7:00 AM)
```bash
python main.py --brief
```

Review:
- Pre-market movers
- Active patterns
- Key levels to watch

### During Day (When Alerts Trigger)
```bash
python main.py --analyze <SYMBOL>
```

Check specific setup in detail before trading.

### Evening Review (5:00 PM)
Log your trades and get AI coaching (coming in Phase 2).

---

## Customization

### Edit Your Watchlist

Open `.env` and modify:
```bash
WATCHLIST=BTC/USDT,ETH/USDT,SOL/USDT,AVAX/USDT,ARB/USDT
```

### Change Default Timeframe
```bash
DEFAULT_TIMEFRAME=1h  # Options: 1m, 5m, 15m, 1h, 4h, 1d
```

### Adjust Risk Settings
```bash
ACCOUNT_SIZE=10000
RISK_PER_TRADE_PERCENT=1.0
```

---

## Understanding the Output

### Pattern Detection Example

```
PATTERN #1: Ascending Triangle
==================================================
Confidence: 78.5%
Formation Time: 72 hours

📍 ENTRY ZONE
   $42,250 - $42,350

🛑 STOP LOSS
   $41,800

🎯 TARGETS
   T1: $42,850
   T2: $43,450
   T3: $44,100

📊 RISK:REWARD
   2.85:1

✓ CONFIRMATIONS
   Volume: ✓
   Institutional: ✓

📝 DESCRIPTION
   Bullish continuation pattern with flat resistance and rising support
```

**What this means:**
- **Confidence 78.5%:** High probability setup
- **Entry Zone:** Wait for price in this range before entering
- **Stop Loss:** Exit if price drops below this (protect capital)
- **Targets:** Take profits at these levels (tiered exit)
- **R:R 2.85:1:** For every $1 risked, potential $2.85 reward
- **Volume ✓:** Volume confirms the pattern
- **Institutional ✓:** Matches institutional behavior

### Chart Files

Charts are saved in `charts/` directory:
```
charts/
  BTC_USDT_20241110_143022.png
  ETH_USDT_20241110_143145.png
```

Open these to see visual representation with:
- Entry zones (green dashed lines)
- Stop loss (red line)
- Targets (blue dotted lines)
- Pattern annotation box

---

## Troubleshooting

### "Failed to connect to Binance"

**Solution:**
1. Check internet connection
2. Verify API key in `.env` is correct
3. Check Binance API restrictions (IP whitelist)
4. Try without API key (public data only, limited)

### "AI analysis unavailable"

**Solution:**
1. Check `ANTHROPIC_API_KEY` in `.env`
2. Verify API key at [Anthropic Console](https://console.anthropic.com)
3. Check API credit balance

### "No patterns detected"

**Solution:**
1. Normal! Not all timeframes have clear patterns
2. Try different timeframe: `--timeframe 1d`
3. Check different symbol
4. Market may be in consolidation phase

### "Module not found" error

**Solution:**
```bash
source venv/bin/activate  # Activate virtual environment
pip install -r requirements.txt  # Reinstall dependencies
```

---

## Next Steps

### Phase 1: Learning (Weeks 1-4)
✓ You're here! Use the app daily to learn patterns
- Run daily brief every morning
- Analyze 2-3 setups per day
- Don't trade yet - just learn to recognize patterns

**Goal:** 70%+ pattern recognition accuracy (vs. AI)

### Phase 2: Paper Trading (Weeks 5-8)
- Log simulated trades
- Get AI coaching feedback
- Build confidence without risk

### Phase 3: Live Trading (Month 3+)
- Start with small positions
- Use proper risk management
- Scale gradually

---

## Command Reference

```bash
# Configuration
python main.py --config              # Show settings

# Analysis
python main.py --analyze BTC/USDT    # Analyze Bitcoin
python main.py --analyze ETH/USDT --timeframe 1d  # Daily chart
python main.py --analyze SOL/USDT --no-chart      # No chart generation

# Scanning
python main.py --scan                # Scan watchlist
python main.py --brief               # Daily briefing

# Database
python -m src.database.init_db       # Initialize database
```

---

## Tips for Success

### 1. Consistency Over Intensity
- 10 minutes daily beats 2 hours weekly
- Review every morning at same time
- Build the habit first

### 2. Focus on Understanding, Not Profits
- Learn WHY patterns work
- Understand institutional behavior
- Study failed patterns too

### 3. Trust the Risk:Reward
- Never enter below 2:1 R:R
- Always use stop losses
- Scale out at targets (don't get greedy)

### 4. Journal Everything
- Track which patterns you recognize
- Note emotional reactions
- Review weekly progress

### 5. Be Patient
- Week 1: Confusing
- Week 2: Starting to see patterns
- Week 4: Recognizing in real-time
- Week 8: Trading like a wolf

---

## Support

**Issues?** Check:
1. This guide
2. Main [README.md](README.md)
3. [GitHub Issues](https://github.com/your-repo/issues)

**API Documentation:**
- [Binance API Docs](https://binance-docs.github.io/apidocs/spot/en/)
- [Anthropic API Docs](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [CCXT Documentation](https://docs.ccxt.com/)

---

## Remember

**This is not a get-rich-quick tool.**

This is a learning system that teaches you to read markets like institutions do.

**Survival > Profit. Understanding > Speed.**

Ten minutes daily. Consistent. Disciplined. Focused on understanding, not greed.

That's how survivors become wealthy in trading.

🐺 **Trade like a wolf, not a sheep.**

---

*Built with FOOS4 methodology by Cameron Fous*
