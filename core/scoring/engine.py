from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from infra.db import Indicator, Score

import yaml  # type: ignore[import-untyped]


@dataclass
class PillarScore:
    name: str
    score: int
    components: list[tuple[str, int]]


def load_weights() -> dict:
    with open("core/scoring/weights.yaml", "r") as fh:
        return yaml.safe_load(fh)


def compute_score(session: Session, asset_id: int) -> Score:
    weights = load_weights()
    breakdown: dict[str, list[tuple[str, int]]] = {}
    total = 0.0
    for pillar_name, pdata in weights["pillars"].items():
        comps: list[tuple[str, int]] = []
        pillar_total = 0.0
        for key, w in pdata["components"].items():
            ind = (
                session.query(Indicator)
                .filter_by(asset_id=asset_id, key=key)
                .order_by(Indicator.ts.desc())
                .first()
            )
            if ind:
                comp_score = ind.value * float(w)
                comps.append((key, int(comp_score)))
                pillar_total += comp_score
        breakdown[pillar_name] = comps
        total += pillar_total
    total_int = max(-24, min(24, int(total)))
    ts_row = session.query(Indicator.ts).order_by(Indicator.ts.desc()).first()
    ts = ts_row[0] if ts_row else datetime.utcnow()
    score_obj = Score(
        asset_id=asset_id,
        ts=ts,
        total=total_int,
        breakdown=breakdown,
        version=weights["version"],
    )
    session.add(score_obj)
    session.commit()
    session.refresh(score_obj)
    return score_obj
