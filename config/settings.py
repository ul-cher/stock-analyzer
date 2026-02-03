"""
Configuration settings for the Stock Analyzer application.
"""

import os
from pathlib import Path

# Project directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_DIR = DATA_DIR / "db"
CACHE_DIR = DATA_DIR / "cache"

# Create directories if they don't exist
DB_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Database settings
DATABASE_PATH = DB_DIR / "stock_analyzer.db"
CACHE_EXPIRY_DAYS = 1  # Cache expiration in days

# Analysis settings
DEFAULT_PERIOD = "1y"  # Default historical data period
MIN_DATA_POINTS = 50  # Minimum data points for technical analysis

# Streamlit settings
PAGE_TITLE = "Stock Analyzer"
PAGE_ICON = "📈"
LAYOUT = "wide"

# Display settings
CHART_HEIGHT = 500
CHART_WIDTH = 800