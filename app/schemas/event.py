from pydantic import BaseModel
from typing import Optional, List

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
    status: str
    number_of_visitors: int

class EventDetailResponse(BaseModel):
    id: str
    name: str
    place: PlaceSchema
    event_time: str
    registration_deadline: Optional[str] = None
    status: str
    number_of_visitors: int

class SeatsResponse(BaseModel):
    event_id: str
    available_seats: List[str]