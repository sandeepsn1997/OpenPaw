from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
import json
import re

from .config import settings
from .services import TaskService


class SimpleAgent:
    """Minimal agent for processing user messages.
    
    Supports basic commands and LLM-powered task creation.
    """

    def run(
        self, 
        user_message: str, 
        db=None,
        history: Optional[List[Dict[str, str]]] = None, 
        system_prompt: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Process user message and return response.
        
        Args:
            user_message: User input message
            db: Optional database session
            history: Optional list of past messages in the conversation
            system_prompt: Optional custom system prompt
            
        Returns:
            Tuple of (response_text, tool_used_name)
        """
        normalized = user_message.lower().strip()

        # Demo: Show current time
        if "time" in normalized or "date" in normalized:
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            return f"Current time: {now}", "time"

        # Demo: Echo command
        if normalized.startswith("echo "):
            return user_message[5:], "echo"

        # Check for task creation intent
        task_keywords = ["add task", "create task", "new task", "todo", "remind me to", "i need to", "task:"]
        is_task_intent = any(kw in normalized for kw in task_keywords) or normalized.startswith("task ")

        from .core.llm import GroqLLM
        llm = GroqLLM(
            api_key=settings.groq_api_key,
            model=settings.llm_model,
            temperature=0.1 if is_task_intent else settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )

        if is_task_intent and db:
            # specialized prompt to extract task details
            extract_prompt = (
                f"The user wants to create a task: \"{user_message}\"\n\n"
                "Extract the following details in JSON format:\n"
                "- title: short summary of the task\n"
                "- description: any additional details\n"
                "- task_type: 'one_time', 'daily', or 'monthly'\n"
                "- scheduled_time: HH:MM format if mentioned, else null\n"
                "- scheduled_date: YYYY-MM-DD format if mentioned, else null\n"
                "- recurrence: 'one_time', 'daily', or 'monthly'\n\n"
                "Respond ONLY with the JSON object."
            )
            
            try:
                task_data = llm.generate_structured(extract_prompt)
                if task_data and "title" in task_data:
                    task_service = TaskService(db)
                    task = task_service.create_task(
                        title=task_data.get("title"),
                        description=task_data.get("description"),
                        task_type=task_data.get("task_type", "one_time"),
                        scheduled_time=task_data.get("scheduled_time"),
                        scheduled_date=task_data.get("scheduled_date"),
                        recurrence=task_data.get("recurrence", "one_time")
                    )
                    return f"✅ Task added: **{task.title}**", "task_creation"
            except Exception as e:
                # Fallback to normal chat if extraction fails
                print(f"Task extraction failed: {e}")

        # Default: Route to Groq LLM
        # Build messages list starting with system prompt
        messages = []
        sys_p = system_prompt or "You are a helpful AI assistant."
        messages.append({"role": "system", "content": sys_p})
        
        if history:
            messages.extend(history)
            
        messages.append({"role": "user", "content": user_message})
        
        reply = llm.chat(messages)
        return reply, "groq"
