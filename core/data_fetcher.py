"""
Data fetcher module for retrieving stock data from yfinance.
Includes caching mechanism via database.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Tuple
import warnings

from data.database import DatabaseManager

warnings.filterwarnings('ignore')


class DataFetcher:
    """Fetches and caches stock data."""
    
    def __init__(self, ticker: str, db_manager: Optional[DatabaseManager] = None):
        """
        Initialize data fetcher.
        
        Args:
            ticker: Stock ticker symbol
            db_manager: Database manager instance for caching
        """
        self.ticker = ticker.upper()
        self.stock = yf.Ticker(self.ticker)
        self.db = db_manager or DatabaseManager()
    
    def fetch_historical_data(self, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch historical price data with caching.
        
        Args:
            period: Time period for historical data
            
        Returns:
            DataFrame with historical prices or None
        """
        # Try to get from cache first
        cached_data = self.db.get_stock_prices(self.ticker)
        
        if cached_data and 'historical' in cached_data:
            try:
                df = pd.DataFrame(cached_data['historical'])
                df.index = pd.to_datetime(df.index)
                return df
            except Exception:
                pass
        
        # Fetch fresh data
        try:
            data = self.stock.history(period=period)
            if data is None or data.empty:
                return None
            
            # Cache the data
            cache_data = {
                'historical': data.reset_index().to_dict('records'),
                'period': period
            }
            self.db.save_stock_prices(self.ticker, cache_data)
            
            return data
        except Exception as e:
            print(f"Error fetching historical data for {self.ticker}: {e}")
            return None
    
    def fetch_fundamentals(self) -> Dict[str, Any]:
        """
        Fetch fundamental data with caching.
        
        Returns:
            Dictionary with fundamental metrics
        """
        # Try to get from cache first
        cached_data = self.db.get_fundamentals(self.ticker)
        if cached_data:
            return cached_data
        
        # Fetch fresh data
        fundamentals = {}
        
        try:
            info = self.stock.info
            
            # Company information
            fundamentals['Company_Name'] = info.get('longName', 'N/A')
            fundamentals['Sector'] = info.get('sector', 'N/A')
            fundamentals['Industry'] = info.get('industry', 'N/A')
            fundamentals['Country'] = info.get('country', 'N/A')
            fundamentals['Description'] = info.get('longBusinessSummary', 'N/A')
            
            # Valuation metrics
            fundamentals['PE_Ratio'] = info.get('trailingPE', None)
            fundamentals['Forward_PE'] = info.get('forwardPE', None)
            fundamentals['PEG_Ratio'] = info.get('pegRatio', None)
            fundamentals['Price_to_Book'] = info.get('priceToBook', None)
            fundamentals['Price_to_Sales'] = info.get('priceToSalesTrailing12Months', None)
            fundamentals['EV_to_Revenue'] = info.get('enterpriseToRevenue', None)
            fundamentals['EV_to_EBITDA'] = info.get('enterpriseToEbitda', None)
            
            # Profitability metrics
            fundamentals['ROE'] = info.get('returnOnEquity', None)
            fundamentals['ROA'] = info.get('returnOnAssets', None)
            fundamentals['Profit_Margin'] = info.get('profitMargins', None)
            fundamentals['Operating_Margin'] = info.get('operatingMargins', None)
            fundamentals['Gross_Margin'] = info.get('grossMargins', None)
            
            # Growth metrics
            fundamentals['Revenue_Growth'] = info.get('revenueGrowth', None)
            fundamentals['Earnings_Growth'] = info.get('earningsGrowth', None)
            fundamentals['Earnings_Quarterly_Growth'] = info.get('earningsQuarterlyGrowth', None)
            fundamentals['Revenue_Per_Share'] = info.get('revenuePerShare', None)
            
            # Debt and liquidity
            fundamentals['Debt_to_Equity'] = info.get('debtToEquity', None)
            fundamentals['Current_Ratio'] = info.get('currentRatio', None)
            fundamentals['Quick_Ratio'] = info.get('quickRatio', None)
            fundamentals['Total_Debt'] = info.get('totalDebt', None)
            fundamentals['Total_Cash'] = info.get('totalCash', None)
            fundamentals['Free_Cash_Flow'] = info.get('freeCashflow', None)
            fundamentals['Operating_Cash_Flow'] = info.get('operatingCashflow', None)
            
            # Efficiency metrics
            fundamentals['Asset_Turnover'] = info.get('assetTurnover', None)
            fundamentals['Inventory_Turnover'] = info.get('inventoryTurnover', None)
            fundamentals['Receivables_Turnover'] = info.get('receivablesTurnover', None)
            
            # Dividend metrics
            fundamentals['Dividend_Yield'] = info.get('dividendYield', None)
            fundamentals['Payout_Ratio'] = info.get('payoutRatio', None)
            fundamentals['Dividend_Rate'] = info.get('dividendRate', None)
            
            # Market metrics
            fundamentals['Market_Cap'] = info.get('marketCap', None)
            fundamentals['Enterprise_Value'] = info.get('enterpriseValue', None)
            fundamentals['Beta'] = info.get('beta', None)
            fundamentals['52_Week_Change'] = info.get('52WeekChange', None)
            fundamentals['Short_Ratio'] = info.get('shortRatio', None)
            fundamentals['Short_Percent'] = info.get('shortPercentOfFloat', None)
            
            # Cache the data
            self.db.save_fundamentals(self.ticker, fundamentals)
            
        except Exception as e:
            print(f"Error fetching fundamentals for {self.ticker}: {e}")
        
        return fundamentals
    
    def fetch_company_info(self) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Fetch basic company information.
        
        Returns:
            Tuple of (sector, industry, country)
        """
        fundamentals = self.fetch_fundamentals()
        return (
            fundamentals.get('Sector'),
            fundamentals.get('Industry'),
            fundamentals.get('Country')
        )
    
    def get_current_price(self) -> Optional[float]:
        """
        Get current stock price.
        
        Returns:
            Current price or None
        """
        try:
            info = self.stock.info
            return info.get('currentPrice') or info.get('regularMarketPrice')
        except Exception:
            # Fallback to historical data
            try:
                data = self.fetch_historical_data(period="1d")
                if data is not None and not data.empty:
                    return data['Close'].iloc[-1]
            except Exception:
                pass
        
        return None