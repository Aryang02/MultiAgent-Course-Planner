from contextlib import contextmanager

from sqlalchemy.orm import Session

from src.database.db import SessionLocal


@contextmanager
def get_db_session() -> Session:
    """Context manager for database sessions outside FastAPI request scope."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
