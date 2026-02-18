# OpenPaw

Starter project for an AI agent platform with:
- **FastAPI backend** (agent API)
- **Angular frontend dashboard/control panel**
- Both served from the **same server process** in production

## Architecture

- `backend/app/main.py` exposes:
  - `POST /api/agent` — send message to agent
  - `GET /api/health` — health check
- Angular app lives in `frontend/`.
- In production, build Angular and FastAPI serves `frontend/dist/openpaw/browser`.

## Quickstart

### 1) Backend setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2) Frontend setup

```bash
cd frontend
npm install
npm run build
cd ..
```

### 3) Run one server for API + dashboard

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Open: `http://localhost:8000`

## Development mode

Run Angular and FastAPI separately while developing:

```bash
# Terminal 1
uvicorn backend.app.main:app --reload

# Terminal 2
cd frontend
npm start
```

Then call backend endpoints from Angular (via relative `/api/...` in this starter).

## Tests

```bash
PYTHONPATH=backend pytest -q
```

## Next steps for a real AI agent

- Swap `SimpleAgent` with an LLM provider client (OpenAI, local model, etc.)
- Add tool integrations (DB, search, task execution)
- Add auth and role-based access for dashboard control
- Persist conversations in PostgreSQL/Redis
