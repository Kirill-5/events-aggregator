from app.db.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.models.place import Place
import uuid

class Event(Base):
    __tablename__ = "event"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    place_id = Column(UUID(as_uuid=True), ForeignKey("place.id"))
    event_time = Column(DateTime)
    registration_deadline = Column(DateTime, nullable=True)
    status = Column(String)
    number_of_visitors = Column(Integer)