from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sync_metadata import SyncMetadata


class SyncMetadataRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_metadata(self) -> SyncMetadata:
        query = select(SyncMetadata)
        result = await self.session.execute(query)
        metadata = result.scalars().first()
        if not metadata:
            metadata = SyncMetadata(
                last_sync_time=None, last_changed_at="2000-01-01", sync_status="pending"
            )
            self.session.add(metadata)
            await self.session.commit()
            await self.session.refresh(metadata)
        return metadata

    async def update_metadata(
        self, last_sync_time: datetime, last_changed_at: str, sync_status: str
    ) -> None:
        query = select(SyncMetadata)
        result = await self.session.execute(query)
        metadata = result.scalars().first()
        if not metadata:
            metadata = SyncMetadata(
                last_sync_time=last_sync_time,
                last_changed_at=last_changed_at,
                sync_status=sync_status,
            )
            self.session.add(metadata)
        else:
            metadata.last_sync_time = last_sync_time
            metadata.last_changed_at = last_changed_at
            metadata.sync_status = sync_status
        await self.session.commit()
