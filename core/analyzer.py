"""
Main stock analyzer class that coordinates all analysis modules.
"""

from typing import Dict, Any, Optional, Tuple, List
import pandas as pd

from core.data_fetcher import DataFetcher
from core.technical_analysis import TechnicalAnalyzer
from core.fundamental_analysis import FundamentalAnalyzer
from data.database import DatabaseManager


class StockAnalyzer:
    """Main stock analyzer coordinating all analysis components."""
    
    def __init__(self, ticker: str, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize stock analyzer.
        
        Args:
            ticker: Stock ticker symbol
            db_manager: Database manager for caching
        """
        self.ticker = ticker.upper()
        self.db = db_manager or DatabaseManager()
        self.data_fetcher = DataFetcher(ticker, self.db)
        
        # Analysis results
        self.historical_data: Optional[pd.DataFrame] = None
        self.fundamentals: Optional[Dict[str, Any]] = None
        self.current_price: Optional[float] = None
        self.sector: Optional[str] = None
        self.industry: Optional[str] = None
        self.country: Optional[str] = None
    
    def fetch_all_data(self, period: str = "1y") -> bool:
        """
        Fetch all necessary data for analysis.
        
        Args:
            period: Historical data period
            
        Returns:
            True if data was fetched successfully
        """
        # Fetch historical data
        self.historical_data = self.data_fetcher.fetch_historical_data(period)
        if self.historical_data is None or self.historical_data.empty:
            return False
        
        # Fetch fundamentals
        self.fundamentals = self.data_fetcher.fetch_fundamentals()
        if not self.fundamentals:
            return False
        
        # Get company info
        self.sector = self.fundamentals.get('Sector', 'Unknown')
        self.industry = self.fundamentals.get('Industry', 'Unknown')
        self.country = self.fundamentals.get('Country', 'Unknown')
        
        # Get current price
        self.current_price = self.data_fetcher.get_current_price()
        
        return True
    
    def analyze(self) -> Dict[str, Any]:
        """
        Perform complete stock analysis.
        
        Returns:
            Dictionary with analysis results
        """
        # Ensure data is fetched
        if self.historical_data is None or self.fundamentals is None:
            if not self.fetch_all_data():
                return {
                    'success': False,
                    'error': 'Unable to fetch data for analysis'
                }
        
        results = {
            'success': True,
            'ticker': self.ticker,
            'current_price': self.current_price,
            'sector': self.sector,
            'industry': self.industry,
            'country': self.country,
        }
        
        # Fundamental analysis
        fund_analyzer = FundamentalAnalyzer(
            self.fundamentals, 
            self.sector, 
            self.industry, 
            self.country
        )
        fund_score, fund_health, fund_signals = fund_analyzer.full_fundamental_analysis()
        
        results['fundamental_score'] = fund_score
        results['fundamental_health'] = fund_health
        results['fundamental_signals'] = fund_signals
        
        # Technical analysis (only if fundamentals are at least neutral)
        if fund_score >= -3:  # Not catastrophic
            tech_analyzer = TechnicalAnalyzer(self.historical_data)
            tech_signals, tech_score = tech_analyzer.full_technical_analysis()
            
            results['technical_score'] = tech_score
            results['technical_signals'] = tech_signals
            
            # Calculate final score
            final_score = fund_score + tech_score
        else:
            results['technical_score'] = None
            results['technical_signals'] = []
            final_score = fund_score
        
        results['final_score'] = final_score
        
        # Generate recommendation
        recommendation, time_horizon = self._generate_recommendation(final_score, fund_score)
        results['recommendation'] = recommendation
        results['time_horizon'] = time_horizon
        
        # Save to database
        self.db.save_analysis_result(
            self.ticker,
            recommendation,
            final_score,
            results
        )
        
        return results
    
    def _generate_recommendation(self, final_score: float, fund_score: float) -> Tuple[str, str]:
        """
        Generate investment recommendation.
        
        Args:
            final_score: Combined fundamental and technical score
            fund_score: Fundamental score only
            
        Returns:
            Tuple of (recommendation, time_horizon)
        """
        if fund_score < -6:
            return "VENTE FORTE", "Court terme"
        elif final_score >= 8:
            return "ACHAT FORT", "Moyen/Long terme"
        elif final_score >= 5:
            return "ACHAT", "Moyen terme"
        elif final_score >= 2:
            return "ACHAT LÉGER", "Court/Moyen terme"
        elif final_score >= -2:
            return "CONSERVER", "Surveillance"
        elif final_score >= -5:
            return "VENTE LÉGÈRE", "Court terme"
        else:
            return "VENTE", "Immédiat"
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """Get historical analysis results."""
        return self.db.get_analysis_history(self.ticker, limit)
    
    def clear_cache(self):
        """Clear cached data for this ticker."""
        self.db.delete_stock_prices(self.ticker)
        self.db.delete_fundamentals(self.ticker)