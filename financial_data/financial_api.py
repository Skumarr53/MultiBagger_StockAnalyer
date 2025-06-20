"""
Financial Data Fetcher Module
----------------------------
Fetches company fundamentals/metrics via financial data APIs (e.g., EODHD, Yahoo Finance/yfinance).
Modular, extensible, robust error handling and logging.

- Initial implementation: EODHD and yfinance (for Indian tickers)
- Can be extended for Screener.in or RapidAPI integrations
"""
from typing import Dict, Optional
import requests
import yfinance as yf
from utils.logger import setup_logger

logger = setup_logger(__name__)

class FinancialDataFetcher:
    """
    Fetches financial metrics for Indian stocks from multiple APIs.
    """
    def __init__(self, eodhd_api_key: Optional[str] = None):
        self.eodhd_api_key = eodhd_api_key
        self.eodhd_base_url = "https://eodhd.com/api/fundamentals/"

    def fetch_eodhd(self, symbol: str, exchange: str = "NSE") -> Dict:
        """
        Fetches fundamentals from EODHD API.
        Args:
            symbol (str): Stock ticker symbol.
            exchange (str): e.g. 'NSE' or 'BSE'
        Returns:
            Dict: Fundamentals data (or empty dict on error)
        """
        url = f"{self.eodhd_base_url}{symbol}.{exchange}?api_token={self.eodhd_api_key}&fmt=json"
        try:
            resp = requests.get(url, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"Fetched EODHD data for {symbol}.{exchange}")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch EODHD data for {symbol}.{exchange}: {e}")
            return {}

    def fetch_yfinance(self, symbol: str) -> Dict:
        """
        Fetches current and historical financials from Yahoo Finance.
        Args:
            symbol (str): Stock ticker symbol (use 'RELIANCE.NS' for NSE stocks)
        Returns:
            Dict: Financial data summary
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            financials = ticker.financials.to_dict() if hasattr(ticker, 'financials') else {}
            logger.info(f"Fetched yfinance data for {symbol}")
            return {"info": info, "financials": financials}
        except Exception as e:
            logger.error(f"Failed to fetch yfinance data for {symbol}: {e}")
            return {}

    def fetch_all(self, symbol: str, exchange: str = "NSE") -> Dict:
        """
        Aggregates all sources for a given symbol.
        Args:
            symbol (str): Stock ticker
            exchange (str): 'NSE' or 'BSE'
        Returns:
            Dict: Aggregated data
        """
        data = {"symbol": symbol, "exchange": exchange}
        if self.eodhd_api_key:
            data["eodhd"] = self.fetch_eodhd(symbol, exchange)
        yf_symbol = f"{symbol}.NS" if exchange.upper() == "NSE" else f"{symbol}.BO"
        data["yfinance"] = self.fetch_yfinance(yf_symbol)
        return data

# Example usage:
# fetcher = FinancialDataFetcher(eodhd_api_key="YOUR_API_KEY")
# data = fetcher.fetch_all("RELIANCE", "NSE")
