from typing import Dict, Any

from app.repositories.event_repository import EventRepository
from app.repositories.place_repository import PlaceRepository


class GetEventDetailUsecase:
    def __init__(self, event_repo: EventRepository, place_repo: PlaceRepository):
        self.event_repo = event_repo
        self.place_repo = place_repo

    async def do(self, event_id: str) -> Dict[str, Any]:
        event = await self.event_repo.get(event_id)
        if not event:
            raise ValueError("Event not found")

        place = await self.place_repo.get(event.place_id)

        return {
            "id": event.id,
            "name": event.name,
            "place": {
                "id": place.id,
                "name": place.name,
                "city": place.city,
                "address": place.address,
                "seats_pattern": place.seats_pattern,
            }
            if place
            else None,
            "event_time": event.event_time,
            "registration_deadline": event.registration_deadline,
            "status": event.status,
            "number_of_visitors": event.number_of_visitors,
        }
