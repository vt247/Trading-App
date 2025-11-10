# 🌐 Wolf Market Analyzer - Web Dashboard

Modern, responsive web interface for market analysis and pattern recognition.

---

## Features

### 📊 Real-time Dashboard
- Live watchlist with 24h price changes
- System status monitoring
- Active patterns counter
- Quick navigation to analysis

### 🔍 Symbol Analysis
- Deep technical analysis
- Pattern detection with confidence scores
- Entry/Stop/Target levels visualization
- Support/Resistance levels
- RSI, MACD, and trend indicators
- Multiple timeframes (1H, 4H, 1D, 1W)

### 🔎 Watchlist Scanner
- Scan all symbols for patterns
- Confidence-based ranking
- Quick setup overview
- One-click detailed analysis

### 📰 Daily Briefing
- Market overview at a glance
- All active setups summary
- AI-powered analysis (if Claude API configured)
- Auto-refresh every 5 minutes

---

## Quick Start

### 1. Start the Web Dashboard

```bash
cd /home/user/Trading-App
source venv/bin/activate
python web_dashboard.py
```

**Default URL:** http://localhost:8080

### 2. Custom Port/Host

```bash
# Custom port
python web_dashboard.py --port 5000

# Specific host
python web_dashboard.py --host 127.0.0.1

# Debug mode
python web_dashboard.py --debug
```

### 3. Access the Dashboard

Open your web browser and go to:
- **Local:** http://localhost:8080
- **Network:** http://YOUR_IP:8080

---

## Dashboard Pages

### 🏠 Home (`/`)
**Main dashboard with:**
- System status (online/offline)
- Account configuration
- Live watchlist prices
- Quick action buttons

**Features:**
- Auto-refresh every 30 seconds
- Click any symbol to analyze
- Real-time price updates

---

### 🔍 Analyze (`/analyze?symbol=BTC/USDT`)
**Deep symbol analysis:**

**Price Info:**
- Current price
- 24h change percentage
- Current timeframe
- Trend direction

**Technical Indicators:**
- RSI with oversold/overbought signals
- MACD with bullish/bearish signals
- Support levels (detected automatically)
- Resistance levels (detected automatically)

**Patterns:**
- Pattern type (Ascending Triangle, etc.)
- Confidence percentage
- Entry zone range
- Stop loss level
- Target prices (T1, T2, T3)
- Risk:Reward ratio
- Volume confirmation status
- Institutional signal status

**Features:**
- Timeframe selector (1H, 4H, 1D, 1W)
- Auto-refresh every 60 seconds
- Responsive design

---

### 🔎 Scan (`/scan`)
**Watchlist pattern scanner:**

**Shows:**
- All detected patterns across watchlist
- Sorted by confidence (highest first)
- Quick setup overview cards
- One-click analysis button

**Each Setup Card:**
- Symbol name
- Pattern type
- Confidence percentage
- Current price
- Entry range
- Stop loss
- First target
- Risk:Reward ratio
- Link to full analysis

**Features:**
- Timeframe selector
- Takes 10-30 seconds to complete
- Real-time scanning status

---

### 📰 Brief (`/brief`)
**Daily market briefing:**

**Market Overview:**
- All watchlist symbols
- Current prices
- 24h changes
- Pattern counts per symbol

**Active Setups:**
- Grouped by symbol
- All detected patterns
- Confidence scores
- Quick analysis links

**AI Analysis:**
- AI-generated briefing (if Claude API available)
- Market sentiment
- Key levels to watch
- Trading recommendations

**Features:**
- Auto-refresh every 5 minutes
- Timestamp display
- Clean, readable format

---

## API Endpoints

### `GET /api/status`
System status check.

**Response:**
```json
{
  "status": "online",
  "timestamp": "2025-11-10T12:00:00",
  "binance_connected": true,
  "claude_connected": true,
  "watchlist_count": 5
}
```

---

### `GET /api/watchlist`
Get all watchlist symbols with current prices.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "symbol": "BTC/USDT",
      "price": 42500.00,
      "change_24h": 2.3,
      "volume_24h": 85000000,
      "high_24h": 43000,
      "low_24h": 41500
    }
  ],
  "timestamp": "2025-11-10T12:00:00"
}
```

---

### `GET /api/analyze/{symbol}?timeframe=4h`
Analyze specific symbol.

**Parameters:**
- `symbol`: Trading pair (e.g., BTC/USDT)
- `timeframe`: Optional timeframe (default: 4h)

**Response:**
```json
{
  "success": true,
  "symbol": "BTC/USDT",
  "timeframe": "4h",
  "current_price": 42500.00,
  "change_24h": 2.3,
  "indicators": {
    "support": [42000, 41500],
    "resistance": [43000, 43500],
    "rsi": 65.5,
    "macd": 125.3,
    "macd_signal": 110.2,
    "macd_histogram": 15.1,
    "trend": "bullish"
  },
  "patterns": [
    {
      "type": "Ascending Triangle",
      "confidence": 0.78,
      "entry_zone": [42250, 42350],
      "stop_loss": 41800,
      "targets": [42850, 43450, 44100],
      "risk_reward": 2.85,
      "description": "Bullish continuation...",
      "volume_confirmation": true,
      "institutional_signal": true
    }
  ]
}
```

---

### `GET /api/scan?timeframe=4h`
Scan all watchlist symbols.

**Parameters:**
- `timeframe`: Optional timeframe (default: 4h)

**Response:**
```json
{
  "success": true,
  "count": 3,
  "setups": [
    {
      "symbol": "BTC/USDT",
      "current_price": 42500,
      "pattern_type": "Ascending Triangle",
      "confidence": 0.78,
      "risk_reward": 2.85,
      "entry_zone": [42250, 42350],
      "stop_loss": 41800,
      "targets": [42850, 43450, 44100],
      "timeframe": "4h"
    }
  ]
}
```

---

### `GET /api/brief`
Get daily market briefing.

**Response:**
```json
{
  "success": true,
  "overview": [
    {
      "symbol": "BTC/USDT",
      "price": 42500,
      "change_24h": 2.3,
      "patterns_count": 1
    }
  ],
  "patterns": {
    "BTC/USDT": [
      {
        "type": "Ascending Triangle",
        "confidence": 0.78,
        "risk_reward": 2.85
      }
    ]
  },
  "ai_briefing": "Market analysis text...",
  "timestamp": "2025-11-10T12:00:00"
}
```

---

## Configuration

Edit `.env` file:

```bash
# Server settings
PORT=8080
HOST=0.0.0.0

# API Keys (for live data)
BINANCE_API_KEY=your_key
BINANCE_API_SECRET=your_secret
ANTHROPIC_API_KEY=your_key

# Watchlist
WATCHLIST=BTC/USDT,ETH/USDT,SOL/USDT
```

---

## Responsive Design

### Desktop (1400px+)
- Full dashboard grid (3-4 columns)
- All indicators visible
- Large charts and cards

### Tablet (768px - 1400px)
- Responsive grid (2 columns)
- Adjusted spacing
- Touch-friendly buttons

### Mobile (< 768px)
- Single column layout
- Stacked navigation
- Optimized for small screens
- Touch gestures

---

## Theme

### Dark Mode (Default)
- Background: `#1a1a2e` (dark blue)
- Cards: `#16213e` (darker blue)
- Primary: `#26a69a` (teal green)
- Danger: `#ef5350` (red)
- Text: `#eaeaea` (light gray)

### Customization
Edit `src/web/static/css/style.css` to change colors:

```css
:root {
    --primary-color: #26a69a;
    --danger-color: #ef5350;
    --dark-bg: #1a1a2e;
    --card-bg: #16213e;
    /* ... */
}
```

---

## Development

### Run in Debug Mode
```bash
python web_dashboard.py --debug
```

**Debug features:**
- Auto-reload on code changes
- Detailed error messages
- Stack traces in browser

### Add New Pages

1. Create template in `src/web/templates/`
2. Add route in `src/web/app.py`
3. Add navigation link in `base.html`

### Add New API Endpoints

```python
# src/web/app.py

@app.route('/api/your-endpoint')
def your_endpoint():
    try:
        # Your logic here
        return jsonify({
            'success': True,
            'data': {}
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

---

## Deployment

### Local Network Access

1. Find your IP address:
```bash
# Linux/Mac
ifconfig | grep "inet "

# Windows
ipconfig
```

2. Start dashboard:
```bash
python web_dashboard.py --host 0.0.0.0
```

3. Access from any device on network:
```
http://YOUR_IP:8080
```

### Production Deployment

#### Railway.app
```bash
# Install Railway CLI
npm install -g @railway/cli

# Deploy
railway login
railway init
railway up
```

#### Heroku
```bash
# Create Procfile
echo "web: python web_dashboard.py --port $PORT" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

#### VPS (Ubuntu/Debian)
```bash
# Install dependencies
sudo apt update
sudo apt install python3-pip nginx

# Setup app
cd /opt
git clone your-repo
cd Trading-App
pip3 install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/wolf-analyzer.service

# Start service
sudo systemctl enable wolf-analyzer
sudo systemctl start wolf-analyzer

# Setup nginx reverse proxy
sudo nano /etc/nginx/sites-available/wolf-analyzer
```

---

## Performance

### Optimization Tips

1. **Caching:** Add Redis for API response caching
2. **CDN:** Serve static files from CDN
3. **Compression:** Enable gzip compression
4. **Database:** Use PostgreSQL for production
5. **Workers:** Use Gunicorn with multiple workers

### Example Production Setup

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 -b 0.0.0.0:8080 src.web.app:app
```

---

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8080
lsof -i :8080

# Kill process
kill -9 PID

# Or use different port
python web_dashboard.py --port 5000
```

### Can't Access from Network
```bash
# Check firewall
sudo ufw allow 8080

# Check if binding to 0.0.0.0
python web_dashboard.py --host 0.0.0.0
```

### API Errors
```bash
# Check API keys in .env
cat .env

# Test Binance connection
python -c "from src.data.market_data import MarketDataConnector; m = MarketDataConnector(); print(m.get_current_price('BTC/USDT'))"

# Enable debug mode
python web_dashboard.py --debug
```

---

## Security

### Production Checklist

- [ ] Change `DEBUG_MODE=False` in .env
- [ ] Use HTTPS (SSL certificate)
- [ ] Set strong `SECRET_KEY` for Flask
- [ ] Enable CORS only for trusted domains
- [ ] Use environment variables (not .env in production)
- [ ] Set up authentication (if exposing publicly)
- [ ] Use rate limiting on API endpoints
- [ ] Keep dependencies updated
- [ ] Monitor logs for suspicious activity

---

## Browser Support

### Tested Browsers
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

### Required Features
- JavaScript ES6+
- Fetch API
- CSS Grid
- CSS Flexbox

---

## Screenshots

### Dashboard
![Dashboard View](Coming Soon)

### Symbol Analysis
![Analysis View](Coming Soon)

### Pattern Scanner
![Scanner View](Coming Soon)

---

## Future Enhancements

- [ ] Real-time WebSocket updates
- [ ] Chart.js integration for price charts
- [ ] User authentication system
- [ ] Trade journal UI
- [ ] Portfolio tracking
- [ ] Alert notifications
- [ ] Email/SMS alerts
- [ ] Mobile app (React Native)

---

**Built with Flask, JavaScript, and CSS**
**🐺 Trade like a wolf, not a sheep**
