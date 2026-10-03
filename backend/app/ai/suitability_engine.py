"""Public, framework-independent parking suitability API."""

from __future__ import annotations

from typing import Any

import skfuzzy as fuzz

from .fuzzy_engine import ParkingFuzzyEngine
from .fuzzy_variables import SUITABILITY
from .membership_functions import OUTPUT_MEMBERSHIP_FUNCTIONS


ENGINE = ParkingFuzzyEngine()


def calculate_parking_suitability(
    distance: float | int,
    congestion: float | int,
    compatibility: float | int,
    walking_distance: float | int,
    priority: float | int,
) -> dict[str, Any]:
    """Calculate a deterministic, explainable 0–100 parking suitability score."""
    result = ENGINE.evaluate(
        distance=distance,
        congestion=congestion,
        compatibility=compatibility,
        walking_distance=walking_distance,
        priority=priority,
    )
    score = result["score"]
    category = _category_for_score(score)
    activated = result["activated_rules"]
    return {
        "score": score,
        "category": category,
        "membership_values": result["membership_values"],
        "activated_rules": activated,
        "explanation": _build_explanation(score, category, activated),
    }


def _category_for_score(score: float) -> str:
    strengths = {
        term: float(fuzz.interp_membership(SUITABILITY.universe, function, score))
        for term, function in OUTPUT_MEMBERSHIP_FUNCTIONS.items()
    }
    return max(strengths, key=strengths.get)


def _build_explanation(score: float, category: str, activated_rules: list[dict[str, Any]]) -> str:
    reasons = [rule["description"] for rule in activated_rules]
    return f"Suitability score: {score:.2f}/100 ({category}). Activated rules: " + "; ".join(reasons)
