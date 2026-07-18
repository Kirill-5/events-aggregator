from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.repositories.event_repository import EventRepository
from app.repositories.ticket_repository import TicketRepository
from app.services.events_provider_client import EventsProviderClient
from app.schemas.ticket import TicketCreate, TicketResponse

router = APIRouter(tags=["tickets"])

@router.post("/api/tickets")
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
        base_url="http://student-system-events-provider-web.student-system-events-provider.svc:8000",
        api_key="d0kdUsSLnnWUTC2v1lzkTQHhtfJSouF1uXuXscvIDoE"
    )
    client_reg = await client.register(
        event_id=ticket.event_id,
        first_name=ticket.first_name,
        last_name=ticket.last_name,
        email=ticket.email,
        seat=ticket.seat
    )

    ticket_id = client_reg.get("ticket_id")
    if not ticket_id:
        raise HTTPException(status_code=500, detail="Failed to get ticket_id from provider")

    ticket_repo = TicketRepository(db)
    ticket_repo.create(
        event_id=ticket.event_id,
        ticket_id=ticket_id,
        first_name=ticket.first_name,
        last_name=ticket.last_name,
        email=ticket.email,
        seat=ticket.seat
    )

    return {"ticket_id": ticket_id}

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
        base_url="http://student-system-events-provider-web.student-system-events-provider.svc:8000",
        api_key="d0kdUsSLnnWUTC2v1lzkTQHhtfJSouF1uXuXscvIDoE"
    )
    await client.cancel(ticket.event_id, ticket_id)
    ticket_repo.delete(ticket_id)
    return {"success": True}
