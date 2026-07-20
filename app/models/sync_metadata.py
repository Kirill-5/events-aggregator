from app.db.database import Base
from sqlalchemy import Column, Integer, String, DateTime


class SyncMetadata(Base):
    __tablename__ = "sync_metadata"
    id = Column(Integer, primary_key=True)
    last_sync_time = Column(DateTime)
    last_changed_at = Column(String)
    sync_status = Column(String)