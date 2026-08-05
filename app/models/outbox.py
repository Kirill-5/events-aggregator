import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, JSON, Index
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base

class Outbox(Base):
    __tablename__ = "outbox"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
    attempts = Column(Integer, default=0)

    __table_args__ = (
        Index("idx_outbox_status_created", "status", "created_at"),
    )