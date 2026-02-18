"""Context builder for LLM prompts."""

from datetime import datetime
from typing import List, Optional

from ..schemas import Agent, Skill, ConversationHistory


class ContextBuilder:
    """Build context for LLM prompts."""

    def __init__(self, agent: Agent, conversation: ConversationHistory):
        """
        Initialize context builder.
        
        Args:
            agent: Agent instance
            conversation: Conversation history
        """
        self.agent = agent
        self.conversation = conversation

    def build_system_prompt(self) -> str:
        """Build system prompt."""
        return f"""{self.agent.config.system_prompt}

You are {self.agent.name}, an AI agent powered by Groq's fast language models.
Current time: {datetime.now().isoformat()}

Instructions:
1. Be helpful, harmless, and honest
2. Provide clear and concise responses
3. If you need to use a tool/skill, indicate it clearly
4. Always maintain context from the conversation history
"""

    def build_user_context(self, user_message: str, retrieved_docs: Optional[List[str]] = None) -> str:
        """
        Build context for user message.
        
        Args:
            user_message: Current user message
            retrieved_docs: Optional retrieved documents for RAG
        """
        context_parts = []

        # Add conversation history
        recent_messages = self.conversation.get_messages_for_context(limit=5)
        if recent_messages:
            context_parts.append("## Recent conversation:")
            for msg in recent_messages:
                role = msg["role"].upper()
                content = msg["content"][:200]  # Truncate long messages
                context_parts.append(f"{role}: {content}")

        # Add retrieved documents if available
        if retrieved_docs:
            context_parts.append("\n## Retrieved knowledge:")
            for doc in retrieved_docs[:3]:  # Limit to top 3
                context_parts.append(f"- {doc[:300]}")

        # Add current message
        context_parts.append(f"\n## Current message:\nUSER: {user_message}")

        return "\n".join(context_parts)

    def build_skills_context(self, skills: List[Skill]) -> str:
        """Build context about available skills."""
        if not skills:
            return "No skills available."

        context_parts = ["## Available Skills:"]

        for skill in skills:
            context_parts.append(
                f"\n### {skill.manifest.name}\n"
                f"Description: {skill.manifest.description}\n"
                f"Triggers: {', '.join(skill.manifest.triggers)}"
            )

            if skill.manifest.input_schema:
                props = skill.manifest.input_schema.get("properties", {})
                required = skill.manifest.input_schema.get("required", [])
                context_parts.append(f"Required inputs: {', '.join(required)}")

        return "\n".join(context_parts)

    def build_full_prompt(
        self,
        user_message: str,
        skills: Optional[List[Skill]] = None,
        retrieved_docs: Optional[List[str]] = None,
    ) -> str:
        """Build complete prompt for LLM."""
        prompt_parts = [
            self.build_system_prompt(),
            self.build_user_context(user_message, retrieved_docs),
        ]

        if skills:
            prompt_parts.append(self.build_skills_context(skills))

        prompt_parts.append(
            "\nRespond with a JSON object containing:\n"
            '{"response": "your response", "use_skill": false/true, "skill_name": "..."}'
        )

        return "\n".join(prompt_parts)
