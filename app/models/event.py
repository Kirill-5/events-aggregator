import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.models.event_status import EventStatus


class Event(Base):
    __tablename__ = "event"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    place_id = Column(UUID(as_uuid=True), ForeignKey("place.id"))
    event_time = Column(DateTime)
    registration_deadline = Column(DateTime, nullable=True)
    status = Column(SQLEnum(EventStatus), default=EventStatus.DRAFT)
    number_of_visitors = Column(Integer)

    place = relationship("Place")