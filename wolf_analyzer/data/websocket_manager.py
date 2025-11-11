"""
WebSocket Manager for Binance
Handles real-time market data via WebSocket connections
"""

import websocket
import json
import threading
import time
from typing import Dict, Callable, Optional, Any
from datetime import datetime
import pandas as pd


class BinanceWebSocketManager:
    """
    Manages WebSocket connections to Binance for real-time market data
    """

    BASE_URL = "wss://stream.binance.com:9443/ws"

    def __init__(self):
        """Initialize WebSocket manager"""
        self.connections: Dict[str, websocket.WebSocketApp] = {}
        self.threads: Dict[str, threading.Thread] = {}
        self.data_cache: Dict[str, Any] = {}
        self.callbacks: Dict[str, Callable] = {}
        self.running = False

    def _symbol_to_stream(self, symbol: str) -> str:
        """Convert trading pair to Binance stream format (e.g., BTC/USDT -> btcusdt)"""
        return symbol.replace('/', '').lower()

    def subscribe_kline(self, symbol: str, interval: str = '4h', callback: Optional[Callable] = None):
        """
        Subscribe to kline (candlestick) data stream

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            interval: Timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            callback: Function to call when new data arrives
        """
        stream_symbol = self._symbol_to_stream(symbol)
        stream_name = f"{stream_symbol}@kline_{interval}"

        if stream_name in self.connections:
            print(f"Already subscribed to {stream_name}")
            return

        url = f"{self.BASE_URL}/{stream_name}"

        def on_message(ws, message):
            try:
                data = json.loads(message)

                if 'k' in data:
                    kline = data['k']

                    # Store in cache
                    cache_key = f"{symbol}:kline:{interval}"
                    self.data_cache[cache_key] = {
                        'timestamp': datetime.fromtimestamp(kline['t'] / 1000),
                        'open': float(kline['o']),
                        'high': float(kline['h']),
                        'low': float(kline['l']),
                        'close': float(kline['c']),
                        'volume': float(kline['v']),
                        'is_closed': kline['x']  # Is candle closed?
                    }

                    # Call callback if provided
                    if callback:
                        callback(self.data_cache[cache_key])

            except Exception as e:
                print(f"Error processing kline message: {e}")

        def on_error(ws, error):
            print(f"WebSocket error on {stream_name}: {error}")

        def on_close(ws, close_status_code, close_msg):
            print(f"WebSocket closed: {stream_name}")
            if stream_name in self.connections:
                del self.connections[stream_name]

        def on_open(ws):
            print(f"✓ WebSocket connected: {stream_name}")

        # Create WebSocket connection
        ws = websocket.WebSocketApp(
            url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

        # Store connection
        self.connections[stream_name] = ws
        if callback:
            self.callbacks[stream_name] = callback

        # Start in separate thread
        thread = threading.Thread(target=ws.run_forever, daemon=True)
        thread.start()
        self.threads[stream_name] = thread

        print(f"Subscribing to {stream_name}...")

    def subscribe_ticker(self, symbol: str, callback: Optional[Callable] = None):
        """
        Subscribe to 24h ticker data stream

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            callback: Function to call when new data arrives
        """
        stream_symbol = self._symbol_to_stream(symbol)
        stream_name = f"{stream_symbol}@ticker"

        if stream_name in self.connections:
            print(f"Already subscribed to {stream_name}")
            return

        url = f"{self.BASE_URL}/{stream_name}"

        def on_message(ws, message):
            try:
                data = json.loads(message)

                # Store in cache
                cache_key = f"{symbol}:ticker"
                self.data_cache[cache_key] = {
                    'symbol': symbol,
                    'price': float(data['c']),
                    'change_24h': float(data['P']),
                    'volume_24h': float(data['q']),
                    'high_24h': float(data['h']),
                    'low_24h': float(data['l']),
                    'bid': float(data['b']),
                    'ask': float(data['a']),
                    'timestamp': datetime.fromtimestamp(data['E'] / 1000)
                }

                # Call callback if provided
                if callback:
                    callback(self.data_cache[cache_key])

            except Exception as e:
                print(f"Error processing ticker message: {e}")

        def on_error(ws, error):
            print(f"WebSocket error on {stream_name}: {error}")

        def on_close(ws, close_status_code, close_msg):
            print(f"WebSocket closed: {stream_name}")
            if stream_name in self.connections:
                del self.connections[stream_name]

        def on_open(ws):
            print(f"✓ WebSocket connected: {stream_name}")

        # Create WebSocket connection
        ws = websocket.WebSocketApp(
            url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

        # Store connection
        self.connections[stream_name] = ws
        if callback:
            self.callbacks[stream_name] = callback

        # Start in separate thread
        thread = threading.Thread(target=ws.run_forever, daemon=True)
        thread.start()
        self.threads[stream_name] = thread

        print(f"Subscribing to {stream_name}...")

    def get_cached_ticker(self, symbol: str) -> Optional[Dict]:
        """Get cached ticker data for symbol"""
        cache_key = f"{symbol}:ticker"
        return self.data_cache.get(cache_key)

    def get_cached_kline(self, symbol: str, interval: str) -> Optional[Dict]:
        """Get cached kline data for symbol"""
        cache_key = f"{symbol}:kline:{interval}"
        return self.data_cache.get(cache_key)

    def unsubscribe(self, stream_name: str):
        """Unsubscribe from a stream"""
        if stream_name in self.connections:
            self.connections[stream_name].close()
            del self.connections[stream_name]
            if stream_name in self.callbacks:
                del self.callbacks[stream_name]
            if stream_name in self.threads:
                del self.threads[stream_name]
            print(f"Unsubscribed from {stream_name}")

    def unsubscribe_all(self):
        """Unsubscribe from all streams"""
        for stream_name in list(self.connections.keys()):
            self.unsubscribe(stream_name)

    def is_connected(self, stream_name: str) -> bool:
        """Check if stream is connected"""
        return stream_name in self.connections

    def __del__(self):
        """Cleanup on deletion"""
        self.unsubscribe_all()


# Example usage
if __name__ == "__main__":
    manager = BinanceWebSocketManager()

    def on_ticker_update(data):
        print(f"Ticker: {data['symbol']} - ${data['price']:,.2f} ({data['change_24h']:+.2f}%)")

    def on_kline_update(data):
        print(f"Kline: O:{data['open']} H:{data['high']} L:{data['low']} C:{data['close']} - Closed: {data['is_closed']}")

    # Subscribe to BTC ticker
    manager.subscribe_ticker('BTC/USDT', on_ticker_update)

    # Subscribe to BTC 1h klines
    manager.subscribe_kline('BTC/USDT', '1h', on_kline_update)

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        manager.unsubscribe_all()
