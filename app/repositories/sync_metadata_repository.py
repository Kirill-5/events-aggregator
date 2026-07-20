from sqlalchemy.orm import Session
from datetime import datetime
from app.models.sync_metadata import SyncMetadata

class SyncMetadataRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_metadata(self) -> SyncMetadata:
        metadata = self.session.query(SyncMetadata).first()
        if not metadata:
            metadata = SyncMetadata(
                last_sync_time=None,
                last_changed_at="2000-01-01",
                sync_status="pending"
            )
            self.session.add(metadata)
            self.session.commit()
            self.session.refresh(metadata)
        return metadata

    def update_metadata(self, last_sync_time: datetime, last_changed_at: str, sync_status: str) -> None:
        metadata = self.session.query(SyncMetadata).first()
        if not metadata:
            metadata = SyncMetadata(
                last_sync_time=last_sync_time,
                last_changed_at=last_changed_at,
                sync_status=sync_status
            )
            self.session.add(metadata)
        else:
            metadata.last_sync_time = last_sync_time
            metadata.last_changed_at = last_changed_at
            metadata.sync_status = sync_status
        self.session.commit()