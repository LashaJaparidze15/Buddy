"""Buddy Web API - FastAPI Backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import activities, weather, news, stocks, analytics, dashboard, settings
from api.routers import activities, weather, news, stocks, analytics, dashboard

# Initialize FastAPI app
app = FastAPI(
    title="Buddy API",
    description="Your Smart Daily Planner API",
    version="1.0.0",
)

# Allow frontend to connect (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://buddy-lime.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(activities.router, prefix="/api/activities", tags=["Activities"])
app.include_router(weather.router, prefix="/api/weather", tags=["Weather"])
app.include_router(news.router, prefix="/api/news", tags=["News"])
app.include_router(stocks.router, prefix="/api/stocks", tags=["Stocks"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(settings.router, prefix="/api/settings", tags=["Settings"])

@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Buddy API is running!"}
