import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

from src.repositories.base import (
    AgentRunRepository,
    AuthTokenRepository,
    ChatRepository,
    DocumentRepository,
    StudyPlanRepository,
    UserRepository,
)


def test_user_repository_get_by_username_and_id():
    db = MagicMock()
    repo = UserRepository(db)
    repo.get_by_username("alice")
    repo.get_by_id(uuid.uuid4())
    assert db.query.call_count == 2


def test_user_repository_create():
    db = MagicMock()
    repo = UserRepository(db)
    user = repo.create("alice", "alice@example.com", b"hash")
    db.add.assert_called_once()
    assert user.username == "alice"


def test_document_repository_get_by_id_and_list():
    db = MagicMock()
    repo = DocumentRepository(db)
    user_id = uuid.uuid4()
    repo.get_by_id(user_id, uuid.uuid4())
    repo.list_for_user(user_id)
    assert db.query.call_count == 2


def test_document_repository_update_status_found():
    db = MagicMock()
    doc = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = doc
    repo = DocumentRepository(db)
    result = repo.update_status(uuid.uuid4(), "completed", chunk_count=3)
    assert result is doc
    assert doc.status == "completed"
    assert doc.chunk_count == 3


def test_document_repository_update_status_not_found():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    repo = DocumentRepository(db)
    assert repo.update_status(uuid.uuid4(), "failed") is None


def test_document_repository_mark_processing():
    db = MagicMock()
    doc = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = doc
    repo = DocumentRepository(db)
    repo.mark_processing([uuid.uuid4(), uuid.uuid4()])
    assert doc.status == "processing"


def test_auth_token_repository_create_and_mark_expired():
    db = MagicMock()
    repo = AuthTokenRepository(db)
    now = datetime.now(UTC)
    record = repo.create(
        user_id=uuid.uuid4(),
        access_token="access",
        refresh_token="refresh",
        expires_at=now,
        refresh_expires_at=now,
    )
    db.add.assert_called_once()
    repo.mark_refresh_expired(record)
    assert record.refresh_expired is True


def test_auth_token_repository_queries():
    db = MagicMock()
    repo = AuthTokenRepository(db)
    repo.get_active_by_refresh_token("refresh")
    repo.get_user(uuid.uuid4())
    assert db.query.call_count == 2


def test_chat_repository_get_and_list():
    db = MagicMock()
    repo = ChatRepository(db)
    user_id = uuid.uuid4()
    repo.get_by_chat_id(user_id, uuid.uuid4())
    repo.list_for_user(user_id)
    assert db.query.call_count == 2


def test_study_plan_repository_get_latest_and_by_id():
    db = MagicMock()
    repo = StudyPlanRepository(db)
    user_id = uuid.uuid4()
    repo.get_latest_for_topic(user_id, "Math")
    repo.get_by_id(user_id, uuid.uuid4())
    repo.list_for_user(user_id)
    assert db.query.call_count == 3


def test_agent_run_repository_lifecycle():
    db = MagicMock()
    run = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = run
    repo = AgentRunRepository(db)
    user_id = uuid.uuid4()
    run_id = uuid.uuid4()

    created = repo.create_run(user_id, ["planner"], {"query": "test"})
    db.add.assert_called()
    assert created.user_id == user_id

    repo.complete_run(run_id, {"status": "done"})
    assert run.final_output == {"status": "done"}

    message = repo.log_message(run_id, "planner", {"text": "hi"}, receiver="tutor")
    assert message.sender_agent == "planner"

    repo.get_messages(run_id)
    repo.get_run_for_user(user_id, run_id)


def test_agent_run_repository_complete_run_missing():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    repo = AgentRunRepository(db)
    assert repo.complete_run(uuid.uuid4(), {}) is None
