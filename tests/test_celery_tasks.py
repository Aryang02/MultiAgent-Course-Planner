from unittest.mock import MagicMock, patch
from uuid import uuid4

from src.worker.task_status import get_task_status
from src.worker.tasks.notifications import send_welcome_email


def test_send_welcome_email_task():
    with patch("src.worker.tasks.notifications.email_helper") as mock_helper:
        result = send_welcome_email("user@example.com", "Hello", "Welcome")
    mock_helper.assert_called_once_with(["user@example.com"], "Hello", "Welcome", html=None)
    assert result == {"sent": True, "to": "user@example.com"}


def test_get_task_status_success():
    user_id = str(uuid4())
    mock_result = MagicMock()
    mock_result.state = "SUCCESS"
    mock_result.successful.return_value = True
    mock_result.failed.return_value = False
    mock_result.result = {"chunks_processed": 10, "user_id": user_id}

    with patch("src.worker.task_status.get_task_owner", return_value=user_id):
        with patch("src.worker.task_status.AsyncResult", return_value=mock_result):
            status = get_task_status("task-123", user_id)

    assert status.task_id == "task-123"
    assert status.status == "completed"
    assert status.result == {"chunks_processed": 10, "user_id": user_id}


def test_get_task_status_pending():
    user_id = str(uuid4())
    mock_result = MagicMock()
    mock_result.state = "PENDING"
    mock_result.successful.return_value = False
    mock_result.failed.return_value = False

    with patch("src.worker.task_status.get_task_owner", return_value=user_id):
        with patch("src.worker.task_status.AsyncResult", return_value=mock_result):
            status = get_task_status("task-789", user_id)

    assert status.status == "pending"
