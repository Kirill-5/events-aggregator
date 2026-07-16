from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

from app.db.database import SessionLocal
from app.repositories import EventRepository, PlaceRepository
from app.services.events_provider_client import EventsProviderClient
from app.usecases.SyncEventsUsecase import SyncEventsUsecase


def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(sync_job, 'interval', days=1)
    scheduler.start()

async def sync_job():
    db = SessionLocal()

    try:
        client = EventsProviderClient(
            base_url="http://student-system-events-provider-web.student-system-events-provider.svc:8000")

        event_repo = EventRepository(db)
        place_repo = PlaceRepository(db)
        usecase = SyncEventsUsecase(client, event_repo, place_repo)

        count = await usecase.do()
        logging.info(f"Sync completed : {count} events processed")

    except Exception as e:
        logging.error(f"Sync failed : {e}")

    finally:
        db.close()

