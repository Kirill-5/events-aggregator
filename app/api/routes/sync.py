import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.events_provider_client import EventsProviderClient
from app.repositories.event_repository import EventRepository
from app.repositories.place_repository import PlaceRepository
from app.repositories.sync_metadata_repository import SyncMetadataRepository
from app.usecases.SyncEventsUsecase import SyncEventsUsecase
from app.core.config import EVENTS_PROVIDER_URL, EVENTS_PROVIDER_API_KEY

router = APIRouter(tags=["sync"])


@router.post("/api/sync/trigger")
async def trigger_sync(db: Session = Depends(get_db)):
    try:
        logging.info("=== sync/trigger: step 1 - creating client ===")
        client = EventsProviderClient(
            base_url=EVENTS_PROVIDER_URL,
            api_key=EVENTS_PROVIDER_API_KEY
        )

        logging.info("=== sync/trigger: step 2 - creating repos ===")
        event_repo = EventRepository(db)
        place_repo = PlaceRepository(db)
        sync_metadata_repo = SyncMetadataRepository(db)

        logging.info("=== sync/trigger: step 3 - creating usecase ===")
        usecase = SyncEventsUsecase(client, event_repo, place_repo)

        logging.info("=== sync/trigger: step 4 - getting metadata ===")
        metadata = sync_metadata_repo.get_metadata()
        changed_at = metadata.last_changed_at or "2000-01-01"

        logging.info("=== sync/trigger: step 5 - calling usecase.do with changed_at=%s ===", changed_at)
        count = await usecase.do(changed_at=changed_at)

        logging.info("=== sync/trigger: step 6 - updating metadata, count=%s ===", count)
        now = datetime.now().isoformat()
        sync_metadata_repo.update_metadata(
            last_sync_time=datetime.now(),
            last_changed_at=now,
            sync_status="success"
        )

        logging.info("=== sync/trigger: step 7 - returning success ===")
        return {"status": "success", "synced": count}
    except Exception as e:
        logging.error("=== sync/trigger: ERROR: %s ===", e)
        raise HTTPException(status_code=500, detail=str(e))