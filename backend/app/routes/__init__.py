"""API routers."""

from .chat import router as chat_router
from .skills import router as skills_router
from .knowledge import router as knowledge_router
from .tasks import router as tasks_router
from .dashboard import router as dashboard_router

__all__ = [
    "chat_router",
    "skills_router",
    "knowledge_router",
    "tasks_router",
    "dashboard_router"
]
