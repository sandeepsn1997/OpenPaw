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
        system_prompt: Optional[str] = None,
    ) -> Tuple[str, Optional[str]]:
        """Process user message and return response."""
        normalized = user_message.lower().strip()

        # Hardcoded demo commands (pre-skill era) - still keeping them for fast response
        # Only match "what time" or "what date" or "current time/date" to avoid matching "times"
        if normalized in ("what time is it", "what time", "what date is it", "current time", "current date"):
            now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            return f"Current time: {now}", "time"

        # Echo command - simple passthrough without LLM
        if normalized.startswith("echo "):
            return user_message[5:].strip(), "echo"

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
        
        # Initial LLM call with tools — handle Groq tool-call failures gracefully
        response_message = None
        tool_calls = None
        try:
            response_message = llm.chat_with_tools(messages, tools)
            tool_calls = getattr(response_message, "tool_calls", None)
        except Exception as e:
            # Groq can return a 400 with a failed_generation payload when it attempted to call a tool
            # Try to extract a tool call from the exception text and continue locally.
            err = str(e)
            
            # Check for email skill first before regex extraction
            if "email" in err.lower():
                from .skills.email.backend import GmailService
                try:
                    gmail_service = GmailService(db)
                    gmail_status = gmail_service.status()
                    if not gmail_status.get("connected"):
                        # Return friendly message for email connection
                        return "To manage your email, I need permission to connect to your Gmail account. Please go to Settings, select Email, and authorize me to access your mail. Once connected, I can help you read and send emails.", "email"
                except Exception:
                    pass

            # Use regex to extract tool call from error message
            matches = re.findall(r"<function=([A-Za-z0-9_\-]+)=?((?:.|\n)*?)</function>", err)
            
            for i, (fname, jstr) in enumerate(matches):
                raw = jstr.strip()
                
                # Remove leading = if present
                if raw.startswith("="):
                    raw = raw[1:].strip()

                # Unescape quotes
                raw = raw.replace('\"', '"').replace("\\'", "'")

                args_obj = {}
                parse_attempts = [raw]
                if "'" in raw and '"' not in raw:
                    parse_attempts.append(raw.replace("'", '"'))

                for attempt in parse_attempts:
                    try:
                        args_obj = json.loads(attempt)
                        break
                    except Exception:
                        try:
                            cleaned = re.sub(r",\s*}\s*$", "}", attempt)
                            args_obj = json.loads(cleaned)
                            break
                        except Exception:
                            pass

                # Build a minimal tool_call-like object
                tc = type("ToolCall", (), {})()
                tc.id = f"failed-{i}"
                fn = type("Function", (), {})()
                fn.name = fname
                fn.arguments = json.dumps(args_obj)
                tc.function = fn
                
                if not tool_calls:
                    tool_calls = []
                tool_calls.append(tc)

            if not tool_calls:
                # Could not extract tool call, return generic message
                return "I encountered an issue processing your request. Please try again.", None

        # If the model wants to call a tool, execute them locally
        if tool_calls:
            # For LLM context, create a proper assistant message
            assistant_message = {"role": "assistant", "content": "", "tool_calls": tool_calls}
            messages.append(assistant_message)

            tool_used_names = []
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                print(f"Agent calling tool: {function_name} with {function_args}")

                # Check if email skill is being called but Gmail is not connected
                if function_name == "email":
                    from .skills.email.backend import GmailService
                    gmail_service = GmailService(db)
                    gmail_status = gmail_service.status()
                    if not gmail_status.get("connected"):
                        # Return a friendly message telling user to connect email via settings
                        tool_result = "To access your emails, please authorize Gmail access through the Settings page. Click Settings > Email > Connect, then return to try again."
                        tool_used_names.append(function_name)
                        # Add this result to messages and skip to next tool
                        messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": tool_result,
                        })
                        continue

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
        # response_message may be an SDK object with .content
        content = getattr(response_message, "content", None)
        if content is None and isinstance(response_message, dict):
            content = response_message.get("content", "")
        return content or "", "groq"
