from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

M_TO_FT = 1 / 0.3048
MM_TO_IN = 1 / 25.4
LB_TO_N = 4.4482216152605
FTLB_TO_NM = 1.3558179483314
PSI_TO_KPA = 6.894757293168
LBFT_TO_NM = 14.5939029372


def unwrap(value: Any) -> Any:
    if isinstance(value, dict):
        if "value" in value and set(value).issubset({"value", "unit", "source", "note"}):
            return unwrap(value["value"])
        return {key: unwrap(item) for key, item in value.items()}
    if isinstance(value, list):
        return [unwrap(item) for item in value]
    return value


def canonical_sha256(data: dict[str, Any]) -> str:
    payload = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_fixture(path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw, unwrap(raw)

