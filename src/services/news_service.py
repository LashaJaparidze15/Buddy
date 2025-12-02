"""News service using NewsAPI."""

from typing import Optional
from dataclasses import dataclass

import requests

from src.config import get_settings


@dataclass
class NewsArticle:
    """Single news article."""
    title: str
    source: str
    description: Optional[str]
    url: str
    published_at: str
    
    def summary(self) -> str:
        """One-line summary."""
        return f"[{self.source}] {self.title}"
    
    def detailed(self) -> str:
        """Detailed view."""
        desc = self.description or "No description available"
        return f"📰 {self.title}\n   {self.source} • {self.published_at[:10]}\n   {desc[:100]}..."


class NewsService:
    """Fetch news from NewsAPI."""
    
    BASE_URL = "https://newsapi.org/v2"
    
    # Available categories
    CATEGORIES = [
        "general",
        "business",
        "technology",
        "science",
        "health",
        "sports",
        "entertainment",
    ]
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.news_api_key
    
    def _make_request(self, endpoint: str, params: dict) -> Optional[dict]:
        """Make API request with error handling."""
        if not self.api_key:
            return None
        
        params["apiKey"] = self.api_key
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
    
    def get_top_headlines(
        self,
        category: str = "general",
        country: str = "us",
        count: int = 5
    ) -> list[NewsArticle]:
        """Get top headlines by category."""
        if category.lower() not in self.CATEGORIES:
            category = "general"
        
        data = self._make_request("top-headlines", {
            "category": category,
            "country": country,
            "pageSize": count,
        })
        
        if not data or data.get("status") != "ok":
            return []
        
        articles = []
        for item in data.get("articles", []):
            articles.append(NewsArticle(
                title=item.get("title", "No title"),
                source=item.get("source", {}).get("name", "Unknown"),
                description=item.get("description"),
                url=item.get("url", ""),
                published_at=item.get("publishedAt", ""),
            ))
        
        return articles
    
    def get_headlines_multi_category(
        self,
        categories: list[str] = None,
        country: str = "us",
        count_per_category: int = 2
    ) -> dict[str, list[NewsArticle]]:
        """Get headlines from multiple categories."""
        if categories is None:
            categories = ["general", "technology", "business"]
        
        results = {}
        for category in categories:
            articles = self.get_top_headlines(
                category=category,
                country=country,
                count=count_per_category
            )
            if articles:
                results[category] = articles
        
        return results
    
    def search(self, query: str, count: int = 5) -> list[NewsArticle]:
        """Search for news articles."""
        data = self._make_request("everything", {
            "q": query,
            "pageSize": count,
            "sortBy": "publishedAt",
        })
        
        if not data or data.get("status") != "ok":
            return []
        
        articles = []
        for item in data.get("articles", []):
            articles.append(NewsArticle(
                title=item.get("title", "No title"),
                source=item.get("source", {}).get("name", "Unknown"),
                description=item.get("description"),
                url=item.get("url", ""),
                published_at=item.get("publishedAt", ""),
            ))
        
        return articles
    
    def format_headlines(self, articles: list[NewsArticle]) -> str:
        """Format articles for display."""
        if not articles:
            return "No news available."
        
        lines = []
        for i, article in enumerate(articles, 1):
            lines.append(f"{i}. {article.summary()}")
        
        return "\n".join(lines)