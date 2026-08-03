import uuid

from sqlalchemy.orm import Session

from src.repositories import AgentRunRepository, UserRepository


def validate_user_exists(db: Session, user_id: str) -> uuid.UUID:
    """Ensure user_id is a valid UUID for an existing user."""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError as exc:
        raise ValueError("Invalid user_id") from exc

    user = UserRepository(db).get_by_id(user_uuid)
    if not user:
        raise ValueError("User not found")
    return user_uuid


def validate_run_belongs_to_user(db: Session, user_id: str, run_id: str) -> uuid.UUID:
    user_uuid = validate_user_exists(db, user_id)
    try:
        run_uuid = uuid.UUID(run_id)
    except ValueError as exc:
        raise ValueError("Invalid run_id") from exc

    run = AgentRunRepository(db).get_run_for_user(user_uuid, run_uuid)
    if not run:
        raise ValueError("Agent run not found for user")
    return run_uuid
