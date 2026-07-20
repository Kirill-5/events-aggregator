from app.models.event_status import EventStatus
from app.repositories.event_repository import EventRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.events_provider_client import EventsProviderClient


class CreateTicketUsecase:
    def __init__(
        self,
        client: EventsProviderClient,
        event_repo: EventRepository,
        ticket_repo: TicketRepository
    ):
        self.client = client
        self.event_repo = event_repo
        self.ticket_repo = ticket_repo

    async def do(self, event_id: str, first_name: str, last_name: str, email: str, seat: str) -> str:
        event = self.event_repo.get(event_id)
        if not event:
            raise ValueError("Event not found")

        if event.status != EventStatus.PUBLISHED:
            raise ValueError("Event is not published")

        result = await self.client.register(event_id, first_name, last_name, email, seat)
        ticket_id = result.get("ticket_id")
        if not ticket_id:
            raise RuntimeError("Failed to get ticket_id from provider")

        self.ticket_repo.create(
            event_id=event_id,
            ticket_id=ticket_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat
        )

        return ticket_id