from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from jose import jwt

from src.auth.token_service import ACCESS_TOKEN_TTL, REFRESH_TOKEN_TTL, issue_tokens, refresh_tokens
from src.core.models import AuthToken, User
from src.settings import settings
from src.utils.email_helper import build_welcome_email, email_helper
from src.worker.task_ownership import get_task_owner, register_task_owner
from src.worker.task_status import get_task_status


def test_build_welcome_email_contains_login_link():
    subject, plain, html = build_welcome_email("https://app.example/login")
    assert subject == "Welcome to MCP"
    assert "https://app.example/login" in plain
    assert "https://app.example/login" in html


def test_issue_tokens_returns_access_and_refresh_tokens():
    user = User(id=uuid4(), username="alice", email="alice@example.com", password=b"x")
    db = MagicMock()

    with patch("src.auth.token_service.AuthTokenRepository") as repo_cls:
        repo = repo_cls.return_value
        access, refresh = issue_tokens(db, user)

    payload = jwt.decode(access, settings.SECRET_KEY, algorithms=["HS256"])
    assert payload["type"] == "access"
    assert payload["sub"] == str(user.id)
    assert payload["jti"]

    refresh_payload = jwt.decode(refresh, settings.SECRET_KEY, algorithms=["HS256"])
    assert refresh_payload["type"] == "refresh"
    repo.create.assert_called_once()
    db.commit.assert_called_once()


def test_refresh_tokens_rotate_pair():
    user = User(id=uuid4(), username="bob", email="bob@example.com", password=b"x")
    db = MagicMock()
    refresh = jwt.encode(
        {
            "sub": str(user.id),
            "jti": str(uuid4()),
            "type": "refresh",
            "exp": datetime.now(timezone.utc) + timedelta(days=1),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    record = AuthToken(
        user_id=user.id,
        token="old-access",
        refresh_token=refresh,
        expires_at=datetime.utcnow() + timedelta(minutes=15),
        refresh_expires_at=datetime.utcnow() + timedelta(days=7),
        refresh_expired=False,
    )

    with patch("src.auth.token_service.AuthTokenRepository") as repo_cls:
        repo = repo_cls.return_value
        repo.get_active_by_refresh_token.return_value = record
        repo.get_user.return_value = user
        with patch("src.auth.token_service.issue_tokens", return_value=("new-access", "new-refresh")):
            access2, refresh2 = refresh_tokens(db, refresh)

    assert access2 == "new-access"
    assert refresh2 == "new-refresh"
    repo.mark_refresh_expired.assert_called_once_with(record)


def test_task_ownership_helpers():
    task_id = f"task-{uuid4()}"
    user_id = str(uuid4())

    with patch("src.worker.task_ownership._get_redis") as mock_redis_factory:
        mock_redis = MagicMock()
        mock_redis.get.return_value = user_id
        mock_redis_factory.return_value = mock_redis

        register_task_owner(task_id, user_id)
        assert get_task_owner(task_id) == user_id
        mock_redis.setex.assert_called_once()


def test_get_task_status_requires_owner():
    task_id = "missing-task"
    with patch("src.worker.task_ownership.get_task_owner", return_value=None):
        with patch("src.worker.task_status.AsyncResult") as mock_result_cls:
            mock_result = MagicMock()
            mock_result.state = "PENDING"
            mock_result.successful.return_value = False
            mock_result.failed.return_value = False
            mock_result_cls.return_value = mock_result

            with pytest.raises(Exception) as exc:
                get_task_status(task_id, str(uuid4()))
            assert exc.value.status_code == 404


def test_access_and_refresh_token_ttl_values():
    assert ACCESS_TOKEN_TTL == timedelta(minutes=15)
    assert REFRESH_TOKEN_TTL == timedelta(days=7)


def test_email_helper_uses_starttls_on_port_587():
    with patch("src.utils.email_helper.SMTP") as mock_smtp_cls:
        mock_smtp = MagicMock()
        mock_smtp_cls.return_value.__enter__.return_value = mock_smtp
        with patch("src.settings.settings.EMAIL_HOST_USER", "user@example.com"):
            with patch("src.settings.settings.EMAIL_HOST_PASSWORD", "secret"):
                with patch("src.settings.settings.EMAIL_PORT", 587):
                    email_helper(["a@example.com"], "hello", "subject")
        mock_smtp.starttls.assert_called_once()
        mock_smtp.login.assert_called_once()
