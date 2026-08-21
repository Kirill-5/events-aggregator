from uuid import UUID

from app.models.outbox_status import OutboxStatus
from app.repositories.outbox_repository import OutboxRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.events_provider_client import EventsProviderClient


class CancelTicketUsecase:
    def __init__(
        self,
        client: EventsProviderClient,
        ticket_repo: TicketRepository,
        outbox_repo: OutboxRepository,
    ):
        self.client = client
        self.ticket_repo = ticket_repo
        self.outbox_repo = outbox_repo

    async def do(self, ticket_id: UUID) -> None:
        ticket = await self.ticket_repo.get(str(ticket_id))
        if not ticket:
            raise ValueError("Ticket not found")

        event_id = ticket.event_id

        await self.client.cancel(event_id, str(ticket_id))
        await self.ticket_repo.delete(str(ticket_id))
        await self.outbox_repo.create(
            event_type="ticket_cancelled",
            payload={"ticket_id": str(ticket_id), "event_id": str(event_id)},
            status=OutboxStatus.SENT,
        )
