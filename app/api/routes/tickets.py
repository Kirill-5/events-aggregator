from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.repositories.event_repository import EventRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.events_provider_client import EventsProviderClient
from app.schemas.ticket import TicketCreate, TicketResponse



router = APIRouter(prefix="/api/events", tags=["events"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_ticket(
        ticket: TicketCreate,
        db: Session = Depends(get_db)
):
    event = EventRepository(db).get(ticket.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    if event.status != "published":
        raise HTTPException(status_code=400, detail="Event is not published")

    client = EventsProviderClient(
        base_url="http://student-system-events-provider-web.student-system-events-provider.svc:8000")
    client_reg = await client.register(
        event_id=ticket.event_id,
        first_name=ticket.first_name,
        last_name=ticket.last_name,
        email=ticket.email,
        seat=ticket.seat

    )

    ticket_id = client_reg.get("ticket_id")
    if not ticket_id:
        raise HTTPException(status_code=500, detail="Ticket not found")

    ticket_repo = TicketRepository(db)
    registration = ticket_repo.create(
        event_id=ticket.event_id,
        first_name=ticket.first_name,
        last_name=ticket.last_name,
        email=ticket.email,
        seat=ticket.seat
    )

    return {"ticket_id": ticket_id}


@router.delete("/{ticket_id}")
async def delete_ticket(
        ticket_id: str,
        db: Session = Depends(get_db)
):
    ticket_repo = TicketRepository(db)
    ticket = ticket_repo.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    client = EventsProviderClient(
        base_url="http://student-system-events-provider-web.student-system-events-provider.svc:8000")
    ticket_cancel = await client.cancel(ticket_id)
    ticket_repo.delete(ticket_id)
    return {"success": True}
