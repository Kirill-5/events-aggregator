import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import EVENTS_PROVIDER_API_KEY, EVENTS_PROVIDER_URL
from app.db.database import SessionLocal
from app.repositories import EventRepository, PlaceRepository, SyncMetadataRepository
from app.services.events_provider_client import EventsProviderClient
from app.usecases.sync_events_usecase import SyncEventsUsecase


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(sync_job, "interval", days=1)
    scheduler.start()


async def sync_job():
    async with SessionLocal() as db:
        try:
            client = EventsProviderClient(
                base_url=EVENTS_PROVIDER_URL, api_key=EVENTS_PROVIDER_API_KEY
            )
            event_repo = EventRepository(db)
            place_repo = PlaceRepository(db)
            sync_metadata_repo = SyncMetadataRepository(db)

            usecase = SyncEventsUsecase(client, event_repo, place_repo)

            metadata = await sync_metadata_repo.get_metadata()
            changed_at = metadata.last_changed_at or "2000-01-01"

            count = await usecase.do(changed_at=changed_at)
            logging.info("Sync completed: %s events processed", count)

            now = datetime.now().isoformat()
            await sync_metadata_repo.update_metadata(
                last_sync_time=datetime.now(),
                last_changed_at=now,
                sync_status="success",
            )

        except Exception as e:
            logging.error("Sync failed: %s", e)
