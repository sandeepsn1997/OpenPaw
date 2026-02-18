from pathlib import Path
from typing import Union
import warnings
import sys

# Suppress Pydantic protected namespace warnings for internal models
warnings.filterwarnings("ignore", category=UserWarning)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .agent import SimpleAgent
from .config import settings
from .db import init_db
from .exceptions import APIException, general_exception_handler, api_exception_handler
from .routes import (
    chat_router,
    skills_router,
    knowledge_router,
    tasks_router,
    dashboard_router
)


class SPAStaticFiles(StaticFiles):
    """Serve SPA with fallback to index.html."""

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 404:
            return await super().get_response("index.html", scope)
        return response


# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    debug=settings.debug,
)

# Initialize database
init_db()

# Initialize agent
agent = SimpleAgent()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Add exception handlers
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(chat_router, prefix=f"{settings.api_prefix}/chat")
app.include_router(skills_router, prefix=f"{settings.api_prefix}/skills")
app.include_router(knowledge_router, prefix=f"{settings.api_prefix}/knowledge")
app.include_router(tasks_router, prefix=f"{settings.api_prefix}/tasks")
app.include_router(dashboard_router, prefix=f"{settings.api_prefix}/dashboard")


@app.get(f"{settings.api_prefix}/health")
def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": settings.app_name}


def _frontend_dist_path() -> Path:
    return Path(__file__).resolve().parents[2] / "frontend" / "dist" / "openpaw" / "browser"


frontend_dist = _frontend_dist_path()
if frontend_dist.exists():
    app.mount("/", SPAStaticFiles(directory=frontend_dist, html=True), name="spa")
else:

    @app.get("/", response_model=None)
    def root_fallback() -> Union[FileResponse, dict]:
        index = Path(__file__).resolve().parents[2] / "frontend" / "src" / "index.html"
        if index.exists():
            return FileResponse(index)
        return {"message": "Frontend not built yet. Run Angular build first."}
