# OpenPaw Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Groq API Key (free from https://console.groq.com)

## Installation & Setup

### 1. Clone Repository
```bash
git clone <repo-url>
cd OpenPaw
```

### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (choose based on OS)
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set Groq API key (choose based on OS)
export GROQ_API_KEY="your-api-key-here"  # Linux/Mac
# OR
set GROQ_API_KEY=your-api-key-here  # Windows PowerShell

# Run backend
cd backend
uvicorn app.main:app --reload
```

Backend runs on: http://localhost:8000

### 3. Frontend Setup (New Terminal)

```bash
cd frontend
npm install
npm start
```

Frontend runs on: http://localhost:4200

### 4. Access the Application

- **Chat Interface:** http://localhost:4200
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/api/health

## Usage

### Sending Messages

1. Type your message in the chat input
2. Press `Ctrl+Enter` or click Send
3. Agent processes and responds
4. Messages appear with timestamps

### Managing Conversations

- **New Chat:** Click "➕ New Chat" to start fresh conversation
- **History:** Click "📋 History" for conversation list (coming soon)

## Project Structure

```
OpenPaw/
├── backend/
│   └── app/
│       ├── core/               # Agent logic
│       ├── services/           # Business services
│       ├── memory/             # Knowledge & memory
│       ├── routes/             # API endpoints
│       ├── config.py           # Configuration
│       ├── database.py         # ORM models
│       ├── exceptions.py       # Error handling
│       └── main.py             # App entry
├── frontend/
│   └── src/                    # Angular app
├── docs/                       # Documentation
└── requirements.txt            # Python deps
```

## API Endpoints

### Chat Management
- `POST /api/chat` - Send message
  ```json
  {
    "conversation_id": "uuid",
    "agent_id": "default_agent",
    "message": "Hello agent!"
  }
  ```

- `GET /api/chat/conversations/{id}` - Get history
- `POST /api/chat/conversations` - Create conversation

### System
- `GET /api/health` - Health check

## Database

SQLite database automatically created on first run:
- File: `openpaw.db`
- Tables: agents, skills, memory, conversations, tasks
- Location: project root

## Vector Store (RAG)

FAISS vector store for semantic search:
- Location: `./data/faiss.index`
- Embeddings: sentence-transformers (all-MiniLM-L6-v2)
- Auto-indexed for knowledge retrieval

## Memory Storage

Markdown-based persistent storage:
- Knowledge: `./memory/knowledge/`
- Tasks: `./memory/tasks/`
- Logs: `./memory/logs/`

## Configuration

Create `.env` file (optional):
```env
GROQ_API_KEY=your-api-key
DATABASE_URL=sqlite:///./openpaw.db
DEBUG=false
API_PREFIX=/api
```

## Troubleshooting

### GROQ_API_KEY not set
```bash
export GROQ_API_KEY="your-key"
```

### Port 8000 already in use
```bash
uvicorn app.main:app --port 8001 --reload
```

### Port 4200 already in use
```bash
npm start -- --port 4201
```

### Database locked
Delete `openpaw.db` and restart

### Module not found errors
```bash
pip install -r requirements.txt --upgrade
```
