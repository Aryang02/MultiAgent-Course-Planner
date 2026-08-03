import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.services.agent_pipeline import _run_pipeline_async


@pytest.mark.asyncio
async def test_run_pipeline_async():
    user_id = uuid.uuid4()
    chat_id = uuid.uuid4()

    mock_chat = MagicMock()
    mock_chat.messages = []
    mock_chat.chat_id = chat_id

    mock_run = MagicMock()
    mock_run.run_id = uuid.uuid4()

    mock_plan = MagicMock()
    mock_plan.id = uuid.uuid4()

    final_plan = {
        "topic": "Linear Algebra",
        "study_topics": ["Vectors"],
        "notes": {"summary": "notes"},
        "test": {"questions": []},
    }

    with patch("src.services.agent_pipeline.get_db_session") as mock_session:
        mock_db = MagicMock()
        mock_session.return_value.__enter__.return_value = mock_db

        with patch("src.services.agent_pipeline.ChatRepository") as mock_chat_repo:
            with patch("src.services.agent_pipeline.AgentRunRepository") as mock_run_repo:
                with patch("src.services.agent_pipeline.StudyPlanRepository") as mock_plan_repo:
                    with patch("src.services.agent_pipeline.create_default_executor") as mock_exec:
                        mock_chat_repo.return_value.get_by_chat_id.return_value = mock_chat
                        mock_run_repo.return_value.create_run.return_value = mock_run
                        mock_plan_repo.return_value.save.return_value = mock_plan

                        mock_planner = MagicMock()
                        mock_planner.create_plan = AsyncMock(return_value=final_plan)
                        mock_exec.return_value.agents = {"planner": mock_planner}

                        result = await _run_pipeline_async(user_id, chat_id, "Linear Algebra")

    assert result["status"] == "completed"
    assert result["plan_id"] == str(mock_plan.id)
    assert result["study_topics"] == ["Vectors"]
