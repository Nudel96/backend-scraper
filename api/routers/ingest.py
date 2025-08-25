from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.schemas.ingest import EventBatch
from infra.db import get_session, Asset, Event
from infra.redis import queue
from core.pipeline.jobs import normalize_event_job

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/events", status_code=status.HTTP_202_ACCEPTED)
def ingest_events(batch: EventBatch, session: Session = Depends(get_session)) -> dict:
    if len(batch.events) > 1000:
        raise HTTPException(status_code=400, detail="batch too large")
    for ev in batch.events:
        asset = session.query(Asset).filter_by(symbol=ev.asset).first()
        if not asset:
            asset = Asset(symbol=ev.asset, kind="unknown")
            session.add(asset)
            session.commit()
            session.refresh(asset)
        exists = session.query(Event).filter_by(trace_id=str(ev.trace_id)).first()
        if exists:
            continue
        event = Event(
            trace_id=str(ev.trace_id),
            source=ev.source,
            asset_id=asset.id,
            kind=ev.kind,
            ingested_at=ev.ingested_at,
            payload=ev.payload,
        )
        session.add(event)
        session.commit()
        queue.enqueue(normalize_event_job, event.trace_id)
    return {"status": "accepted"}
