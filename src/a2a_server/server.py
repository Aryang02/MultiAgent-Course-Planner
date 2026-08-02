from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.agents.tutor_agent.__main__ import tutor_agent_card
from src.agents.planner_agent.__main__ import planner_agent_card
from src.agents.notes_agent.__main__ import notes_agent_card
from src.agents.critic_agent.__main__ import critic_agent_card

app = FastAPI(title="A2A Agent Discovery")

AGENT_CARDS = {
    "tutor": tutor_agent_card,
    "planner": planner_agent_card,
    "notes": notes_agent_card,
    "critic": critic_agent_card,
}


@app.get("/.well-known/agent.json")
def default_agent_card():
    return JSONResponse(tutor_agent_card.model_dump())


@app.get("/agents/{agent_name}/.well-known/agent.json")
def agent_card(agent_name: str):
    card = AGENT_CARDS.get(agent_name)
    if not card:
        return JSONResponse({"detail": "Agent not found"}, status_code=404)
    return JSONResponse(card.model_dump())
