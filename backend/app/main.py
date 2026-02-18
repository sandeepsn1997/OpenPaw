from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .agent import SimpleAgent
from .models import AgentRequest, AgentResponse


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 404:
            return await super().get_response("index.html", scope)
        return response


app = FastAPI(title="OpenPaw Agent Server", version="0.1.0")
agent = SimpleAgent()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/agent", response_model=AgentResponse)
def ask_agent(payload: AgentRequest) -> AgentResponse:
    reply, tool = agent.run(payload.message)
    return AgentResponse(reply=reply, tool_used=tool)


def _frontend_dist_path() -> Path:
    return Path(__file__).resolve().parents[2] / "frontend" / "dist" / "openpaw" / "browser"


frontend_dist = _frontend_dist_path()
if frontend_dist.exists():
    app.mount("/", SPAStaticFiles(directory=frontend_dist, html=True), name="spa")
else:

    @app.get("/")
    def root_fallback() -> FileResponse | dict[str, str]:
        index = Path(__file__).resolve().parents[2] / "frontend" / "src" / "index.html"
        if index.exists():
            return FileResponse(index)
        return {"message": "Frontend not built yet. Run Angular build first."}
