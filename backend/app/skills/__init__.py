import importlib
import pkgutil
from typing import Dict, List, Type
from .base import BaseSkill

class SkillManager:
    """Manager to discover and execute skills."""

    def __init__(self):
        self.skills: Dict[str, BaseSkill] = {}
        self.discover_skills()

    def discover_skills(self):
        """Automatically load all skills by searching for skill.json and main.py in subdirectories."""
        import os
        from pathlib import Path
        import json
        import importlib.util
        from ..schemas import SkillManifest, SkillInputSchema
        
        # Point to the local 'app/skills' directory
        root_dir = Path(__file__).resolve().parent
        
        if not root_dir.exists():
            print(f"Warning: Skills directory not found at {root_dir}")
            return

        for name in os.listdir(root_dir):
            skill_path = root_dir / name
            
            if skill_path.is_dir():
                manifest_file = skill_path / "skill.json"
                logic_file = skill_path / "main.py"
                
                if manifest_file.exists() and logic_file.exists():
                    try:
                        # Load manifest
                        with open(manifest_file, "r") as f:
                            data = json.load(f)
                        
                        # Handle input_schema if exists in JSON
                        input_schema = None
                        if "input_schema" in data:
                            input_schema = SkillInputSchema(**data["input_schema"])
                        
                        manifest = SkillManifest(
                            name=data["name"],
                            description=data["description"],
                            version=data.get("version", "1.0.0"),
                            input_schema=input_schema
                        )
                        
                        # Load logic from main.py
                        spec = importlib.util.spec_from_file_location(f"{name}.logic", str(logic_file))
                        if spec and spec.loader:
                            module = importlib.util.module_from_spec(spec)
                            # Add package context so inner imports work if needed
                            module.__package__ = f"app.skills.{name}"
                            spec.loader.exec_module(module)
                            
                            if hasattr(module, "run"):
                                skill_instance = BaseSkill(manifest, module.run)
                                self.skills[manifest.name] = skill_instance
                                print(f"Loaded skill from folder: {manifest.name}")
                            else:
                                print(f"Error: Skill folder '{name}' logic file has no 'run' function")
                            
                    except Exception as e:
                        print(f"Failed to load skill in {name}: {e}")

    def sync_with_db(self, db):
        """Sync discovered skills with the database."""
        from ..database import SkillDB
        from ..schemas import SkillStatus
        import json

        # Add or update existing skills
        for name, skill in self.skills.items():
            manifest = skill.manifest
            db_skill = db.query(SkillDB).filter(SkillDB.id == name).first()
            
            if not db_skill:
                db_skill = SkillDB(
                    id=name,
                    name=manifest.name,
                    description=manifest.description,
                    manifest=manifest.model_dump_json(),
                    status=SkillStatus.ACTIVE,
                )
                db.add(db_skill)
            else:
                # Update manifest and info
                db_skill.description = manifest.description
                db_skill.manifest = manifest.model_dump_json()
            
        # Remove skills from DB that are no longer in the filesystem
        all_db_skills = db.query(SkillDB).all()
        for db_skill in all_db_skills:
            if db_skill.id not in self.skills:
                db.delete(db_skill)

        db.commit()

    def get_tool_definitions(self) -> List[Dict]:
        """Return all skills as JSON tool definitions."""
        return [skill.to_tool_definition() for skill in self.skills.values()]

    async def execute_skill(self, name: str, arguments: Dict) -> str:
        """Call a skill by name with provided arguments."""
        if name not in self.skills:
            return f"Error: Skill '{name}' not found."
        
        try:
            return await self.skills[name].run(**arguments)
        except Exception as e:
            return f"Error executing skill '{name}': {str(e)}"

# Singleton instance
skill_manager = SkillManager()
