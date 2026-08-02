from fastapi import FastAPI
from src.agents.agent_executor import AgentExecutor

app = FastAPI(title="A2A Server")
executor = AgentExecutor()
