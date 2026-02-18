# Groq-Powered Modular AI Agent (Python)

## 1. Overview

This document defines the high-level architecture of a modular, extensible AI agent system built in Python, inspired by OpenClaw-style design principles.

The system is:

- **LLM-powered** using Groq
- **Markdown-driven** for persistent knowledge
- **Plugin-based** via structured skill modules
- **Cron-capable** for automation
- **Zero-core-modification extensible**

The agent is designed as an orchestration engine — not a monolithic AI script.

## 2. Core Design Principles

### 2.1 Markdown as Source of Truth

All long-term knowledge and logs are stored in .md files.

**Benefits:**
- Human readable
- Git versionable
- No database dependency (initial phase)
- Easy manual inspection and editing

### 2.2 Skills as Plugins

Each skill lives in its own directory with a fixed structure.

Adding a new skill requires:
- Creating a folder
- Following the defined structure
- No changes to the core system are required

### 2.3 LLM for Reasoning, Not Execution

The LLM decides what to do

Skills perform how to do it

This keeps execution deterministic and safe.

### 2.4 Strict Interface Contracts

Every skill must implement the same interface.

This guarantees:
- Predictable behavior
- Automatic loading
- Cron compatibility
- Clean scaling

## 3. High-Level Architecture
```
User Input / Cron
        ↓
     Agent Core
        ↓
   Context Builder
        ↓
    LLM Decision (Groq)
        ↓
  ┌───────────────┐
  │ Skill Needed? │
  └───────┬───────┘
          │
   No ────┘         Yes
                      ↓
               Skill Execution
                      ↓
               Result Returned
                      ↓
               Final LLM Output
                      ↓
                  Logging (.md)
```

## 4. Directory Structure

```
root/
│
├── core/
│   ├── agent.py
│   ├── llm.py
│   ├── skill_loader.py
│   ├── scheduler.py
│   ├── memory.py
│   └── context_builder.py
│
├── skills/
│   ├── example_skill/
│   │   ├── manifest.yaml
│   │   ├── skill.py
│   │   ├── prompt.md
│   │   └── schema.json
│   │
│   └── ...
│
├── memory/
│   ├── knowledge/
│   ├── tasks/
│   └── logs/
│
├── cron/
│   └── jobs.yaml
│
├── config/
│   └── agent.yaml
│
```

## 5. Core Components

### 5.1 Agent Core (agent.py)

The orchestrator.

**Responsibilities:**
- Accept input (CLI/API/WhatsApp/etc.)
- Load memory
- Load skills
- Ask LLM if a skill is needed
- Execute skill if required
- Send result back to LLM
- Log interaction

**Does NOT:**
- Contain business logic
- Implement skills
- Hardcode capabilities

### 5.2 LLM Layer (llm.py)

Abstraction over Groq API.

**Responsibilities:**
- Model selection
- Structured JSON output mode
- Prompt formatting
- Retry handling
- Rate limiting

**Exposed Interface:**
```python
generate(prompt: str) -> str
generate_structured(prompt: str, schema: dict) -> dict
```

The rest of the system must not depend on Groq-specific details.

### 5.3 Skill Loader (skill_loader.py)

Automatically loads skills at startup.

**Behavior:**
- Scan /skills directory
- Read each manifest.yaml
- Import skill.py
- Register skill in a central registry

**Registry Structure (Conceptual):**
```json
{
  "skill_name": {
    "instance": "Skill()",
    "description": "...",
    "schema": {...},
    "cron_capable": true
  }
}
```

When a new skill folder is added: → Agent gains new ability automatically.

### 5.4 Memory Engine (memory.py)

Handles all Markdown-based persistence.

**Directory Layout:**
```
memory/
 ├── knowledge/
 │   ├── system.md
 │   ├── user_profile.md
 │
 ├── tasks/
 │   └── active.md
 │
 └── logs/
     └── YYYY-MM-DD.md
```

**Responsibilities:**
- Load all .md knowledge files
- Inject into system prompt
- Append daily logs
- Store task results
- Persist cron executions
- No database required in phase 1

### 5.5 Context Builder (context_builder.py)

Builds the full LLM context.

**Includes:**
- System personality
- Knowledge markdown
- List of available skills
- Skill descriptions from prompt.md
- Required JSON output format

This ensures the LLM understands:
- What tools exist
- When to use them
- What structure to return

### 5.6 Scheduler (scheduler.py)

Provides cron job support.

**Cron Configuration (cron/jobs.yaml):**
```yaml
- name: daily_summary
  schedule: "0 9 * * *"
  skill: stock_analysis
  input:
    ticker: AAPL
```

**Behavior:**
- Load cron jobs
- Register scheduler
- On trigger:
  - Call skill directly
  - Log output
  - Optionally notify via another skill

Cron does not require LLM unless post-processing is needed.

## 6. Skill Architecture

Each skill must follow this strict structure:

```
skills/
 └── skill_name/
     ├── manifest.yaml
     ├── skill.py
     ├── prompt.md
     └── schema.json
```

### 6.1 manifest.yaml

Metadata only.

**Example:**
```yaml
name: whatsapp
description: Send and receive WhatsApp messages
triggers:
  - send whatsapp
  - message via whatsapp
cron_capable: true
input_schema: schema.json
```

### 6.2 skill.py

Must implement fixed interface:

```python
class Skill:
    def execute(self, context: dict, input_data: dict) -> dict:
        pass
```

No variation allowed.

### 6.3 prompt.md

Describes the skill to the LLM.

**Example content:**

This skill sends WhatsApp messages.

Required fields:
- phone_number
- message

Used during skill decision reasoning.

### 6.4 schema.json

Defines structured input expected from LLM.

**Example:**
```json
{
  "phone_number": "string",
  "message": "string"
}
```

LLM must return structured JSON matching this schema.

## 7. Skill Invocation Flow

**Step 1: Input Received**
User input arrives via CLI/API/integration.

**Step 2: Context Built**
System gathers:
- Markdown knowledge
- Available skills
- Skill descriptions
- Structured output requirements

**Step 3: LLM Decision**
Groq returns:
```json
{
  "use_skill": true,
  "skill_name": "whatsapp",
  "arguments": {
    "phone_number": "...",
    "message": "..."
  }
}
```

**Step 4: Execution**
If use_skill == true:
- Skill is executed
- Result captured

**Step 5: Final Response**
- Result is sent back to LLM for formatting
- Response returned to user
- Logs appended

## 8. Execution Modes

### 8.1 Interactive Mode

User → Agent → LLM → Skill → Response

### 8.2 Autonomous Mode

Cron → Skill → Log → Optional LLM formatting

## 9. Extensibility Strategy

### 9.1 Add New Skill

- Create folder in /skills
- Follow required structure
- Restart agent (or enable hot reload)
- No core modification required

### 9.2 Future Enhancements

- Vector-based memory retrieval
- Skill dependency graph
- Skill permission sandboxing
- Multi-agent orchestration
- Remote skill execution
- Skill marketplace
- Hot reloading
- Self-modifying markdown knowledge

## 10. Security Model (High-Level)

- Skills execute deterministic code
- LLM cannot execute arbitrary Python
- Skill interface strictly validated
- JSON schema enforced before execution
- Cron jobs only call registered skills

## 11. Scalability Path

### Phase 1

- Single agent
- Local filesystem memory
- Simple cron

### Phase 2

- Multi-agent coordination
- Vector memory
- Web UI

### Phase 3

- Distributed skill execution
- Marketplace
- Cloud deployment
- Skill versioning

## 12. Summary

This architecture provides:

- Modular plugin system
- Groq-powered reasoning
- Markdown-based persistent knowledge
- Deterministic skill execution
- Cron automation
- Zero-core-modification extensibility
- Clean separation of reasoning and execution

The system is intentionally minimal at the core and infinitely extensible at the edges.