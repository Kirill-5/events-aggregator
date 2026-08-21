from pydantic import BaseModel
from typing import Optional


class TicketCreate(BaseModel):
    event_id: str
    first_name: str
    last_name: str
    email: str
    seat: str
    idempotency_key: Optional[str] = None


class TicketResponse(BaseModel):
    ticket_id: str
