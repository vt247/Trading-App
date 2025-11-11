"""
Historical Data Storage using SQLite
Stores 2 years of OHLCV data efficiently, fetches only missing periods
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
import os


class HistoricalDataDB:
    """
    SQLite database for storing and managing historical OHLCV data
    """

    def __init__(self, db_path: str = None):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file (default: wolf_analyzer/database/historical.db)
        """
        if db_path is None:
            # Default path in database directory
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_dir = os.path.join(base_dir, 'database')
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, 'historical.db')

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_tables()

    def _create_tables(self):
        """Create database schema if not exists"""
        cursor = self.conn.cursor()

        # Trading pairs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_pairs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                exchange TEXT NOT NULL DEFAULT 'binance',
                first_timestamp INTEGER,
                last_timestamp INTEGER,
                total_candles INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # OHLCV data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ohlcv_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pair_id INTEGER NOT NULL,
                timestamp INTEGER NOT NULL,
                timeframe TEXT NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                FOREIGN KEY (pair_id) REFERENCES trading_pairs(id),
                UNIQUE(pair_id, timestamp, timeframe)
            )
        """)

        # Index for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ohlcv_pair_time
            ON ohlcv_data(pair_id, timeframe, timestamp DESC)
        """)

        # Detected patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detected_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pair_id INTEGER NOT NULL,
                pattern_type TEXT NOT NULL,
                confidence REAL NOT NULL,
                detected_at INTEGER NOT NULL,
                timeframe TEXT NOT NULL,
                phase_1_start INTEGER,
                phase_2_start INTEGER,
                phase_3_breakout INTEGER,
                neckline_price REAL,
                entry_low REAL,
                entry_high REAL,
                stop_loss REAL,
                target_1 REAL,
                target_2 REAL,
                target_3 REAL,
                risk_reward REAL,
                lead_in_trend TEXT,
                volume_spike_confirmed BOOLEAN,
                ema_13_position TEXT,
                is_active BOOLEAN DEFAULT 1,
                notes TEXT,
                FOREIGN KEY (pair_id) REFERENCES trading_pairs(id)
            )
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_patterns_pair_active
            ON detected_patterns(pair_id, is_active, detected_at DESC)
        """)

        # Market cycles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_cycles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pair_id INTEGER NOT NULL,
                cycle_phase TEXT NOT NULL,
                started_at INTEGER NOT NULL,
                ended_at INTEGER,
                pattern_sequence TEXT,
                is_current BOOLEAN DEFAULT 1,
                FOREIGN KEY (pair_id) REFERENCES trading_pairs(id)
            )
        """)

        self.conn.commit()
        print("✓ Database schema initialized")

    def get_or_create_pair(self, symbol: str, exchange: str = 'binance') -> int:
        """Get pair_id or create new pair entry"""
        cursor = self.conn.cursor()

        # Try to get existing
        cursor.execute(
            "SELECT id FROM trading_pairs WHERE symbol = ? AND exchange = ?",
            (symbol, exchange)
        )
        result = cursor.fetchone()

        if result:
            return result[0]

        # Create new
        cursor.execute(
            "INSERT INTO trading_pairs (symbol, exchange) VALUES (?, ?)",
            (symbol, exchange)
        )
        self.conn.commit()
        return cursor.lastrowid

    def store_ohlcv(self, symbol: str, df: pd.DataFrame, timeframe: str = '4h'):
        """
        Store OHLCV data, ignoring duplicates

        Args:
            symbol: Trading pair symbol
            df: DataFrame with OHLCV data (index = timestamp)
            timeframe: Candle timeframe
        """
        if df.empty:
            return

        pair_id = self.get_or_create_pair(symbol)
        cursor = self.conn.cursor()

        # Prepare data for bulk insert
        records = []
        for idx, row in df.iterrows():
            timestamp = int(idx.timestamp() * 1000)  # Convert to milliseconds
            records.append((
                pair_id,
                timestamp,
                timeframe,
                float(row['open']),
                float(row['high']),
                float(row['low']),
                float(row['close']),
                float(row['volume'])
            ))

        # Bulk insert with IGNORE to skip duplicates
        cursor.executemany("""
            INSERT OR IGNORE INTO ohlcv_data
            (pair_id, timestamp, timeframe, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, records)

        # Update pair stats
        cursor.execute("""
            UPDATE trading_pairs SET
                first_timestamp = (
                    SELECT MIN(timestamp) FROM ohlcv_data WHERE pair_id = ?
                ),
                last_timestamp = (
                    SELECT MAX(timestamp) FROM ohlcv_data WHERE pair_id = ?
                ),
                total_candles = (
                    SELECT COUNT(*) FROM ohlcv_data WHERE pair_id = ? AND timeframe = ?
                ),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (pair_id, pair_id, pair_id, timeframe, pair_id))

        self.conn.commit()
        print(f"✓ Stored {len(records)} candles for {symbol} ({timeframe})")

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = '4h',
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Retrieve OHLCV data from database

        Args:
            symbol: Trading pair symbol
            timeframe: Candle timeframe
            start_time: Start datetime
            end_time: End datetime
            limit: Maximum number of candles

        Returns:
            DataFrame with OHLCV data
        """
        pair_id = self.get_or_create_pair(symbol)

        query = """
            SELECT timestamp, open, high, low, close, volume
            FROM ohlcv_data
            WHERE pair_id = ? AND timeframe = ?
        """
        params = [pair_id, timeframe]

        if start_time:
            query += " AND timestamp >= ?"
            params.append(int(start_time.timestamp() * 1000))

        if end_time:
            query += " AND timestamp <= ?"
            params.append(int(end_time.timestamp() * 1000))

        query += " ORDER BY timestamp ASC"

        if limit:
            query += f" LIMIT {limit}"

        df = pd.read_sql_query(query, self.conn, params=params)

        if df.empty:
            return df

        # Convert timestamp to datetime and set as index
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)

        return df

    def get_missing_periods(
        self,
        symbol: str,
        timeframe: str,
        lookback_days: int = 730  # 2 years default
    ) -> List[Tuple[datetime, datetime]]:
        """
        Identify missing periods in historical data

        Args:
            symbol: Trading pair
            timeframe: Candle timeframe
            lookback_days: How far back to check

        Returns:
            List of (start_time, end_time) tuples for missing periods
        """
        pair_id = self.get_or_create_pair(symbol)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=lookback_days)

        # Get all existing timestamps
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT timestamp FROM ohlcv_data
            WHERE pair_id = ? AND timeframe = ?
            AND timestamp >= ? AND timestamp <= ?
            ORDER BY timestamp ASC
        """, (
            pair_id,
            timeframe,
            int(start_time.timestamp() * 1000),
            int(end_time.timestamp() * 1000)
        ))

        existing = [datetime.fromtimestamp(row[0] / 1000) for row in cursor.fetchall()]

        if not existing:
            # No data at all - need full range
            return [(start_time, end_time)]

        # Find gaps
        missing_periods = []

        # Gap before first record
        if existing[0] > start_time:
            missing_periods.append((start_time, existing[0]))

        # Gaps between records
        timeframe_minutes = self._timeframe_to_minutes(timeframe)
        expected_delta = timedelta(minutes=timeframe_minutes)

        for i in range(len(existing) - 1):
            actual_delta = existing[i + 1] - existing[i]
            if actual_delta > expected_delta * 1.5:  # Allow 50% tolerance
                gap_start = existing[i] + expected_delta
                gap_end = existing[i + 1]
                missing_periods.append((gap_start, gap_end))

        # Gap after last record
        if existing[-1] < end_time - expected_delta:
            missing_periods.append((existing[-1] + expected_delta, end_time))

        return missing_periods

    def store_pattern(self, symbol: str, pattern_data: dict):
        """Store detected pattern to database"""
        pair_id = self.get_or_create_pair(symbol)
        cursor = self.conn.cursor()

        cursor.execute("""
            INSERT INTO detected_patterns (
                pair_id, pattern_type, confidence, detected_at, timeframe,
                phase_1_start, phase_2_start, phase_3_breakout,
                neckline_price, entry_low, entry_high, stop_loss,
                target_1, target_2, target_3, risk_reward,
                lead_in_trend, volume_spike_confirmed, ema_13_position, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            pair_id,
            pattern_data['pattern_type'],
            pattern_data['confidence'],
            pattern_data['detected_at'],
            pattern_data.get('timeframe', '4h'),
            pattern_data.get('phase_1_start'),
            pattern_data.get('phase_2_start'),
            pattern_data.get('phase_3_breakout'),
            pattern_data.get('neckline_price'),
            pattern_data.get('entry_low'),
            pattern_data.get('entry_high'),
            pattern_data.get('stop_loss'),
            pattern_data.get('target_1'),
            pattern_data.get('target_2'),
            pattern_data.get('target_3'),
            pattern_data.get('risk_reward'),
            pattern_data.get('lead_in_trend'),
            pattern_data.get('volume_spike_confirmed'),
            pattern_data.get('ema_13_position'),
            pattern_data.get('notes')
        ))

        self.conn.commit()
        print(f"✓ Stored {pattern_data['pattern_type']} pattern for {symbol}")

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
        self.conn.close()

    def __del__(self):
        """Cleanup on deletion"""
        try:
            self.conn.close()
        except:
            pass
