import os

DATABASE_URL = os.getenv("POSTGRES_CONNECTION_STRING", "").replace("postgres://", "postgresql+asyncpg://", 1)


EVENTS_PROVIDER_URL = os.getenv("EVENTS_PROVIDER_URL", "http://student-system-events-provider-web.student-system-events-provider.svc:8000")
EVENTS_PROVIDER_API_KEY = os.getenv("EVENTS_PROVIDER_API_KEY", "").strip()
CAPASHINO_URL = os.getenv("CAPASHINO_URL")
CAPASHINO_API_KEY = os.getenv("CAPASHINO_API_KEY")