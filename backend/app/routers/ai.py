"""Endpoints that expose the independent fuzzy intelligence engine."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.ai import calculate_parking_suitability
from app.ai.fuzzy_rules import FUZZY_RULES
from app.database import get_db
from app.models import ParkingSlot, User
from app.schemas import FuzzyScoreRequest, ParkingRequest, RecommendationResponse
from app.services.parking_service import parking_service
from app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/api/ai", tags=["artificial intelligence"])


@router.post("/calculate-score")
def calculate_score(payload: FuzzyScoreRequest) -> dict[str, object]:
    """Call the pure Python fuzzy engine directly without database access."""
    return calculate_parking_suitability(**payload.model_dump())


@router.post("/recommend", response_model=RecommendationResponse)
def recommend_with_ai(
    payload: ParkingRequest, db: Session = Depends(get_db), _: User = Depends(get_current_user)
) -> RecommendationResponse:
    return RecommendationResponse(recommendations=parking_service.recommend(db, payload))


@router.get("/rules")
def get_rules() -> dict[str, list[dict[str, object]]]:
    return {"rules": [
        {
            "id": rule.identifier,
            "antecedents": [{"variable": variable, "term": term} for variable, term in rule.antecedents],
            "consequent": rule.consequent,
            "description": rule.description,
        }
        for rule in FUZZY_RULES
    ]}


@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN"))) -> dict[str, int]:
    total_slots = db.scalar(select(func.count()).select_from(ParkingSlot)) or 0
    occupied_slots = db.scalar(select(func.count()).select_from(ParkingSlot).where(ParkingSlot.is_occupied.is_(True))) or 0
    return {"total_slots": total_slots, "available_slots": total_slots - occupied_slots, "occupied_slots": occupied_slots, "fuzzy_rules": len(FUZZY_RULES)}
