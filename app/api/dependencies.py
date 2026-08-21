from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.events_provider_client import EventsProviderClient
from app.core.config import EVENTS_PROVIDER_URL, EVENTS_PROVIDER_API_KEY
from app.repositories.outbox_repository import OutboxRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.event_repository import EventRepository
from app.usecases.cancel_ticket import CancelTicketUsecase
from app.usecases.get_seats import GetSeatsUsecase
from app.db.database import get_db


async def get_events_provider_client() -> EventsProviderClient:
    return EventsProviderClient(
        base_url=EVENTS_PROVIDER_URL,
        api_key=EVENTS_PROVIDER_API_KEY
    )


def get_cancel_ticket_usecase(
    db: AsyncSession = Depends(get_db),
    client: EventsProviderClient = Depends(get_events_provider_client),
) -> CancelTicketUsecase:
    ticket_repo = TicketRepository(db)
    outbox_repo = OutboxRepository(db)
    return CancelTicketUsecase(client, ticket_repo, outbox_repo)


def get_seats_usecase(
    db: AsyncSession = Depends(get_db),
    client: EventsProviderClient = Depends(get_events_provider_client),
) -> GetSeatsUsecase:
    event_repo = EventRepository(db)
    return GetSeatsUsecase(client, event_repo)