from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_events_provider_client
from app.db.database import get_db
from app.repositories.event_repository import EventRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate
from app.services.events_provider_client import EventsProviderClient
from app.usecases.create_ticket import CreateTicketUsecase
from app.repositories.idempotency_key_repository import IdempotencyKeyRepository
from app.repositories.outbox_repository import OutboxRepository

router = APIRouter(tags=["tickets"])


@router.post("/api/tickets", status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db),
    client: EventsProviderClient = Depends(get_events_provider_client)
):
    try:
        UUID(ticket.event_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid event_id format")


    if ticket.idempotency_key:
        idempotency_repo = IdempotencyKeyRepository(db)
        existing = idempotency_repo.get_by_key(ticket.idempotency_key)
        if existing:

            if (str(existing.event_id) == ticket.event_id and
                existing.seat == ticket.seat):

                return {"ticket_id": str(existing.ticket_id)}
            else:

                raise HTTPException(
                    status_code=409,
                    detail="Idempotency key already used with different data"
                )

    event_repo = EventRepository(db)
    ticket_repo = TicketRepository(db)

    event = event_repo.get(ticket.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    usecase = CreateTicketUsecase(client, event_repo, ticket_repo)

    try:
        ticket_id = await usecase.do(
            event_id=ticket.event_id,
            first_name=ticket.first_name,
            last_name=ticket.last_name,
            email=ticket.email,
            seat=ticket.seat
        )

        #
        if ticket.idempotency_key:
            idempotency_repo = IdempotencyKeyRepository(db)
            idempotency_repo.save(
                key=ticket.idempotency_key,
                ticket_id=ticket_id,
                event_id=ticket.event_id,
                seat=ticket.seat
            )

        outbox_repo = OutboxRepository(db)
        outbox_repo.create(
            event_type="ticket_purchased",
            payload={
                "ticket_id": str(ticket_id),
                "event_name": event.name,
                "user_email": ticket.email,
                "seat": ticket.seat,
                "message": f"Ticket {ticket_id} purchased for event {event.name}",
                "idempotency_key": ticket.idempotency_key or f"ticket_{ticket_id}"
            }
        )

        return {"ticket_id": ticket_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: str,
    db: Session = Depends(get_db),
    client: EventsProviderClient = Depends(get_events_provider_client)
):
    ticket_repo = TicketRepository(db)
    ticket = ticket_repo.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    await client.cancel(ticket.event_id, ticket_id)
    ticket_repo.delete(ticket_id)
    return {"success": True}
