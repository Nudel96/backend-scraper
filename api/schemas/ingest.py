from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional, Literal
from uuid import UUID

from pydantic import BaseModel


class EventDTO(BaseModel):
    schema_version: str
    source: str
    asset: str
    kind: Literal["indicator", "news", "price", "yield"]
    ingested_at: datetime
    payload: dict[str, Any]
    trace_id: UUID
    tags: Optional[list[str]] = None


class EventBatch(BaseModel):
    events: List[EventDTO]
