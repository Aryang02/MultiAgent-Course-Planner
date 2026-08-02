import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from jose import jwt

from src.auth.auth import get_user
from src.auth.authorization import validate_run_belongs_to_user, validate_user_exists
from src.auth.token_blocklist import block_token, is_token_blocked
from src.auth.token_service import revoke_session
from src.core.models import AgentRun, AuthToken, User
from src.settings import settings


def test_validate_user_exists_success():
    user_id = uuid.uuid4()
    db = MagicMock()
    with patch("src.auth.authorization.UserRepository") as repo_cls:
        repo_cls.return_value.get_by_id.return_value = User(
            id=user_id, username="a", email="a@x.com", password=b"x"
        )
        result = validate_user_exists(db, str(user_id))
    assert result == user_id


def test_validate_user_exists_invalid_uuid():
    with pytest.raises(ValueError, match="Invalid user_id"):
        validate_user_exists(MagicMock(), "not-a-uuid")


def test_validate_user_exists_not_found():
    db = MagicMock()
    with patch("src.auth.authorization.UserRepository") as repo_cls:
        repo_cls.return_value.get_by_id.return_value = None
        with pytest.raises(ValueError, match="User not found"):
            validate_user_exists(db, str(uuid.uuid4()))


def test_validate_run_belongs_to_user_success():
    user_id = uuid.uuid4()
    run_id = uuid.uuid4()
    db = MagicMock()
    with patch("src.auth.authorization.UserRepository") as user_repo_cls:
        with patch("src.auth.authorization.AgentRunRepository") as run_repo_cls:
            user_repo_cls.return_value.get_by_id.return_value = User(
                id=user_id, username="a", email="a@x.com", password=b"x"
            )
            run_repo_cls.return_value.get_run_for_user.return_value = AgentRun(
                user_id=user_id, agents_involved=[], input={}
            )
            result = validate_run_belongs_to_user(db, str(user_id), str(run_id))
    assert result == run_id


def test_validate_run_belongs_to_user_invalid_run_id():
    user_id = uuid.uuid4()
    db = MagicMock()
    with patch("src.auth.authorization.UserRepository") as user_repo_cls:
        user_repo_cls.return_value.get_by_id.return_value = User(
            id=user_id, username="a", email="a@x.com", password=b"x"
        )
        with pytest.raises(ValueError, match="Invalid run_id"):
            validate_run_belongs_to_user(db, str(user_id), "bad-run-id")


def test_validate_run_belongs_to_user_not_found():
    user_id = uuid.uuid4()
    db = MagicMock()
    with patch("src.auth.authorization.UserRepository") as user_repo_cls:
        with patch("src.auth.authorization.AgentRunRepository") as run_repo_cls:
            user_repo_cls.return_value.get_by_id.return_value = User(
                id=user_id, username="a", email="a@x.com", password=b"x"
            )
            run_repo_cls.return_value.get_run_for_user.return_value = None
            with pytest.raises(ValueError, match="Agent run not found"):
                validate_run_belongs_to_user(db, str(user_id), str(uuid.uuid4()))


def test_block_and_check_token():
    jti = str(uuid.uuid4())
    expires_at = datetime.now(UTC) + timedelta(minutes=15)
    with patch("src.auth.token_blocklist._get_redis") as mock_redis_factory:
        mock_redis = MagicMock()
        mock_redis.exists.return_value = 1
        mock_redis_factory.return_value = mock_redis
        block_token(jti, expires_at)
        assert is_token_blocked(jti) is True
        mock_redis.setex.assert_called_once()


def test_is_token_blocked_redis_error_returns_false():
    import redis

    with patch("src.auth.token_blocklist._get_redis") as mock_redis_factory:
        mock_redis = MagicMock()
        mock_redis.exists.side_effect = redis.RedisError("redis down")
        mock_redis_factory.return_value = mock_redis
        assert is_token_blocked("jti-123") is False


def test_get_user_valid_token(user):
    request = MagicMock()
    db = MagicMock()
    token = jwt.encode(
        {
            "sub": str(user.id),
            "jti": str(uuid.uuid4()),
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=15),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    db.query.return_value.filter.return_value.first.return_value = user
    with patch("src.auth.auth.is_token_blocked", return_value=False):
        result = get_user(request, token, db)
    assert result.id == user.id
    assert request.state.user_id == user.id


def test_get_user_blocked_token():
    request = MagicMock()
    token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "jti": str(uuid.uuid4()),
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=15),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    with patch("src.auth.auth.is_token_blocked", return_value=True):
        with pytest.raises(HTTPException) as exc:
            get_user(request, token, MagicMock())
    assert exc.value.status_code == 401


def test_get_user_wrong_token_type():
    request = MagicMock()
    token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "type": "refresh",
            "exp": datetime.now(UTC) + timedelta(minutes=15),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    with patch("src.auth.auth.is_token_blocked", return_value=False):
        with pytest.raises(HTTPException) as exc:
            get_user(request, token, MagicMock())
    assert exc.value.status_code == 401


def test_revoke_session_with_tokens():
    db = MagicMock()
    access = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "jti": str(uuid.uuid4()),
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=15),
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    refresh = "refresh-token-value"
    record = AuthToken(
        user_id=uuid.uuid4(),
        token=access,
        refresh_token=refresh,
        expires_at=datetime.now(UTC) + timedelta(minutes=15),
        refresh_expires_at=datetime.now(UTC) + timedelta(days=7),
        refresh_expired=False,
    )
    with patch("src.auth.token_service.block_token") as mock_block:
        with patch("src.auth.token_service.AuthTokenRepository") as repo_cls:
            repo_cls.return_value.get_active_by_refresh_token.return_value = record
            revoke_session(db, access_token=access, refresh_token=refresh)
    mock_block.assert_called_once()
    db.commit.assert_called_once()
