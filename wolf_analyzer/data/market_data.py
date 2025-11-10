"""
Market Data Connector
Handles real-time and historical market data from exchanges via CCXT
"""

import ccxt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import time

from wolf_analyzer.core.config import Config


class MarketDataConnector:
    """
    Connects to cryptocurrency exchanges and fetches market data
    """

    def __init__(self, exchange_name: str = "binance"):
        """
        Initialize market data connector

        Args:
            exchange_name: Name of exchange (default: binance)
        """
        self.exchange_name = exchange_name
        self.exchange = self._initialize_exchange()

    def _initialize_exchange(self) -> ccxt.Exchange:
        """Initialize and configure exchange connection"""
        try:
            # Initialize exchange
            exchange_class = getattr(ccxt, self.exchange_name)

            # Use API keys if provided, otherwise public data
            config = {'enableRateLimit': True, 'options': {'defaultType': 'spot'}}

            if Config.BINANCE_API_KEY and Config.BINANCE_API_SECRET:
                config['apiKey'] = Config.BINANCE_API_KEY
                config['secret'] = Config.BINANCE_API_SECRET

            exchange = exchange_class(config)

            # Try to load markets (optional, will work without)
            try:
                exchange.load_markets()
            except:
                pass  # Ignore errors, we can still fetch OHLCV

            print(f"✓ Connected to {self.exchange_name.upper()}")
            return exchange

        except Exception as e:
            print(f"⚠️  Exchange connection warning: {str(e)}")
            # Return basic exchange instance
            exchange_class = getattr(ccxt, self.exchange_name)
            return exchange_class({'enableRateLimit': True})

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "4h",
        limit: int = 500,
        since: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles to fetch
            since: Timestamp to fetch from (milliseconds)

        Returns:
            DataFrame with OHLCV data
        """
        try:
            # Fetch OHLCV data
            ohlcv = self.exchange.fetch_ohlcv(
                symbol=symbol,
                timeframe=timeframe,
                limit=limit,
                since=since
            )

            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )

            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            # Ensure numeric types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            return df

        except Exception as e:
            print(f"Error fetching OHLCV for {symbol}: {str(e)}")
            return pd.DataFrame()

    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current market price for a symbol

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')

        Returns:
            Current price or None if error
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error fetching price for {symbol}: {str(e)}")
            return None

    def get_ticker_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get comprehensive ticker information

        Args:
            symbol: Trading pair

        Returns:
            Dictionary with ticker data
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'price': ticker['last'],
                'change_24h': ticker['percentage'],
                'volume_24h': ticker['quoteVolume'],
                'high_24h': ticker['high'],
                'low_24h': ticker['low'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            print(f"Error fetching ticker for {symbol}: {str(e)}")
            return {}

    def get_historical_data(
        self,
        symbol: str,
        timeframe: str = "4h",
        days: int = 180
    ) -> pd.DataFrame:
        """
        Fetch historical data for extended period

        Args:
            symbol: Trading pair
            timeframe: Candle timeframe
            days: Number of days of history

        Returns:
            DataFrame with historical OHLCV data
        """
        try:
            # Calculate required candles
            timeframe_minutes = self._timeframe_to_minutes(timeframe)
            total_candles = int((days * 24 * 60) / timeframe_minutes)

            # CCXT limit is usually 500-1000 candles per request
            limit_per_request = 500
            all_data = []

            # Calculate start time
            since = self.exchange.milliseconds() - (days * 24 * 60 * 60 * 1000)

            print(f"Fetching {total_candles} candles for {symbol}...")

            while len(all_data) < total_candles:
                # Fetch batch
                batch = self.exchange.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=limit_per_request,
                    since=since
                )

                if not batch:
                    break

                all_data.extend(batch)

                # Update since to last timestamp + 1
                since = batch[-1][0] + 1

                # Rate limiting
                time.sleep(self.exchange.rateLimit / 1000)

                print(f"  Fetched {len(all_data)} / {total_candles} candles...")

            # Convert to DataFrame
            df = pd.DataFrame(
                all_data,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )

            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            # Remove duplicates
            df = df[~df.index.duplicated(keep='first')]

            # Ensure numeric types
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = pd.to_numeric(df[col], errors='coerce')

            print(f"✓ Fetched {len(df)} candles for {symbol}")

            return df

        except Exception as e:
            print(f"Error fetching historical data for {symbol}: {str(e)}")
            return pd.DataFrame()

    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get order book data

        Args:
            symbol: Trading pair
            limit: Depth of order book

        Returns:
            Dictionary with bids and asks
        """
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit=limit)
            return {
                'bids': orderbook['bids'][:limit],
                'asks': orderbook['asks'][:limit],
                'timestamp': orderbook['timestamp']
            }
        except Exception as e:
            print(f"Error fetching orderbook for {symbol}: {str(e)}")
            return {'bids': [], 'asks': [], 'timestamp': None}

    def get_watchlist_data(
        self,
        timeframe: str = "4h",
        limit: int = 200
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for all symbols in watchlist

        Args:
            timeframe: Candle timeframe
            limit: Number of candles per symbol

        Returns:
            Dictionary mapping symbols to DataFrames
        """
        watchlist = Config.get_watchlist()
        data = {}

        print(f"Fetching data for {len(watchlist)} symbols...")

        for symbol in watchlist:
            print(f"  {symbol}...", end=" ")
            df = self.get_ohlcv(symbol, timeframe, limit)
            if not df.empty:
                data[symbol] = df
                print("✓")
            else:
                print("✗")

            # Rate limiting
            time.sleep(self.exchange.rateLimit / 1000)

        return data

    @staticmethod
    def _timeframe_to_minutes(timeframe: str) -> int:
        """Convert timeframe string to minutes"""
        mapping = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '30m': 30,
            '1h': 60,
            '4h': 240,
            '1d': 1440,
            '1w': 10080
        }
        return mapping.get(timeframe, 240)  # Default 4h

    def get_market_overview(self) -> Dict[str, Any]:
        """
        Get overview of all watchlist markets

        Returns:
            Dictionary with market overview data
        """
        watchlist = Config.get_watchlist()
        overview = {
            'timestamp': datetime.now().isoformat(),
            'markets': []
        }

        for symbol in watchlist:
            ticker = self.get_ticker_info(symbol)
            if ticker:
                overview['markets'].append(ticker)

        return overview

    def calculate_vwap(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate Volume Weighted Average Price (VWAP)

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Series with VWAP values
        """
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
        return vwap


# Example usage and testing
if __name__ == "__main__":
    # Initialize connector
    connector = MarketDataConnector()

    # Test current price
    btc_price = connector.get_current_price("BTC/USDT")
    print(f"\nBTC Current Price: ${btc_price:,.2f}")

    # Test OHLCV data
    df = connector.get_ohlcv("BTC/USDT", timeframe="4h", limit=100)
    print(f"\nFetched {len(df)} candles")
    print(df.tail())

    # Test watchlist
    watchlist_data = connector.get_watchlist_data(timeframe="4h", limit=50)
    print(f"\nWatchlist data: {len(watchlist_data)} symbols loaded")
