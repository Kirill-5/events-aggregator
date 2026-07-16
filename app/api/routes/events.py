from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app import db
from app.db.database import get_db
from app.repositories.event_repository import EventRepository
from app.repositories.place_repository import PlaceRepository
from app.models.event import Event


seats_cache = {}

router = APIRouter(prefix="/api/events", tags=["events"])

@router.get("/")
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

    return {
        "count": total_count,
        "page": page,
        "page_size": page_size,
        "results": events
    }


@router.get("/{event_id}")
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


@router.get("/{event_id}/seats")
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
            base_url="http://student-system-events-provider-web.student-system-events-provider.svc:8000")
    seats_data = await client.seats(event.id)
    available_seats = seats_data.get("available_seats", [])
    seats_cache[event_id] = (available_seats, time.time())

    return {
        "event_id": event.id,
        "available_seats": available_seats
    }