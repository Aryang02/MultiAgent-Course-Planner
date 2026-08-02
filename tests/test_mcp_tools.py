import uuid
from unittest.mock import MagicMock, patch

import pytest

from src.mcp.orchestrator_server import fetch_plan, get_chat_history
from src.mcp.tutor_server import get_agent_conversation, search_user_documents


@pytest.mark.asyncio
async def test_orchestrator_get_chat_history():
    user_id = str(uuid.uuid4())
    chat_id = str(uuid.uuid4())
    with patch("src.mcp.orchestrator_server.get_db_session") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        with patch(
            "src.mcp.orchestrator_server.validate_user_exists",
            return_value=uuid.UUID(user_id),
        ):
            with patch("src.mcp.orchestrator_server.ChatRepository") as repo_cls:
                chat = MagicMock()
                chat.messages = [{"role": "user", "content": "hi"}]
                repo_cls.return_value.get_by_chat_id.return_value = chat
                result = await get_chat_history(user_id, chat_id)
    assert result == [{"role": "user", "content": "hi"}]


def test_orchestrator_fetch_plan_found():
    user_id = str(uuid.uuid4())
    with patch("src.mcp.orchestrator_server.get_db_session") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        with patch(
            "src.mcp.orchestrator_server.validate_user_exists",
            return_value=uuid.UUID(user_id),
        ):
            with patch("src.mcp.orchestrator_server.StudyPlanRepository") as repo_cls:
                plan = MagicMock()
                plan.id = uuid.uuid4()
                plan.topic = "Math"
                plan.study_topics = ["Algebra"]
                plan.notes = {}
                plan.test = {}
                repo_cls.return_value.get_latest_for_topic.return_value = plan
                result = fetch_plan(user_id, "Math")
    assert result["topic"] == "Math"


def test_orchestrator_fetch_plan_missing():
    user_id = str(uuid.uuid4())
    with patch("src.mcp.orchestrator_server.get_db_session") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        with patch(
            "src.mcp.orchestrator_server.validate_user_exists",
            return_value=uuid.UUID(user_id),
        ):
            with patch("src.mcp.orchestrator_server.StudyPlanRepository") as repo_cls:
                repo_cls.return_value.get_latest_for_topic.return_value = None
                result = fetch_plan(user_id, "Missing")
    assert "No plans found" in result


@pytest.mark.asyncio
async def test_tutor_search_documents():
    user_id = str(uuid.uuid4())
    with patch("src.mcp.tutor_server.get_db_session") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        with patch(
            "src.mcp.tutor_server.validate_user_exists",
            return_value=uuid.UUID(user_id),
        ):
            with patch(
                "src.database.vector_search.search_documents",
                return_value=[{"text": "chunk"}],
            ):
                result = await search_user_documents(user_id, "query")
    assert result == [{"text": "chunk"}]


@pytest.mark.asyncio
async def test_tutor_get_agent_conversation():
    user_id = str(uuid.uuid4())
    run_id = str(uuid.uuid4())
    with patch("src.mcp.tutor_server.get_db_session") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db
        with patch(
            "src.mcp.tutor_server.validate_run_belongs_to_user",
            return_value=uuid.UUID(run_id),
        ):
            with patch("src.mcp.tutor_server.AgentRunRepository") as repo_cls:
                message = MagicMock()
                message.sender_agent = "planner"
                message.receiver_agent = "tutor"
                message.content = {"text": "hello"}
                repo_cls.return_value.get_messages.return_value = [message]
                result = await get_agent_conversation(user_id, run_id)
    assert result[0]["sender_agent"] == "planner"
