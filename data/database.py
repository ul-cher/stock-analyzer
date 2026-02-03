"""
Database manager for caching stock data using SQLite.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

from config.settings import DATABASE_PATH, CACHE_EXPIRY_DAYS


class DatabaseManager:
    """Manages SQLite database for caching stock data."""
    
    def __init__(self, db_path: Path = DATABASE_PATH):
        """Initialize database connection and create tables."""
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Create necessary tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table for stock price data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_prices (
                    ticker TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expiry_date DATETIME NOT NULL
                )
            """)
            
            # Table for fundamental data
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fundamentals (
                    ticker TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expiry_date DATETIME NOT NULL
                )
            """)
            
            # Table for analysis results
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    recommendation TEXT,
                    score REAL,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def _is_expired(self, expiry_date: str) -> bool:
        """Check if cached data has expired."""
        expiry = datetime.fromisoformat(expiry_date)
        return datetime.now() > expiry
    
    def get_stock_prices(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached stock price data.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with stock price data or None if not found/expired
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data, expiry_date FROM stock_prices WHERE ticker = ?",
                (ticker.upper(),)
            )
            result = cursor.fetchone()
            
            if result and not self._is_expired(result[1]):
                return json.loads(result[0])
            
            # Remove expired data
            if result:
                self.delete_stock_prices(ticker)
            
            return None
    
    def save_stock_prices(self, ticker: str, data: Dict[str, Any]):
        """
        Save stock price data to cache.
        
        Args:
            ticker: Stock ticker symbol
            data: Stock price data dictionary
        """
        expiry_date = datetime.now() + timedelta(days=CACHE_EXPIRY_DAYS)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO stock_prices (ticker, data, expiry_date)
                VALUES (?, ?, ?)
                """,
                (ticker.upper(), json.dumps(data), expiry_date.isoformat())
            )
            conn.commit()
    
    def get_fundamentals(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached fundamental data.
        
        Args:
            ticker: Stock ticker symbol
            
        Returns:
            Dictionary with fundamental data or None if not found/expired
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data, expiry_date FROM fundamentals WHERE ticker = ?",
                (ticker.upper(),)
            )
            result = cursor.fetchone()
            
            if result and not self._is_expired(result[1]):
                return json.loads(result[0])
            
            # Remove expired data
            if result:
                self.delete_fundamentals(ticker)
            
            return None
    
    def save_fundamentals(self, ticker: str, data: Dict[str, Any]):
        """
        Save fundamental data to cache.
        
        Args:
            ticker: Stock ticker symbol
            data: Fundamental data dictionary
        """
        expiry_date = datetime.now() + timedelta(days=CACHE_EXPIRY_DAYS)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO fundamentals (ticker, data, expiry_date)
                VALUES (?, ?, ?)
                """,
                (ticker.upper(), json.dumps(data), expiry_date.isoformat())
            )
            conn.commit()
    
    def save_analysis_result(self, ticker: str, recommendation: str, 
                           score: float, data: Dict[str, Any]):
        """
        Save analysis result to database.
        
        Args:
            ticker: Stock ticker symbol
            recommendation: Analysis recommendation
            score: Analysis score
            data: Complete analysis data
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO analysis_results (ticker, recommendation, score, data)
                VALUES (?, ?, ?, ?)
                """,
                (ticker.upper(), recommendation, score, json.dumps(data))
            )
            conn.commit()
    
    def get_analysis_history(self, ticker: str, limit: int = 10):
        """
        Get analysis history for a ticker.
        
        Args:
            ticker: Stock ticker symbol
            limit: Maximum number of results to return
            
        Returns:
            List of analysis results
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT recommendation, score, data, timestamp
                FROM analysis_results
                WHERE ticker = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (ticker.upper(), limit)
            )
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'recommendation': row[0],
                    'score': row[1],
                    'data': json.loads(row[2]),
                    'timestamp': row[3]
                })
            
            return results
    
    def delete_stock_prices(self, ticker: str):
        """Delete cached stock prices for a ticker."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM stock_prices WHERE ticker = ?",
                (ticker.upper(),)
            )
            conn.commit()
    
    def delete_fundamentals(self, ticker: str):
        """Delete cached fundamentals for a ticker."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM fundamentals WHERE ticker = ?",
                (ticker.upper(),)
            )
            conn.commit()
    
    def clear_all_cache(self):
        """Clear all cached data."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM stock_prices")
            cursor.execute("DELETE FROM fundamentals")
            conn.commit()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM stock_prices")
            prices_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM fundamentals")
            fundamentals_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM analysis_results")
            analysis_count = cursor.fetchone()[0]
            
            return {
                'stock_prices': prices_count,
                'fundamentals': fundamentals_count,
                'analysis_results': analysis_count
            }