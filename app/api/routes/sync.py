from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import db
from app.db.database import get_db
from app.services.events_provider_client import EventsProviderClient
from app.repositories.event_repository import EventRepository
from app.repositories.place_repository import PlaceRepository
from app.usecases.SyncEventsUsecase import SyncEventsUsecase

router = APIRouter(tags=["sync"])

@router.post("/api/sync/trigger")
async def trigger_sync(db: Session = Depends(get_db)):
    try:
        client = EventsProviderClient(
            base_url="http://student-system-events-provider-web.student-system-events-provider.svc:8000",
            api_key="d0kdUsSLnnWUTC2v1lzkTQHhtfJSouF1uXuXscvIDoE"
        )
        event_repo = EventRepository(db)
        place_repo = PlaceRepository(db)
        usecase = SyncEventsUsecase(client, event_repo, place_repo)

        count = await usecase.do()
        return {"status": "success", "synced": count}
    except Exception as e:
        return {"status": "error", "detail": str(e)}