"""Extensible declarative rule set for parking suitability inference."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FuzzyRule:
    identifier: str
    antecedents: tuple[tuple[str, str], ...]
    consequent: str
    description: str


# These rules directly implement the twelve rules defined in PROJECT_CONTEXT.md.
FUZZY_RULES: tuple[FuzzyRule, ...] = (
    FuzzyRule("R1", (("distance", "NEAR"), ("congestion", "LOW"), ("compatibility", "EXCELLENT")), "VERY_HIGH", "Near entrance, low congestion, and excellent compatibility."),
    FuzzyRule("R2", (("distance", "NEAR"), ("congestion", "MEDIUM"), ("compatibility", "EXCELLENT")), "HIGH", "Near entrance and excellent compatibility despite medium congestion."),
    FuzzyRule("R3", (("distance", "FAR"), ("congestion", "HIGH")), "LOW", "Far from the entrance with high congestion."),
    FuzzyRule("R4", (("compatibility", "POOR"),), "VERY_LOW", "Poor vehicle-to-slot compatibility."),
    FuzzyRule("R5", (("distance", "MEDIUM"), ("congestion", "LOW"), ("compatibility", "EXCELLENT")), "HIGH", "Medium distance with low congestion and excellent compatibility."),
    FuzzyRule("R6", (("walking_distance", "SHORT"), ("congestion", "LOW")), "HIGH", "Short walking distance and low congestion."),
    FuzzyRule("R7", (("walking_distance", "LONG"), ("congestion", "HIGH")), "LOW", "Long walking distance with high congestion."),
    FuzzyRule("R8", (("priority", "HIGH"), ("compatibility", "EXCELLENT")), "VERY_HIGH", "High user priority and excellent compatibility."),
    FuzzyRule("R9", (("priority", "LOW"), ("distance", "FAR")), "LOW", "Low user priority and a far slot."),
    FuzzyRule("R10", (("distance", "NEAR"), ("compatibility", "ACCEPTABLE"), ("congestion", "LOW")), "HIGH", "Near, acceptably compatible, and uncongested."),
    FuzzyRule("R11", (("distance", "FAR"), ("compatibility", "EXCELLENT"), ("congestion", "LOW")), "MEDIUM", "Far but excellently compatible and uncongested."),
    FuzzyRule("R12", (("distance", "MEDIUM"), ("walking_distance", "SHORT"), ("congestion", "LOW")), "HIGH", "Medium entrance distance but short walking distance and low congestion."),
)
