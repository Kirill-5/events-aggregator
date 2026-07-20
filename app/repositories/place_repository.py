from sqlalchemy.orm import Session
from app.models.place import Place
from typing import Optional

class PlaceRepository:
    def __init__(self, session: Session):
        self.session = session


    def get(self, place_id: int) -> Optional[Place]:
        return self.session.query(Place).filter(Place.id == place_id).first()

    def upsert(self, place_data: dict) -> Place:
        place = self.session.query(Place).filter(Place.id == place_data['id']).first()

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

        self.session.commit()
        return place
