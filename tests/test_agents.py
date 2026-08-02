import uuid
from unittest.mock import patch

import pytest

from src.agents.critic_agent.agent import CriticAgent
from src.agents.notes_agent.agent import NotesAgent
from src.agents.registry import create_default_executor
from src.agents.tutor_agent.agent import TutorAgent


def test_tutor_explain_parses_json():
    agent = TutorAgent()
    with patch("src.agents.base_agent.generate", return_value='["Vectors", "Matrices"]'):
        topics = agent.explain("Linear Algebra")
    assert topics == ["Vectors", "Matrices"]


def test_tutor_explain_uses_rag_context():
    agent = TutorAgent()
    user_id = uuid.uuid4()
    with patch(
        "src.agents.tutor_agent.agent.search_documents",
        return_value=["Vectors are quantities with magnitude and direction."],
    ):
        with patch(
            "src.agents.base_agent.generate",
            return_value='["Vectors", "Dot Product"]',
        ) as mock_generate:
            topics = agent.explain("Linear Algebra", user_id=user_id)

    assert topics == ["Vectors", "Dot Product"]
    prompt = mock_generate.call_args.kwargs.get("user_prompt") or mock_generate.call_args[0][0]
    assert "uploaded materials" in prompt


def test_notes_create_notes_parses_json():
    agent = NotesAgent()
    with patch(
        "src.agents.base_agent.generate",
        return_value='{"summary": "Overview", "sections": [{"title": "A", "content": "B"}]}',
    ):
        notes = agent.create_notes(["Vectors"])
    assert notes["summary"] == "Overview"
    assert len(notes["sections"]) == 1


def test_critic_create_test_parses_json():
    agent = CriticAgent()
    with patch(
        "src.agents.base_agent.generate",
        return_value='{"questions": [{"question": "Q1", "answer": "A1"}]}',
    ):
        test = agent.create_test({"summary": "notes"})
    assert len(test["questions"]) == 1


@pytest.mark.asyncio
async def test_planner_create_plan_orchestrates_agents():
    executor = create_default_executor()
    planner = executor.agents["planner"]

    with patch.object(TutorAgent, "explain", return_value=["Topic A", "Topic B"]) as mock_explain:
        with patch.object(
            NotesAgent,
            "create_notes",
            return_value={"summary": "Notes", "sections": []},
        ):
            with patch.object(
                CriticAgent,
                "create_test",
                return_value={"questions": [{"question": "Q", "answer": "A"}]},
            ):
                plan = await planner.create_plan(
                    user_id=uuid.uuid4(),
                    conversation_id=uuid.uuid4(),
                    topic="Linear Algebra",
                    run_id=uuid.uuid4(),
                )

    mock_explain.assert_called()
    call_kwargs = mock_explain.call_args.kwargs
    assert "user_id" in call_kwargs

    assert plan["topic"] == "Linear Algebra"
    assert plan["study_topics"] == ["Topic A", "Topic B"]
    assert plan["notes"]["summary"] == "Notes"
    assert len(plan["test"]["questions"]) == 1
