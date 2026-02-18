"""Persistent memory service."""

import os
from pathlib import Path
from typing import Dict, Optional, List
import json

from ..config import settings
from ..core.llm import GroqLLM

class PersistentMemoryService:
    """Service for managing persistent markdown memory files."""

    def __init__(self):
        """Initialize memory service."""
        # Use absolute path relative to this file's parent's parent
        self.base_path = Path(__file__).resolve().parent.parent / "persistent"
        self.files = ["soul.md", "user_info.md", "memory.md"]
        
        # Ensure directory exists
        self.base_path.mkdir(exist_ok=True)

    def get_all_memory(self) -> str:
        """Read all memory files and return combined text for the system prompt."""
        combined = []
        for filename in self.files:
            file_path = self.base_path / filename
            if file_path.exists():
                content = file_path.read_text(encoding="utf-8")
                combined.append(f"--- {filename.upper()} ---\n{content}")
            else:
                # Initialize if missing
                file_path.write_text(f"# {filename.replace('.md', '').replace('_', ' ').title()}\n", encoding="utf-8")
        
        return "\n\n".join(combined)

    def update_memory(self, filename: str, content: str):
        """Update a specific memory file."""
        if filename not in self.files:
            raise ValueError(f"Invalid memory file: {filename}")
            
        file_path = self.base_path / filename
        file_path.write_text(content, encoding="utf-8")

    def get_file_content(self, filename: str) -> str:
        """Get content of a single memory file."""
        file_path = self.base_path / filename
        if file_path.exists():
            return file_path.read_text(encoding="utf-8")
        return ""

    def analyze_and_update(self, user_message: str, agent_reply: str):
        """Analyze the latest interaction and update persistent memory if needed."""
        llm = GroqLLM(
            api_key=settings.groq_api_key,
            model=settings.llm_model,
        )

        current_memory = self.get_all_memory()
        
        prompt = f"""
        You are a memory management module for the OpenPaw agent.
        Your task is to identify if the current interaction contains NEW information that should be persisted in the following memory files:
        1. user_info.md (User's profile, preferences, goals, habits)
        2. memory.md (Project facts, milestones, cross-session context, durable knowledge)
        3. soul.md (Agent's personality changes, core values, behavioral shifts - RARE)

        CURRENT MEMORY CONTENT:
        {current_memory}

        LATEST INTERACTION:
        User: {user_message}
        Agent: {agent_reply}

        INSTRUCTIONS:
        1. If no NEW or CONTRADICTORY information is found, respond with "NO_UPDATE".
        2. If information should be updated, provide the ENTIRE NEW CONTENT for the specific file(s) that need changing.
        3. Format your response as a JSON object: {{"user_info.md": "full content...", "memory.md": "full content..."}}
        4. Keep the content simple and structured in Markdown.
        5. DO NOT update soul.md unless explicitly asked or a major shift occurred.

        RESPONSE:
        """

        try:
            update_data = llm.generate_structured(prompt)
            if isinstance(update_data, dict):
                for filename, content in update_data.items():
                    if filename in self.files and content and content != "NO_UPDATE":
                        self.update_memory(filename, content)
        except Exception as e:
            # Silent fail for memory updates to not break chat
            print(f"Memory update failed: {e}")
