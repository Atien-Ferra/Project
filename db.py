import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv(Path(__file__).resolve().parent / ".env")  # adjust if .env is elsewhere

_client: MongoClient | None = None

def get_db():
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise RuntimeError("MONGODB_URI not set")
        _client = MongoClient(uri)
        _client.admin.command("ping")  # fail fast if connection is wrong
    return _client.get_database()