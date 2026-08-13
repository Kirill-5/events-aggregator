from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import Outbox
from app.models.outbox_status import OutboxStatus


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, event_type: str, payload: dict) -> Outbox:
        new_message = Outbox(
            event_type=event_type,
            payload=payload,
            status=OutboxStatus.PENDING,
            attempts=0
        )
        self.session.add(new_message)
        await self.session.commit()
        await self.session.refresh(new_message)
        return new_message

    async def get_pending(self, limit: int = 10) -> List[Outbox]:
        query = select(Outbox).filter(Outbox.status == OutboxStatus.PENDING)
        query = query.order_by(Outbox.created_at.asc()).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def mark_as_sent(self, outbox_id: UUID) -> None:
        query = select(Outbox).filter(Outbox.id == outbox_id)
        result = await self.session.execute(query)
        message = result.scalars().first()
        if message:
            message.status = OutboxStatus.SENT
            await self.session.commit()

    async def increment_attempts(self, outbox_id: UUID) -> None:
        query = select(Outbox).filter(Outbox.id == outbox_id)
        result = await self.session.execute(query)
        message = result.scalars().first()
        if message:
            message.attempts += 1
            await self.session.commit()

    async def mark_as_failed(self, outbox_id: UUID) -> None:
        query = select(Outbox).filter(Outbox.id == outbox_id)
        result = await self.session.execute(query)
        message = result.scalars().first()
        if message:
            message.status = OutboxStatus.FAILED
            await self.session.commit()