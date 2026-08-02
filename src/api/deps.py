from src.settings import settings


def get_cors_origins() -> list[str]:
    raw = getattr(settings, "CORS_ORIGINS", "http://localhost:3000,http://localhost:8000")
    if isinstance(raw, str):
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return list(raw)
