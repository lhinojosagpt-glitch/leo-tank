from __future__ import annotations

import pytest

from app.engine.seismic import calculate_seismic


def test_t78_seismic_chain(t78: dict) -> None:
    result = calculate_seismic(t78)
    v = result.values
    assert v["Ss"] == pytest.approx(1.125, abs=1e-6)
    assert v["S1"] == pytest.approx(0.5625, abs=1e-6)
    assert v["SDS"] == pytest.approx(1.18125, abs=1e-6)
    assert v["Ai"] == pytest.approx(0.2953125, abs=1e-7)
    assert v["Ac"] == pytest.approx(0.045761, rel=1e-4)
    assert v["Tc_s"] == pytest.approx(t78["golden"]["Tc_s"], abs=1e-4)
    assert v["J"] == pytest.approx(t78["golden"]["J"], abs=1e-4)
    assert v["anchorage_classification"] == "MECHANICAL_ANCHORAGE_REQUIRED"
    assert v["required_anchor_bolts"] == 48


def test_t78_seismic_hoop_stress(t78: dict) -> None:
    result = calculate_seismic(t78)
    actual = [row["stress_kPa"] for row in result.values["hoop"]]
    assert actual == pytest.approx(t78["golden"]["hoop_stress_kPa"], rel=0.001)
    assert all(row["status"] == "PASS" for row in result.values["hoop"])

