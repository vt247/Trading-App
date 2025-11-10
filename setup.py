#!/usr/bin/env python3
"""
Wolf Market Analyzer - Setup Script
Makes the package installable with pip
"""

from setuptools import setup, find_packages

setup(
    name="wolf-market-analyzer",
    version="1.0.0",
    description="AI-powered trading analysis using FOOS4 methodology",
    author="Wolf Trading Team",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*"]),
    python_requires=">=3.11",
    install_requires=[
        # Core Dependencies
        "python-dotenv==1.0.0",

        # Exchange & Market Data
        "ccxt==4.2.25",
        "pandas==2.1.4",
        "numpy==1.26.3",

        # Chart Analysis & Technical Indicators
        "mplfinance",
        "matplotlib>=3.8.0",
        "ta>=0.11.0",

        # AI Integration
        "anthropic==0.18.1",

        # Telegram Bot
        "python-telegram-bot==20.7",

        # Web Framework
        "flask==3.0.0",
        "flask-cors==4.0.0",

        # Database
        "sqlalchemy==2.0.25",
        "alembic==1.13.1",

        # Utilities
        "requests==2.31.0",
        "python-dateutil==2.8.2",
        "pytz==2023.3",
        "schedule==1.2.0",
    ],
    entry_points={
        'console_scripts': [
            'wolf-analyzer=main:main',
            'wolf-dashboard=web_dashboard:main',
        ],
    },
)
