from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import get_seats_usecase
from app.db.database import get_db
from app.repositories.event_repository import EventRepository
from app.repositories.place_repository import PlaceRepository
from app.usecases.get_seats import GetSeatsUsecase
from app.usecases.get_events import GetEventsUsecase
from app.usecases.get_event_detail import GetEventDetailUsecase

router = APIRouter(tags=["events"])


@router.get("/api/events")
async def get_events(
    date_from: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    event_repo = EventRepository(db)
    place_repo = PlaceRepository(db)
    usecase = GetEventsUsecase(event_repo, place_repo)

    result = await usecase.do(
        date_from=date_from,
        page=page,
        page_size=page_size,
        base_url="/api/events"
    )

    return result


@router.get("/api/events/{event_id}")
async def get_event(
    event_id: str,
    db: Session = Depends(get_db)
):
    event_repo = EventRepository(db)
    place_repo = PlaceRepository(db)
    usecase = GetEventDetailUsecase(event_repo, place_repo)

    try:
        result = await usecase.do(event_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/api/events/{event_id}/seats")
async def get_seats(
    event_id: str,
    db: Session = Depends(get_db),
    usecase: GetSeatsUsecase = Depends(get_seats_usecase),
):
    try:
        seats = await usecase.do(event_id)
        return {"event_id": event_id, "available_seats": seats}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))