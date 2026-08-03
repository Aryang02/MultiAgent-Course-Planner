import os

from src.settings import settings

APP_URL = settings.APP_URL

AGENT_REGISTRY = [
    f"{APP_URL}:10000",
    f"{APP_URL}:10001",
    f"{APP_URL}:10002",
    f"{APP_URL}:10003",
]
