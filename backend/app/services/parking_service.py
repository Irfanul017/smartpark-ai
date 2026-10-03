"""Parking-slot CRUD and fuzzy recommendation business logic."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.ai import calculate_parking_suitability
from app.models import ParkingSlot
from app.schemas import ParkingRequest, SlotCreate, SlotUpdate


class ParkingService:
    def list_slots(self, db: Session) -> list[ParkingSlot]:
        return list(db.scalars(select(ParkingSlot).order_by(ParkingSlot.slot_number)))

    def get_slot(self, db: Session, slot_id: int) -> ParkingSlot | None:
        return db.get(ParkingSlot, slot_id)

    def create_slot(self, db: Session, payload: SlotCreate) -> ParkingSlot:
        slot = ParkingSlot(**payload.model_dump())
        db.add(slot)
        return self._commit_slot(db, slot)

    def update_slot(self, db: Session, slot: ParkingSlot, payload: SlotUpdate) -> ParkingSlot:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(slot, field, value)
        return self._commit_slot(db, slot)

    def delete_slot(self, db: Session, slot: ParkingSlot) -> None:
        db.delete(slot)
        db.commit()

    def set_slot_status(self, db: Session, slot: ParkingSlot, is_occupied: bool) -> ParkingSlot:
        slot.is_occupied = is_occupied
        db.commit()
        db.refresh(slot)
        return slot

    def recommend(self, db: Session, request: ParkingRequest) -> list[dict[str, object]]:
        eligible_slots = [
            slot for slot in db.scalars(
                select(ParkingSlot).where(ParkingSlot.is_occupied.is_(False), ParkingSlot.is_reserved.is_(False))
            )
            if self.is_compatible(slot, request)
        ]
        recommendations: list[dict[str, object]] = []
        for slot in eligible_slots:
            fuzzy_result = calculate_parking_suitability(
                distance=slot.distance_from_entrance,
                congestion=slot.congestion_level,
                compatibility=100,
                walking_distance=slot.walking_distance,
                priority=request.priority,
            )
            recommendations.append({
                "slot": slot.slot_number,
                "slot_id": slot.id,
                "score": fuzzy_result["score"],
                "category": fuzzy_result["category"],
                "reason": fuzzy_result["explanation"],
                "factors": {
                    "distance": slot.distance_from_entrance,
                    "congestion": slot.congestion_level,
                    "compatibility": 100,
                    "walking_distance": slot.walking_distance,
                    "priority": request.priority,
                    "membership_values": fuzzy_result["membership_values"],
                    "activated_rules": fuzzy_result["activated_rules"],
                },
            })
        return sorted(recommendations, key=lambda item: float(item["score"]), reverse=True)[:3]

    @staticmethod
    def is_compatible(slot: ParkingSlot, request: ParkingRequest) -> bool:
        if request.requires_ev and not slot.is_ev:
            return False
        if request.requires_accessible and not slot.is_accessible:
            return False
        return slot.vehicle_type.strip().casefold() == request.vehicle_type.strip().casefold()

    @staticmethod
    def _commit_slot(db: Session, slot: ParkingSlot) -> ParkingSlot:
        try:
            db.commit()
        except IntegrityError as error:
            db.rollback()
            raise ValueError("A parking slot with this slot number already exists.") from error
        db.refresh(slot)
        return slot


parking_service = ParkingService()
