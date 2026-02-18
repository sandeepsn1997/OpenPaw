# OpenPaw AI Agent Instructions for Coding Agents

## Quick Context
OpenPaw is a production-ready AI Agent platform with a FastAPI backend and Angular frontend. It integrates Groq LLM for inference, uses FAISS for vector search/RAG, and persists data with SQLite.

**Key Tech Stack:**
- Backend: FastAPI, SQLAlchemy, Groq API
- Frontend: Angular 17+, TypeScript
- Storage: SQLite (data), FAISS (vectors), Markdown (knowledge)

---

## Architecture Overview

### Data Flow: Message → Agent → Response
```
User Chat (Frontend)
    ↓
POST /api/chat (FastAPI router)
    ↓
ConversationService (stores message)
    ↓
SimpleAgent.run() (logic/LLM decision)
    ↓
Result + metadata back through SQLAlchemy DB
    ↓
ChatResponse model → Frontend
```

### Core Components
- **[backend/app/main.py](backend/app/main.py)** - FastAPI app initialization, middleware, exception handlers
- **[backend/app/routes/chat.py](backend/app/routes/chat.py)** - Chat endpoints (`POST /api/chat`, `GET /conversations/{id}`)
- **[backend/app/agent.py](backend/app/agent.py)** - `SimpleAgent` class with `run()` method (placeholder for LLM integration)
- **[backend/app/services/](backend/app/services/)** - `AgentService`, `ConversationService` (business logic)
- **[backend/app/core/llm.py](backend/app/core/llm.py)** - `GroqLLM` wrapper (official Groq SDK)
- **[backend/app/database.py](backend/app/database.py)** - SQLAlchemy models (`AgentDB`, `ConversationDB`, `MessageDB`, etc.)

### Database Schema Pattern
All models use `id` (String, PK), `created_at`, `updated_at`. Messages stored as JSON in conversations for flexibility.

---

## Critical Developer Workflows

### Starting the App
```bash
# Backend (Terminal 1)
set GROQ_API_KEY=your-key  # Windows
cd backend
uvicorn app.main:app --reload

# Frontend (Terminal 2)
cd frontend
npm install  # first time only
npm start
```
**Access:** http://localhost:4200 (frontend), http://localhost:8000/docs (API docs)

### Running Tests
```powershell
# PowerShell (Windows)
.\test.ps1          # Full test suite
python test_api.py  # Python test client
```

---

## Project-Specific Patterns

### 1. Response Models (`app/models.py` and `app/schemas.py`)
- Use **Pydantic** for request/response validation
- `ChatRequest` expects `message`, optional `conversation_id`, optional `agent_id`
- Always return `ChatResponse` with `conversation_id`, `message`, `reply`
- **Key pattern:** Separate `models.py` (API contracts) from `schemas.py` (domain/business models)

### 2. Service Layer (e.g., `app/services/conversation.py`)
- Services receive `db: Session` as dependency
- Use repository pattern: query DB, map to domain models, return business objects
- Example: `ConversationService.add_message()` returns `ConversationMessage` (Pydantic), not raw DB object

### 3. Exception Handling (`app/exceptions.py`)
- Define custom exceptions: `APIException`, `AgentException`
- Use `general_exception_handler` and `api_exception_handler` registered in `main.py`
- FastAPI auto-converts HTTPException to 4xx responses

### 4. Configuration (`app/config.py`)
- **Single source of truth:** `Settings` class with Pydantic BaseSettings
- Auto-loads from `.env` file and environment variables
- Example: `GROQ_API_KEY` from env, `CORS_ORIGINS` with sensible defaults

### 5. LLM Integration (`app/core/llm.py`)
- `GroqLLM` class wraps official Groq SDK
- Constructor takes `api_key` (or reads `GROQ_API_KEY` env var)
- **API Ref:** https://console.groq.com/docs/overview
- Available models: `mixtral-8x7b-32768`, `llama2-70b-4096`, `gemma-7b-it`

### 6. Agent as Orchestrator (`app/agent.py`)
- `SimpleAgent.run(user_message)` returns `(response_str, tool_used_str)`
- Currently hardcoded demo logic (time, echo commands)
- **Design principle:** LLM decides *what*, skills execute *how*
- Future: Route to skill plugins based on LLM decision

### 7. CORS Configuration
- Currently allows all origins (`["*"]`) for dev convenience
- Change `app.config.py:cors_origins` before production

---

## Integration Points & Dependencies

### External: Groq API
- Free tier at https://console.groq.com
- Requires `GROQ_API_KEY` environment variable
- Rate limits: Check console for current limits

### Internal: Database Dependency Injection
- All routes use `db: Session = Depends(get_db)` from FastAPI
- Defined in [backend/app/db.py](backend/app/db.py)
- Auto-commits, session closes after request

### Frontend-Backend Contract
- Frontend expects JSON responses at `/api/chat`
- Conversation history cached client-side in Angular signals
- WebSocket support planned (not yet implemented)

---

## Adding Features: Common Tasks

### Add a New Chat Endpoint
1. Add route handler in [backend/app/routes/chat.py](backend/app/routes/chat.py)
2. Create request/response models in [backend/app/models.py](backend/app/models.py)
3. Inject `db: Session = Depends(get_db)` for database access
4. Use `ConversationService` or `AgentService` for business logic
5. Catch exceptions, return proper HTTP status

### Extend Agent Logic
1. Modify `SimpleAgent.run()` in [backend/app/agent.py](backend/app/agent.py)
2. For LLM calls, use `GroqLLM` from [backend/app/core/llm.py](backend/app/core/llm.py)
3. For persistent knowledge, use `MarkdownMemory` in [backend/app/memory/](backend/app/memory/)
4. Log execution with timestamps in conversation history

### Add a Database Model
1. Create SQLAlchemy class in [backend/app/database.py](backend/app/database.py)
2. Use consistent columns: `id`, `created_at`, `updated_at`
3. Create corresponding Pydantic schema in [backend/app/schemas.py](backend/app/schemas.py)
4. Wire into service layer (e.g., `ConversationService`)

---

## Code Quality & Testing

- **Type hints:** All functions must have type hints (enforce with Pylance)
- **Docstrings:** Use triple-quoted summaries for public methods
- **Async:** FastAPI supports async endpoints; use `async def` if I/O-bound
- **Testing:** Use `pytest` + `httpx` client (see [backend/app/routes/chat.py](backend/app/routes/chat.py) for examples)

---

## File Organization Rules

- **backend/app/core/**: Reusable infrastructure (LLM, skills, context)
- **backend/app/services/**: Business logic orchestrators
- **backend/app/routes/**: HTTP handlers (thin layer)
- **backend/app/memory/**: Knowledge and logs (markdown-first)
- **backend/app/models.py**: Pydantic request/response schemas
- **backend/app/schemas.py**: Domain/business object schemas
- **frontend/src/**: Angular components (see frontend README)

---

## When in Doubt

- Check existing patterns in [backend/app/routes/chat.py](backend/app/routes/chat.py) and [backend/app/services/](backend/app/services/)
- FastAPI docs: http://localhost:8000/docs (auto-generated from code)
- Architecture details: [docs/architecture.md](docs/architecture.md)
- Use Groq API reference: https://console.groq.com/docs/overview
