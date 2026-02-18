from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
import json
import re

from .config import settings
from .services import TaskService
from .skills import skill_manager


class SimpleAgent:
    """Agent for processing user messages with tool support.
    
    Uses SkillManager to discover and execute capabilities.
    """

    async def run(
        self, 
        user_message: str, 
        db=None,
        history: Optional[List[Dict[str, str]]] = None, 
        system_prompt: Optional[str] = None
    ) -> Tuple[str, Optional[str]]:
        """
        Process user message and return response.
        """
        normalized = user_message.lower().strip()

        # Hardcoded demo commands (pre-skill era) - still keeping them for fast response
        if "time" in normalized or "date" in normalized:
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            return f"Current time: {now}", "time"

        if normalized.startswith("echo "):
            return user_message[5:], "echo"

        from .core.llm import GroqLLM
        llm = GroqLLM(
            api_key=settings.groq_api_key,
            model=settings.llm_model,
        )

        # Build messages list
        messages = []
        sys_p = system_prompt or "You are a helpful AI assistant."
        messages.append({"role": "system", "content": sys_p})
        
        if history:
            messages.extend(history)
            
        messages.append({"role": "user", "content": user_message})

        # Get available tools from SkillManager
        tools = skill_manager.get_tool_definitions()
        
        # Initial LLM call with tools
        response_message = llm.chat_with_tools(messages, tools)
        
        # Check if the model wants to call a tool
        if response_message.tool_calls:
            messages.append(response_message)  # Add assistant's tool call to history
            
            tool_used_names = []
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                print(f"Agent calling tool: {function_name} with {function_args}")
                
                # Execute the skill
                tool_result = await skill_manager.execute_skill(function_name, function_args)
                tool_used_names.append(function_name)
                
                # Add tool result to messages
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": tool_result,
                })
            
            # Second LLM call to generate final response based on tool results
            final_reply = llm.chat(messages)
            return final_reply, ", ".join(tool_used_names)

        # No tool called, return normal reply
        return response_message.content, "groq"
