"""Skill execution engine."""

import json
from typing import Any, Dict, Optional

from ..schemas import Skill


class SkillExecutor:
    """Execute skills."""

    def __init__(self):
        """Initialize skill executor."""
        self.executed_skills = {}

    def execute(
        self,
        skill: Skill,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a skill.
        
        Args:
            skill: Skill to execute
            arguments: Arguments for skill
        
        Returns:
            Execution result
        """
        try:
            # Validate arguments against schema if present
            if skill.manifest.input_schema:
                self._validate_arguments(arguments, skill.manifest.input_schema)

            # Simulate skill execution
            result = self._simulate_skill_execution(skill, arguments)

            # Track execution
            self.executed_skills[skill.id] = self.executed_skills.get(skill.id, 0) + 1

            return {
                "success": True,
                "skill_id": skill.id,
                "result": result,
                "executed_count": self.executed_skills[skill.id],
            }

        except Exception as e:
            return {
                "success": False,
                "skill_id": skill.id,
                "error": str(e),
            }

    def _validate_arguments(self, arguments: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Validate arguments against schema."""
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # Check required fields
        for field in required:
            if field not in arguments:
                raise ValueError(f"Missing required argument: {field}")

        # Basic type checking
        for field, value in arguments.items():
            if field in properties:
                prop_schema = properties[field]
                expected_type = prop_schema.get("type", "string")

                if expected_type == "string" and not isinstance(value, str):
                    raise ValueError(f"Argument {field} must be string")
                elif expected_type == "number" and not isinstance(value, (int, float)):
                    raise ValueError(f"Argument {field} must be number")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    raise ValueError(f"Argument {field} must be boolean")

    def _simulate_skill_execution(
        self,
        skill: Skill,
        arguments: Dict[str, Any],
    ) -> str:
        """Simulate skill execution (placeholder)."""
        # In real implementation, this would call the actual skill
        return f"Executed skill '{skill.manifest.name}' with args: {json.dumps(arguments)}"

    def can_execute(self, skill: Skill, arguments: Dict[str, Any]) -> bool:
        """Check if skill can be executed."""
        try:
            if skill.manifest.input_schema:
                self._validate_arguments(arguments, skill.manifest.input_schema)
            return True
        except Exception:
            return False
