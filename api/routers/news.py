"""News API endpoint."""

from typing import Optional
from fastapi import APIRouter

from src.services import NewsService

router = APIRouter()


@router.get("")
def get_news(category: str = "general", country: str = "us", count: int = 10):
    """Get top news headlines."""
    service = NewsService()
    articles = service.get_top_headlines(category, country, count)
    
    return [
        {
            "title": a.title,
            "source": a.source,
            "description": a.description,
            "url": a.url,
            "published_at": a.published_at,
        }
        for a in articles
    ]


@router.get("/categories")
def get_categories():
    """Get available news categories."""
    return {"categories": NewsService.CATEGORIES}


@router.get("/search")
def search_news(query: str, count: int = 10):
    """Search for news articles."""
    service = NewsService()
    articles = service.search(query, count)
    
    return [
        {
            "title": a.title,
            "source": a.source,
            "description": a.description,
            "url": a.url,
            "published_at": a.published_at,
        }
        for a in articles
    ]