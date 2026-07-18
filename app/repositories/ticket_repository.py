from sqlalchemy.orm import Session
from app.models.registration import Registration
from typing import Optional


class TicketRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, ticket_id: str) -> Optional[Registration]:
        return self.session.query(Registration).filter(Registration.ticket_id == ticket_id).first()

    def create(self, event_id: str, ticket_id: str, first_name: str, last_name: str, email: str, seat:str) -> Registration:
        registration = Registration(
            event_id = event_id,
            ticket_id = ticket_id,
            first_name = first_name,
            last_name = last_name,
            email = email,
            seat = seat
        )
        self.session.add(registration)
        self.session.commit()
        self.session.refresh(registration)
        return registration

    def delete(self, ticket_id: str) -> None:
        ticket_registration = self.session.query(Registration).filter(Registration.ticket_id == ticket_id).first()
        if ticket_registration:
            self.session.delete(ticket_registration)
            self.session.commit()
        else:
            pass