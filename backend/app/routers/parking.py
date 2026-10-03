"""Parking slot and recommendation endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import ParkingRequest, RecommendationResponse, SlotCreate, SlotRead, SlotStatusUpdate, SlotUpdate
from app.services.auth_service import get_current_user, require_roles
from app.services.parking_service import parking_service

router = APIRouter(prefix="/api/parking", tags=["parking"])


@router.get("/slots", response_model=list[SlotRead])
def list_slots(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> list[SlotRead]:
    return parking_service.list_slots(db)


@router.get("/slots/{slot_id}", response_model=SlotRead)
def get_slot(slot_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> SlotRead:
    slot = parking_service.get_slot(db, slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Parking slot not found.")
    return slot


@router.post("/slots", response_model=SlotRead, status_code=status.HTTP_201_CREATED)
def create_slot(payload: SlotCreate, db: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN"))) -> SlotRead:
    try:
        return parking_service.create_slot(db, payload)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.put("/slots/{slot_id}", response_model=SlotRead)
def update_slot(slot_id: int, payload: SlotUpdate, db: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN"))) -> SlotRead:
    slot = parking_service.get_slot(db, slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Parking slot not found.")
    try:
        return parking_service.update_slot(db, slot, payload)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.delete("/slots/{slot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_slot(slot_id: int, db: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN"))) -> None:
    slot = parking_service.get_slot(db, slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Parking slot not found.")
    parking_service.delete_slot(db, slot)


@router.patch("/slots/{slot_id}/status", response_model=SlotRead)
def update_slot_status(
    slot_id: int,
    payload: SlotStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles("ADMIN", "PARKING_OPERATOR")),
) -> SlotRead:
    slot = parking_service.get_slot(db, slot_id)
    if slot is None:
        raise HTTPException(status_code=404, detail="Parking slot not found.")
    return parking_service.set_slot_status(db, slot, payload.is_occupied)


@router.post("/recommend", response_model=RecommendationResponse)
def recommend_parking(
    payload: ParkingRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> RecommendationResponse:
    return RecommendationResponse(recommendations=parking_service.recommend(db, payload))
