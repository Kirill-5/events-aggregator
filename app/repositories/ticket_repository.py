from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.registration import Registration


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, ticket_id: str) -> Optional[Registration]:
        query = select(Registration).filter(Registration.ticket_id == ticket_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def create(self, event_id: str, ticket_id: str, first_name: str, last_name: str, email: str, seat: str) -> Registration:
        registration = Registration(
            event_id=event_id,
            ticket_id=ticket_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            seat=seat
        )
        self.session.add(registration)
        await self.session.commit()
        await self.session.refresh(registration)
        return registration

    async def delete(self, ticket_id: str) -> None:
        query = select(Registration).filter(Registration.ticket_id == ticket_id)
        result = await self.session.execute(query)
        ticket_registration = result.scalars().first()
        if ticket_registration:
            await self.session.delete(ticket_registration)
            await self.session.commit()