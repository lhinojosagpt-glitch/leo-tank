from __future__ import annotations

import copy
from itertools import product
from typing import Any

from app.assistant.variables import VARIABLES, fixed_for, variables_for
from app.engine.runner import calculate


def _find_check(result: dict[str, Any], check_id: str) -> dict[str, Any]:
    for module in result.get("modules", {}).values():
        for check in module.get("checks", []):
            if check.get("check_id") == check_id:
                return check
    raise KeyError(check_id)


def _set(target: dict[str, Any], path: str, value: Any) -> None:
    cursor: Any = target
    parts = path.replace("]", "").replace("[", ".").split(".")
    for part in parts[:-1]:
        cursor = cursor[int(part)] if isinstance(cursor, list) else cursor[part]
    if isinstance(cursor, list):
        cursor[int(parts[-1])] = value
    else:
        cursor[parts[-1]] = value


def _candidate_changes(variable, value: float, inputs: dict[str, Any]) -> dict[str, Any]:
    changes = {variable.path: value}
    if variable.id == "annular_plate_thickness":
        changes["bottom.annular_effective_thickness_mm"] = value - inputs["bottom"]["annular_corrosion_allowance_mm"]
    return changes


def analyze_run(result: dict[str, Any], inputs: dict[str, Any]) -> dict[str, Any]:
    failed = []
    for module_name, module in result.get("modules", {}).items():
        for check in module.get("checks", []):
            if check.get("status") == "FAIL":
                check_id = check["check_id"]
                adjustable = variables_for(check_id, inputs)
                for variable_data in adjustable:
                    variable = next(row for row in VARIABLES if row.id == variable_data["id"])
                    trial_values = [value for value in variable.discrete_values if value != variable_data["current_value"]]
                    if trial_values and check.get("utilization") is not None:
                        trial_inputs = copy.deepcopy(inputs)
                        for path, changed_value in _candidate_changes(variable, trial_values[0], inputs).items():
                            _set(trial_inputs, path, changed_value)
                        trial_check = _find_check(calculate(trial_inputs).to_dict(), check_id)
                        delta_x = trial_values[0] - variable_data["current_value"]
                        derivative = ((trial_check.get("utilization") or 0) - check["utilization"]) / delta_x if delta_x else 0
                        magnitude = abs(derivative * max(abs(variable_data["current_value"]), 1))
                        variable_data["sensitivity"] = {"classification": "HIGH" if magnitude >= 0.25 else "MEDIUM" if magnitude >= 0.08 else "LOW", "delta_utilization_per_unit": derivative, "trial_value": trial_values[0]}
                failed.append({
                    **check,
                    "module": module_name,
                    "difference_to_limit": (check.get("demand") or 0) - (check.get("capacity") or 0),
                    "classification": check.get("fail_classification") or "DESIGN_FAIL",
                    "adjustable_variables": adjustable,
                    "fixed_variables": fixed_for(check_id, inputs),
                    "overall_design_status": result.get("overall_status"),
                })
    return {"failed_checks": failed, "overall_design_status": result.get("overall_status"), "engine_version": result.get("engine_version"), "standard_profile": result.get("standard_profile")}


def execute_study(inputs: dict[str, Any], check_id: str, selected_ids: list[str], target_utilization: float, max_simulations: int) -> list[dict[str, Any]]:
    allowed = [v for v in VARIABLES if check_id in v.affects_checks and v.editable and not v.derived and not v.standard_defined]
    if selected_ids:
        allowed = [v for v in allowed if v.id in selected_ids]
    allowed = allowed[:3]
    if not allowed:
        return []
    value_sets = []
    for variable in allowed:
        values = variable.discrete_values
        if not values and variable.increment and variable.maximum is not None:
            values = tuple(variable.minimum + i * variable.increment for i in range(int((variable.maximum - variable.minimum) / variable.increment) + 1))
        value_sets.append(values)
    candidates = []
    for values in list(product(*value_sets))[:max_simulations]:
        candidate_inputs = copy.deepcopy(inputs)
        changes: dict[str, Any] = {}
        tested = {}
        for variable, value in zip(allowed, values):
            tested[variable.id] = value
            for path, changed_value in _candidate_changes(variable, value, inputs).items():
                _set(candidate_inputs, path, changed_value)
                changes[path] = changed_value
        calculated = calculate(candidate_inputs).to_dict()
        check = _find_check(calculated, check_id)
        utilization = check.get("utilization") or float("inf")
        passing = check.get("status") == "PASS" and utilization <= target_utilization + 1e-12
        normalized_change = 0.0
        for variable, value in zip(allowed, values):
            current = variable.public(inputs)["current_value"]
            span = max((variable.maximum or value) - (variable.minimum or current), 1.0)
            normalized_change += abs(value - current) / span
        candidates.append({"changes": changes, "values_tested": tested, "result": calculated, "check": check, "passing": passing, "score": normalized_change})
    candidates.sort(key=lambda row: (not row["passing"], row["score"], row["check"].get("utilization") or 999))
    return candidates
