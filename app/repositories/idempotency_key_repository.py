from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idempotency_key import IdempotencyKey


class IdempotencyKeyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_key(self, key: str) -> Optional[IdempotencyKey]:
        query = select(IdempotencyKey).filter(IdempotencyKey.key == key)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def save(
        self, key: str, ticket_id: UUID, event_id: UUID, seat: str
    ) -> IdempotencyKey:
        new_key = IdempotencyKey(
            key=key, ticket_id=ticket_id, event_id=event_id, seat=seat
        )
        self.session.add(new_key)
        await self.session.commit()
        await self.session.refresh(new_key)
        return new_key
