from typing import Any, Dict, Optional, Callable
from ..schemas import SkillManifest, SkillInputSchema

class BaseSkill:
    """Base class for all agent skills."""

    def __init__(self, manifest: SkillManifest, run_func: Callable):
        self._manifest = manifest
        self._run_func = run_func

    @property
    def manifest(self) -> SkillManifest:
        return self._manifest

    async def run(self, **kwargs) -> Any:
        # Check if it's an async function
        import inspect
        if inspect.iscoroutinefunction(self._run_func):
            return await self._run_func(**kwargs)
        else:
            return self._run_func(**kwargs)

    def to_tool_definition(self) -> Dict[str, Any]:
        """Convert skill manifest to Groq/OpenAI tool format."""
        manifest = self.manifest
        tool = {
            "type": "function",
            "function": {
                "name": manifest.name,
                "description": manifest.description,
            }
        }
        if manifest.input_schema:
            tool["function"]["parameters"] = {
                "type": "object",
                "properties": manifest.input_schema.properties,
                "required": manifest.input_schema.required,
            }
        return tool
