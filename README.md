# OpenPaw - AI Agent Platform

A **complete, production-ready** AI Agent platform with FastAPI backend and Angular frontend.

## 🚀 Features

✨ **Real-time Chat** - WebSocket-ready chat interface
🤖 **Groq LLM** - Powered by Groq's fastest inference
🧠 **Vector Search** - FAISS-based semantic search & RAG
💾 **Persistent Memory** - Markdown-based knowledge storage
🔌 **Modular Skills** - Plugin architecture for extensibility
📊 **REST API** - Full automatic documentation
🎨 **Modern UI** - Angular 17+ with responsive design

## ⚡ Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Groq API Key (free: https://console.groq.com)

### 1-Minute Setup

```bash
# Install backend
pip install -r requirements.txt

# Set Groq API key
export GROQ_API_KEY="your-key"  # Linux/Mac
set GROQ_API_KEY=your-key       # Windows

# Terminal 1: Start backend
cd backend
uvicorn app.main:app --reload

# Terminal 2: Start frontend
cd frontend
npm install
npm start
```

**Open:** http://localhost:4200

**API Docs:** http://localhost:8000/docs

## 📁 Architecture

```
OpenPaw/
├── backend/app/
│   ├── core/              # Agent logic (LLM, skills, context)
│   ├── services/          # Conversation, agent, vector DB
│   ├── memory/            # Markdown storage, knowledge base
│   ├── routes/            # API endpoints
│   ├── config.py          # Settings
│   ├── database.py        # ORM models
│   └── main.py            # FastAPI app
├── frontend/src/
│   ├── main.ts           # Angular component
│   ├── app.component.html # Chat UI
│   └── styles.css        # Styling
└── docs/                 # Documentation
```

## 🔌 API Endpoints

```
POST   /api/chat                      Send message
GET    /api/chat/conversations/{id}   Get history
POST   /api/chat/conversations        Create conversation
GET    /api/health                    Health check
```

## 🛠️ Tech Stack

**Backend:**
- FastAPI - Web framework
- SQLAlchemy - ORM
- Groq - LLM API
- FAISS - Vector search
- sentence-transformers - Embeddings

**Frontend:**
- Angular 17+ - Framework
- TypeScript - Language
- Signals - State management

**Database:**
- SQLite - Data storage
- FAISS - Vector store

## 📚 Documentation

- `QUICKSTART.md` - Setup guide
- `IMPLEMENTATION_COMPLETE.md` - What's included
- `docs/architecture.md` - System design
- `docs/plan.md` - Development plan

## 🎯 What's Included

✅ 16 completed tasks
✅ Full backend implementation
✅ Modern frontend UI
✅ Database with ORM
✅ Vector search for RAG
✅ Markdown memory system
✅ Error handling
✅ Production-ready
✅ API documentation
✅ Responsive design

## 🚀 Next Steps

1. See `QUICKSTART.md` for detailed setup
2. Check `docs/architecture.md` for system design
3. Explore API at http://localhost:8000/docs
4. Start building with the API

## 📝 Configuration

Create `.env` (optional):
```
GROQ_API_KEY=your-api-key
DATABASE_URL=sqlite:///./openpaw.db
DEBUG=false
```

## ❓ Troubleshooting

**No API key?**
```bash
export GROQ_API_KEY="your-key"
```

**Port in use?**
```bash
uvicorn app.main:app --port 8001
npm start -- --port 4201
```

**Issues?** Check `QUICKSTART.md`

---

**Ready to chat with AI! 🚀**

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
