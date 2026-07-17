from sqlalchemy.orm import Session
from app.models.event import Event
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import joinedload

class EventRepository:

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, event_id: str) -> Optional[Event]:
        return self.session.query(Event).filter(Event.id == event_id).first()

    def list(self, date_from: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[Event]:
        query = self.session.query(Event).options(joinedload(Event.place))
        if date_from:
            query = query.filter(Event.event_time >= date_from)
        query = query.offset(skip).limit(limit)
        return query.all()


    def upsert(self, event_data: dict) -> Event:
        event = self.session.query(Event).filter(Event.id == event_data['id']).first()

        if event:
            event.name = event_data.get('name', event.name)
            event.place_id = event_data.get('place_id', event.place_id)
            event.event_time = event_data.get('event_time', event.event_time)
            event.registration_deadline = event_data.get('registration_deadline', event.registration_deadline)
            event.status = event_data.get('status', event.status)
            event.number_of_visitors = event_data.get('number_of_visitors', event.number_of_visitors)

        else:
            event = Event(
                id=event_data['id'],
                name=event_data['name'],
                place_id=event_data['place_id'],
                event_time=event_data['event_time'],
                registration_deadline=event_data['registration_deadline'],
                status=event_data['status'],
                number_of_visitors=event_data['number_of_visitors'],
                )
            self.session.add(event)

        self.session.commit()
        return event