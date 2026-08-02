from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.settings import settings

SQLALCHEMY_DATABASE_URL = settings.DB_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
