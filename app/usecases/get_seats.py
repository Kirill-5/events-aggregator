import time
from typing import List, Dict

from app.repositories.event_repository import EventRepository
from app.services.events_provider_client import EventsProviderClient


class GetSeatsUsecase:
    def __init__(self, client: EventsProviderClient, event_repo: EventRepository):
        self.client = client
        self.event_repo = event_repo
        self._cache: Dict[str, tuple] = {}

    async def do(self, event_id: str) -> List[str]:
        event = self.event_repo.get(event_id)
        if not event:
            raise ValueError("Event not found")

        if event_id in self._cache:
            cached_data, cache_time = self._cache[event_id]
            if time.time() - cache_time < 30:
                return cached_data

        data = await self.client.seats(event.id)
        seats = data.get("seats", [])

        self._cache[event_id] = (seats, time.time())

        return seats