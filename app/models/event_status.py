from enum import Enum

class EventStatus(str, Enum):
    PUBLISHED = "published"
    DRAFT = "draft"
    CANCELLED = "cancelled"