from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_events_provider_client, get_cancel_ticket_usecase
from app.db.database import get_db
from app.repositories.event_repository import EventRepository
from app.repositories.ticket_repository import TicketRepository
from app.repositories.idempotency_key_repository import IdempotencyKeyRepository
from app.repositories.outbox_repository import OutboxRepository
from app.schemas.ticket import TicketCreate
from app.services.events_provider_client import EventsProviderClient
from app.usecases.create_ticket import CreateTicketUsecase, ConflictError
from app.usecases.cancel_ticket import CancelTicketUsecase


router = APIRouter(tags=["tickets"])


@router.post("/api/tickets", status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket: TicketCreate,
    db: AsyncSession = Depends(get_db),
    client: EventsProviderClient = Depends(get_events_provider_client),
):
    try:
        UUID(ticket.event_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid event_id format")

    event_repo = EventRepository(db)
    ticket_repo = TicketRepository(db)
    idempotency_repo = IdempotencyKeyRepository(db)
    outbox_repo = OutboxRepository(db)

    usecase = CreateTicketUsecase(
        client=client,
        event_repo=event_repo,
        ticket_repo=ticket_repo,
        idempotency_repo=idempotency_repo,
        outbox_repo=outbox_repo,
    )

    try:
        ticket_id = await usecase.do(
            event_id=ticket.event_id,
            first_name=ticket.first_name,
            last_name=ticket.last_name,
            email=ticket.email,
            seat=ticket.seat,
            idempotency_key=ticket.idempotency_key,
        )
        return {"ticket_id": ticket_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/tickets/{ticket_id}", status_code=status.HTTP_200_OK)
async def cancel_ticket(
    ticket_id: UUID,
    usecase: CancelTicketUsecase = Depends(get_cancel_ticket_usecase),
):
    try:
        await usecase.do(ticket_id)
        return {"success": True}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
