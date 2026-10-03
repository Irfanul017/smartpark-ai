"""Membership functions used by the SmartPark AI fuzzy inference engine."""

from __future__ import annotations

import numpy as np
import skfuzzy as fuzz

from .fuzzy_variables import COMPATIBILITY, CONGESTION, DISTANCE, PRIORITY, SUITABILITY, WALKING_DISTANCE


def _trap(universe: np.ndarray, points: list[float]) -> np.ndarray:
    return fuzz.trapmf(universe, points)


def _tri(universe: np.ndarray, points: list[float]) -> np.ndarray:
    return fuzz.trimf(universe, points)


# Each term overlaps its neighbours so gradual input changes create gradual scores.
INPUT_MEMBERSHIP_FUNCTIONS: dict[str, dict[str, np.ndarray]] = {
    "distance": {"NEAR": _trap(DISTANCE.universe, [0, 0, 30, 50]), "MEDIUM": _tri(DISTANCE.universe, [30, 75, 120]), "FAR": _trap(DISTANCE.universe, [100, 150, 200, 200])},
    "congestion": {"LOW": _trap(CONGESTION.universe, [0, 0, 20, 30]), "MEDIUM": _tri(CONGESTION.universe, [20, 45, 70]), "HIGH": _trap(CONGESTION.universe, [60, 80, 100, 100])},
    "compatibility": {"POOR": _trap(COMPATIBILITY.universe, [0, 0, 30, 40]), "ACCEPTABLE": _tri(COMPATIBILITY.universe, [30, 52.5, 75]), "EXCELLENT": _trap(COMPATIBILITY.universe, [65, 80, 100, 100])},
    "walking_distance": {"SHORT": _trap(WALKING_DISTANCE.universe, [0, 0, 30, 50]), "MEDIUM": _tri(WALKING_DISTANCE.universe, [30, 75, 120]), "LONG": _trap(WALKING_DISTANCE.universe, [100, 150, 200, 200])},
    "priority": {"LOW": _trap(PRIORITY.universe, [0, 0, 30, 40]), "MEDIUM": _tri(PRIORITY.universe, [30, 52.5, 75]), "HIGH": _trap(PRIORITY.universe, [65, 80, 100, 100])},
}

OUTPUT_MEMBERSHIP_FUNCTIONS: dict[str, np.ndarray] = {
    "VERY_LOW": _trap(SUITABILITY.universe, [0, 0, 10, 25]),
    "LOW": _tri(SUITABILITY.universe, [15, 30, 45]),
    "MEDIUM": _tri(SUITABILITY.universe, [40, 55, 70]),
    "HIGH": _tri(SUITABILITY.universe, [65, 77.5, 90]),
    "VERY_HIGH": _trap(SUITABILITY.universe, [85, 95, 100, 100]),
}
