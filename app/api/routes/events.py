from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import time
from app.db.database import get_db
from app.repositories.event_repository import EventRepository
from app.repositories.place_repository import PlaceRepository
from app.services.events_provider_client import EventsProviderClient
from app.models.event import Event

router = APIRouter(tags=["events"])
seats_cache = {}


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
    total_count = db.query(Event).count()


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
async def get_event(event_id: str, db: Session = Depends(get_db)):
    event = EventRepository(db).get(event_id)
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
async def get_seats(event_id: str, db: Session = Depends(get_db)):
    event = EventRepository(db).get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event_id in seats_cache:
        cached_data, cache_time = seats_cache[event_id]
        if time.time() - cache_time < 30:
            return {
                "event_id": event_id,
                "available_seats": cached_data
            }

    client = EventsProviderClient(
        base_url="http://student-system-events-provider-web.student-system-events-provider.svc:8000",
        api_key="d0kdUsSLnnWUTC2v1lzkTQHhtfJSouF1uXuXscvIDoE"
    )
    seats_data = await client.seats(event.id)
    available_seats = seats_data.get("available_seats", [])
    seats_cache[event_id] = (available_seats, time.time())

    return {
        "event_id": event.id,
        "available_seats": available_seats
    }