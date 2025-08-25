from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.schemas.base import ORMBase
from infra.db import get_session, Asset, Indicator

router = APIRouter(prefix="/assets", tags=["assets"])


class IndicatorOut(ORMBase):
    key: str
    ts: datetime
    value: float


@router.get("/{symbol}/indicators", response_model=List[IndicatorOut])
def get_indicators(symbol: str, from_: datetime | None = None, to: datetime | None = None, session: Session = Depends(get_session)) -> List[IndicatorOut]:
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
