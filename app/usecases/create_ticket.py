from app.repositories.event_repository import EventRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.idempotency_key_repository import IdempotencyKeyRepository
from app.repositories.outbox_repository import OutboxRepository
from app.services.events_provider_client import EventsProviderClient


class ConflictError(Exception):
    pass


class CreateTicketUsecase:
    def __init__(
        self,
        client: EventsProviderClient,
        event_repo: EventRepository,
        ticket_repo: TicketRepository,
        idempotency_repo: IdempotencyKeyRepository,
        outbox_repo: OutboxRepository
    ):
        self.client = client
        self.event_repo = event_repo
        self.ticket_repo = ticket_repo
        self.idempotency_repo = idempotency_repo
        self.outbox_repo = outbox_repo

    async def do(
        self,
        event_id: str,
        first_name: str,
        last_name: str,
        email: str,
        seat: str,
        idempotency_key: str = None
    ) -> str:
        event = await self.event_repo.get(event_id)
        if not event:
            raise ValueError("Event not found")

        provider_event = await self.client.event_detail(event_id)
        if provider_event.get("status") != "published":
            raise ValueError("Event is not published")

        if idempotency_key:
            existing = await self.idempotency_repo.get_by_key(idempotency_key)
            if existing:
                if (str(existing.event_id) == event_id and
                    existing.seat == seat):
                    return str(existing.ticket_id)
                else:
                    raise ConflictError("Idempotency key already used with different data")

        result = await self.client.register(event_id, first_name, last_name, email, seat)

        if isinstance(result, list):
            raise ValueError(result[0] if result else "Unknown provider error")
        if "detail" in result:
            raise ValueError(result["detail"])

        ticket_id = result.get("ticket_id")
        if not ticket_id:
            raise RuntimeError("Failed to get ticket_id from provider")

        await self.ticket_repo.create(
            event_id=event_id,
            ticket_id=ticket_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat
        )

        if idempotency_key:
            await self.idempotency_repo.save(
                key=idempotency_key,
                ticket_id=ticket_id,
                event_id=event_id,
                seat=seat
            )

        await self.outbox_repo.create(
            event_type="ticket_purchased",
            payload={
                "ticket_id": str(ticket_id),
                "event_name": event.name,
                "user_email": email,
                "seat": seat,
                "message": f"Ticket {ticket_id} purchased for event {event.name}",
                "idempotency_key": idempotency_key or f"ticket_{ticket_id}"
            }
        )

        return ticket_id