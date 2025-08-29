from __future__ import annotations

from datetime import datetime
from typing import List, Tuple, Optional, Union

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
    score: Union[int, float]  # Allow both int and float for normalized scores
    scale: Tuple[Union[int, float], Union[int, float]]
    pillars: List[Pillar]
    as_of: Optional[datetime]  # Allow None for assets without scores
    version: str


class HeatmapBatchResponse(BaseModel):
    heatmaps: List[HeatmapResponse]
    requested_assets: List[str]
    errors: Optional[List[str]] = None
