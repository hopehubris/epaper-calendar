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
            logger.warning("No API key configured")
            return None
        
        try:
            # Use Polygon's snapshot endpoint for real-time data
            snapshot_url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{ticker.upper()}"
            params = {"apiKey": self.api_key}
            
            logger.debug(f"Fetching {ticker} from {snapshot_url}")
            response = requests.get(snapshot_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Response for {ticker}: {data}")
                
                if data.get('status') == 'OK' and 'results' in data and data['results']:
                    result = data['results'][0]
                    
                    # Extract pricing data
                    last_quote = result.get('lastQuote', {})
                    last_trade = result.get('lastTrade', {})
                    prev_close = result.get('prevDay', {})
                    
                    last_price = last_quote.get('ask') or last_trade.get('p')
                    prev_close_price = prev_close.get('c')
                    
                    if last_price and prev_close_price:
                        change = last_price - prev_close_price
                        change_pct = (change / prev_close_price * 100) if prev_close_price else 0
                        
                        logger.info(f"{ticker}: ${last_price} ({change_pct:+.2f}%)")
                        return {
                            'price': round(last_price, 2),
                            'change': round(change, 2),
                            'change_pct': round(change_pct, 2),
                            'timestamp': datetime.now()
                        }
                else:
                    logger.warning(f"Invalid response for {ticker}: {data.get('status')}")
            else:
                logger.warning(f"HTTP {response.status_code} for {ticker}")
                logger.debug(f"Response: {response.text[:200]}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching {ticker}: {e}", exc_info=True)
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
