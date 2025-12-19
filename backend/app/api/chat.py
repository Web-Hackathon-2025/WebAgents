"""Chat endpoints for customer and provider portals."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime

from app.core.security.dependencies import get_current_user
from app.core.exceptions import NotFoundError, BadRequestError
from app.db.client import get_db
from app.db.models import User, ChatConversation, ChatMessage as ChatMessageModel
from app.domain.models import ChatMessageCreate, ChatMessage, ChatConversation as ChatConversationResponse, ChatResponse
from app.agents.chat_agent import CustomerChatAgent, ProviderChatAgent

router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

customer_chat_agent = CustomerChatAgent()
provider_chat_agent = ProviderChatAgent()


@router.post("/message", response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def send_chat_message(
    message_data: ChatMessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Send a message to the chat assistant."""
    if current_user.role not in ["customer", "provider"]:
        raise BadRequestError("Chat is only available for customers and providers")
    
    # Get or create conversation
    conversation = None
    session_id = None
    
    if message_data.conversation_id:
        # Get existing conversation
        result = await db.execute(
            select(ChatConversation).where(
                ChatConversation.id == message_data.conversation_id,
                ChatConversation.user_id == current_user.id
            )
        )
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise NotFoundError("Conversation not found")
        
        session_id = conversation.session_id
    else:
        # Create new conversation
        session_id = f"chat_{current_user.id}_{uuid4().hex[:16]}"
        conversation = ChatConversation(
            user_id=current_user.id,
            role=current_user.role,
            session_id=session_id,
            title=message_data.message[:50] + "..." if len(message_data.message) > 50 else message_data.message
        )
        db.add(conversation)
        await db.flush()
    
    # Save user message
    user_message = ChatMessageModel(
        conversation_id=conversation.id,
        role="user",
        content=message_data.message
    )
    db.add(user_message)
    await db.flush()
    
    # Get appropriate chat agent
    if current_user.role == "customer":
        chat_agent = customer_chat_agent
    else:
        chat_agent = provider_chat_agent
    
    # Prepare context for the agent
    # Get user's recent bookings, profile info, etc. for context
    context = {
        "user_id": str(current_user.id),
        "user_role": current_user.role,
        "user_message": message_data.message,
        "conversation_history": [],  # Could add recent messages here
        "execution_context": "chat"
    }
    
    # Get conversation history (last 10 messages for context)
    history_result = await db.execute(
        select(ChatMessageModel)
        .where(ChatMessageModel.conversation_id == conversation.id)
        .order_by(ChatMessageModel.created_at.desc())
        .limit(10)
    )
    history_messages = history_result.scalars().all()
    
    # Build conversation context
    if history_messages:
        context["conversation_history"] = [
            {"role": msg.role, "content": msg.content}
            for msg in reversed(history_messages[:-1])  # Exclude current message
        ]
    
    # Execute chat agent
    try:
        agent_response = await chat_agent.execute(
            context=context,
            db=db,
            use_cache=False,  # Don't cache chat messages
            session_id=session_id
        )
        
        # Extract message from agent response
        assistant_message = agent_response.get("message", "I apologize, but I couldn't process your message. Please try again.")
        
        # Save assistant message
        assistant_msg = ChatMessageModel(
            conversation_id=conversation.id,
            role="assistant",
            content=assistant_message,
            metadata=agent_response.get("metadata")
        )
        db.add(assistant_msg)
        
        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()
        
        await db.commit()
        
        return ChatResponse(
            message=assistant_message,
            conversation_id=conversation.id,
            session_id=session_id,
            metadata=agent_response.get("metadata")
        )
        
    except Exception as e:
        await db.rollback()
        # Save error message
        error_msg = ChatMessageModel(
            conversation_id=conversation.id,
            role="assistant",
            content="I apologize, but I'm having trouble processing your request right now. Please try again or contact support.",
            metadata={"error": str(e)}
        )
        db.add(error_msg)
        await db.commit()
        
        return ChatResponse(
            message="I apologize, but I'm having trouble processing your request right now. Please try again or contact support.",
            conversation_id=conversation.id,
            session_id=session_id,
            metadata={"error": True}
        )


@router.get("/conversations", response_model=List[ChatConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all chat conversations for the current user."""
    if current_user.role not in ["customer", "provider"]:
        raise BadRequestError("Chat is only available for customers and providers")
    
    result = await db.execute(
        select(ChatConversation)
        .where(ChatConversation.user_id == current_user.id)
        .order_by(ChatConversation.updated_at.desc())
    )
    conversations = result.scalars().all()
    
    # Load messages for each conversation
    conversation_list = []
    for conv in conversations:
        messages_result = await db.execute(
            select(ChatMessageModel)
            .where(ChatMessageModel.conversation_id == conv.id)
            .order_by(ChatMessageModel.created_at.asc())
        )
        messages = messages_result.scalars().all()
        
        conversation_list.append(ChatConversationResponse(
            id=conv.id,
            title=conv.title,
            session_id=conv.session_id,
            is_active=conv.is_active,
            created_at=conv.created_at,
            updated_at=conv.updated_at,
            messages=[ChatMessage.model_validate(msg) for msg in messages]
        ))
    
    return conversation_list


@router.get("/conversations/{conversation_id}", response_model=ChatConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation with all messages."""
    if current_user.role not in ["customer", "provider"]:
        raise BadRequestError("Chat is only available for customers and providers")
    
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    # Load messages
    messages_result = await db.execute(
        select(ChatMessageModel)
        .where(ChatMessageModel.conversation_id == conversation.id)
        .order_by(ChatMessageModel.created_at.asc())
    )
    messages = messages_result.scalars().all()
    
    return ChatConversationResponse(
        id=conversation.id,
        title=conversation.title,
        session_id=conversation.session_id,
        is_active=conversation.is_active,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        messages=[ChatMessage.model_validate(msg) for msg in messages]
    )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a conversation."""
    if current_user.role not in ["customer", "provider"]:
        raise BadRequestError("Chat is only available for customers and providers")
    
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise NotFoundError("Conversation not found")
    
    await db.delete(conversation)
    await db.commit()
    
    return None

