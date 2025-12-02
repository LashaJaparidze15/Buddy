"""External services for Buddy."""

from src.services.weather_service import WeatherService, WeatherData
from src.services.news_service import NewsService, NewsArticle
from src.services.stocks_service import StocksService, StockQuote
from src.services.holidays_service import HolidaysService, Holiday

__all__ = [
    "WeatherService",
    "WeatherData",
    "NewsService",
    "NewsArticle",
    "StocksService",
    "StockQuote",
    "HolidaysService",
    "Holiday",
]