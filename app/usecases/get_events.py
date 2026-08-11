from typing import List, Optional, Dict, Any

from app.repositories.event_repository import EventRepository
from app.repositories.place_repository import PlaceRepository



class GetEventsUsecase:
    def __init__(self, event_repo: EventRepository, place_repo: PlaceRepository):
        self.event_repo = event_repo
        self.place_repo = place_repo

    async def do(
        self,
        date_from: Optional[str] = None,
        page: int = 1,
        page_size: int = 20,
        base_url: str = "/api/events"
    ) -> Dict[str, Any]:
        skip = (page - 1) * page_size


        events = self.event_repo.list(date_from, skip, page_size)
        total_count = self.event_repo.count(date_from)


        next_page = page + 1 if skip + page_size < total_count else None
        previous_page = page - 1 if page > 1 else None

        next_url = f"{base_url}?page={next_page}&page_size={page_size}" if next_page else None
        previous_url = f"{base_url}?page={previous_page}&page_size={page_size}" if previous_page else None


        results = []
        for event in events:
            place = self.place_repo.get(event.place_id)
            results.append({
                "id": event.id,
                "name": event.name,
                "place": {
                    "id": place.id,
                    "name": place.name,
                    "city": place.city,
                    "address": place.address,
                    "seats_pattern": place.seats_pattern,
                } if place else None,
                "event_time": event.event_time,
                "registration_deadline": event.registration_deadline,
                "status": event.status,
                "number_of_visitors": event.number_of_visitors,
            })

        return {
            "count": total_count,
            "next": next_url,
            "previous": previous_url,
            "results": results,
        }