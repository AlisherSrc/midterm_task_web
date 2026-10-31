"""Router for Bounty Hunting Journal (HuntLog) CRUD endpoints."""

from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import HuntLog, WantedCriminal
from ..schemas import HuntLogCreate, HuntLogOut, HuntLogUpdate

router = APIRouter(prefix="/api/hunts", tags=["Bounty Hunting Journal"])


@router.get(
    "/",
    response_model=list[HuntLogOut],
    summary="List all hunt logs",
    description="Retrieve capture attempt journal logs with optional filtering by criminal ID.",
)
def list_hunts(
    db: Annotated[Session, Depends(get_db)],
    criminal_id: Annotated[
        int | None,
        Query(description="Filter logs for a specific criminal ID"),
    ] = None,
) -> list[HuntLog]:
    stmt = select(HuntLog)
    if criminal_id is not None:
        stmt = stmt.where(HuntLog.criminal_id == criminal_id)

    stmt = stmt.order_by(HuntLog.created_at.desc(), HuntLog.id.desc())
    logs = db.scalars(stmt).all()
    return list(logs)


@router.get(
    "/{hunt_id}/",
    response_model=HuntLogOut,
    summary="Get one hunt log",
    description="Retrieve a single bounty encounter log by its unique identifier.",
)
def get_hunt(
    hunt_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> HuntLog:
    hunt_log = db.get(HuntLog, hunt_id)
    if not hunt_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hunt log with id {hunt_id} not found.",
        )
    return hunt_log


@router.post(
    "/",
    response_model=HuntLogOut,
    status_code=status.HTTP_201_CREATED,
    summary="Record a capture attempt",
    description="Record a new bounty hunting attempt. The criminal must exist and timestamp is server-generated.",
)
def create_hunt(
    payload: HuntLogCreate,
    db: Annotated[Session, Depends(get_db)],
) -> HuntLog:
    # Validate referenced criminal exists
    criminal = db.get(WantedCriminal, payload.criminal_id)
    if not criminal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cannot record hunt: Wanted criminal with id {payload.criminal_id} does not exist.",
        )

    # Server generates the creation timestamp automatically
    hunt_log = HuntLog(
        criminal_id=payload.criminal_id,
        success=payload.success,
        notes=payload.notes.strip(),
        created_at=datetime.now(timezone.utc),
    )
    db.add(hunt_log)
    db.commit()
    db.refresh(hunt_log)
    return hunt_log


@router.patch(
    "/{hunt_id}/",
    response_model=HuntLogOut,
    summary="Update success or notes of a hunt log",
    description="Partially update capture status and/or encounter notes of an existing log entry.",
)
def update_hunt(
    hunt_id: int,
    payload: HuntLogUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> HuntLog:
    hunt_log = db.get(HuntLog, hunt_id)
    if not hunt_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hunt log with id {hunt_id} not found.",
        )

    if payload.success is None and payload.notes is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field ('success' or 'notes') must be provided for update.",
        )

    if payload.success is not None:
        hunt_log.success = payload.success
    if payload.notes is not None:
        hunt_log.notes = payload.notes.strip()

    db.commit()
    db.refresh(hunt_log)
    return hunt_log


@router.delete(
    "/{hunt_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a hunt log",
    description="Permanently remove a hunt log entry from the journal.",
)
def delete_hunt(
    hunt_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    hunt_log = db.get(HuntLog, hunt_id)
    if not hunt_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hunt log with id {hunt_id} not found.",
        )

    db.delete(hunt_log)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
