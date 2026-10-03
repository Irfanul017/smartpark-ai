"""Minimal simulation service boundary reserved for the simulation module."""

from __future__ import annotations


class SimulationService:
    def status(self) -> dict[str, str]:
        return {"status": "not_started"}


simulation_service = SimulationService()
