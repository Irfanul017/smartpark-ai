"""Simulation router boundary for the later simulation module."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/simulation", tags=["simulation"])
