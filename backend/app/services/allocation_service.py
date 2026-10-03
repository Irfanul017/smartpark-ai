"""Transactional parking allocation and release operations."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ParkingSession, ParkingSlot
from app.schemas import AllocationRequest
from app.services.parking_service import parking_service


class AllocationService:
    def allocate(self, db: Session, request: AllocationRequest, user_id: int) -> tuple[ParkingSession, ParkingSlot]:
        slot = db.get(ParkingSlot, request.selected_slot_id)
        if slot is None:
            raise LookupError("Selected parking slot was not found.")
        if slot.is_occupied:
            raise ValueError("Selected parking slot is no longer available.")
        if not parking_service.is_compatible(slot, request):
            raise ValueError("Selected parking slot is incompatible with this request.")

        session = ParkingSession(slot_id=slot.id, user_id=user_id, vehicle_type=request.vehicle_type, priority=request.priority)
        slot.is_occupied = True
        db.add(session)
        db.commit()
        db.refresh(session)
        db.refresh(slot)
        return session, slot

    def release(self, db: Session, slot_id: int, user_id: int, is_privileged: bool = False) -> ParkingSession:
        slot = db.get(ParkingSlot, slot_id)
        if slot is None:
            raise LookupError("Parking slot was not found.")
        if not slot.is_occupied:
            raise ValueError("Parking slot is already available.")
        session = db.scalar(
            select(ParkingSession)
            .where(ParkingSession.slot_id == slot_id, ParkingSession.ended_at.is_(None))
            .order_by(ParkingSession.started_at.desc())
        )
        if session is None:
            raise ValueError("No active parking session exists for this slot.")
        if not is_privileged and session.user_id != user_id:
            raise PermissionError("You can release only your own parking session.")
        slot.is_occupied = False
        session.ended_at = datetime.utcnow()
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def history(db: Session, user_id: int | None = None, active_only: bool = False) -> list[ParkingSession]:
        statement = select(ParkingSession).order_by(ParkingSession.started_at.desc())
        if user_id is not None:
            statement = statement.where(ParkingSession.user_id == user_id)
        if active_only:
            statement = statement.where(ParkingSession.ended_at.is_(None))
        return list(db.scalars(statement))


allocation_service = AllocationService()
