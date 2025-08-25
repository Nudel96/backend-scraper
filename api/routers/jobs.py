from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from infra.db import get_session, Asset
from infra.redis import queue
from core.pipeline.jobs import recompute_score_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/recompute-bias")
def recompute(asset: str | None = None, session: Session = Depends(get_session)) -> dict:
    if asset:
        asset_obj = session.query(Asset).filter_by(symbol=asset).first()
        if asset_obj:
            queue.enqueue(recompute_score_job, asset_obj.id)
    else:
        for a in session.query(Asset).all():
            queue.enqueue(recompute_score_job, a.id)
    return {"status": "queued"}
