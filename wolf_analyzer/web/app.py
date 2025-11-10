"""
Wolf Market Analyzer - Web Dashboard
Flask-based web interface for market analysis
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from datetime import datetime
import sys
import os
import traceback
from collections import deque

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from wolf_analyzer.core.config import Config
from wolf_analyzer.data.market_data import MarketDataConnector
from wolf_analyzer.analysis.pattern_recognition import PatternRecognition
from wolf_analyzer.analysis.technical_indicators import TechnicalIndicators
from wolf_analyzer.ai.claude_analyzer import ClaudeAnalyzer

app = Flask(__name__)
CORS(app)

# Debug system - store last 50 errors
error_log = deque(maxlen=50)

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
    """Debug endpoint - show recent errors"""
    return jsonify({
        'success': True,
        'errors': list(error_log),
        'total_errors': len(error_log),
        'components': {
            'market_data': market_data is not None,
            'pattern_recognition': pattern_recognition is not None,
            'indicators': indicators is not None,
            'ai_analyzer': ai_analyzer is not None
        }
    })


@app.route('/api/analyze/<path:symbol>')
def api_analyze(symbol):
    """Analyze specific symbol"""
    try:
        if not market_data:
            raise Exception("MarketDataConnector not initialized")
        if not indicators:
            raise Exception("TechnicalIndicators not initialized")
        if not pattern_recognition:
            raise Exception("PatternRecognition not initialized")

        timeframe = request.args.get('timeframe', '4h')

        # Fetch data
        df = market_data.get_ohlcv(symbol, timeframe=timeframe, limit=200)

        if df.empty:
            return jsonify({
                'success': False,
                'error': 'No data available for this symbol'
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
