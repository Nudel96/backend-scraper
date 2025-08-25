from __future__ import annotations

from fastapi import FastAPI

from infra.logging import setup_logging
from infra.db import Base, engine
from api.routers import ingest, heatmap, assets, health, jobs

setup_logging()

app = FastAPI(title="Bias Backend")
Base.metadata.create_all(bind=engine)

app.include_router(ingest.router)
app.include_router(heatmap.router)
app.include_router(assets.router)
app.include_router(health.router)
app.include_router(jobs.router)
