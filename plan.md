# OpenPaw Dashboard — Implementation Plan

> **Goal:** Transform the current chat-only interface into a full AI Agent dashboard (inspired by OpenClaw), with a persistent side navigation and multiple feature pages.

---

## 📐 Side Menu Structure

| #  | Icon | Menu Item         | Description                                              | Backend Support     |
|----|------|-------------------|----------------------------------------------------------|---------------------|
| 1  | 📊  | **Dashboard**      | Overview — agent stats, recent activity, quick actions    | Health, DB stats    |
| 2  | 💬  | **Chat**           | Existing chat playground (current UI, enhanced)          | ✅ Already built     |
| 3  | 🤖  | **Agents**         | Create, configure, and manage AI agents                  | ✅ AgentService      |
| 4  | 🔌  | **Skills**         | Browse, register, and manage agent skills/plugins        | ✅ SkillService      |
| 5  | 🧠  | **Knowledge Base** | Upload docs, view indexed chunks, search memory          | ✅ KnowledgeBase     |
| 6  | 📝  | **Tasks**          | Kanban-style task board for agent work items              | ✅ TaskDB            |
| 7  | 📜  | **Conversations**  | Browse and review past conversation histories             | ✅ ConversationService |
| 8  | ⚙️  | **Settings**       | App config, API keys, model selection, preferences       | ✅ Config/Settings   |

---

## 🗂️ Phase-by-Phase Implementation (BACKEND)

### Phase 1 — Layout & Navigation Shell
- [ ] Create a responsive **side navigation** (collapsible sidebar)
- [ ] Add **Angular routing** with lazy-loaded pages
- [ ] Build the **app shell** (sidebar + header + content area)
- [ ] Move existing chat into the `/chat` route
- [ ] Add active-state highlighting and route transitions

### Phase 2 — Dashboard Page (`/dashboard`)
- [ ] **Stats cards** — Total conversations, active agents, skills count, knowledge entries
- [ ] **Recent activity feed** — Latest messages, agent actions
- [ ] **Quick actions** — New Chat, Create Agent, Upload Knowledge
- [ ] **System health** indicator (backend `/api/health`)

### Phase 3 — Chat Page (`/chat`) — Enhancement
- [ ] Migrate current chat UI into its own routed component
- [ ] Add **conversation sidebar** — list & switch between past conversations
- [ ] Add **model selector** dropdown for switching LLM models
- [ ] Add **markdown rendering** for agent responses
- [ ] Improve message bubbles with avatars and better timestamps

### Phase 4 — Agents Page (`/agents`)
- [ ] **Agent list** — cards/table showing all agents with status
- [ ] **Create agent** dialog — name, model, temperature, system prompt
- [ ] **Agent detail** view — config, assigned skills, state, history
- [ ] **Edit/delete** agent functionality

### Phase 5 — Skills Page (`/skills`)
- [ ] **Skills catalog** — grid/list of registered skills with status badges
- [ ] **Skill detail** — manifest info, triggers, input schema, execution count
- [ ] **Register skill** dialog — upload manifest, set triggers
- [ ] **Enable/disable** skill toggle

### Phase 6 — Knowledge Base Page (`/knowledge`)
- [ ] **Document list** — uploaded knowledge files with metadata
- [ ] **Upload document** — drag & drop or file picker for .md/.txt
- [ ] **Search** — semantic search across knowledge base
- [ ] **Document viewer** — preview content chunks
- [ ] **Delete/manage** documents

### Phase 7 — Tasks Page (`/tasks`)
- [ ] **Kanban board** — columns for Pending, In Progress, Completed, Failed
- [ ] **Create task** — title, description, assign to agent
- [ ] **Drag & drop** between statuses
- [ ] **Task detail** panel — description, progress notes, agent assignment

### Phase 8 — Conversations Page (`/conversations`)
- [ ] **Conversation list** — filterable table with agent, date, message count
- [ ] **Conversation viewer** — full message thread replay
- [ ] **Search** conversations by content
- [ ] **Delete** conversation

### Phase 9 — Settings Page (`/settings`)
- [ ] **API Configuration** — Groq API key input (masked), model selection
- [ ] **App Preferences** — theme toggle (dark/light), language
- [ ] **System Info** — version, database stats, vector store size
- [ ] **Danger Zone** — reset database, clear knowledge base

---

## 🎨 Design Guidelines

- **Dark theme** (current slate palette) as default
- **Glassmorphism** accents on cards and panels
- **Micro-animations** on navigation, cards, and page transitions
- **Responsive** — collapsible sidebar for mobile
- **Google Fonts** — Inter or Outfit for modern typography
- **Color palette** — Slate base (`#0f172a`), Teal accents (`#14b8a6`), Sky blue highlights (`#38bdf8`)

---

## 🔄 Implementation Order

> Build the **BACKEND**, one page at a time. Backend API endpoints will be added/extended as needed per phase.

1. **Phase 1** — Layout & Navigation Shell ← _Start here_
2. **Phase 2** — Dashboard
3. **Phase 3** — Chat Enhancement
4. **Phase 4** — Agents
5. **Phase 5** — Skills
6. **Phase 6** — Knowledge Base
7. **Phase 7** — Tasks
8. **Phase 8** — Conversations
9. **Phase 9** — Settings