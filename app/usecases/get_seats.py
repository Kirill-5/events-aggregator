from typing import List

from app.core.metrics import cache_hits_total, cache_misses_total
from app.repositories.event_repository import EventRepository
from app.services import seats_cache
from app.services.events_provider_client import EventsProviderClient


class GetSeatsUsecase:
    def __init__(self, client: EventsProviderClient, event_repo: EventRepository):
        self.client = client
        self.event_repo = event_repo

    async def do(self, event_id: str) -> List[str]:
        event = await self.event_repo.get(event_id)
        if not event:
            raise ValueError("Event not found")

        cached = seats_cache.get(event_id)
        if cached is not None:
            cache_hits_total.inc()
            return cached

        cache_misses_total.inc()

        data = await self.client.seats(event.id)
        seats = data.get("seats", [])

        seats_cache.set(event_id, seats)

        return seats