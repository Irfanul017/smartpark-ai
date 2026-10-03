"""Parking allocation lifecycle endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import AllocationRequest, AllocationResponse, ReleaseRequest, ReleaseResponse, SessionRead
from app.services.allocation_service import allocation_service
from app.services.auth_service import get_current_user, require_roles

router = APIRouter(prefix="/api/parking", tags=["allocation"])


@router.post("/allocate", response_model=AllocationResponse)
def allocate_parking(
    payload: AllocationRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> AllocationResponse:
    try:
        session, slot = allocation_service.allocate(db, payload, current_user.id)
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    return AllocationResponse(
        session_id=session.id,
        slot_id=slot.id,
        slot=slot.slot_number,
        status="allocated",
        started_at=session.started_at,
    )


@router.post("/release", response_model=ReleaseResponse)
def release_parking(
    payload: ReleaseRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> ReleaseResponse:
    try:
        session = allocation_service.release(
            db, payload.slot_id, current_user.id, current_user.role in {"ADMIN", "PARKING_OPERATOR"}
        )
    except LookupError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    except PermissionError as error:
        raise HTTPException(status_code=403, detail=str(error)) from error
    return ReleaseResponse(session_id=session.id, slot_id=payload.slot_id, status="released", ended_at=session.ended_at)


@router.get("/history", response_model=list[SessionRead])
def own_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> list[SessionRead]:
    return allocation_service.history(db, user_id=current_user.id)


@router.get("/allocation-history", response_model=list[SessionRead])
def allocation_history(
    db: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN"))
) -> list[SessionRead]:
    return allocation_service.history(db)


@router.get("/active-sessions", response_model=list[SessionRead])
def active_sessions(
    db: Session = Depends(get_db), _: User = Depends(require_roles("ADMIN", "PARKING_OPERATOR"))
) -> list[SessionRead]:
    return allocation_service.history(db, active_only=True)
