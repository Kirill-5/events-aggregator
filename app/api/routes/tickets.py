from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import EVENTS_PROVIDER_API_KEY, EVENTS_PROVIDER_URL
from app.db.database import get_db
from app.repositories.event_repository import EventRepository
from app.repositories.ticket_repository import TicketRepository
from app.schemas.ticket import TicketCreate, TicketResponse
from app.services.events_provider_client import EventsProviderClient
from app.usecases.create_ticket import CreateTicketUsecase

router = APIRouter(tags=["tickets"])

@router.post("/api/tickets", status_code=status.HTTP_201_CREATED)
async def create_ticket(
    ticket: TicketCreate,
    db: Session = Depends(get_db)
):
    try:
        UUID(ticket.event_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid event_id format")

    client = EventsProviderClient(
        base_url=EVENTS_PROVIDER_URL,
        api_key=EVENTS_PROVIDER_API_KEY
    )
    event_repo = EventRepository(db)
    ticket_repo = TicketRepository(db)

    #UseCase
    usecase = CreateTicketUsecase(client, event_repo, ticket_repo)

    try:
        ticket_id = await usecase.do(
            event_id=ticket.event_id,
            first_name=ticket.first_name,
            last_name=ticket.last_name,
            email=ticket.email,
            seat=ticket.seat
        )
        return {"ticket_id": ticket_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: str,
    db: Session = Depends(get_db)
):
    ticket_repo = TicketRepository(db)
    ticket = ticket_repo.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    client = EventsProviderClient(
        base_url=EVENTS_PROVIDER_URL,
        api_key=EVENTS_PROVIDER_API_KEY
    )
    await client.cancel(ticket.event_id, ticket_id)
    ticket_repo.delete(ticket_id)
    return {"success": True}
