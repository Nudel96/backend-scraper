from __future__ import annotations

from sqlalchemy.orm import Session

from infra.db import Event, Indicator
from core.scoring import features


def normalize_event(session: Session, event: Event) -> Indicator:
    key, value = features.payload_to_indicator(event.payload)
    indicator = Indicator(
        asset_id=event.asset_id,
        key=key,
        ts=event.ingested_at,
        value=value,
        meta={},
    )
    session.merge(indicator)
    session.commit()
    return indicator
