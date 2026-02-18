from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ChatRequest, ChatResponse, ConversationResponse, ChatMessage
from ..services import AgentService, ConversationService, PersistentMemoryService
from ..exceptions import AgentException
from ..agent import SimpleAgent

router = APIRouter(tags=["chat"])


@router.get("/conversations", response_model=List[ConversationResponse])
def list_conversations(
    db: Session = Depends(get_db),
) -> List[ConversationResponse]:
    """List all conversations."""
    try:
        conversation_service = ConversationService(db)
        conversations = conversation_service.list_conversations()
        
        return [
            ConversationResponse(
                conversation_id=c.id,
                messages=[
                    ChatMessage(
                        id=msg.id,
                        role=msg.role,
                        content=msg.content,
                        tool_used=msg.tool_used,
                        created_at=msg.created_at,
                    )
                    for msg in c.messages
                ],
            )
            for c in conversations
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """
    Chat with the agent.
    
    - If `conversation_id` is not provided, a new conversation is created
    """
    try:
        agent_service = AgentService(db)
        conversation_service = ConversationService(db)
        
        # Always use default agent
        agent = agent_service.get_agent()
        
        # Get or create conversation
        if request.conversation_id:
            conversation = conversation_service.get_conversation(request.conversation_id)
            if not conversation:
                raise AgentException(
                    message="Conversation not found",
                    detail=f"Conversation {request.conversation_id} does not exist",
                )
        else:
            conversation = conversation_service.create_conversation()
        
        # --- GLOBAL CONTEXT (Across Conversations) ---
        # Get last 3 conversations to provide cross-talk memory
        all_convs = conversation_service.list_conversations()
        # Sort by updated_at descending
        all_convs.sort(key=lambda x: x.updated_at, reverse=True)
        
        global_memory = []
        for c in all_convs:
            if c.id != conversation.id and c.messages:
                # Add a brief snippet of what was discussed in past sessions
                first_msg = c.messages[0].content[:100]
                global_memory.append(f"Past session {c.id[:8]}: \"{first_msg}...\"")
            if len(global_memory) >= 3:
                break
        
        # --- LOCAL CONTEXT (Current Conversation) ---
        # Get history for context (last 15 messages)
        history = conversation_service.get_conversation_messages(conversation.id, limit=15)
        
        # Combine global hints into system prompt hint
        extra_context = ""
        if global_memory:
            extra_context = "\n\nRefer to past sessions if helpful:\n" + "\n".join(global_memory)
        
        # Add user message
        conversation_service.add_message(
            conversation.id,
            role="user",
            content=request.message,
        )
        
        # Process message with SimpleAgent/LLM
        simple_agent = SimpleAgent()
        
        # --- PERSISTENT MEMORY ---
        memory_service = PersistentMemoryService()
        persistent_context = memory_service.get_all_memory()
        
        full_system_prompt = (
            f"{agent.config.system_prompt}\n\n"
            f"--- PERSISTENT STATE ---\n"
            f"{persistent_context}\n\n"
            f"{extra_context}"
        )

        reply, tool_used = simple_agent.run(
            request.message,
            db=db,
            history=history,
            system_prompt=full_system_prompt
        )
        agent_reply = reply
        
        # Add assistant message
        assistant_msg = conversation_service.add_message(
            conversation.id,
            role="assistant",
            content=agent_reply,
            tool_used=tool_used,
        )

        # Trigger background memory update
        background_tasks.add_task(memory_service.analyze_and_update, request.message, agent_reply)
        
        # Get recent messages for response
        recent_messages = conversation_service.get_conversation(conversation.id).messages
        
        return ChatResponse(
            conversation_id=conversation.id,
            message=ChatMessage(
                id=assistant_msg.id,
                role=assistant_msg.role,
                content=assistant_msg.content,
                tool_used=assistant_msg.tool_used,
                created_at=assistant_msg.created_at,
            ),
            reply=agent_reply,
            messages=[
                ChatMessage(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    tool_used=msg.tool_used,
                    created_at=msg.created_at,
                )
                for msg in recent_messages[-10:]  # Last 10 messages
            ],
        )
    
    except AgentException:
        raise
    except Exception as e:
        raise AgentException(
            message="Failed to process chat message",
            detail=str(e),
        )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
) -> ConversationResponse:
    """Get conversation history."""
    try:
        conversation_service = ConversationService(db)
        conversation = conversation_service.get_conversation(conversation_id)
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found",
            )
        
        return ConversationResponse(
            conversation_id=conversation.id,
            messages=[
                ChatMessage(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    tool_used=msg.tool_used,
                    created_at=msg.created_at,
                )
                for msg in conversation.messages
            ],
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    db: Session = Depends(get_db),
) -> ConversationResponse:
    """Create a new conversation."""
    try:
        conversation_service = ConversationService(db)
        conversation = conversation_service.create_conversation()
        
        return ConversationResponse(
            conversation_id=conversation.id,
            messages=[],
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
):
    """Delete a conversation."""
    try:
        conversation_service = ConversationService(db)
        success = conversation_service.delete_conversation(conversation_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation {conversation_id} not found",
            )
            
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
