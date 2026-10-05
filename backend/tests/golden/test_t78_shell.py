from __future__ import annotations

import pytest

from app.engine.shell import calculate_shell


GOLDEN_TOLERANCES = {"thickness_mm": 0.01}


def test_shell_t78_design_thickness(t78: dict) -> None:
    result = calculate_shell(t78)
    actual = [row["design_mm"] for row in result.values["courses"]]
    expected = t78["golden"]["shell_design_mm"]
    assert actual == pytest.approx(expected, abs=GOLDEN_TOLERANCES["thickness_mm"])


def test_shell_t78_hydrotest_thickness(t78: dict) -> None:
    result = calculate_shell(t78)
    actual = [row["hydrotest_mm"] for row in result.values["courses"]]
    expected = t78["golden"]["shell_hydrotest_mm"]
    assert actual == pytest.approx(expected, abs=GOLDEN_TOLERANCES["thickness_mm"])


def test_shell_t78_minimum_thickness(t78: dict) -> None:
    result = calculate_shell(t78)
    assert [row["design_mm"] for row in result.values["courses"]][-2:] == [8.0, 8.0]
    assert [row["hydrotest_mm"] for row in result.values["courses"]][-2:] == [8.0, 8.0]
    assert result.status == "PASS"

