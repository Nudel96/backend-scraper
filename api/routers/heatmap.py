from __future__ import annotations

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.schemas.heatmap import HeatmapResponse, HeatmapBatchResponse, Pillar, Component
from infra.db import get_session, Asset, Score

router = APIRouter(prefix="", tags=["heatmap"])


@router.get("/heatmap", response_model=HeatmapResponse)
def get_heatmap(asset: str, session: Session = Depends(get_session)) -> HeatmapResponse:
    asset_obj = session.query(Asset).filter_by(symbol=asset).first()
    if not asset_obj:
        raise HTTPException(status_code=404, detail="asset not found")
    score = (
        session.query(Score)
        .filter_by(asset_id=asset_obj.id)
        .order_by(Score.ts.desc())
        .first()
    )
    if not score:
        raise HTTPException(status_code=404, detail="score not found")
    pillars = []
    for name, comps in score.breakdown.items():
        components = [Component(key=c[0], score=c[1]) for c in comps]
        pscore = sum(c.score for c in components)
        pillars.append(Pillar(name=name, score=pscore, components=components))
    return HeatmapResponse(
        asset=asset,
        score=score.total,
        scale=(-24, 24),
        pillars=pillars,
        as_of=score.ts,
        version=score.version,
    )


def _normalize_score_for_heatmap(backend_score: int) -> float:
    """Normalize backend score (-24 to +24) to heatmap range (-2 to +2)"""
    # Clamp to valid backend range
    backend_score = max(-24, min(24, backend_score))
    # Scale to heatmap range: -24→-2, 0→0, +24→+2
    return round(backend_score / 12.0, 2)


def _get_heatmap_for_asset(session: Session, asset_symbol: str) -> HeatmapResponse:
    """Get heatmap response for a single asset"""
    asset_obj = session.query(Asset).filter_by(symbol=asset_symbol).first()
    if not asset_obj:
        raise HTTPException(status_code=404, detail=f"asset '{asset_symbol}' not found")

    score = (
        session.query(Score)
        .filter_by(asset_id=asset_obj.id)
        .order_by(Score.ts.desc())
        .first()
    )
    if not score:
        # Return default response if no score found
        return HeatmapResponse(
            asset=asset_symbol,
            score=0,
            scale=(-2, 2),  # Normalized scale for heatmap
            pillars=[],
            as_of=None,
            version="0.0.0",
        )

    pillars = []
    for name, comps in score.breakdown.items():
        components = [Component(key=c[0], score=c[1]) for c in comps]
        pscore = sum(c.score for c in components)
        pillars.append(Pillar(name=name, score=pscore, components=components))

    # Normalize score for heatmap display
    normalized_score = _normalize_score_for_heatmap(score.total)

    return HeatmapResponse(
        asset=asset_symbol,
        score=normalized_score,
        scale=(-2, 2),  # Normalized scale for heatmap
        pillars=pillars,
        as_of=score.ts,
        version=score.version,
    )


@router.get("/heatmap/batch", response_model=HeatmapBatchResponse)
def get_heatmap_batch(
    assets: str = Query(..., description="Comma-separated list of asset symbols (e.g., 'USD,EUR,GBP')"),
    session: Session = Depends(get_session)
) -> HeatmapBatchResponse:
    """Get heatmap data for multiple assets in a single request"""
    # Parse asset symbols
    asset_symbols = [symbol.strip().upper() for symbol in assets.split(",") if symbol.strip()]

    if not asset_symbols:
        raise HTTPException(status_code=400, detail="No valid asset symbols provided")

    if len(asset_symbols) > 20:  # Reasonable limit
        raise HTTPException(status_code=400, detail="Too many assets requested (max 20)")

    # Get heatmap data for each asset
    heatmaps = []
    errors = []

    for symbol in asset_symbols:
        try:
            heatmap = _get_heatmap_for_asset(session, symbol)
            heatmaps.append(heatmap)
        except HTTPException as e:
            if e.status_code == 404:
                errors.append(f"Asset '{symbol}' not found")
            else:
                errors.append(f"Error processing '{symbol}': {e.detail}")
        except Exception as e:
            errors.append(f"Unexpected error processing '{symbol}': {str(e)}")

    return HeatmapBatchResponse(
        heatmaps=heatmaps,
        requested_assets=asset_symbols,
        errors=errors if errors else None
    )
