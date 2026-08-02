from uuid import uuid4
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from src.api.app import create_app
from src.auth.auth import get_user
from src.core.models import User


def _make_app():
    return create_app(run_migrations_on_startup=False)


def test_health_endpoint():
    client = TestClient(_make_app())
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_validation_error():
    client = TestClient(_make_app())
    response = client.post(
        "/v1/register",
        json={"username": "ab", "email": "not-an-email", "password": "short"},
    )
    assert response.status_code == 422


def test_login_validation_error():
    client = TestClient(_make_app())
    response = client.post("/v1/login", json={"email": "bad", "password": ""})
    assert response.status_code == 422


def test_protected_route_requires_auth():
    client = TestClient(_make_app())
    response = client.get("/v1/me")
    assert response.status_code == 401


def test_generate_requires_auth():
    client = TestClient(_make_app())
    response = client.post(
        "/v1/generate",
        json={
            "query": "Explain linear algebra",
            "chat_id": "00000000-0000-0000-0000-000000000001",
        },
    )
    assert response.status_code == 401


def test_generate_enqueues_celery_task():
    app = _make_app()
    user = User(id=uuid4(), username="tester", email="test@example.com", password=b"x")
    app.dependency_overrides[get_user] = lambda: user

    mock_result = MagicMock()
    mock_result.id = "task-abc-123"

    with patch("src.api.routes.generate.run_agent_pipeline") as mock_task:
        mock_task.delay.return_value = mock_result
        client = TestClient(app)
        response = client.post(
            "/v1/generate",
            json={"query": "Explain linear algebra", "chat_id": str(uuid4())},
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 202
    body = response.json()
    assert body["task_id"] == "task-abc-123"
    assert body["status"] == "pending"
    mock_task.delay.assert_called_once()


def test_task_status_endpoint():
    app = _make_app()
    user = User(id=uuid4(), username="tester", email="test@example.com", password=b"x")
    app.dependency_overrides[get_user] = lambda: user

    with patch("src.api.routes.generate.get_task_status") as mock_status:
        from src.serializers.backend import TaskStatusResponse

        mock_status.return_value = TaskStatusResponse(
            task_id="task-abc-123",
            status="completed",
            result={"chunks_processed": 5},
        )
        client = TestClient(app)
        response = client.get(
            "/v1/tasks/task-abc-123",
            headers={"Authorization": "Bearer fake-token"},
        )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"