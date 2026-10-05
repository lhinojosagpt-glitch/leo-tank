from __future__ import annotations

import pytest

from app.engine.runner import calculate


def test_t78_full_case(t78: dict) -> None:
    result = calculate(t78)
    assert result.overall_status == "PASS_WITH_MECHANICAL_ANCHORAGE"
    assert result.summary["shell"]["status"] == "PASS"
    assert result.summary["wind"]["anchors_required"] is False
    assert result.summary["anchorage"]["required"] is True
    assert result.summary["anchorage"]["selected_bolts"] == 60
    combined = result.modules["anchorage"].values["load_cases"][-1]
    assert combined["stress_kPa"] == pytest.approx(t78["golden"]["anchor_combined_stress_kPa"], rel=0.001)
    assert result.modules["anchor_chairs"].values["required_top_plate_mm"] == pytest.approx(t78["golden"]["chair_required_mm"], abs=0.01)
    assert len(result.geometry["courses"]) == 8
    assert len(result.geometry["anchors"]) == 60

