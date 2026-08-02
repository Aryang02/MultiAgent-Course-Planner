"""Agent pipeline service — orchestrates planner → tutor → notes → critic."""

import asyncio
import uuid
from datetime import datetime, timezone

from src.agents.registry import create_default_executor
from src.database.session import get_db_session
from src.repositories import AgentRunRepository, ChatRepository, StudyPlanRepository


async def _run_pipeline_async(
    user_id: uuid.UUID,
    chat_id: uuid.UUID,
    query: str,
) -> dict:
    with get_db_session() as db:
        chats = ChatRepository(db)
        chat = chats.get_by_chat_id(user_id, chat_id)
        if not chat:
            raise ValueError("Chat not found")

        runs = AgentRunRepository(db)

        def log_callback(run_id, sender, receiver, content):
            runs.log_message(
                run_id=run_id,
                sender=sender,
                receiver=receiver,
                content=content,
            )

        agent_run = runs.create_run(
            user_id=user_id,
            agents_involved=["planner", "tutor", "notes", "critic"],
            input_data={"query": query, "chat_id": str(chat_id)},
        )

        executor = create_default_executor(
            run_id=agent_run.run_id,
            log_callback=log_callback,
        )
        planner = executor.agents["planner"]
        final_plan = await planner.create_plan(
            user_id=user_id,
            conversation_id=chat_id,
            topic=query,
            run_id=agent_run.run_id,
        )

        saved_plan = StudyPlanRepository(db).save(
            user_id=user_id,
            topic=query,
            study_topics=final_plan["study_topics"],
            notes=final_plan["notes"],
            test=final_plan["test"],
        )

        output = {
            **final_plan,
            "plan_id": str(saved_plan.id),
            "run_id": str(agent_run.run_id),
            "status": "completed",
        }

        runs.complete_run(agent_run.run_id, output)

        now = datetime.now(timezone.utc).isoformat()
        chat.messages = (chat.messages or []) + [
            {"role": "user", "content": query, "timestamp": now},
            {
                "role": "assistant",
                "content": f"Study plan created for '{query}' with {len(final_plan['study_topics'])} topics.",
                "plan_id": str(saved_plan.id),
                "timestamp": now,
            },
        ]
        db.add(chat)

    return output


def run_pipeline(
    user_id: uuid.UUID,
    chat_id: uuid.UUID,
    query: str,
    run_id: uuid.UUID | None = None,
) -> dict:
    return asyncio.run(_run_pipeline_async(user_id, chat_id, query))
