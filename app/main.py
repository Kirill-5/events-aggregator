from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.scheduler import start_scheduler
from app.api.routes import health, events, tickets, sync

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(health.router)
app.include_router(events.router)
app.include_router(tickets.router)
app.include_router(sync.router)