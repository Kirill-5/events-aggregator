from typing import Optional, List, Dict, Any
from app.services.events_provider_client import EventsProviderClient
from app.repositories.event_repository import EventRepository
from app.repositories.place_repository import PlaceRepository

class SyncEventsUsecase:
    def __init__(self, client : EventsProviderClient, event_repo : EventRepository, place_repo : PlaceRepository):
        self.client = client
        self.event_repo = event_repo
        self.place_repo = place_repo


    async def do(self, changed_at : str = "2000-01-01") -> int:
        cursor = None
        count = 0
        while True:
            data = await self.client.events(cursor=cursor, changed_at=changed_at)
            for event_data in data["results"]:
                place = await self.place_repo.upsert(event_data["place"])

                await self.event_repo.upsert({
                    "id": event_data["id"],
                    "name": event_data["name"],
                    "place_id": place.id,
                    "event_time": event_data["event_time"],
                    "registration_deadline": event_data["registration_deadline"],
                    "status": event_data["status"],
                    "number_of_visitors": event_data.get("number_of_visitors", 0)

                })
                count += 1
            next_cursor = data.get("next")
            if not next_cursor:
                break
            cursor = next_cursor
        return count

