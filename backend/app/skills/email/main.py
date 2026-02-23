from typing import Optional
import json
from .backend import GmailService
from ...db import SessionLocal

async def run(
    action: str, 
    message_id: Optional[str] = None, 
    to: Optional[str] = None, 
    subject: Optional[str] = None, 
    body: Optional[str] = None
) -> str:
    """Execute Gmail actions."""
    db = SessionLocal()
    try:
        service = GmailService(db)
        status = service.status()
        if not status.get("connected"):
            return "Gmail is not connected. Help the user connect via the settings page."

        if action == "read_inbox":
            msgs = service.list_messages(max_results=5)
            return json.dumps(msgs, indent=2)
            
        elif action == "list_unread":
            msgs = service.list_messages(unread_only=True, max_results=5)
            return json.dumps(msgs, indent=2)
            
        elif action == "read_email":
            if not message_id:
                return "Error: message_id is required to read an email."
            msg = service.get_message(message_id)
            return json.dumps(msg, indent=2)
            
        elif action == "send_email":
            if not to or not subject or not body:
                return "Error: to, subject, and body are required to send an email."
            res = service.send_email(to, subject, body)
            return f"Email sent successfully. ID: {res.get('id')}"
            
        elif action == "reply_email":
            if not message_id or not body:
                return "Error: message_id and body are required to reply."
            res = service.reply_email(message_id, body)
            return f"Reply sent successfully. ID: {res.get('id')}"
            
        elif action == "auto_reply":
            # Just a placeholder for now
            return "Auto-reply logic not implemented yet."
            
        return f"Unknown action: {action}"
    except Exception as e:
        return f"Error in Gmail skill: {str(e)}"
    finally:
        db.close()
