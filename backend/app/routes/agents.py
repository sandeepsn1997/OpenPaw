from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..services.agent import AgentService
from ..schemas import Agent, AgentConfig

router = APIRouter()

@router.get("/", response_model=List[Agent])
def list_agents(db: Session = Depends(get_db)):
    """List all agents."""
    # This is a bit simplistic, we might want a proper list_agents in AgentService
    from ..database import AgentDB
    import json
    from ..schemas import AgentState
    
    db_agents = db.query(AgentDB).all()
    agents = []
    for db_agent in db_agents:
        config = AgentConfig(**json.loads(db_agent.config))
        agents.append(Agent(
            id=db_agent.id,
            name=db_agent.name,
            config=config,
            state=AgentState(db_agent.state),
            memory_enabled=db_agent.memory_enabled,
            created_at=db_agent.created_at,
            updated_at=db_agent.updated_at,
        ))
    return agents

@router.post("/", response_model=Agent)
def create_agent(agent_data: AgentConfig, name: str, db: Session = Depends(get_db)):
    """Create a new agent."""
    service = AgentService(db)
    return service.create_agent(name=name, config=agent_data)

@router.get("/{agent_id}", response_model=Agent)
def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Get agent by ID."""
    service = AgentService(db)
    agent = service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
