from src.agents.agent_executor import AgentExecutor
from src.agents.critic_agent.agent import CriticAgent
from src.agents.notes_agent.agent import NotesAgent
from src.agents.planner_agent.agent import PlannerAgent
from src.agents.tutor_agent.agent import TutorAgent


def create_default_executor(
    run_id=None,
    log_callback=None,
) -> AgentExecutor:
    executor = AgentExecutor(run_id=run_id, log_callback=log_callback)
    executor.register("tutor", TutorAgent())
    executor.register("notes", NotesAgent())
    executor.register("critic", CriticAgent())
    planner = PlannerAgent(executor)
    executor.register("planner", planner)
    return executor
