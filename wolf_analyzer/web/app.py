"""
Wolf Market Analyzer - Web Dashboard
Flask-based web interface for market analysis
"""

from flask import Flask, render_template, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
import sys
import os
import traceback
from collections import deque
import io
import base64
import logging
from logging.handlers import RotatingFileHandler
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Render
import matplotlib.pyplot as plt
import mplfinance as mpf

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from wolf_analyzer.core.config import Config
from wolf_analyzer.data.market_data import MarketDataConnector
from wolf_analyzer.analysis.pattern_recognition import PatternRecognition
from wolf_analyzer.analysis.technical_indicators import TechnicalIndicators
from wolf_analyzer.ai.claude_analyzer import ClaudeAnalyzer

# Setup logging
logs_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Create logger
logger = logging.getLogger('wolf_analyzer')
logger.setLevel(logging.INFO)

# File handler with rotation (10MB max, keep 3 backups)
log_file = os.path.join(logs_dir, 'wolf_analyzer.log')
file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=3)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.info("="*80)
logger.info("Wolf Market Analyzer Starting")
logger.info("="*80)

app = Flask(__name__)
CORS(app)

# Debug system - store last 50 errors and 200 general logs
error_log = deque(maxlen=50)
activity_log = deque(maxlen=200)

def log_activity(message, level='INFO'):
    """Log general activity"""
    activity_entry = {
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'message': message
    }
    activity_log.append(activity_entry)

    # Also log to file
    if level == 'INFO':
        logger.info(message)
    elif level == 'WARNING':
        logger.warning(message)
    elif level == 'ERROR':
        logger.error(message)

def log_error(error, context=""):
    """Log error to debug system"""
    error_entry = {
        'timestamp': datetime.now().isoformat(),
        'error': str(error),
        'type': type(error).__name__,
        'context': context,
        'traceback': traceback.format_exc()
    }
    error_log.append(error_entry)

    # Also log to file and activity log
    error_msg = f"ERROR [{context}]: {error}"
    logger.error(error_msg)
    logger.error(traceback.format_exc())

    activity_log.append({
        'timestamp': datetime.now().isoformat(),
        'level': 'ERROR',
        'message': f"{context}: {str(error)}"
    })

    print(f"ERROR [{context}]: {error}")
    print(traceback.format_exc())

# Initialize components
try:
    market_data = MarketDataConnector()
except Exception as e:
    log_error(e, "MarketDataConnector init")
    market_data = None

try:
    pattern_recognition = PatternRecognition()
except Exception as e:
    log_error(e, "PatternRecognition init")
    pattern_recognition = None

try:
    indicators = TechnicalIndicators()
except Exception as e:
    log_error(e, "TechnicalIndicators init")
    indicators = None

try:
    ai_analyzer = ClaudeAnalyzer()
except Exception as e:
    log_error(e, "ClaudeAnalyzer init")
    ai_analyzer = None


@app.route('/')
def index():
    """Dashboard homepage"""
    return render_template('index.html',
                         watchlist=Config.get_watchlist(),
                         account_size=Config.ACCOUNT_SIZE,
                         risk_per_trade=Config.RISK_PER_TRADE_PERCENT)


@app.route('/api/status')
def api_status():
    """Get system status"""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'binance_connected': bool(Config.BINANCE_API_KEY),
        'claude_connected': bool(Config.ANTHROPIC_API_KEY),
        'watchlist_count': len(Config.get_watchlist())
    })


@app.route('/api/watchlist')
def api_watchlist():
    """Get watchlist overview"""
    log_activity("Fetching watchlist data")
    watchlist = Config.get_watchlist()
    overview = []

    for symbol in watchlist:
        try:
            ticker = market_data.get_ticker_info(symbol)
            if ticker:
                overview.append({
                    'symbol': symbol,
                    'price': ticker.get('price', 0),
                    'change_24h': ticker.get('change_24h', 0),
                    'volume_24h': ticker.get('volume_24h', 0),
                    'high_24h': ticker.get('high_24h', 0),
                    'low_24h': ticker.get('low_24h', 0)
                })
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            overview.append({
                'symbol': symbol,
                'price': 0,
                'change_24h': 0,
                'volume_24h': 0,
                'error': str(e)
            })

    return jsonify({
        'success': True,
        'data': overview,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/debug')
def api_debug():
    """Debug endpoint - show recent errors and activity"""
    return jsonify({
        'success': True,
        'errors': list(error_log),
        'total_errors': len(error_log),
        'activity': list(activity_log),
        'total_activity': len(activity_log),
        'log_file': log_file,
        'components': {
            'market_data': market_data is not None,
            'pattern_recognition': pattern_recognition is not None,
            'indicators': indicators is not None,
            'ai_analyzer': ai_analyzer is not None
        }
    })


@app.route('/logs')
def view_logs():
    """View recent logs from file"""
    try:
        # Read last 500 lines from log file
        lines = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Get last 500 lines
                lines = lines[-500:]

        return render_template('logs.html', log_lines=lines, log_file=log_file)
    except Exception as e:
        log_error(e, "view_logs")
        return f"Error reading logs: {str(e)}", 500


@app.route('/api/logs')
def api_logs():
    """API endpoint for logs (last N lines)"""
    try:
        count = int(request.args.get('count', 200))
        count = min(count, 1000)  # Max 1000 lines

        lines = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                lines = lines[-count:]

        return jsonify({
            'success': True,
            'log_file': log_file,
            'line_count': len(lines),
            'logs': ''.join(lines)
        })
    except Exception as e:
        log_error(e, "api_logs")
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/analyze/<path:symbol>')
def api_analyze(symbol):
    """Analyze specific symbol"""
    try:
        timeframe = request.args.get('timeframe', '4h')
        log_activity(f"Analyzing {symbol} ({timeframe})")

        if not market_data:
            raise Exception("MarketDataConnector not initialized")
        if not indicators:
            raise Exception("TechnicalIndicators not initialized")
        if not pattern_recognition:
            raise Exception("PatternRecognition not initialized")

        # Fetch data
        df = market_data.get_ohlcv(symbol, timeframe=timeframe, limit=200)

        if df.empty:
            # Check if API keys are configured
            has_api_keys = bool(Config.BINANCE_API_KEY and Config.BINANCE_API_SECRET)
            error_msg = 'No data available for this symbol. '
            if not has_api_keys:
                error_msg += 'Binance API keys are not configured in Render environment variables. Please add BINANCE_API_KEY and BINANCE_API_SECRET to your service settings.'
            else:
                error_msg += 'Check Render logs for detailed error information.'

            return jsonify({
                'success': False,
                'error': error_msg,
                'has_api_keys': has_api_keys
            }), 404

        # Get current price
        current_price = df['close'].iloc[-1]
        change_24h = ((df['close'].iloc[-1] / df['close'].iloc[-6] - 1) * 100) if len(df) >= 6 else 0

        # Technical indicators
        support, resistance = indicators.calculate_support_resistance(df)
        rsi = indicators.calculate_rsi(df)
        macd, signal_line, histogram = indicators.calculate_macd(df)
        trend = indicators.identify_trend(df)

        # Pattern recognition
        patterns = pattern_recognition.analyze_chart(df, symbol)

        patterns_data = []
        for pattern in patterns:
            patterns_data.append({
                'type': str(pattern.pattern_type),
                'confidence': float(pattern.confidence),
                'entry_zone': [float(x) for x in pattern.entry_zone],
                'stop_loss': float(pattern.stop_loss),
                'targets': [float(t) for t in pattern.targets],
                'risk_reward': float(pattern.risk_reward),
                'description': str(pattern.description),
                'volume_confirmation': bool(pattern.volume_confirmation),
                'institutional_signal': bool(pattern.institutional_signal)
            })

        return jsonify({
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'current_price': float(current_price),
            'change_24h': float(change_24h),
            'indicators': {
                'support': [float(s) for s in support],
                'resistance': [float(r) for r in resistance],
                'rsi': float(rsi.iloc[-1]),
                'macd': float(macd.iloc[-1]),
                'macd_signal': float(signal_line.iloc[-1]),
                'macd_histogram': float(histogram.iloc[-1]),
                'trend': trend
            },
            'patterns': patterns_data,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        log_error(e, f"api_analyze({symbol})")
        return jsonify({
            'success': False,
            'error': str(e),
            'type': type(e).__name__
        }), 500


@app.route('/api/chart/<path:symbol>')
def api_chart(symbol):
    """Generate chart image for symbol"""
    try:
        timeframe = request.args.get('timeframe', '4h')
        log_activity(f"Generating chart for {symbol} ({timeframe})")

        if not market_data:
            raise Exception("MarketDataConnector not initialized")
        if not indicators:
            raise Exception("TechnicalIndicators not initialized")
        if not pattern_recognition:
            raise Exception("PatternRecognition not initialized")

        # Fetch data
        df = market_data.get_ohlcv(symbol, timeframe=timeframe, limit=100)

        if df.empty:
            return jsonify({'success': False, 'error': 'No data available'}), 404

        # Calculate indicators for chart
        support, resistance = indicators.calculate_support_resistance(df)
        patterns = pattern_recognition.analyze_chart(df, symbol)

        # Create chart style
        mc = mpf.make_marketcolors(
            up='#26a69a',
            down='#ef5350',
            edge='inherit',
            wick='inherit',
            volume='in',
            alpha=0.9
        )

        s = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle='',
            y_on_right=False,
            facecolor='#1a1a2e',
            edgecolor='#16213e',
            figcolor='#1a1a2e',
            gridcolor='#2a2a3e'
        )

        # Prepare horizontal lines for support/resistance
        # mplfinance expects separate lists for y-values, colors, linestyles, linewidths
        hline_values = []
        hline_colors = []
        hline_styles = []
        hline_widths = []

        # Support levels (green dashed)
        if len(support) > 0:
            for sup_level in support[:3]:
                hline_values.append(float(sup_level))
                hline_colors.append('#26a69a')
                hline_styles.append('--')
                hline_widths.append(1)

        # Resistance levels (red dashed)
        if len(resistance) > 0:
            for res_level in resistance[:3]:
                hline_values.append(float(res_level))
                hline_colors.append('#ef5350')
                hline_styles.append('--')
                hline_widths.append(1)

        # Add pattern levels if available
        if patterns:
            pattern = patterns[0]  # Use first pattern
            # Entry zone (orange solid)
            if hasattr(pattern, 'entry_zone') and len(pattern.entry_zone) >= 2:
                hline_values.append(float(pattern.entry_zone[0]))
                hline_colors.append('#FFA726')
                hline_styles.append('-')
                hline_widths.append(2)
            # Stop loss (red solid)
            if hasattr(pattern, 'stop_loss'):
                hline_values.append(float(pattern.stop_loss))
                hline_colors.append('#EF5350')
                hline_styles.append('-')
                hline_widths.append(2)
            # Target (green solid)
            if hasattr(pattern, 'targets') and len(pattern.targets) > 0:
                hline_values.append(float(pattern.targets[0]))
                hline_colors.append('#66BB6A')
                hline_styles.append('-')
                hline_widths.append(2)

        # Create chart without hlines first (mplfinance hlines are problematic)
        # We'll draw lines manually on the axes instead
        fig, axes = mpf.plot(
            df,
            type='candle',
            style=s,
            title=f'{symbol} - {timeframe.upper()}',
            ylabel='Price (USDT)',
            volume=True,
            returnfig=True,
            figsize=(12, 6),
            tight_layout=True
        )

        # Draw horizontal lines manually on the price axis (more reliable)
        if hline_values:
            ax = axes[0]  # Price axis
            for i, y_val in enumerate(hline_values):
                ax.axhline(
                    y=y_val,
                    color=hline_colors[i],
                    linestyle=hline_styles[i],
                    linewidth=hline_widths[i],
                    alpha=0.7,
                    zorder=3
                )

        # Save to bytes buffer
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, facecolor='#1a1a2e')
        buf.seek(0)
        plt.close(fig)

        # Convert to base64
        img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

        return jsonify({
            'success': True,
            'image': f'data:image/png;base64,{img_base64}'
        })

    except Exception as e:
        log_error(e, f"api_chart({symbol})")
        return jsonify({
            'success': False,
            'error': str(e),
            'type': type(e).__name__
        }), 500


@app.route('/api/scan')
def api_scan():
    """Scan all watchlist for patterns"""
    try:
        watchlist = Config.get_watchlist()
        timeframe = request.args.get('timeframe', '4h')

        results = []

        for symbol in watchlist:
            try:
                # Fetch data
                df = market_data.get_ohlcv(symbol, timeframe=timeframe, limit=100)

                if df.empty:
                    continue

                # Get patterns
                patterns = pattern_recognition.analyze_chart(df, symbol)

                if patterns:
                    # Get current price
                    current_price = df['close'].iloc[-1]

                    for pattern in patterns:
                        results.append({
                            'symbol': symbol,
                            'current_price': float(current_price),
                            'pattern_type': pattern.pattern_type,
                            'confidence': pattern.confidence,
                            'risk_reward': pattern.risk_reward,
                            'entry_zone': pattern.entry_zone,
                            'stop_loss': pattern.stop_loss,
                            'targets': pattern.targets,
                            'timeframe': timeframe
                        })
            except Exception as e:
                print(f"Error scanning {symbol}: {e}")
                continue

        # Sort by confidence
        results.sort(key=lambda x: x['confidence'], reverse=True)

        return jsonify({
            'success': True,
            'count': len(results),
            'setups': results,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/brief')
def api_brief():
    """Get daily market briefing"""
    try:
        watchlist = Config.get_watchlist()

        # Get market overview
        overview = []
        all_patterns = {}

        for symbol in watchlist:
            try:
                ticker = market_data.get_ticker_info(symbol)
                df = market_data.get_ohlcv(symbol, timeframe='4h', limit=100)

                if not df.empty:
                    patterns = pattern_recognition.analyze_chart(df, symbol)

                    overview.append({
                        'symbol': symbol,
                        'price': ticker.get('price', 0),
                        'change_24h': ticker.get('change_24h', 0),
                        'patterns_count': len(patterns)
                    })

                    if patterns:
                        all_patterns[symbol] = [{
                            'type': p.pattern_type,
                            'confidence': p.confidence,
                            'risk_reward': p.risk_reward
                        } for p in patterns]
            except Exception as e:
                print(f"Error in brief for {symbol}: {e}")
                continue

        # Generate AI briefing if available
        ai_brief = None
        if ai_analyzer.client and overview:
            try:
                # Convert to proper format for AI
                watchlist_data = {item['symbol']: item for item in overview}
                ai_brief = ai_analyzer.generate_daily_brief(watchlist_data, all_patterns)
            except Exception as e:
                print(f"AI briefing error: {e}")

        return jsonify({
            'success': True,
            'overview': overview,
            'patterns': all_patterns,
            'ai_briefing': ai_brief,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/analyze')
def analyze_page():
    """Analysis page"""
    symbol = request.args.get('symbol', 'BTC/USDT')
    return render_template('analyze.html', symbol=symbol)


@app.route('/scan')
def scan_page():
    """Scan page"""
    return render_template('scan.html')


@app.route('/brief')
def brief_page():
    """Daily briefing page"""
    return render_template('brief.html')


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'Not found'}), 404
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    log_error(e, "500 Internal Server Error")
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500
    return render_template('500.html'), 500


@app.errorhandler(Exception)
def handle_exception(e):
    log_error(e, f"Unhandled exception on {request.path}")
    if request.path.startswith('/api/'):
        return jsonify({
            'success': False,
            'error': str(e),
            'type': type(e).__name__
        }), 500
    return render_template('500.html'), 500


def run_dashboard(host='0.0.0.0', port=None, debug=False):
    """Run the web dashboard"""
    if port is None:
        port = Config.PORT

    print("=" * 60)
    print("🐺 Wolf Market Analyzer - Web Dashboard")
    print("=" * 60)
    print(f"\n🌐 Starting server on http://{host}:{port}")
    print(f"📊 Watchlist: {', '.join(Config.get_watchlist())}")
    print(f"💰 Account Size: ${Config.ACCOUNT_SIZE:,.2f}")
    print(f"⚠️  Risk per Trade: {Config.RISK_PER_TRADE_PERCENT}%")
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_dashboard(debug=Config.DEBUG_MODE)
