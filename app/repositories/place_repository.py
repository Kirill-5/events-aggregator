from typing import Optional

from sqlalchemy import select
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
        query = select(Place).filter(Place.id == place_data['id'])
        result = await self.session.execute(query)
        place = result.scalars().first()

        if place:
            place.name = place_data.get('name', place.name)
            place.city = place_data.get('city', place.city)
            place.address = place_data.get('address', place.address)
            place.seats_pattern = place_data.get('seats_pattern', place.seats_pattern)
        else:
            place = Place(
                id=place_data['id'],
                name=place_data['name'],
                city=place_data['city'],
                address=place_data['address'],
                seats_pattern=place_data['seats_pattern']
            )
            self.session.add(place)

        await self.session.commit()
        return place