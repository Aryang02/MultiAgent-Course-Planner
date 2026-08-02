"""Agent pipeline service. Full MCP/A2A wiring completed in Phase 4."""

import uuid
from datetime import datetime

from src.database.session import get_db_session
from src.repositories import AgentRunRepository, ChatRepository


def run_pipeline(
    user_id: uuid.UUID,
    chat_id: uuid.UUID,
    query: str,
    run_id: uuid.UUID,
) -> dict:
    with get_db_session() as db:
        chats = ChatRepository(db)
        chat = chats.get_by_chat_id(user_id, chat_id)
        if not chat:
            raise ValueError("Chat not found")

        runs = AgentRunRepository(db)
        agent_run = runs.create_run(
            user_id=user_id,
            agents_involved=["planner"],
            input_data={"query": query, "chat_id": str(chat_id)},
        )

        # Phase 4 will replace this stub with PlannerAgent orchestration
        output = {
            "run_id": str(agent_run.run_id),
            "topic": query,
            "status": "completed",
            "message": (
                "Pipeline stub executed. Full tutor/notes/critic orchestration "
                "will be wired in Phase 4."
            ),
            "study_topics": [],
            "notes": None,
            "test": None,
        }

        runs.complete_run(agent_run.run_id, output)
        runs.log_message(
            run_id=agent_run.run_id,
            sender="planner",
            content={"role": "assistant", "content": output["message"]},
        )

        chat.messages = (chat.messages or []) + [
            {"role": "user", "content": query, "timestamp": datetime.utcnow().isoformat()},
            {
                "role": "assistant",
                "content": output["message"],
                "timestamp": datetime.utcnow().isoformat(),
            },
        ]
        db.add(chat)

    return output
