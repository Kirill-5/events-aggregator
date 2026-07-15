from app.db.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.models.event import Event
import uuid

class Registration(Base):
    __tablename__ = "registration"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey('event.id'), nullable=False)
    ticket_id = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    seat = Column(String)
