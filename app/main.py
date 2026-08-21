import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import (
    events_router,
    health_router,
    metrics_router,
    sync_router,
    tickets_router,
)
from app.core.metrics_middleware import MetricsMiddleware
from app.core.scheduler import start_scheduler
from app.core.outbox_worker import outbox_worker
from app.services.capashino_client import CapashinoClient
from app.core.config import CAPASHINO_URL, CAPASHINO_API_KEY
from app.db.database import engine
from app.models.outbox import Outbox


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()

    capashino_client = CapashinoClient(CAPASHINO_URL, CAPASHINO_API_KEY)

    async with engine.begin() as conn:
        await conn.run_sync(Outbox.metadata.create_all)

    worker_task = asyncio.create_task(outbox_worker(capashino_client))

    yield

    worker_task.cancel()
    await worker_task


app = FastAPI(lifespan=lifespan)

app.add_middleware(MetricsMiddleware)

app.include_router(health_router)
app.include_router(events_router)
app.include_router(tickets_router)
app.include_router(sync_router)
app.include_router(metrics_router)
