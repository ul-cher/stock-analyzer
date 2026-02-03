"""
Basic tests for Stock Analyzer.
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.analyzer import StockAnalyzer
from core.benchmarks import SectorBenchmarks
from data.database import DatabaseManager


class TestSectorBenchmarks(unittest.TestCase):
    """Test sector benchmarks functionality."""
    
    def test_get_benchmarks(self):
        """Test getting sector benchmarks."""
        benchmarks = SectorBenchmarks.get_benchmarks()
        
        self.assertIsInstance(benchmarks, dict)
        self.assertIn('Technology', benchmarks)
        self.assertIn('weights', benchmarks['Technology'])
    
    def test_get_geographic_adjustments(self):
        """Test getting geographic adjustments."""
        adjustments = SectorBenchmarks.get_geographic_adjustments()
        
        self.assertIsInstance(adjustments, dict)
        self.assertIn('United States', adjustments)
        self.assertIn('pe_factor', adjustments['United States'])


class TestDatabaseManager(unittest.TestCase):
    """Test database manager functionality."""
    
    def setUp(self):
        """Set up test database."""
        self.db = DatabaseManager()
    
    def test_cache_stats(self):
        """Test getting cache statistics."""
        stats = self.db.get_cache_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('stock_prices', stats)
        self.assertIn('fundamentals', stats)
        self.assertIn('analysis_results', stats)


class TestStockAnalyzer(unittest.TestCase):
    """Test stock analyzer functionality."""
    
    def test_analyzer_initialization(self):
        """Test analyzer can be initialized."""
        analyzer = StockAnalyzer('AAPL')
        
        self.assertEqual(analyzer.ticker, 'AAPL')
        self.assertIsNotNone(analyzer.db)
        self.assertIsNotNone(analyzer.data_fetcher)
    
    # Note: Additional tests would require mocking yfinance data
    # to avoid making real API calls during testing


if __name__ == '__main__':
    unittest.main()