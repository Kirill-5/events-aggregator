import os

DATABASE_URL = os.getenv("POSTGRES_CONNECTION_STRING", "").replace("postgres://", "postgresql://", 1)