from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FormulaDefinition:
    id: str
    symbol: str
    description: str
    reference: str
    unit: str
    expression: str


class FormulaRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, FormulaDefinition] = {}

    def register(self, definition: FormulaDefinition) -> None:
        if definition.id in self._definitions:
            raise ValueError(f"Duplicate formula id: {definition.id}")
        self._definitions[definition.id] = definition

    def get(self, formula_id: str) -> FormulaDefinition:
        return self._definitions[formula_id]

    def all(self) -> list[FormulaDefinition]:
        return list(self._definitions.values())


REGISTRY = FormulaRegistry()


def formula(
    formula_id: str,
    symbol: str,
    description: str,
    reference: str,
    unit: str,
    expression: str,
) -> FormulaDefinition:
    definition = FormulaDefinition(formula_id, symbol, description, reference, unit, expression)
    REGISTRY.register(definition)
    return definition

