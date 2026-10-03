"""Pydantic DTOs for SmartPark AI's HTTP API."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class SlotBase(BaseModel):
    slot_number: str = Field(min_length=1, max_length=20)
    floor: str = Field(default="G", min_length=1, max_length=20)
    zone: str = Field(default="A", min_length=1, max_length=20)
    slot_type: str = Field(default="Normal", min_length=1, max_length=30)
    vehicle_type: str = Field(default="Car", min_length=1, max_length=30)
    is_ev: bool = False
    is_accessible: bool = False
    is_reserved: bool = False
    is_occupied: bool = False
    distance_from_entrance: float = Field(ge=0, le=200)
    walking_distance: float = Field(ge=0, le=200)
    congestion_level: float = Field(ge=0, le=100)


class SlotCreate(SlotBase):
    pass


class SlotUpdate(BaseModel):
    slot_number: str | None = Field(default=None, min_length=1, max_length=20)
    floor: str | None = Field(default=None, min_length=1, max_length=20)
    zone: str | None = Field(default=None, min_length=1, max_length=20)
    slot_type: str | None = Field(default=None, min_length=1, max_length=30)
    vehicle_type: str | None = Field(default=None, min_length=1, max_length=30)
    is_ev: bool | None = None
    is_accessible: bool | None = None
    is_reserved: bool | None = None
    is_occupied: bool | None = None
    distance_from_entrance: float | None = Field(default=None, ge=0, le=200)
    walking_distance: float | None = Field(default=None, ge=0, le=200)
    congestion_level: float | None = Field(default=None, ge=0, le=100)


class SlotRead(SlotBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class ParkingRequest(BaseModel):
    vehicle_type: str = Field(min_length=1, max_length=30)
    requires_ev: bool = False
    requires_accessible: bool = False
    priority: float = Field(default=50, ge=0, le=100)


class Recommendation(BaseModel):
    slot: str
    slot_id: int
    score: float
    category: str
    reason: str
    factors: dict[str, Any]


class RecommendationResponse(BaseModel):
    recommendations: list[Recommendation]


class AllocationRequest(ParkingRequest):
    selected_slot_id: int = Field(gt=0)


class ReleaseRequest(BaseModel):
    slot_id: int = Field(gt=0)


class AllocationResponse(BaseModel):
    session_id: int
    slot_id: int
    slot: str
    status: str
    started_at: datetime


class ReleaseResponse(BaseModel):
    session_id: int
    slot_id: int
    status: str
    ended_at: datetime


class FuzzyScoreRequest(BaseModel):
    distance: float = Field(ge=0, le=200)
    congestion: float = Field(ge=0, le=100)
    compatibility: float = Field(ge=0, le=100)
    walking_distance: float = Field(ge=0, le=200)
    priority: float = Field(ge=0, le=100)


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)
    # Roles are selectable for the academic demonstration environment.
    role: Literal["USER", "ADMIN", "PARKING_OPERATOR"] = "USER"


class LoginRequest(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str
    role: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SlotStatusUpdate(BaseModel):
    is_occupied: bool


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slot_id: int
    user_id: int | None
    vehicle_type: str
    priority: float
    started_at: datetime
    ended_at: datetime | None
