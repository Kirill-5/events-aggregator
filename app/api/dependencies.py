from functools import lru_cache

from fastapi import Depends

from app.services.events_provider_client import EventsProviderClient
from app.core.config import EVENTS_PROVIDER_URL, EVENTS_PROVIDER_API_KEY
from app.repositories.ticket_repository import TicketRepository
from app.repositories.event_repository import EventRepository
from app.usecases.cancel_ticket import CancelTicketUsecase
from app.usecases.get_seats import GetSeatsUsecase
from app.db.database import SessionLocal


async def get_events_provider_client() -> EventsProviderClient:
    return EventsProviderClient(
        base_url=EVENTS_PROVIDER_URL,
        api_key=EVENTS_PROVIDER_API_KEY
    )


def get_cancel_ticket_usecase(
    client: EventsProviderClient = Depends(get_events_provider_client),
) -> CancelTicketUsecase:
    db = SessionLocal()
    ticket_repo = TicketRepository(db)
    return CancelTicketUsecase(client, ticket_repo)


@lru_cache(maxsize=1)
def get_seats_usecase(
    client: EventsProviderClient = Depends(get_events_provider_client),
) -> GetSeatsUsecase:
    db = SessionLocal()
    event_repo = EventRepository(db)
    return GetSeatsUsecase(client, event_repo)