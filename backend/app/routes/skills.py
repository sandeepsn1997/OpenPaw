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
    # Strip and lowercase to be robust against frontend inconsistencies
    skill_id = skill_id.strip().lower()
    
    # Robust path resolution
    current_dir = Path(__file__).resolve().parent
    skill_dir = current_dir.parent / "skills" / skill_id
    
    settings_file = skill_dir / "settings.json"
    manifest_file = skill_dir / "skill.json"
    
    print(f"[SkillsAPI] Loading settings for skill_id='{skill_id}'")
    print(f"[SkillsAPI] Path: {settings_file}")

    # Check for dedicated settings.json first
    if settings_file.exists():
        try:
            with open(settings_file, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception as e:
            print(f"[SkillsAPI] Error reading settings.json: {e}")
            raise HTTPException(status_code=500, detail=f"Error reading settings.json: {e}")
            
    # Fallback: check skill.json for 'extra_settings'
    if manifest_file.exists():
        try:
            with open(manifest_file, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if "extra_settings" in data:
                    return data["extra_settings"]
        except Exception as e:
            print(f"[SkillsAPI] Error reading skill.json: {e}")

    print(f"[SkillsAPI] No settings found for '{skill_id}'")
    raise HTTPException(status_code=404, detail=f"settings.json not found for skill '{skill_id}'")
