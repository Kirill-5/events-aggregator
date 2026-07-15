from sqlalchemy.orm import Session
from app.models.event import Event
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select

class EventRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, event_id: str) -> Optional[Event]:
        return self.session.query(Event).filter(Event.id == event_id).first()


    def list(self, date_from: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[Event]:
        query = self.session.query(Event)
        if date_from:
            query = query.filter(Event.event_time >= date_from)

        query = query.offset(skip).limit(limit)
        return query.all()
