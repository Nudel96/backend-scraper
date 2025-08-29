from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infra.logging import setup_logging
from infra.db import Base, engine
from api.routers import ingest, heatmap, assets, health, jobs

setup_logging()

app = FastAPI(
    title="PAT Trading Heatmap Backend",
    description="Backend service for trading bias heatmap with economic indicators",
    version="1.0.0"
)

# Configure CORS for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Svelte dev server
        "http://localhost:5173",  # Vite dev server
        "https://your-heatmap-domain.com",  # Production domain
        "*"  # Allow all origins for development (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(ingest.router)
app.include_router(heatmap.router)
app.include_router(assets.router)
app.include_router(health.router)
app.include_router(jobs.router)

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "PAT Trading Heatmap Backend",
        "version": "1.0.0",
        "endpoints": {
            "heatmap_single": "/heatmap?asset=USD",
            "heatmap_batch": "/heatmap/batch?assets=USD,EUR,GBP",
            "health": "/health",
            "metrics": "/metrics",
            "assets": "/assets/{symbol}/indicators"
        },
        "supported_assets": ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "NZD", "USOIL"]
    }
