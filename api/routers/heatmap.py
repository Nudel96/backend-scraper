from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.schemas.heatmap import HeatmapResponse, Pillar, Component
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
