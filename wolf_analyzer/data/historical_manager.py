"""
Historical Data Manager
Fetches and maintains 2 years of historical data, only fetching missing periods
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import time

from wolf_analyzer.data.market_data import MarketDataConnector
from wolf_analyzer.database.historical_data import HistoricalDataDB


class HistoricalDataManager:
    """
    Manages historical data fetching and storage
    Only fetches missing periods to minimize API calls
    """

    def __init__(self, market_connector: MarketDataConnector = None):
        """
        Initialize historical data manager

        Args:
            market_connector: MarketDataConnector instance (creates new if None)
        """
        self.market = market_connector or MarketDataConnector(use_websocket=False)
        self.db = HistoricalDataDB()

    def ensure_data(
        self,
        symbol: str,
        timeframe: str = '4h',
        lookback_days: int = 730  # 2 years
    ) -> pd.DataFrame:
        """
        Ensure we have complete historical data, fetching only what's missing

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe
            lookback_days: Days of history to maintain

        Returns:
            Complete DataFrame with all historical data
        """
        print(f"\n📊 Ensuring {lookback_days} days of data for {symbol} ({timeframe})...")

        # Check what periods are missing
        missing_periods = self.db.get_missing_periods(symbol, timeframe, lookback_days)

        if not missing_periods:
            print(f"✓ All data already present for {symbol}")
        else:
            print(f"⚠️  Found {len(missing_periods)} missing period(s)")

            # Fetch each missing period
            for i, (start, end) in enumerate(missing_periods, 1):
                print(f"\n  Period {i}/{len(missing_periods)}: {start.date()} → {end.date()}")

                # Calculate how many candles we need
                timeframe_minutes = self._timeframe_to_minutes(timeframe)
                duration_minutes = (end - start).total_seconds() / 60
                candles_needed = int(duration_minutes / timeframe_minutes)

                # Skip if period is too small (less than 1 candle)
                if candles_needed < 1:
                    print(f"    ⏭️  Skipping: period too small (< 1 candle)")
                    continue

                # Binance limit is 1000 candles per request
                batch_size = 1000
                current_start = start

                while current_start < end:
                    # Fetch batch
                    since_ms = int(current_start.timestamp() * 1000)

                    # Ensure limit is at least 1
                    fetch_limit = max(1, min(batch_size, candles_needed))

                    try:
                        df_batch = self.market.get_ohlcv(
                            symbol=symbol,
                            timeframe=timeframe,
                            limit=fetch_limit,
                            since=since_ms
                        )

                        if not df_batch.empty:
                            # Store to database
                            self.db.store_ohlcv(symbol, df_batch, timeframe)

                            # Move to next batch
                            last_timestamp = df_batch.index[-1]
                            current_start = last_timestamp + timedelta(minutes=timeframe_minutes)

                            print(f"    ✓ Fetched {len(df_batch)} candles up to {last_timestamp.date()}")
                        else:
                            print(f"    ⚠️  No more data available from API")
                            break

                        # Rate limiting (1.2s between requests)
                        time.sleep(1.2)

                    except Exception as e:
                        print(f"    ❌ Error fetching batch: {type(e).__name__}: {str(e)}")
                        # Continue trying if it's a transient error, break if it's likely persistent
                        if "rate limit" in str(e).lower() or "429" in str(e):
                            print(f"    ⏸️  Rate limited, waiting 60s before retry...")
                            time.sleep(60)
                            # Don't break, try again
                        else:
                            break

        # Return complete dataset from database
        end_time = datetime.now()
        start_time = end_time - timedelta(days=lookback_days)
        df = self.db.get_ohlcv(symbol, timeframe, start_time, end_time)

        if not df.empty:
            print(f"\n✓ Complete dataset: {len(df)} candles from {df.index[0].date()} to {df.index[-1].date()}")
        else:
            print(f"\n⚠️  Warning: No data available for {symbol} - API may be unavailable or rate limited")

        return df

    def update_latest(self, symbol: str, timeframe: str = '4h') -> pd.DataFrame:
        """
        Update with latest candles (last 24 hours)

        Args:
            symbol: Trading pair
            timeframe: Candle timeframe

        Returns:
            Latest data DataFrame
        """
        # Fetch last 100 candles (covers ~16 days for 4h timeframe)
        df_latest = self.market.get_ohlcv(symbol, timeframe, limit=100)

        if not df_latest.empty:
            self.db.store_ohlcv(symbol, df_latest, timeframe)
            print(f"✓ Updated latest data for {symbol}")

        return df_latest

    def get_data(
        self,
        symbol: str,
        timeframe: str = '4h',
        lookback_days: int = 730
    ) -> pd.DataFrame:
        """
        Get historical data from database

        Args:
            symbol: Trading pair
            timeframe: Candle timeframe
            lookback_days: Days of history

        Returns:
            DataFrame with historical data
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(days=lookback_days)
        return self.db.get_ohlcv(symbol, timeframe, start_time, end_time)

    @staticmethod
    def _timeframe_to_minutes(timeframe: str) -> int:
        """Convert timeframe string to minutes"""
        mapping = {
            '1m': 1, '5m': 5, '15m': 15, '30m': 30,
            '1h': 60, '4h': 240, '1d': 1440, '1w': 10080
        }
        return mapping.get(timeframe, 240)

    def close(self):
        """Close database connection"""
        self.db.close()


# Example usage
if __name__ == "__main__":
    manager = HistoricalDataManager()

    # Ensure we have 2 years of data for BTC
    df = manager.ensure_data('BTC/USDT', '4h', lookback_days=730)

    print(f"\nDataFrame shape: {df.shape}")
    print(f"Date range: {df.index[0]} to {df.index[-1]}")
    print(f"\nLast 5 candles:")
    print(df.tail())

    manager.close()
