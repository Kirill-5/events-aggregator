from pydantic import BaseModel
from typing import Optional, List

from app.models.event_status import EventStatus


class PlaceSchema(BaseModel):
    id: str
    name: str
    city: str
    address: Optional[str] = None
    seats_pattern: Optional[str] = None


class EventResponse(BaseModel):
    id: str
    name: str
    place: PlaceSchema
    event_time: str
    registration_deadline: Optional[str] = None
    status: EventStatus
    number_of_visitors: int


class EventDetailResponse(BaseModel):
    id: str
    name: str
    place: PlaceSchema
    event_time: str
    registration_deadline: Optional[str] = None
    status: EventStatus
    number_of_visitors: int


class SeatsResponse(BaseModel):
    event_id: str
    available_seats: List[str]
