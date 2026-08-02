from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    DB_URL: str = os.getenv(
        "DB_URL",
        "postgresql+psycopg2://admin:admin123@localhost:5432/demo",
    )
    DB_USER: str = os.getenv("DB_USER", "admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "admin123")
    DB_NAME: str = os.getenv("DB_NAME", "demo")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_HOST_USER: str = os.getenv("EMAIL_HOST_USER", "")
    EMAIL_HOST_PASSWORD: str = os.getenv("EMAIL_HOST_PASSWORD", "")
    APP_URL: str = os.getenv("APP_URL", "http://localhost")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/1"
    )
    MCP_ORCHESTRATOR_URL: str = os.getenv(
        "MCP_ORCHESTRATOR_URL", "http://localhost:8001/mcp/"
    )
    MCP_PLANNER_URL: str = os.getenv("MCP_PLANNER_URL", "http://localhost:8002/mcp/")
    MCP_TUTOR_URL: str = os.getenv("MCP_TUTOR_URL", "http://localhost:8003/mcp/")
    MCP_CRITIC_URL: str = os.getenv("MCP_CRITIC_URL", "http://localhost:8004/mcp/")
    MCP_NOTES_URL: str = os.getenv("MCP_NOTES_URL", "http://localhost:8005/mcp/")
    CORS_ORIGINS: str = os.getenv(
        "CORS_ORIGINS", "http://localhost:3000,http://localhost:8000"
    )
    MAX_UPLOAD_FILE_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_FILE_SIZE_MB", "50"))
    MAX_UPLOAD_REQUEST_SIZE_MB: int = int(os.getenv("MAX_UPLOAD_REQUEST_SIZE_MB", "200"))
    DEFAULT_VECTOR_INDEX: str = os.getenv("DEFAULT_VECTOR_INDEX", "vector_db_index")


settings = Settings()
