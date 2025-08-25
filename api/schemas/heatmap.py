from __future__ import annotations

from datetime import datetime
from typing import List, Tuple

from pydantic import BaseModel


class Component(BaseModel):
    key: str
    score: int


class Pillar(BaseModel):
    name: str
    score: int
    components: List[Component]


class HeatmapResponse(BaseModel):
    asset: str
    score: int
    scale: Tuple[int, int]
    pillars: List[Pillar]
    as_of: datetime
    version: str
