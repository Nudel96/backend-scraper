from __future__ import annotations

from infra.db import SessionLocal, Event
from .normalize import normalize_event
from core.scoring.engine import compute_score


def normalize_event_job(trace_id: str) -> None:
    with SessionLocal() as session:
        event = session.query(Event).filter_by(trace_id=trace_id).one()
        normalize_event(session, event)
        recompute_score_job(event.asset_id)


def recompute_score_job(asset_id: int) -> None:
    with SessionLocal() as session:
        compute_score(session, asset_id)
