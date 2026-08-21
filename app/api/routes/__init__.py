from app.api.routes.events import router as events_router
from app.api.routes.health import router as health_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.sync import router as sync_router
from app.api.routes.tickets import router as tickets_router

__all__ = [
    "events_router",
    "health_router",
    "metrics_router",
    "sync_router",
    "tickets_router",
]
