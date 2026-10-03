"""Mamdani fuzzy inference and centroid defuzzification implementation."""

from __future__ import annotations

from typing import Any

import numpy as np
import skfuzzy as fuzz

from .fuzzy_rules import FUZZY_RULES
from .fuzzy_variables import INPUT_VARIABLES, SUITABILITY
from .membership_functions import INPUT_MEMBERSHIP_FUNCTIONS, OUTPUT_MEMBERSHIP_FUNCTIONS


class ParkingFuzzyEngine:
    """Evaluate parking suitability using declared fuzzy variables and rules."""

    def evaluate(self, **inputs: float | int) -> dict[str, Any]:
        values = self._validate_inputs(inputs)
        memberships = self._fuzzify(values)
        activated_rules = self._activate_rules(memberships)
        aggregate = self._aggregate(activated_rules)

        # The prescribed rules do not cover every all-medium combination. A neutral,
        # deterministic medium fallback keeps valid inputs defuzzifiable and explicit.
        if not activated_rules:
            aggregate = OUTPUT_MEMBERSHIP_FUNCTIONS["MEDIUM"].copy()
            activated_rules = [{
                "id": "FALLBACK",
                "strength": 1.0,
                "consequent": "MEDIUM",
                "description": "No project rule was activated; using neutral medium suitability.",
            }]

        score = float(fuzz.defuzz(SUITABILITY.universe, aggregate, "centroid"))
        return {
            "score": round(float(np.clip(score, 0, 100)), 2),
            "membership_values": memberships,
            "activated_rules": activated_rules,
        }

    @staticmethod
    def _validate_inputs(inputs: dict[str, float | int]) -> dict[str, float]:
        missing = set(INPUT_VARIABLES) - set(inputs)
        extra = set(inputs) - set(INPUT_VARIABLES)
        if missing or extra:
            details = []
            if missing:
                details.append(f"missing: {', '.join(sorted(missing))}")
            if extra:
                details.append(f"unexpected: {', '.join(sorted(extra))}")
            raise ValueError("Invalid fuzzy-engine inputs (" + "; ".join(details) + ").")
        return {name: variable.validate(inputs[name]) for name, variable in INPUT_VARIABLES.items()}

    @staticmethod
    def _fuzzify(values: dict[str, float]) -> dict[str, dict[str, float]]:
        return {
            name: {
                term: round(float(fuzz.interp_membership(INPUT_VARIABLES[name].universe, function, values[name])), 4)
                for term, function in terms.items()
            }
            for name, terms in INPUT_MEMBERSHIP_FUNCTIONS.items()
        }

    @staticmethod
    def _activate_rules(memberships: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
        activated: list[dict[str, Any]] = []
        for rule in FUZZY_RULES:
            strength = min(memberships[variable][term] for variable, term in rule.antecedents)
            if strength > 0:
                activated.append({
                    "id": rule.identifier,
                    "strength": round(strength, 4),
                    "consequent": rule.consequent,
                    "description": rule.description,
                })
        return activated

    @staticmethod
    def _aggregate(activated_rules: list[dict[str, Any]]) -> np.ndarray:
        aggregate = np.zeros_like(SUITABILITY.universe)
        for activation in activated_rules:
            clipped = np.fmin(activation["strength"], OUTPUT_MEMBERSHIP_FUNCTIONS[activation["consequent"]])
            aggregate = np.fmax(aggregate, clipped)
        return aggregate
