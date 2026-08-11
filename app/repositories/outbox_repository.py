from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.models.outbox import Outbox
from app.models.outbox_status import OutboxStatus


class OutboxRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, event_type: str, payload: dict) -> Outbox:
        new_message = Outbox(
            event_type=event_type,
            payload=payload,
            status=OutboxStatus.PENDING,
            attempts=0
        )
        self.session.add(new_message)
        self.session.commit()
        self.session.refresh(new_message)
        return new_message

    def get_pending(self, limit: int = 10) -> List[Outbox]:
        pending_messages = self.session.query(Outbox).filter(Outbox.status == OutboxStatus.PENDING)
        return pending_messages.order_by(Outbox.created_at.asc()).limit(limit).all()

    def mark_as_sent(self, outbox_id: UUID) -> None:
        message = self.session.query(Outbox).filter(Outbox.id == outbox_id).first()
        if message:
            message.status = OutboxStatus.SENT
            self.session.commit()

    def increment_attempts(self, outbox_id: UUID) -> None:
        message = self.session.query(Outbox).filter(Outbox.id == outbox_id).first()
        if message:
            message.attempts += 1
            self.session.commit()

    def mark_as_failed(self, outbox_id: UUID) -> None:
        message = self.session.query(Outbox).filter(Outbox.id == outbox_id).first()
        if message:
            message.status = OutboxStatus.FAILED
            self.session.commit()