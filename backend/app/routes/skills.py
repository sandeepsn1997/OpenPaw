from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..services.agent import SkillService
from ..schemas import Skill, SkillManifest

router = APIRouter()

@router.get("/", response_model=List[Skill])
def list_skills(db: Session = Depends(get_db)):
    """List all registered skills."""
    from ..database import SkillDB
    import json
    from ..schemas import SkillStatus
    
    db_skills = db.query(SkillDB).all()
    skills = []
    for db_skill in db_skills:
        manifest = SkillManifest(**json.loads(db_skill.manifest))
        skills.append(Skill(
            id=db_skill.id,
            manifest=manifest,
            status=SkillStatus(db_skill.status),
            last_executed=db_skill.last_executed,
            execution_count=int(db_skill.execution_count),
            created_at=db_skill.created_at,
            updated_at=db_skill.updated_at,
        ))
    return skills

@router.post("/", response_model=Skill)
def register_skill(manifest: SkillManifest, db: Session = Depends(get_db)):
    """Register a new skill."""
    service = SkillService(db)
    return service.register_skill(manifest)
