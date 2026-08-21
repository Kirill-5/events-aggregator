from typing import Optional

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.place import Place


class PlaceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, place_id: int) -> Optional[Place]:
        query = select(Place).filter(Place.id == place_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def upsert(self, place_data: dict) -> Place:
        stmt = pg_insert(Place).values(
            id=place_data["id"],
            name=place_data["name"],
            city=place_data["city"],
            address=place_data["address"],
            seats_pattern=place_data["seats_pattern"],
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={
                "name": stmt.excluded.name,
                "city": stmt.excluded.city,
                "address": stmt.excluded.address,
                "seats_pattern": stmt.excluded.seats_pattern,
            },
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get(place_data["id"])
