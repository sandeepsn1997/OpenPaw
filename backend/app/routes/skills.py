from pathlib import Path
from typing import Any, Dict, List
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..services.agent import SkillService
from ..schemas import Skill, SkillManifest, SkillStatus

router = APIRouter()


@router.get("/", response_model=List[Skill])
@router.get("", response_model=List[Skill])
def list_skills(db: Session = Depends(get_db)):
    """List all registered skills."""
    from ..database import SkillDB

    db_skills = db.query(SkillDB).all()
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


@router.post("/register", response_model=Skill)
def register_skill(manifest: SkillManifest, db: Session = Depends(get_db)):
    """Register a new skill."""
    service = SkillService(db)
    return service.register_skill(manifest)


@router.get("/{skill_id}", response_model=Skill)
def get_skill(skill_id: str, db: Session = Depends(get_db)):
    """Get single skill by ID."""
    service = SkillService(db)
    skill = service.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@router.delete("/{skill_id}", response_model=Dict[str, Any])
def delete_skill(skill_id: str, db: Session = Depends(get_db)):
    """Delete skill by ID."""
    service = SkillService(db)
    if not service.delete_skill(skill_id):
        raise HTTPException(status_code=404, detail="Skill not found")
    return {"message": "Skill deleted successfully"}


@router.get("/{skill_id}/settings", response_model=Dict[str, Any])
def get_skill_settings(skill_id: str):
    """Load optional per-skill UI settings config."""
    # Look in the internal backend/app/skills directory
    skill_dir = Path(__file__).resolve().parents[1] / "skills" / skill_id
    
    # Check for dedicated settings.json first
    settings_file = skill_dir / "settings.json"
    if settings_file.exists():
        with open(settings_file, "r", encoding="utf-8") as fh:
            return json.load(fh)
            
    # Fallback: check skill.json for 'extra_settings'
    manifest_file = skill_dir / "skill.json"
    if manifest_file.exists():
        with open(manifest_file, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            if "extra_settings" in data:
                return data["extra_settings"]
                
    raise HTTPException(status_code=404, detail="settings.json not found for skill")
