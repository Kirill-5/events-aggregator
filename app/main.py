from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.scheduler import start_scheduler
from app.api.routes import health_router, events_router, tickets_router, sync_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(health_router)
app.include_router(events_router)
app.include_router(tickets_router)
app.include_router(sync_router)