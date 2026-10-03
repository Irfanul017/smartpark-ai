"""Universes of discourse and validation for parking fuzzy variables."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class FuzzyVariable:
    """A numeric variable accepted by the parking suitability engine."""

    name: str
    minimum: float
    maximum: float
    universe: np.ndarray

    def validate(self, value: float | int) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float, np.number)):
            raise ValueError(f"{self.name} must be a number.")
        normalized = float(value)
        if not np.isfinite(normalized):
            raise ValueError(f"{self.name} must be a finite number.")
        if not self.minimum <= normalized <= self.maximum:
            raise ValueError(f"{self.name} must be between {self.minimum:g} and {self.maximum:g}.")
        return normalized


DISTANCE = FuzzyVariable("distance", 0, 200, np.arange(0, 201, 1, dtype=float))
CONGESTION = FuzzyVariable("congestion", 0, 100, np.arange(0, 101, 1, dtype=float))
COMPATIBILITY = FuzzyVariable("compatibility", 0, 100, np.arange(0, 101, 1, dtype=float))
WALKING_DISTANCE = FuzzyVariable("walking_distance", 0, 200, np.arange(0, 201, 1, dtype=float))
PRIORITY = FuzzyVariable("priority", 0, 100, np.arange(0, 101, 1, dtype=float))
SUITABILITY = FuzzyVariable("suitability", 0, 100, np.arange(0, 101, 1, dtype=float))

INPUT_VARIABLES = {variable.name: variable for variable in (DISTANCE, CONGESTION, COMPATIBILITY, WALKING_DISTANCE, PRIORITY)}
