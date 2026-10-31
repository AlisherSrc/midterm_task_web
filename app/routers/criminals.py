"""Router for Wanted Criminals endpoints."""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from ..database import get_db
from ..models import WantedCriminal
from ..schemas import (
    WantedCriminalCreate,
    WantedCriminalDetailOut,
    WantedCriminalOut,
)

router = APIRouter(prefix="/api/criminals", tags=["Wanted Criminals"])


@router.get(
    "/",
    response_model=list[WantedCriminalOut],
    summary="List wanted criminals with filtering and sorting",
    description="Retrieve wanted criminals with optional filtering by bounty range, attributes, and sorting.",
)
def list_criminals(
    db: Annotated[Session, Depends(get_db)],
    min_reward: Annotated[
        float | None,
        Query(description="Filter by minimum bounty amount", ge=0),
    ] = None,
    max_reward: Annotated[
        float | None,
        Query(description="Filter by maximum bounty amount", ge=0),
    ] = None,
    armed: Annotated[
        bool | None,
        Query(description="Filter by armed status (true/false)"),
    ] = None,
    has_crew: Annotated[
        bool | None,
        Query(description="Filter by crew membership (true/false)"),
    ] = None,
    escape_master: Annotated[
        bool | None,
        Query(description="Filter by escape master reputation (true/false)"),
    ] = None,
    sort: Annotated[
        str | None,
        Query(description="Sort order: 'reward' for ascending, '-reward' for descending"),
    ] = None,
) -> list[WantedCriminal]:
    stmt = select(WantedCriminal)

    # Combined filters
    if min_reward is not None:
        stmt = stmt.where(WantedCriminal.reward >= min_reward)
    if max_reward is not None:
        stmt = stmt.where(WantedCriminal.reward <= max_reward)
    if armed is not None:
        stmt = stmt.where(WantedCriminal.armed.is_(armed))
    if has_crew is not None:
        stmt = stmt.where(WantedCriminal.has_crew.is_(has_crew))
    if escape_master is not None:
        stmt = stmt.where(WantedCriminal.escape_master.is_(escape_master))

    # Sorting
    if sort is not None:
        cleaned_sort = sort.strip()
        if cleaned_sort == "reward":
            stmt = stmt.order_by(WantedCriminal.reward.asc(), WantedCriminal.id.asc())
        elif cleaned_sort == "-reward":
            stmt = stmt.order_by(WantedCriminal.reward.desc(), WantedCriminal.id.asc())
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid sort parameter '{sort}'. Valid options are 'reward' or '-reward'.",
            )
    else:
        # Default stable sorting by primary key
        stmt = stmt.order_by(WantedCriminal.id.asc())

    criminals = db.scalars(stmt).all()
    return list(criminals)


@router.get(
    "/{criminal_id}/",
    response_model=WantedCriminalDetailOut,
    summary="Get details of a specific wanted criminal",
    description="Returns detailed dossier for a criminal including all recorded hunt logs.",
)
def get_criminal(
    criminal_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> WantedCriminal:
    stmt = (
        select(WantedCriminal)
        .where(WantedCriminal.id == criminal_id)
        .options(selectinload(WantedCriminal.hunt_logs))
    )
    criminal = db.scalar(stmt)
    if not criminal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wanted criminal with id {criminal_id} not found.",
        )
    return criminal


@router.post(
    "/",
    response_model=WantedCriminalOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new wanted criminal",
    description="Create a new bounty record in the galactic criminal database.",
)
def create_criminal(
    payload: WantedCriminalCreate,
    db: Annotated[Session, Depends(get_db)],
) -> WantedCriminal:
    criminal = WantedCriminal(
        name=payload.name,
        nickname=payload.nickname,
        reward=payload.reward,
        last_known_coordinates=payload.last_known_coordinates,
        difficulty=payload.difficulty,
        armed=payload.armed,
        has_crew=payload.has_crew,
        escape_master=payload.escape_master,
    )
    db.add(criminal)
    db.commit()
    db.refresh(criminal)
    return criminal
