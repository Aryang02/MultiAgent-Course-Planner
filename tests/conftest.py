import uuid
from datetime import UTC, datetime
from unittest.mock import MagicMock

import factory
import pytest
from fastapi.testclient import TestClient

from src.api.app import create_app
from src.auth.auth import get_user
from src.core.models import ChatHistory, Document, StudyPlan, User
from src.database.db import get_db


class UserFactory(factory.Factory):
    class Meta:
        model = User

    id = factory.LazyFunction(uuid.uuid4)
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    password = factory.LazyFunction(lambda: b"hashed")


@pytest.fixture
def user():
    test_user = User(
        id=uuid.uuid4(),
        username="tester",
        email="test@example.com",
        password=b"x",
    )
    test_user.set_password("password123")
    return test_user


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def app(mock_db):
    application = create_app(run_migrations_on_startup=False)
    application.dependency_overrides[get_db] = lambda: mock_db
    yield application
    application.dependency_overrides.clear()


@pytest.fixture
def authed_app(app, user):
    app.dependency_overrides[get_user] = lambda: user
    return app


@pytest.fixture
def client(app):
    return TestClient(app)


@pytest.fixture
def authed_client(authed_app):
    return TestClient(authed_app)


@pytest.fixture
def sample_document(user):
    return Document(
        id=uuid.uuid4(),
        user_id=user.id,
        file_name="notes.txt",
        file_path=f"data/{user.id}/notes.txt",
        status="completed",
        chunk_count=5,
        index_name="vector_db_index",
        uploaded_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_chat(user):
    return ChatHistory(
        id=uuid.uuid4(),
        user_id=user.id,
        chat_id=uuid.uuid4(),
        messages=[{"role": "user", "content": "hello"}],
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def sample_plan(user):
    return StudyPlan(
        id=uuid.uuid4(),
        user_id=user.id,
        topic="Linear Algebra",
        study_topics=["Vectors", "Matrices"],
        notes={"summary": "test"},
        test={"questions": []},
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_gemini():
    with pytest.MonkeyPatch.context() as mp:
        yield mp


@pytest.fixture
def mock_pinecone():
    with pytest.MonkeyPatch.context() as mp:
        yield mp
