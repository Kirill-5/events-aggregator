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
                    logging.info(f"Outbox record {record.id} sent successfully")
                except Exception as e:
                    logging.error(f"Failed to send outbox record {record.id}: {e}")
                    outbox_repo.increment_attempts(record.id)
                    if record.attempts >= max_attempts:
                        logging.warning(f"Outbox record {record.id} exceeded max attempts, marking as failed")
                        # Опционально: добавить статус "failed" в модель Outbox
        except Exception as e:
            logging.error(f"Outbox worker error: {e}")

        await asyncio.sleep(interval)