from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.models.idempotency_key import IdempotencyKey


class IdempotencyKeyRepository:
    def __init__(self, session: Session):
        self.session = session



def get_by_key(self, key: str) -> Optional[IdempotencyKey]:
    return self.session.query(IdempotencyKey).filter(IdempotencyKey.key == key).first()

def save(self, key: str, ticket_id: UUID, event_id: UUID, seat: str) -> IdempotencyKey:
    new_key = IdempotencyKey(
        key=key,
        ticket_id=ticket_id,
        event_id=event_id,
        seat=seat

    )
    self.session.add(new_key)
    self.session.commit()
    self.session.refresh(new_key)
    return new_key
