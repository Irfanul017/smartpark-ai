"""SQLAlchemy entities used by the Module 3 parking APIs."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class ParkingSlot(Base):
    __tablename__ = "parking_slots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slot_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    floor: Mapped[str] = mapped_column(String(20), default="G")
    zone: Mapped[str] = mapped_column(String(20), default="A")
    slot_type: Mapped[str] = mapped_column(String(30), default="Normal")
    vehicle_type: Mapped[str] = mapped_column(String(30), default="Car")
    is_ev: Mapped[bool] = mapped_column(Boolean, default=False)
    is_accessible: Mapped[bool] = mapped_column(Boolean, default=False)
    is_reserved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_occupied: Mapped[bool] = mapped_column(Boolean, default=False)
    distance_from_entrance: Mapped[float] = mapped_column(default=100.0)
    walking_distance: Mapped[float] = mapped_column(default=100.0)
    congestion_level: Mapped[float] = mapped_column(default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="USER")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ParkingSession(Base):
    __tablename__ = "parking_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slot_id: Mapped[int] = mapped_column(ForeignKey("parking_slots.id"), index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    vehicle_type: Mapped[str] = mapped_column(String(30))
    priority: Mapped[float] = mapped_column(default=50.0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
