from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.event import Event


class EventRepository:

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def count(self, date_from: Optional[str] = None) -> int:
        query = select(func.count()).select_from(Event)
        if date_from:
            query = query.where(Event.event_time >= datetime.fromisoformat(date_from))
        result = await self.session.execute(query)
        return result.scalar_one()

    async def get(self, event_id: str) -> Optional[Event]:
        query = select(Event).filter(Event.id == event_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def list(self, date_from: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[Event]:
        query = select(Event).options(joinedload(Event.place))
        if date_from:
            query = query.where(Event.event_time >= datetime.fromisoformat(date_from))
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def upsert(self, event_data: dict) -> Event:
        event_time = self._parse_datetime(event_data.get('event_time'))
        registration_deadline = self._parse_datetime(event_data.get('registration_deadline'))

        stmt = pg_insert(Event).values(
            id=event_data['id'],
            name=event_data['name'],
            place_id=event_data['place_id'],
            event_time=event_time,
            registration_deadline=registration_deadline,
            status=event_data['status'],
            number_of_visitors=event_data.get('number_of_visitors', 0),
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=['id'],
            set_={
                'name': stmt.excluded.name,
                'place_id': stmt.excluded.place_id,
                'event_time': stmt.excluded.event_time,
                'registration_deadline': stmt.excluded.registration_deadline,
                'status': stmt.excluded.status,
                'number_of_visitors': stmt.excluded.number_of_visitors,
            }
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get(event_data['id'])

    @staticmethod
    def _parse_datetime(value):
        if value is None:
            return None
        if isinstance(value, str):
            value = datetime.fromisoformat(value)
        if value.tzinfo is not None:
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value