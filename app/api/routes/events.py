from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.api.dependencies import get_events_provider_client
from app.db.database import get_db
from app.repositories.event_repository import EventRepository
from app.repositories.place_repository import PlaceRepository
from app.services.events_provider_client import EventsProviderClient
from app.models.event import Event
from app.core.config import EVENTS_PROVIDER_URL, EVENTS_PROVIDER_API_KEY
from app.usecases.get_seats import GetSeatsUsecase

router = APIRouter(tags=["events"])


@router.get("/api/events")
async def get_events(
        date_from: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        db: Session = Depends(get_db)
):
    skip = (page - 1) * page_size
    event_repo = EventRepository(db)
    events = event_repo.list(date_from, skip, page_size)
    total_count = event_repo.count(date_from)

    next_page = page + 1 if skip + page_size < total_count else None
    previous_page = page - 1 if page > 1 else None

    base_url = "/api/events"
    next_url = f"{base_url}?page={next_page}&page_size={page_size}" if next_page else None
    previous_url = f"{base_url}?page={previous_page}&page_size={page_size}" if previous_page else None

    return {
        "count": total_count,
        "next": next_url,
        "previous": previous_url,
        "results": events
    }


@router.get("/api/events/{event_id}")
async def get_event(
        event_id: str,
        db: Session = Depends(get_db)
):
    event_repo = EventRepository(db)
    event = event_repo.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    place_repo = PlaceRepository(db)
    place = place_repo.get(event.place_id)

    return {
        "id": event.id,
        "name": event.name,
        "place": {
            "id": place.id,
            "name": place.name,
            "city": place.city,
            "address": place.address,
            "seats_pattern": place.seats_pattern,
        },
        "event_time": event.event_time,
        "registration_deadline": event.registration_deadline,
        "status": event.status,
        "number_of_visitors": event.number_of_visitors,
    }


@router.get("/api/events/{event_id}/seats")
async def get_seats(
        event_id: str,
        db: Session = Depends(get_db),
        client: EventsProviderClient = Depends(get_events_provider_client)
):
    event_repo = EventRepository(db)
    event = event_repo.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    usecase = GetSeatsUsecase(client, event_repo)

    try:
        seats = await usecase.do(event_id)
        return {"event_id": event_id, "available_seats": seats}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
