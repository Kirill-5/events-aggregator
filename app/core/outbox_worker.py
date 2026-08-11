import asyncio
import logging
from app.repositories.outbox_repository import OutboxRepository
from app.services.capashino_client import CapashinoClient


async def outbox_worker(
        capashino_client: CapashinoClient,
        outbox_repo: OutboxRepository,
        interval: int = 10,
        max_attempts: int = 5
) -> None:
    while True:
        try:
            pending = outbox_repo.get_pending(limit=10)
            for record in pending:
                try:
                    await capashino_client.send_notification(
                        message=record.payload["message"],
                        reference_id=record.payload["ticket_id"],
                        idempotency_key=str(record.id)
                    )
                    outbox_repo.mark_as_sent(record.id)
                    logging.info("Outbox record %s sent successfully", record.id)
                except Exception as e:
                    logging.error("Failed to send outbox record %s: %s", record.id, e)
                    outbox_repo.session.rollback()
                    outbox_repo.increment_attempts(record.id)
                    if record.attempts >= max_attempts:
                        logging.warning("Outbox record %s exceeded max attempts, marking as failed", record.id)
                        outbox_repo.mark_as_failed(record.id)
        except Exception as e:
            outbox_repo.session.rollback()
            logging.error("Outbox worker error: %s", e)

        try:
            await asyncio.sleep(interval)
        except asyncio.CancelledError:
            logging.info("Outbox worker cancelled, shutting down gracefully.")
            break