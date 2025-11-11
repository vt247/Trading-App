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
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Render
import matplotlib.pyplot as plt
import mplfinance as mpf

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from wolf_analyzer.core.config import Config
from wolf_analyzer.data.market_data import MarketDataConnector
from wolf_analyzer.data.historical_manager import HistoricalDataManager
from wolf_analyzer.analysis.pattern_recognition import PatternRecognition
from wolf_analyzer.analysis.foos_patterns import FOOSPatternDetector
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
    historical_manager = HistoricalDataManager(market_data)
    logger.info("✓ Historical Data Manager initialized")
except Exception as e:
    log_error(e, "HistoricalDataManager init")
    historical_manager = None

try:
    pattern_recognition = PatternRecognition()
except Exception as e:
    log_error(e, "PatternRecognition init")
    pattern_recognition = None

try:
    foos_detector = FOOSPatternDetector(min_confidence=0.65)
    logger.info("✓ FOOS Pattern Detector initialized")
except Exception as e:
    log_error(e, "FOOSPatternDetector init")
    foos_detector = None

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
    """Analyze specific symbol with FOOS methodology"""
    try:
        timeframe = request.args.get('timeframe', '4h')
        log_activity(f"Analyzing {symbol} ({timeframe}) with FOOS")

        if not market_data:
            raise Exception("MarketDataConnector not initialized")
        if not indicators:
            raise Exception("TechnicalIndicators not initialized")
        if not foos_detector:
            raise Exception("FOOSPatternDetector not initialized")

        # Try to get data from historical database first (more reliable)
        df = None
        errors = []

        if historical_manager:
            try:
                log_activity(f"Attempting to fetch historical data for {symbol}...")
                # Ensure we have recent data (last 30 days is enough for analysis)
                historical_manager.ensure_data(symbol, timeframe, lookback_days=30)
                # Get last 500 candles from database
                df = historical_manager.db.get_ohlcv(symbol, timeframe, lookback_days=30)
                if not df.empty:
                    df = df.tail(500)  # Use last 500 candles
                    log_activity(f"✓ Using historical data for {symbol} ({len(df)} candles)")
                else:
                    msg = "Historical database is empty (first run or no data stored)"
                    log_activity(msg, level='WARNING')
                    errors.append(msg)
            except Exception as e:
                msg = f"Historical data error: {type(e).__name__}: {str(e)}"
                log_activity(msg, level='WARNING')
                errors.append(msg)

        # Fallback to live API if historical data unavailable
        if df is None or df.empty:
            try:
                log_activity(f"Attempting live API fetch for {symbol}...")
                df = market_data.get_ohlcv(symbol, timeframe=timeframe, limit=500)
                if not df.empty:
                    log_activity(f"✓ Using live API data for {symbol} ({len(df)} candles)")
                else:
                    msg = "Live API returned empty data"
                    log_activity(msg, level='ERROR')
                    errors.append(msg)
            except Exception as e:
                msg = f"Live API error: {type(e).__name__}: {str(e)}"
                log_activity(msg, level='ERROR')
                errors.append(msg)

        if df is None or df.empty:
            has_api_keys = bool(Config.BINANCE_API_KEY and Config.BINANCE_API_SECRET)
            error_msg = f'No data available for {symbol}. '
            if not has_api_keys:
                error_msg += 'Binance API keys are not configured in Render environment variables.'
            else:
                error_msg += 'Errors encountered: ' + ' | '.join(errors) if errors else 'Unknown error.'

            log_activity(f"Failed to fetch data for {symbol}: {error_msg}", level='ERROR')

            return jsonify({
                'success': False,
                'error': error_msg,
                'has_api_keys': has_api_keys,
                'errors': errors
            }), 404

        # Current price info
        current_price = df['close'].iloc[-1]
        change_24h = ((df['close'].iloc[-1] / df['close'].iloc[-6] - 1) * 100) if len(df) >= 6 else 0

        # FOOS Indicators
        foos_indicators = indicators.calculate_foos_indicators(df)
        ema_13 = foos_indicators['ema_13'].iloc[-1] if not foos_indicators['ema_13'].empty else None
        ma_50 = foos_indicators['ma_50'].iloc[-1] if not foos_indicators['ma_50'].empty else None
        ma_200 = foos_indicators['ma_200'].iloc[-1] if not foos_indicators['ma_200'].empty else None
        vwap = foos_indicators['vwap'].iloc[-1] if not foos_indicators['vwap'].empty else None

        # Price position relative to indicators
        price_position = indicators.get_price_position(df)

        # Traditional indicators (keeping for compatibility)
        rsi = indicators.calculate_rsi(df)
        macd, signal_line, histogram = indicators.calculate_macd(df)

        # FOOS Pattern Detection
        foos_patterns = foos_detector.detect_patterns(df, symbol)

        patterns_data = []
        for pattern in foos_patterns:
            patterns_data.append({
                'type': str(pattern.pattern_type),
                'confidence': float(pattern.confidence),
                'detected_at': pattern.detected_at.isoformat(),
                'phase_1_start': int(pattern.phase_1_start),
                'phase_2_start': int(pattern.phase_2_start),
                'phase_3_breakout': int(pattern.phase_3_breakout),
                'neckline_price': float(pattern.neckline_price),
                'neckline_touches': int(pattern.neckline_touches),
                'entry_low': float(pattern.entry_low),
                'entry_high': float(pattern.entry_high),
                'stop_loss': float(pattern.stop_loss),
                'targets': [float(pattern.target_1), float(pattern.target_2), float(pattern.target_3)],
                'risk_reward': float(pattern.risk_reward),
                'lead_in_trend': str(pattern.lead_in_trend),
                'consolidation_days': int(pattern.consolidation_days),
                'volume_spike_confirmed': bool(pattern.volume_spike_confirmed),
                'ema_13_position': str(pattern.ema_13_position),
                'neckline_coords': {
                    'start_idx': int(pattern.neckline_start_idx),
                    'end_idx': int(pattern.neckline_end_idx)
                },
                'trendline_coords': {
                    'start_idx': int(pattern.trendline_start_idx),
                    'end_idx': int(pattern.trendline_end_idx),
                    'slope': float(pattern.trendline_slope)
                },
                'description': str(pattern.description),
                'notes': str(pattern.notes)
            })

        return jsonify({
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'current_price': float(current_price),
            'change_24h': float(change_24h),
            'foos_indicators': {
                'ema_13': float(ema_13) if ema_13 else None,
                'ma_50': float(ma_50) if ma_50 else None,
                'ma_200': float(ma_200) if ma_200 else None,
                'vwap': float(vwap) if vwap else None,
                'price_position': price_position
            },
            'traditional_indicators': {
                'rsi': float(rsi.iloc[-1]) if not rsi.empty else None,
                'macd': float(macd.iloc[-1]) if not macd.empty else None,
                'macd_signal': float(signal_line.iloc[-1]) if not signal_line.empty else None,
                'macd_histogram': float(histogram.iloc[-1]) if not histogram.empty else None
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
    """Generate FOOS-style chart with indicators and patterns"""
    try:
        timeframe = request.args.get('timeframe', '4h')
        log_activity(f"Generating FOOS chart for {symbol} ({timeframe})")

        if not market_data:
            raise Exception("MarketDataConnector not initialized")
        if not indicators:
            raise Exception("TechnicalIndicators not initialized")
        if not foos_detector:
            raise Exception("FOOSPatternDetector not initialized")

        # Fetch more data for pattern context (500 candles)
        df = market_data.get_ohlcv(symbol, timeframe=timeframe, limit=500)

        if df.empty:
            return jsonify({'success': False, 'error': 'No data available'}), 404

        # Show last 100 candles on chart (but use all 500 for pattern detection)
        df_display = df.tail(100).copy()

        # Calculate FOOS indicators on full dataset
        foos_indicators = indicators.calculate_foos_indicators(df)
        ema_13 = foos_indicators['ema_13']
        ma_50 = foos_indicators['ma_50']
        ma_200 = foos_indicators['ma_200']

        # Detect FOOS patterns on full dataset
        foos_patterns = foos_detector.detect_patterns(df, symbol)

        # Create FOOS chart style (white up candles, red down candles - Cameron Fous style)
        mc = mpf.make_marketcolors(
            up='white',
            down='#ef5350',
            edge='inherit',
            wick='inherit',
            volume='in',
            alpha=0.9
        )

        foos_style = mpf.make_mpf_style(
            marketcolors=mc,
            gridstyle='',
            y_on_right=False,
            facecolor='#1a1a2e',
            edgecolor='#16213e',
            figcolor='#1a1a2e',
            gridcolor='#2a2a3e'
        )

        # Prepare additional plots for FOOS indicators
        # mplfinance requires these as lists of (index, value) tuples
        ema_13_display = ema_13.tail(100)
        ma_50_display = ma_50.tail(100)
        ma_200_display = ma_200.tail(100)

        addplot_lines = [
            # 13 EMA (YELLOW - primary trend)
            mpf.make_addplot(ema_13_display, color='#FFD700', width=2, alpha=0.9, label='13 EMA'),
            # 50 MA (PINK - medium-term)
            mpf.make_addplot(ma_50_display, color='#FF69B4', width=2, alpha=0.8, label='50 MA'),
            # 200 MA (BLUE - long-term)
            mpf.make_addplot(ma_200_display, color='#00BFFF', width=2, alpha=0.8, label='200 MA')
        ]

        # Create chart
        fig, axes = mpf.plot(
            df_display,
            type='candle',
            style=foos_style,
            title=f'{symbol} - {timeframe.upper()} (FOOS Analysis)',
            ylabel='Price (USDT)',
            volume=True,
            addplot=addplot_lines,
            returnfig=True,
            figsize=(16, 9),
            tight_layout=True
        )

        ax_price = axes[0]  # Price axis

        # === DRAW FOOS PATTERNS ===
        if foos_patterns:
            pattern = foos_patterns[0]  # Use best pattern (highest confidence)

            # Calculate display indices (since we're showing last 100 candles)
            display_offset = len(df) - 100

            # === RISK ZONE (Entry to Stop Loss) - RED background ===
            if pattern.entry_high and pattern.stop_loss:
                ax_price.axhspan(
                    min(pattern.entry_high, pattern.stop_loss),
                    max(pattern.entry_high, pattern.stop_loss),
                    alpha=0.12,
                    color='#EF5350',
                    zorder=1
                )

            # === PROFIT ZONE (Entry to Target) - GREEN background ===
            if pattern.entry_high and pattern.target_1:
                ax_price.axhspan(
                    min(pattern.entry_high, pattern.target_1),
                    max(pattern.entry_high, pattern.target_1),
                    alpha=0.10,
                    color='#66BB6A',
                    zorder=1
                )

            # === NECKLINE (Flat Resistance) ===
            neckline_start_idx = max(0, pattern.neckline_start_idx - display_offset)
            neckline_end_idx = max(0, pattern.neckline_end_idx - display_offset)

            if neckline_start_idx >= 0 and neckline_end_idx <= 100:
                ax_price.plot(
                    [neckline_start_idx, neckline_end_idx],
                    [pattern.neckline_price, pattern.neckline_price],
                    color='#EF5350',
                    linestyle='-',
                    linewidth=2.5,
                    alpha=0.85,
                    label=f'Neckline: ${pattern.neckline_price:,.2f}'
                )

            # === ASCENDING TRENDLINE (Rising Support) ===
            trendline_start_idx = max(0, pattern.trendline_start_idx - display_offset)
            trendline_end_idx = max(0, pattern.trendline_end_idx - display_offset)

            if trendline_start_idx >= 0 and trendline_end_idx <= 100:
                # Calculate trendline Y values
                trendline_start_price = df.iloc[pattern.trendline_start_idx]['low']
                trendline_end_price = df.iloc[pattern.trendline_end_idx]['low']

                ax_price.plot(
                    [trendline_start_idx, trendline_end_idx],
                    [trendline_start_price, trendline_end_price],
                    color='#26a69a',
                    linestyle='-',
                    linewidth=2.5,
                    alpha=0.85,
                    label='Ascending Trendline'
                )

            # === ENTRY/SL/TP LINES ===
            ax_price.axhline(y=pattern.entry_high, color='#FFA726', linestyle='--',
                           linewidth=2, alpha=0.8, label=f'Entry: ${pattern.entry_high:,.2f}')
            ax_price.axhline(y=pattern.stop_loss, color='#EF5350', linestyle='-',
                           linewidth=3, alpha=0.9, label=f'SL: ${pattern.stop_loss:,.2f}')
            ax_price.axhline(y=pattern.target_1, color='#66BB6A', linestyle='-',
                           linewidth=3, alpha=0.9, label=f'TP1: ${pattern.target_1:,.2f}')

            # === PHASE ANNOTATIONS ===
            phase_2_idx = max(0, pattern.phase_2_start - display_offset)
            phase_3_idx = max(0, pattern.phase_3_breakout - display_offset)

            if 0 <= phase_2_idx <= 100:
                ax_price.annotate('Phase 2\n(Consolidation)',
                                xy=(phase_2_idx, pattern.neckline_price * 1.02),
                                xytext=(phase_2_idx, pattern.neckline_price * 1.05),
                                fontsize=9, color='#FFA726',
                                ha='center',
                                bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a2e', alpha=0.8))

            if 0 <= phase_3_idx <= 100:
                ax_price.annotate('Phase 3\n(Breakout!)',
                                xy=(phase_3_idx, pattern.neckline_price),
                                xytext=(phase_3_idx, pattern.neckline_price * 1.06),
                                arrowprops=dict(arrowstyle='->', color='#66BB6A', lw=2),
                                fontsize=10, color='#66BB6A', weight='bold',
                                ha='center',
                                bbox=dict(boxstyle='round,pad=0.3', facecolor='#1a1a2e', alpha=0.9))

            # === PATTERN INFO BOX ===
            pattern_text = f"🎯 {pattern.pattern_type.upper()}\n"
            pattern_text += f"Confidence: {pattern.confidence:.0%}\n"
            pattern_text += f"R:R {pattern.risk_reward:.2f}:1\n"
            pattern_text += f"Lead-in: {pattern.lead_in_trend.title()}\n"
            pattern_text += f"Consolidation: {pattern.consolidation_days} candles"

            ax_price.text(
                0.02, 0.98, pattern_text,
                transform=ax_price.transAxes,
                fontsize=10,
                verticalalignment='top',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#1a1a2e', alpha=0.95,
                         edgecolor='#FFA726', linewidth=2.5),
                color='#FFA726',
                weight='bold',
                family='monospace'
            )

            # Add legend
            ax_price.legend(loc='upper right', fontsize=8, framealpha=0.95,
                          facecolor='#1a1a2e', edgecolor='#2a2a3e')

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


@app.route('/api/chart_data/<path:symbol>')
def api_chart_data(symbol):
    """Get 2 years of historical data for interactive chart"""
    try:
        timeframe = request.args.get('timeframe', '4h')
        log_activity(f"Fetching chart data for {symbol} ({timeframe}) - 2 years")

        if not market_data:
            raise Exception("MarketDataConnector not initialized")
        if not historical_manager:
            raise Exception("HistoricalDataManager not initialized")
        if not indicators:
            raise Exception("TechnicalIndicators not initialized")
        if not foos_detector:
            raise Exception("FOOSPatternDetector not initialized")

        # Ensure we have 2 years of historical data
        historical_manager.ensure_data(symbol, timeframe, lookback_days=730)

        # Fetch all available data from database
        df = historical_manager.db.get_ohlcv(symbol, timeframe, lookback_days=730)

        if df.empty:
            return jsonify({'success': False, 'error': 'No data available'}), 404

        # Calculate FOOS indicators
        foos_indicators = indicators.calculate_foos_indicators(df)
        ema_13 = foos_indicators['ema_13']
        ma_50 = foos_indicators['ma_50']
        ma_200 = foos_indicators['ma_200']

        # Detect FOOS patterns
        foos_patterns = foos_detector.detect_patterns(df, symbol)

        # Format data for Lightweight Charts
        candlestick_data = []
        ema13_data = []
        ma50_data = []
        ma200_data = []

        for idx in range(len(df)):
            row = df.iloc[idx]
            timestamp = int(df.index[idx].timestamp())  # Unix timestamp in seconds

            candlestick_data.append({
                'time': timestamp,
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume'])
            })

            # Add indicators (skip NaN values)
            if not pd.isna(ema_13.iloc[idx]):
                ema13_data.append({
                    'time': timestamp,
                    'value': float(ema_13.iloc[idx])
                })

            if not pd.isna(ma_50.iloc[idx]):
                ma50_data.append({
                    'time': timestamp,
                    'value': float(ma_50.iloc[idx])
                })

            if not pd.isna(ma_200.iloc[idx]):
                ma200_data.append({
                    'time': timestamp,
                    'value': float(ma_200.iloc[idx])
                })

        # Format patterns for drawing
        patterns_data = []
        for pattern in foos_patterns:
            # Get timestamps for pattern coordinates
            neckline_start_ts = int(df.index[pattern.neckline_start_idx].timestamp())
            neckline_end_ts = int(df.index[pattern.neckline_end_idx].timestamp())
            trendline_start_ts = int(df.index[pattern.trendline_start_idx].timestamp())
            trendline_end_ts = int(df.index[pattern.trendline_end_idx].timestamp())

            # Calculate trendline prices
            trendline_start_price = float(df.iloc[pattern.trendline_start_idx]['low'])
            trendline_end_price = trendline_start_price + (pattern.trendline_slope * (pattern.trendline_end_idx - pattern.trendline_start_idx))

            patterns_data.append({
                'type': str(pattern.pattern_type),
                'confidence': float(pattern.confidence),
                'neckline': {
                    'start_time': neckline_start_ts,
                    'end_time': neckline_end_ts,
                    'price': float(pattern.neckline_price)
                },
                'trendline': {
                    'start_time': trendline_start_ts,
                    'end_time': trendline_end_ts,
                    'start_price': trendline_start_price,
                    'end_price': float(trendline_end_price)
                },
                'entry_high': float(pattern.entry_high),
                'entry_low': float(pattern.entry_low),
                'stop_loss': float(pattern.stop_loss),
                'target_1': float(pattern.target_1),
                'target_2': float(pattern.target_2),
                'target_3': float(pattern.target_3),
                'description': str(pattern.description),
                'lead_in_trend': str(pattern.lead_in_trend),
                'consolidation_days': int(pattern.consolidation_days),
                'risk_reward': float(pattern.risk_reward)
            })

        return jsonify({
            'success': True,
            'symbol': symbol,
            'timeframe': timeframe,
            'candlestick': candlestick_data,
            'indicators': {
                'ema_13': ema13_data,
                'ma_50': ma50_data,
                'ma_200': ma200_data
            },
            'patterns': patterns_data,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        log_error(e, f"api_chart_data({symbol})")
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
