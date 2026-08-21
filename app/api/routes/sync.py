import logging
import traceback
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.events_provider_client import EventsProviderClient
from app.repositories.event_repository import EventRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.sync_metadata_repository import SyncMetadataRepository
from app.usecases.sync_events_usecase import SyncEventsUsecase
from app.core.config import EVENTS_PROVIDER_URL, EVENTS_PROVIDER_API_KEY

router = APIRouter(tags=["sync"])


@router.post("/api/sync/trigger")
async def trigger_sync(db: AsyncSession = Depends(get_db)):
    try:
        client = EventsProviderClient(
            base_url=EVENTS_PROVIDER_URL, api_key=EVENTS_PROVIDER_API_KEY
        )

        event_repo = EventRepository(db)
        place_repo = PlaceRepository(db)
        sync_metadata_repo = SyncMetadataRepository(db)

        usecase = SyncEventsUsecase(client, event_repo, place_repo)

        metadata = await sync_metadata_repo.get_metadata()
        changed_at = (metadata.last_changed_at or "2000-01-01").split("T")[0]

        count = await usecase.do(changed_at=changed_at)

        now = datetime.now().isoformat()
        await sync_metadata_repo.update_metadata(
            last_sync_time=datetime.now(), last_changed_at=now, sync_status="success"
        )

        return {"status": "success", "synced": count}
    except Exception as e:
        logging.error("Sync trigger error: %s", e)
        logging.error("Traceback: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
