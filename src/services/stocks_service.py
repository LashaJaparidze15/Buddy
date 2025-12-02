"""Stock market service using Alpha Vantage API."""

from typing import Optional
from dataclasses import dataclass

import requests

from src.config import get_settings


@dataclass
class StockQuote:
    """Single stock quote."""
    symbol: str
    price: float
    change: float
    change_percent: float
    high: float
    low: float
    volume: int
    
    @property
    def direction(self) -> str:
        """Return up/down indicator."""
        if self.change > 0:
            return "🟢"
        elif self.change < 0:
            return "🔴"
        return "⚪"
    
    def summary(self) -> str:
        """One-line summary."""
        sign = "+" if self.change >= 0 else ""
        return f"{self.direction} {self.symbol}: ${self.price:.2f} ({sign}{self.change_percent:.2f}%)"
    
    def detailed(self) -> str:
        """Detailed view."""
        sign = "+" if self.change >= 0 else ""
        return (
            f"{self.direction} {self.symbol}\n"
            f"   Price: ${self.price:.2f}\n"
            f"   Change: {sign}${self.change:.2f} ({sign}{self.change_percent:.2f}%)\n"
            f"   High: ${self.high:.2f} | Low: ${self.low:.2f}\n"
            f"   Volume: {self.volume:,}"
        )


class StocksService:
    """Fetch stock data from Alpha Vantage."""
    
    BASE_URL = "https://www.alphavantage.co/query"
    
    # Default watchlist
    DEFAULT_WATCHLIST = ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"]
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.stocks_api_key
        self.watchlist = self.DEFAULT_WATCHLIST
    
    def _make_request(self, params: dict) -> Optional[dict]:
        """Make API request with error handling."""
        if not self.api_key:
            return None
        
        params["apikey"] = self.api_key
        
        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if "Error Message" in data or "Note" in data:
                return None
            
            return data
        except requests.RequestException:
            return None
    
    def get_quote(self, symbol: str) -> Optional[StockQuote]:
        """Get quote for a single stock."""
        data = self._make_request({
            "function": "GLOBAL_QUOTE",
            "symbol": symbol.upper(),
        })
        
        if not data or "Global Quote" not in data:
            return None
        
        quote = data["Global Quote"]
        
        if not quote:
            return None
        
        try:
            return StockQuote(
                symbol=quote.get("01. symbol", symbol),
                price=float(quote.get("05. price", 0)),
                change=float(quote.get("09. change", 0)),
                change_percent=float(quote.get("10. change percent", "0%").rstrip("%")),
                high=float(quote.get("03. high", 0)),
                low=float(quote.get("04. low", 0)),
                volume=int(quote.get("06. volume", 0)),
            )
        except (ValueError, KeyError):
            return None
    
    def get_watchlist_quotes(self, symbols: list[str] = None) -> list[StockQuote]:
        """Get quotes for multiple stocks."""
        if symbols is None:
            symbols = self.watchlist
        
        quotes = []
        for symbol in symbols:
            quote = self.get_quote(symbol)
            if quote:
                quotes.append(quote)
        
        return quotes
    
    def get_market_summary(self) -> dict[str, Optional[StockQuote]]:
        """Get summary of major indices (using ETFs as proxies)."""
        indices = {
            "S&P 500": "SPY",
            "Nasdaq": "QQQ",
            "Dow Jones": "DIA",
        }
        
        summary = {}
        for name, symbol in indices.items():
            summary[name] = self.get_quote(symbol)
        
        return summary
    
    def format_watchlist(self, quotes: list[StockQuote]) -> str:
        """Format quotes for display."""
        if not quotes:
            return "No stock data available."
        
        lines = []
        for quote in quotes:
            lines.append(quote.summary())
        
        return "\n".join(lines)
    
    def set_watchlist(self, symbols: list[str]) -> None:
        """Update the watchlist."""
        self.watchlist = [s.upper() for s in symbols]