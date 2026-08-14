import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Index
from sqlalchemy.dialects.postgresql import UUID

from app.db.database import Base


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String, unique=True, nullable=False, index=True)
    ticket_id = Column(UUID(as_uuid=True), nullable=False)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    seat = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc).replace(tzinfo=None))

    __table_args__ = (
        Index("idx_idempotency_keys_ticket_id", "ticket_id"),
    )