from __future__ import annotations

from typing import Any, Dict, Tuple


def payload_to_indicator(payload: Dict[str, Any]) -> Tuple[str, float]:
    key = str(payload["key"])
    value = float(payload["value"])
    return key, value
