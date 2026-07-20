from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import events_router, health_router, sync_router, tickets_router
from app.core.scheduler import start_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(health_router)
app.include_router(events_router)
app.include_router(tickets_router)
app.include_router(sync_router)