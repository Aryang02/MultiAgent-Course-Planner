import uuid
from unittest.mock import MagicMock

from src.repositories.base import ChatRepository, StudyPlanRepository, UserRepository


def test_user_repository_get_by_email():
    db = MagicMock()
    repo = UserRepository(db)
    repo.get_by_email("alice@example.com")
    db.query.assert_called_once()


def test_chat_repository_create_chat():
    db = MagicMock()
    repo = ChatRepository(db)
    user_id = uuid.uuid4()
    chat = repo.create_chat(user_id)
    db.add.assert_called_once()
    assert chat.user_id == user_id
    assert chat.messages == []


def test_study_plan_repository_save():
    db = MagicMock()
    repo = StudyPlanRepository(db)
    user_id = uuid.uuid4()
    plan = repo.save(
        user_id=user_id,
        topic="Linear Algebra",
        study_topics=["Vectors"],
        notes={"summary": "test"},
        test={"questions": []},
    )
    db.add.assert_called_once()
    assert plan.topic == "Linear Algebra"
