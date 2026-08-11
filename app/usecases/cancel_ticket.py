from uuid import UUID

from app.repositories.ticket_repository import TicketRepository
from app.services.events_provider_client import EventsProviderClient


class CancelTicketUsecase:
    def __init__(self, client: EventsProviderClient, ticket_repo: TicketRepository):
        self.client = client
        self.ticket_repo = ticket_repo

    async def do(self, ticket_id: UUID) -> None:
        ticket = self.ticket_repo.get(str(ticket_id))
        if not ticket:
            raise ValueError("Ticket not found")

        await self.client.cancel(ticket.event_id, str(ticket_id))
        self.ticket_repo.delete(str(ticket_id))