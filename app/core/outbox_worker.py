import asyncio
import logging

from app.db.database import SessionLocal
from app.repositories.outbox_repository import OutboxRepository
from app.services.capashino_client import CapashinoClient


async def outbox_worker(
    capashino_client: CapashinoClient, interval: int = 10, max_attempts: int = 5
) -> None:
    while True:
        try:
            async with SessionLocal() as db:
                outbox_repo = OutboxRepository(db)
                pending = await outbox_repo.get_pending(limit=10)
                records_data = [(r.id, dict(r.payload)) for r in pending]

                for record_id, payload in records_data:
                    try:
                        await capashino_client.send_notification(
                            message=payload["message"],
                            reference_id=payload["ticket_id"],
                            idempotency_key=str(record_id),
                        )
                        await outbox_repo.mark_as_sent(record_id)
                        await db.commit()
                        logging.info("Outbox record %s sent successfully", record_id)
                    except Exception as e:
                        logging.error(
                            "Failed to send outbox record %s: %s", record_id, e
                        )
                        await db.rollback()
                        await outbox_repo.increment_attempts(record_id)
                        await db.commit()
                        updated = await outbox_repo.get_by_id(record_id)
                        if updated and updated.attempts >= max_attempts:
                            logging.warning(
                                "Outbox record %s exceeded max attempts, marking as failed",
                                record_id,
                            )
                            await outbox_repo.mark_as_failed(record_id)
                            await db.commit()
        except Exception as e:
            logging.error("Outbox worker error: %s", e)

        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logging.info("Outbox worker cancelled, shutting down gracefully.")
            break
