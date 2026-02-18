"""Agent management service."""

import json
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ..database import AgentDB, SkillDB
from ..schemas import Agent, AgentConfig, AgentState, Skill, SkillManifest, SkillStatus


class AgentService:
    """Service for managing the system agent."""

    def __init__(self, db: Session):
        """Initialize agent service."""
        self.db = db

    def create_or_update_agent(self, name: str = "default_agent", config: Optional[AgentConfig] = None) -> Agent:
        """Create or get the existing persistent agent."""
        db_agent = self.db.query(AgentDB).filter(AgentDB.name == name).first()
        
        if not db_agent:
            agent_id = "default_agent"
            if config is None:
                config = AgentConfig()
            
            db_agent = AgentDB(
                id=agent_id,
                name=name,
                config=config.model_dump_json(),
                state=AgentState.IDLE,
                memory_enabled=True,
            )
            self.db.add(db_agent)
            self.db.commit()
            self.db.refresh(db_agent)
        
        return self._to_schema(db_agent)

    def get_agent(self) -> Agent:
        """Get the default agent."""
        return self.create_or_update_agent("default_agent")

    def update_agent_state(self, state: AgentState) -> Agent:
        """Update agent state."""
        db_agent = self.db.query(AgentDB).filter(AgentDB.id == "default_agent").first()
        if not db_agent:
            db_agent = self.create_or_update_agent("default_agent")
        
        db_agent.state = state.value
        db_agent.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self._to_schema(db_agent)

    def _to_schema(self, db_agent: AgentDB) -> Agent:
        """Convert database model to Pydantic schema."""
        config = AgentConfig(**json.loads(db_agent.config))
        
        return Agent(
            id=db_agent.id,
            name=db_agent.name,
            config=config,
            state=AgentState(db_agent.state),
            skills=self._get_all_skill_ids(),
            memory_enabled=db_agent.memory_enabled,
            created_at=db_agent.created_at,
            updated_at=db_agent.updated_at,
        )

    def _get_all_skill_ids(self) -> List[str]:
        """Get IDs of all available skills."""
        skills = self.db.query(SkillDB).all()
        return [skill.id for skill in skills]


class SkillService:
    """Service for managing skills."""

    def __init__(self, db: Session):
        """Initialize skill service."""
        self.db = db

    def register_skill(self, manifest: SkillManifest) -> Skill:
        """Register a new skill."""
        skill_id = manifest.name
        
        skill = Skill(
            id=skill_id,
            manifest=manifest,
        )
        
        # Save to database
        db_skill = SkillDB(
            id=skill_id,
            name=manifest.name,
            description=manifest.description,
            manifest=manifest.model_dump_json(),
            status=SkillStatus.ACTIVE,
        )
        self.db.add(db_skill)
        self.db.commit()
        
        return skill

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get skill by ID."""
        db_skill = self.db.query(SkillDB).filter(
            SkillDB.id == skill_id
        ).first()
        
        if not db_skill:
            return None
        
        manifest = SkillManifest(**json.loads(db_skill.manifest))
        
        return Skill(
            id=db_skill.id,
            manifest=manifest,
            status=SkillStatus(db_skill.status),
            last_executed=db_skill.last_executed,
            execution_count=int(db_skill.execution_count),
            created_at=db_skill.created_at,
            updated_at=db_skill.updated_at,
        )

    def list_skills(self) -> List[Skill]:
        """List all skills."""
        db_skills = self.db.query(SkillDB).all()
        
        skills = []
        for db_skill in db_skills:
            manifest = SkillManifest(**json.loads(db_skill.manifest))
            skills.append(
                Skill(
                    id=db_skill.id,
                    manifest=manifest,
                    status=SkillStatus(db_skill.status),
                    last_executed=db_skill.last_executed,
                    execution_count=int(db_skill.execution_count),
                    created_at=db_skill.created_at,
                    updated_at=db_skill.updated_at,
                )
            )
        
        return skills

    def update_skill_execution(self, skill_id: str) -> Skill:
        """Update skill last execution time and count."""
        db_skill = self.db.query(SkillDB).filter(
            SkillDB.id == skill_id
        ).first()
        
        if not db_skill:
            raise ValueError(f"Skill {skill_id} not found")
        
        db_skill.last_executed = datetime.utcnow()
        db_skill.execution_count = str(int(db_skill.execution_count) + 1)
        db_skill.updated_at = datetime.utcnow()
        self.db.commit()
        
        return self.get_skill(skill_id)
