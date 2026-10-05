from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.engine.common import unwrap


@pytest.fixture(scope="session")
def fixture_raw() -> dict:
    path = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "T78_2019.json"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def t78(fixture_raw: dict) -> dict:
    return unwrap(fixture_raw)

