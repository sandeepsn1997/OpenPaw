"""Dynamic loader for skill-provided backend extensions."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import List, Optional

from fastapi import APIRouter


@dataclass
class SkillExtension:
    skill_id: str
    route_prefix: str
    router: APIRouter


def _load_module(path: Path) -> Optional[ModuleType]:
    spec = importlib.util.spec_from_file_location(f"skill_ext_{path.parent.name}", path)
    if not spec or not spec.loader:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_skill_extensions(skills_dir: Optional[Path] = None) -> List[SkillExtension]:
    root = skills_dir or Path("skills")
    if not root.exists():
        return []

    loaded: List[SkillExtension] = []
    for skill_dir in root.iterdir():
        if not skill_dir.is_dir() or skill_dir.name.startswith("_"):
            continue
        backend_path = skill_dir / "backend.py"
        if not backend_path.exists():
            continue

        module = _load_module(backend_path)
        if not module:
            continue

        router = getattr(module, "router", None)
        route_prefix = getattr(module, "route_prefix", f"/skills/{skill_dir.name}")
        if isinstance(router, APIRouter):
            loaded.append(
                SkillExtension(skill_id=skill_dir.name, route_prefix=route_prefix, router=router)
            )

    return loaded
