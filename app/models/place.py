from app.db.database import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String
import uuid

class Place(Base):
    __tablename__ = "place"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    city = Column(String)
    address = Column(String , nullable=True)
    seats_pattern  = Column(String, nullable=True)