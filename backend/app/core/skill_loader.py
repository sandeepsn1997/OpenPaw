"""Skill loader for discovering and registering skills."""

import importlib.util
import json
from pathlib import Path
from typing import Dict, List, Optional

from ..schemas import Skill, SkillManifest, SkillStatus


class SkillLoader:
    """Load and register skills from directory."""

    def __init__(self, skills_dir: Optional[Path] = None):
        """
        Initialize skill loader.
        
        Args:
            skills_dir: Directory containing skills (default: ./skills)
        """
        self.skills_dir = skills_dir or Path("./skills")
        self.skills: Dict[str, Skill] = {}

    def load_all_skills(self) -> Dict[str, Skill]:
        """Load all skills from directory."""
        if not self.skills_dir.exists():
            self.skills_dir.mkdir(parents=True, exist_ok=True)
            return {}

        skills_found = 0
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith("_"):
                skill = self._load_skill(skill_dir)
                if skill:
                    self.skills[skill.id] = skill
                    skills_found += 1

        print(f"Loaded {skills_found} skills from {self.skills_dir}")
        return self.skills

    def _load_skill(self, skill_dir: Path) -> Optional[Skill]:
        """Load a single skill from directory."""
        manifest_path = skill_dir / "manifest.yaml"
        
        if not manifest_path.exists():
            return None

        try:
            import yaml
            
            with open(manifest_path) as f:
                manifest_data = yaml.safe_load(f)
            
            # Parse input schema if exists
            schema_path = skill_dir / "schema.json"
            input_schema = None
            if schema_path.exists():
                with open(schema_path) as f:
                    schema_data = json.load(f)
                    input_schema = {
                        "properties": schema_data.get("properties", {}),
                        "required": schema_data.get("required", []),
                    }

            manifest = SkillManifest(
                name=manifest_data.get("name", skill_dir.name),
                description=manifest_data.get("description", ""),
                version=manifest_data.get("version", "1.0.0"),
                triggers=manifest_data.get("triggers", []),
                cron_capable=manifest_data.get("cron_capable", False),
                input_schema=input_schema,
            )

            skill = Skill(
                id=manifest.name,
                manifest=manifest,
                status=SkillStatus.ACTIVE,
            )

            return skill

        except Exception as e:
            print(f"Failed to load skill from {skill_dir}: {e}")
            return None

    def get_skill(self, skill_id: str) -> Optional[Skill]:
        """Get skill by ID."""
        return self.skills.get(skill_id)

    def list_skills(self) -> List[Skill]:
        """List all loaded skills."""
        return list(self.skills.values())

    def find_skills_by_trigger(self, trigger_phrase: str) -> List[Skill]:
        """Find skills matching trigger phrase."""
        matching_skills = []
        trigger_lower = trigger_phrase.lower()
        
        for skill in self.skills.values():
            for trigger in skill.manifest.triggers:
                if trigger_lower in trigger.lower():
                    matching_skills.append(skill)
                    break
        
        return matching_skills
