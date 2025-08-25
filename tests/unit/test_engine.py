from __future__ import annotations

from datetime import datetime

from infra.db import SessionLocal, Asset, Indicator, Score
from core.scoring.engine import compute_score


def test_compute_score_clamps(tmp_path):
    with SessionLocal() as s:
        asset = Asset(symbol="ABC", kind="x")
        s.add(asset)
        s.commit()
        s.refresh(asset)
        ind = Indicator(asset_id=asset.id, key="macro", ts=datetime.utcnow(), value=30, meta={})
        s.add(ind)
        s.commit()
        compute_score(s, asset.id)
        score = s.query(Score).filter_by(asset_id=asset.id).first()
        assert score.total == 24
