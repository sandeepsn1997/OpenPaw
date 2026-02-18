"""Markdown-based memory system."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class MarkdownMemory:
    """Markdown-based memory storage."""

    def __init__(self, memory_dir: Path = Path("./memory")):
        """
        Initialize markdown memory.
        
        Args:
            memory_dir: Directory for memory storage
        """
        self.memory_dir = memory_dir
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.knowledge_dir = self.memory_dir / "knowledge"
        self.tasks_dir = self.memory_dir / "tasks"
        self.logs_dir = self.memory_dir / "logs"

        for directory in [self.knowledge_dir, self.tasks_dir, self.logs_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def add_knowledge(self, title: str, content: str, tags: List[str] = None) -> Path:
        """Add knowledge entry."""
        if tags is None:
            tags = []

        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{title.replace(' ', '_')}.md"
        filepath = self.knowledge_dir / filename

        markdown_content = f"""# {title}

**Created:** {datetime.now().isoformat()}
**Tags:** {', '.join(tags)}

## Content

{content}
"""

        filepath.write_text(markdown_content, encoding="utf-8")
        return filepath

    def get_knowledge(self) -> str:
        """Get all knowledge as formatted text."""
        content = "# Knowledge Base\n\n"

        for file in sorted(self.knowledge_dir.glob("*.md")):
            content += file.read_text(encoding="utf-8")
            content += "\n\n---\n\n"

        return content

    def add_task(self, title: str, description: str, status: str = "pending") -> Path:
        """Add task entry."""
        filename = f"{title.replace(' ', '_').lower()}.md"
        filepath = self.tasks_dir / filename

        markdown_content = f"""# Task: {title}

**Status:** {status}
**Created:** {datetime.now().isoformat()}

## Description

{description}

## Progress

- [ ] Subtask 1
- [ ] Subtask 2

## Notes

(Add notes as you work)
"""

        filepath.write_text(markdown_content, encoding="utf-8")
        return filepath

    def get_active_tasks(self) -> List[Dict[str, str]]:
        """Get all active tasks."""
        tasks = []

        for file in self.tasks_dir.glob("*.md"):
            content = file.read_text(encoding="utf-8")
            if "pending" in content or "in_progress" in content:
                tasks.append({
                    "title": file.stem,
                    "path": str(file),
                    "content": content,
                })

        return tasks

    def log_interaction(
        self,
        user_input: str,
        agent_output: str,
        tool_used: Optional[str] = None,
    ) -> Path:
        """Log conversation interaction."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filepath = self.logs_dir / f"{date_str}.md"

        timestamp = datetime.now().isoformat()
        interaction = f"""## {timestamp}

**User:** {user_input}

**Agent:** {agent_output}
"""

        if tool_used:
            interaction += f"\n**Tool Used:** {tool_used}\n"

        if filepath.exists():
            filepath.write_text(filepath.read_text(encoding="utf-8") + interaction + "\n")
        else:
            filepath.write_text(f"# Interaction Log - {date_str}\n\n{interaction}\n")

        return filepath

    def get_today_logs(self) -> str:
        """Get today's interaction logs."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        filepath = self.logs_dir / f"{date_str}.md"

        if filepath.exists():
            return filepath.read_text(encoding="utf-8")

        return f"# No interactions logged for {date_str}"

    def search_memory(self, query: str) -> List[Path]:
        """Search memory by query."""
        results = []

        for directory in [self.knowledge_dir, self.tasks_dir, self.logs_dir]:
            for file in directory.glob("*.md"):
                content = file.read_text(encoding="utf-8")
                if query.lower() in content.lower():
                    results.append(file)

        return results

    def get_memory_summary(self) -> str:
        """Get summary of all memory."""
        summary = "# Memory Summary\n\n"

        # Knowledge summary
        knowledge_files = list(self.knowledge_dir.glob("*.md"))
        summary += f"## Knowledge Base\n- Entries: {len(knowledge_files)}\n\n"

        # Tasks summary
        active_tasks = self.get_active_tasks()
        summary += f"## Tasks\n- Active: {len(active_tasks)}\n\n"

        # Logs summary
        log_files = list(self.logs_dir.glob("*.md"))
        summary += f"## Interaction Logs\n- Days logged: {len(log_files)}\n\n"

        return summary
