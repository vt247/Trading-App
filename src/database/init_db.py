"""
Database Initialization Script
Run this to create the database and tables
"""

from src.database.models import init_database

if __name__ == "__main__":
    print("🐺 Wolf Market Analyzer - Database Setup")
    print("=" * 50)

    init_database()

    print("=" * 50)
    print("✓ Database setup complete!")
    print("\nTables created:")
    print("  - trades (trade journal)")
    print("  - patterns (pattern history)")
    print("  - daily_briefs (market briefings)")
