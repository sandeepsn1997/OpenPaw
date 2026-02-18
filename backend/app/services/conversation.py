"""Conversation management service."""

import json
import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from ..database import ConversationDB
from ..schemas import ConversationHistory, ConversationMessage


class ConversationService:
    """Service for managing conversations."""

    def __init__(self, db: Session):
        """Initialize conversation service."""
        self.db = db

    def create_conversation(self) -> ConversationHistory:
        """Create a new conversation."""
        conversation_id = str(uuid.uuid4())
        
        conversation = ConversationHistory(
            id=conversation_id,
            messages=[],
        )
        
        # Save to database
        db_conv = ConversationDB(
            id=conversation_id,
            messages=json.dumps([]),
        )
        self.db.add(db_conv)
        self.db.commit()
        
        return conversation

    def get_conversation(self, conversation_id: str) -> Optional[ConversationHistory]:
        """Get conversation by ID."""
        db_conv = self.db.query(ConversationDB).filter(
            ConversationDB.id == conversation_id
        ).first()
        
        if not db_conv:
            return None
        
        messages_data = json.loads(db_conv.messages)
        messages = [
            ConversationMessage(**msg) for msg in messages_data
        ]
        
        return ConversationHistory(
            id=db_conv.id,
            messages=messages,
            created_at=db_conv.created_at,
            updated_at=db_conv.updated_at,
        )

    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        tool_used: Optional[str] = None,
    ) -> ConversationMessage:
        """Add a message to conversation."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        message = conversation.add_message(role, content, tool_used)
        
        # Update database
        db_conv = self.db.query(ConversationDB).filter(
            ConversationDB.id == conversation_id
        ).first()
        
        messages_data = [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "tool_used": msg.tool_used,
                "created_at": msg.created_at.isoformat(),
            }
            for msg in conversation.messages
        ]
        db_conv.messages = json.dumps(messages_data)
        db_conv.updated_at = datetime.utcnow()
        self.db.commit()
        
        return message

    def get_conversation_messages(
        self,
        conversation_id: str,
        limit: int = 10,
    ) -> List[dict]:
        """Get recent messages for LLM context."""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        return conversation.get_messages_for_context(limit)

    def list_conversations(self) -> List[ConversationHistory]:
        """List all conversations."""
        db_convs = self.db.query(ConversationDB).all()
        
        conversations = []
        for db_conv in db_convs:
            messages_data = json.loads(db_conv.messages)
            messages = [
                ConversationMessage(**msg) for msg in messages_data
            ]
            conversations.append(
                ConversationHistory(
                    id=db_conv.id,
                    messages=messages,
                    created_at=db_conv.created_at,
                    updated_at=db_conv.updated_at,
                )
            )
        
        return conversations

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        db_conv = self.db.query(ConversationDB).filter(
            ConversationDB.id == conversation_id
        ).first()
        
        if not db_conv:
            return False
            
        self.db.delete(db_conv)
        self.db.commit()
        return True
