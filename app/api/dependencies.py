from app.services.events_provider_client import EventsProviderClient
from app.core.config import EVENTS_PROVIDER_URL, EVENTS_PROVIDER_API_KEY

async def get_events_provider_client() -> EventsProviderClient:
    return EventsProviderClient(
        base_url=EVENTS_PROVIDER_URL,
        api_key=EVENTS_PROVIDER_API_KEY
    )