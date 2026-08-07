import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import events_router, health_router, sync_router, tickets_router
from app.core.scheduler import start_scheduler
from app.core.outbox_worker import outbox_worker
from app.services.capashino_client import CapashinoClient
from app.repositories.outbox_repository import OutboxRepository
from app.core.config import CAPASHINO_URL, CAPASHINO_API_KEY


from app.db.database import SessionLocal, engine
from app.models.outbox import Outbox


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()

    capashino_client = CapashinoClient(CAPASHINO_URL, CAPASHINO_API_KEY)
    outbox_repo = OutboxRepository(SessionLocal())


    Outbox.metadata.create_all(engine)

    worker_task = asyncio.create_task(outbox_worker(capashino_client, outbox_repo))

    yield

    worker_task.cancel()
    await worker_task


app = FastAPI(lifespan=lifespan)

app.include_router(health_router)
app.include_router(events_router)
app.include_router(tickets_router)
app.include_router(sync_router)