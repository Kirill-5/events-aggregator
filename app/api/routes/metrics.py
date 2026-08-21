from fastapi import APIRouter, Depends, Response
from prometheus_client import REGISTRY, generate_latest

from app.api.dependencies import get_event_repository, get_outbox_repository
from app.core.metrics import events_total, tickets_cancelled_total, tickets_created_total
from app.repositories.event_repository import EventRepository
from app.repositories.outbox_repository import OutboxRepository

router = APIRouter()


@router.get("/metrics")
async def metrics(
    event_repo: EventRepository = Depends(get_event_repository),
    outbox_repo: OutboxRepository = Depends(get_outbox_repository),
):
    events_count = await event_repo.count()
    created_count = await outbox_repo.count_by_event_type("ticket_purchased")
    cancelled_count = await outbox_repo.count_by_event_type("ticket_cancelled")

    events_total.set(events_count)
    tickets_created_total.set(created_count)
    tickets_cancelled_total.set(cancelled_count)

    return Response(
        content=generate_latest(REGISTRY),
        media_type="text/plain",
    )