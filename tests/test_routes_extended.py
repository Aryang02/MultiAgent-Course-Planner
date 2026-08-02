import uuid
from datetime import UTC
from unittest.mock import MagicMock, patch

from src.api.deps import get_cors_origins
from src.api.exceptions import (
    AppError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from src.core.models import User


def test_get_cors_origins_parses_csv():
    with patch("src.api.deps.settings") as mock_settings:
        mock_settings.CORS_ORIGINS = "http://a.com, http://b.com"
        assert get_cors_origins() == ["http://a.com", "http://b.com"]


def test_exception_status_codes():
    assert NotFoundError().status_code == 404
    assert ConflictError().status_code == 409
    assert UnauthorizedError().status_code == 401
    assert ForbiddenError().status_code == 403
    assert AppError("bad", status_code=400).status_code == 400


def test_register_success(client, mock_db):
    new_user = User(id=uuid.uuid4(), username="newbie", email="new@example.com", password=b"x")
    with patch("src.api.routes.auth.UserRepository") as repo_cls:
        repo = repo_cls.return_value
        repo.get_by_email.return_value = None
        repo.get_by_username.return_value = None
        with patch("src.api.routes.auth.send_welcome_email") as mock_email:
            mock_email.delay.return_value = None
            with patch("src.api.routes.auth.User") as user_cls:
                user_cls.return_value = new_user
                response = client.post(
                    "/v1/register",
                    json={
                        "username": "newbie",
                        "email": "new@example.com",
                        "password": "password123",
                    },
                )
    assert response.status_code == 201


def test_register_conflict(client, mock_db):
    existing = User(id=uuid.uuid4(), username="taken", email="taken@example.com", password=b"x")
    with patch("src.api.routes.auth.UserRepository") as repo_cls:
        repo = repo_cls.return_value
        repo.get_by_email.return_value = existing
        response = client.post(
            "/v1/register",
            json={
                "username": "taken",
                "email": "taken@example.com",
                "password": "password123",
            },
        )
    assert response.status_code == 409


def test_login_success(client, mock_db, user):
    with patch("src.api.routes.auth.UserRepository") as repo_cls:
        repo = repo_cls.return_value
        repo.get_by_email.return_value = user
        with patch("src.api.routes.auth.issue_tokens", return_value=("access", "refresh")):
            response = client.post(
                "/v1/login",
                json={"email": user.email, "password": "password123"},
            )
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "access"
    assert body["refresh_token"] == "refresh"


def test_login_invalid_credentials(client, mock_db):
    with patch("src.api.routes.auth.UserRepository") as repo_cls:
        repo_cls.return_value.get_by_email.return_value = None
        response = client.post(
            "/v1/login",
            json={"email": "nobody@example.com", "password": "wrong"},
        )
    assert response.status_code == 401


def test_refresh_success(client, mock_db, user):
    from datetime import datetime, timedelta

    from jose import jwt

    from src.settings import settings

    access = jwt.encode(
        {
            "sub": str(user.id),
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=15),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    with patch("src.api.routes.auth.refresh_tokens", return_value=(access, "new-refresh")):
        with patch("src.api.routes.auth.UserRepository") as repo_cls:
            repo_cls.return_value.get_by_id.return_value = user
            response = client.post("/v1/refresh", json={"refresh_token": "old-refresh"})
    assert response.status_code == 200
    assert response.json()["access_token"] == access


def test_refresh_invalid_token(client, mock_db):
    with patch("src.api.routes.auth.refresh_tokens", side_effect=ValueError("bad token")):
        response = client.post("/v1/refresh", json={"refresh_token": "bad"})
    assert response.status_code == 401


def test_logout(client, mock_db):
    with patch("src.api.routes.auth.revoke_session") as mock_revoke:
        response = client.post(
            "/v1/logout",
            json={"refresh_token": "refresh"},
            headers={"Authorization": "Bearer access-token"},
        )
    assert response.status_code == 204
    mock_revoke.assert_called_once()


def test_me_endpoint(authed_client, user):
    response = authed_client.get("/v1/me", headers={"Authorization": "Bearer token"})
    assert response.status_code == 200
    assert response.json()["email"] == user.email


def test_list_chats(authed_client, mock_db, user, sample_chat):
    with patch("src.api.routes.chat.ChatRepository") as repo_cls:
        repo_cls.return_value.list_for_user.return_value = [sample_chat]
        response = authed_client.get("/v1/chats", headers={"Authorization": "Bearer token"})
    assert response.status_code == 200
    assert len(response.json()["chats"]) == 1


def test_get_chat_not_found(authed_client, mock_db):
    with patch("src.api.routes.chat.ChatRepository") as repo_cls:
        repo_cls.return_value.get_by_chat_id.return_value = None
        response = authed_client.get(
            f"/v1/chats/{uuid.uuid4()}",
            headers={"Authorization": "Bearer token"},
        )
    assert response.status_code == 404


def test_create_chat(authed_client, mock_db, sample_chat):
    with patch("src.api.routes.chat.ChatRepository") as repo_cls:
        repo_cls.return_value.create_chat.return_value = sample_chat
        response = authed_client.post("/v1/chats", headers={"Authorization": "Bearer token"})
    assert response.status_code == 201
    assert "chat_id" in response.json()


def test_list_documents(authed_client, sample_document):
    with patch("src.api.routes.documents.DocumentRepository") as repo_cls:
        repo_cls.return_value.list_for_user.return_value = [sample_document]
        response = authed_client.get("/v1/documents", headers={"Authorization": "Bearer token"})
    assert response.status_code == 200
    assert len(response.json()["documents"]) == 1


def test_get_document_not_found(authed_client):
    with patch("src.api.routes.documents.DocumentRepository") as repo_cls:
        repo_cls.return_value.get_by_id.return_value = None
        response = authed_client.get(
            f"/v1/documents/{uuid.uuid4()}",
            headers={"Authorization": "Bearer token"},
        )
    assert response.status_code == 404


def test_list_study_plans(authed_client, sample_plan):
    with patch("src.api.routes.study_plans.StudyPlanRepository") as repo_cls:
        repo_cls.return_value.list_for_user.return_value = [sample_plan]
        response = authed_client.get("/v1/study-plans", headers={"Authorization": "Bearer token"})
    assert response.status_code == 200
    assert len(response.json()["plans"]) == 1


def test_get_study_plan_not_found(authed_client):
    with patch("src.api.routes.study_plans.StudyPlanRepository") as repo_cls:
        repo_cls.return_value.get_by_id.return_value = None
        response = authed_client.get(
            f"/v1/study-plans/{uuid.uuid4()}",
            headers={"Authorization": "Bearer token"},
        )
    assert response.status_code == 404


def test_upload_no_files(authed_client):
    response = authed_client.post("/v1/upload", headers={"Authorization": "Bearer token"})
    assert response.status_code == 422


def test_upload_success(authed_client, user):
    mock_result = MagicMock()
    mock_result.id = "upload-task-1"
    with patch("src.api.routes.upload.DataIngestion") as ingestion_cls:
        ingestion_cls.return_value.save_uploaded_files.return_value = [
            ("/tmp/file.txt", "file.txt", 100),
        ]
        with patch("src.api.routes.upload.ingest_documents") as mock_task:
            mock_task.delay.return_value = mock_result
            with patch("src.api.routes.upload.register_task_owner"):
                response = authed_client.post(
                    "/v1/upload",
                    files={"documents": ("file.txt", b"hello", "text/plain")},
                    headers={"Authorization": "Bearer token"},
                )
    assert response.status_code == 202
    assert response.json()["task_id"] == "upload-task-1"


def test_ready_degraded_when_db_fails(client):
    with patch("src.api.routes.health._check_database", return_value="error"):
        with patch("src.api.routes.health._check_redis", return_value="ok"):
            with patch("src.api.routes.health._check_pinecone", return_value="not_configured"):
                response = client.get("/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"


def test_app_error_handler_returns_json(client):
    from fastapi import APIRouter
    from fastapi.testclient import TestClient

    from src.api.app import create_app
    from src.api.exceptions import AppError

    app = create_app(run_migrations_on_startup=False)
    router = APIRouter()

    @router.get("/boom")
    def boom():
        raise AppError("bad request", status_code=400)

    app.include_router(router)
    response = TestClient(app, raise_server_exceptions=False).get("/boom")
    assert response.status_code == 400
    assert response.json()["detail"] == "bad request"
