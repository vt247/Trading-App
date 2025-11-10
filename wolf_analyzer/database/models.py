"""
Database Models for Trade Journal
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from wolf_analyzer.core.config import Config

Base = declarative_base()


class Trade(Base):
    """Trade journal entry"""
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String(20), nullable=False)
    pattern_type = Column(String(50))
    direction = Column(String(10))  # 'long' or 'short'

    # Entry
    entry_price = Column(Float)
    entry_time = Column(DateTime)
    position_size = Column(Float)

    # Exit
    exit_price = Column(Float, nullable=True)
    exit_time = Column(DateTime, nullable=True)

    # Risk Management
    stop_loss = Column(Float)
    target_1 = Column(Float)
    target_2 = Column(Float, nullable=True)
    target_3 = Column(Float, nullable=True)

    # Results
    pnl = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)
    risk_reward_actual = Column(Float, nullable=True)

    # Analysis
    pattern_confidence = Column(Float)
    followed_plan = Column(Boolean, default=True)
    emotional_state = Column(String(50))
    notes = Column(Text)

    # AI Coaching
    ai_feedback = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Trade {self.symbol} {self.direction} @ ${self.entry_price}>"


class Pattern(Base):
    """Historical pattern detection"""
    __tablename__ = 'patterns'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    symbol = Column(String(20), nullable=False)
    pattern_type = Column(String(50))
    timeframe = Column(String(10))
    confidence = Column(Float)

    # Pattern details
    entry_zone_low = Column(Float)
    entry_zone_high = Column(Float)
    stop_loss = Column(Float)
    risk_reward = Column(Float)

    # Outcome (filled later)
    resolved = Column(Boolean, default=False)
    successful = Column(Boolean, nullable=True)
    actual_move = Column(Float, nullable=True)

    def __repr__(self):
        return f"<Pattern {self.pattern_type} {self.symbol}>"


class DailyBrief(Base):
    """Daily market briefings"""
    __tablename__ = 'daily_briefs'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow)
    content = Column(Text)
    market_sentiment = Column(String(20))  # 'bullish', 'bearish', 'neutral'
    active_setups_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<DailyBrief {self.date}>"


# Database initialization
def init_database():
    """Initialize database and create tables"""
    engine = create_engine(Config.DATABASE_URL)
    Base.metadata.create_all(engine)
    print("✓ Database initialized")
    return engine


def get_session():
    """Get database session"""
    engine = create_engine(Config.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()


# Example usage
if __name__ == "__main__":
    # Initialize database
    init_database()

    # Create sample trade
    session = get_session()

    trade = Trade(
        symbol="BTC/USDT",
        pattern_type="Ascending Triangle",
        direction="long",
        entry_price=42500.0,
        entry_time=datetime.now(),
        position_size=1.0,
        stop_loss=41800.0,
        target_1=43500.0,
        pattern_confidence=0.85,
        followed_plan=True,
        emotional_state="Confident",
        notes="Clear pattern formation, good volume confirmation"
    )

    session.add(trade)
    session.commit()

    print(f"Sample trade created: {trade}")

    # Query trades
    all_trades = session.query(Trade).all()
    print(f"Total trades in database: {len(all_trades)}")

    session.close()
