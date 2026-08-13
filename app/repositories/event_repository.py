from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.event import Event


class EventRepository:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count(self, date_from: Optional[str] = None) -> int:
        query = select(func.count()).select_from(Event)
        if date_from:
            query = query.where(Event.event_time >= date_from)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get(self, event_id: str) -> Optional[Event]:
        query = select(Event).filter(Event.id == event_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list(self, date_from: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[Event]:
        query = select(Event).options(joinedload(Event.place))
        if date_from:
            query = query.where(Event.event_time >= date_from)
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def upsert(self, event_data: dict) -> Event:
        query = select(Event).filter(Event.id == event_data['id'])
        result = await self.session.execute(query)
        event = result.scalars().first()

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

        await self.session.commit()
        return event