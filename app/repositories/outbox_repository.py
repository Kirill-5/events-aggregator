from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import Outbox
from app.models.outbox_status import OutboxStatus


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, event_type: str, payload: dict, status: OutboxStatus = OutboxStatus.PENDING) -> Outbox:
        new_message = Outbox(
            event_type=event_type,
            payload=payload,
            status=status,
            attempts=0
        )
        self.session.add(new_message)
        await self.session.commit()
        await self.session.refresh(new_message)
        return new_message

    async def get_pending(self, limit: int = 10) -> List[Outbox]:
        query = select(Outbox).filter(Outbox.status == OutboxStatus.PENDING)
        query = query.order_by(Outbox.created_at.asc()).limit(limit)
        query = query.with_for_update(skip_locked=True)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, outbox_id: UUID) -> Optional[Outbox]:
        query = select(Outbox).filter(Outbox.id == outbox_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def count_by_event_type(self, event_type: str) -> int:
        query = select(func.count()).select_from(Outbox).filter(Outbox.event_type == event_type)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def mark_as_sent(self, outbox_id: UUID) -> None:
        message = await self.get_by_id(outbox_id)
        if message:
            message.status = OutboxStatus.SENT

    async def increment_attempts(self, outbox_id: UUID) -> None:
        message = await self.get_by_id(outbox_id)
        if message:
            message.attempts += 1

    async def mark_as_failed(self, outbox_id: UUID) -> None:
        message = await self.get_by_id(outbox_id)
        if message:
            message.status = OutboxStatus.FAILED