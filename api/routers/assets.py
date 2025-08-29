from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from api.schemas.base import ORMBase
from infra.db import get_session, Asset, Indicator, Score

router = APIRouter(prefix="/assets", tags=["assets"])


class IndicatorOut(ORMBase):
    key: str
    ts: datetime
    value: float


class AssetOut(ORMBase):
    id: int
    symbol: str
    kind: str


class AssetSummary(BaseModel):
    asset: AssetOut
    latest_score: Optional[int]
    latest_score_ts: Optional[datetime]
    indicator_count: int
    last_updated: Optional[datetime]


@router.get("/", response_model=List[AssetSummary])
def list_assets(session: Session = Depends(get_session)) -> List[AssetSummary]:
    """List all assets with summary information"""
    assets = session.query(Asset).all()
    summaries = []

    for asset in assets:
        # Get latest score
        latest_score = (
            session.query(Score)
            .filter_by(asset_id=asset.id)
            .order_by(Score.ts.desc())
            .first()
        )

        # Get indicator count and last update
        indicator_stats = (
            session.query(
                func.count(Indicator.id).label('count'),
                func.max(Indicator.ts).label('last_updated')
            )
            .filter_by(asset_id=asset.id)
            .first()
        )

        summaries.append(AssetSummary(
            asset=AssetOut.model_validate(asset),
            latest_score=latest_score.total if latest_score else None,
            latest_score_ts=latest_score.ts if latest_score else None,
            indicator_count=indicator_stats.count or 0,
            last_updated=indicator_stats.last_updated
        ))

    return summaries


@router.get("/{symbol}/indicators", response_model=List[IndicatorOut])
def get_indicators(
    symbol: str,
    from_: datetime | None = None,
    to: datetime | None = None,
    session: Session = Depends(get_session)
) -> List[IndicatorOut]:
    """Get indicators for a specific asset"""
    asset = session.query(Asset).filter_by(symbol=symbol).first()
    if not asset:
        raise HTTPException(status_code=404, detail="asset not found")
    q = session.query(Indicator).filter_by(asset_id=asset.id)
    if from_:
        q = q.filter(Indicator.ts >= from_)
    if to:
        q = q.filter(Indicator.ts <= to)
    q = q.order_by(Indicator.ts.asc())
    indicators = [IndicatorOut.model_validate(i) for i in q.all()]
    return indicators


@router.get("/{symbol}", response_model=AssetSummary)
def get_asset(symbol: str, session: Session = Depends(get_session)) -> AssetSummary:
    """Get detailed information about a specific asset"""
    asset = session.query(Asset).filter_by(symbol=symbol).first()
    if not asset:
        raise HTTPException(status_code=404, detail="asset not found")

    # Get latest score
    latest_score = (
        session.query(Score)
        .filter_by(asset_id=asset.id)
        .order_by(Score.ts.desc())
        .first()
    )

    # Get indicator count and last update
    indicator_stats = (
        session.query(
            func.count(Indicator.id).label('count'),
            func.max(Indicator.ts).label('last_updated')
        )
        .filter_by(asset_id=asset.id)
        .first()
    )

    return AssetSummary(
        asset=AssetOut.model_validate(asset),
        latest_score=latest_score.total if latest_score else None,
        latest_score_ts=latest_score.ts if latest_score else None,
        indicator_count=indicator_stats.count or 0,
        last_updated=indicator_stats.last_updated
    )
