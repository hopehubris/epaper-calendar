"""Fetch stock prices using Polygon API."""

import logging
import os
from typing import Dict, Optional, List
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StockFetcher:
    """Fetches current stock prices from Polygon API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize stock fetcher.
        
        Args:
            api_key: Polygon API key (or from env POLYGON_API_KEY)
        """
        self.api_key = api_key or os.environ.get('POLYGON_API_KEY')
        if not self.api_key:
            logger.warning("No Polygon API key configured")
        
        self.base_url = "https://api.polygon.io/v1"
    
    def get_current_price(self, ticker: str) -> Optional[Dict]:
        """Get current price for a ticker.
        
        Args:
            ticker: Stock ticker (e.g., "NFLX", "MSFT")
            
        Returns:
            Dict with {price, change, change_pct} or None if failed
        """
        if not self.api_key:
            return None
        
        try:
            # Use Polygon's snapshot endpoint for real-time data
            url = f"{self.base_url}/open-close/{ticker}/2024-02-09"
            params = {"apiKey": self.api_key}
            
            # Note: For truly real-time, would use /snapshot/locale/us/markets/stocks/tickers/{ticker}
            # But open-close works for previous day. Let's try the snapshot endpoint instead.
            
            snapshot_url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}"
            response = requests.get(snapshot_url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'results' in data and data['results']:
                    result = data['results'][0]
                    last_price = result.get('last', {}).get('price')
                    prev_close = result.get('prevDay', {}).get('c')
                    
                    if last_price and prev_close:
                        change = last_price - prev_close
                        change_pct = (change / prev_close * 100) if prev_close else 0
                        
                        return {
                            'price': round(last_price, 2),
                            'change': round(change, 2),
                            'change_pct': round(change_pct, 2),
                            'timestamp': datetime.now()
                        }
            
            logger.warning(f"Failed to fetch {ticker}: status {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching {ticker}: {e}")
            return None
    
    def get_multiple_prices(self, tickers: List[str]) -> Dict[str, Dict]:
        """Get prices for multiple tickers.
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Dict mapping ticker → price data
        """
        result = {}
        for ticker in tickers:
            data = self.get_current_price(ticker)
            if data:
                result[ticker] = data
        
        return result
