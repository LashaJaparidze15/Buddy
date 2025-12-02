"""Stocks API endpoint."""

from typing import List, Optional
from fastapi import APIRouter

from src.services import StocksService

router = APIRouter()


@router.get("")
def get_watchlist():
    """Get stock quotes for watchlist."""
    service = StocksService()
    quotes = service.get_watchlist_quotes()
    
    return [
        {
            "symbol": q.symbol,
            "price": q.price,
            "change": q.change,
            "change_percent": q.change_percent,
            "high": q.high,
            "low": q.low,
            "volume": q.volume,
            "direction": q.direction,
        }
        for q in quotes
    ]


@router.get("/quote/{symbol}")
def get_quote(symbol: str):
    """Get quote for a single stock."""
    service = StocksService()
    quote = service.get_quote(symbol)
    
    if not quote:
        return {"error": f"Quote for {symbol} not available"}
    
    return {
        "symbol": quote.symbol,
        "price": quote.price,
        "change": quote.change,
        "change_percent": quote.change_percent,
        "high": quote.high,
        "low": quote.low,
        "volume": quote.volume,
        "direction": quote.direction,
    }


@router.get("/market")
def get_market_summary():
    """Get market indices summary."""
    service = StocksService()
    summary = service.get_market_summary()
    
    result = {}
    for name, quote in summary.items():
        if quote:
            result[name] = {
                "symbol": quote.symbol,
                "price": quote.price,
                "change": quote.change,
                "change_percent": quote.change_percent,
                "direction": quote.direction,
            }
    
    return result