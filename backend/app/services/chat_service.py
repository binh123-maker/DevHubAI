import google.generativeai as genai
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.config import settings
from app.models.chat import Chat, ChatMessage, Citation
from app.models.enums import MessageRole, ChatMode, CitationSourceType
from app.services.search_service import search_documents
from app.schemas.chat import ChatCreate, ChatMessageCreate, ChatMessageResponse, CitationResponse
 
# Configure Gemini
if settings.gemini_api_key:
    genai.configure(api_key=settings.gemini_api_key)


class ChatError(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


def create_chat(db: Session, user_id: UUID, chat_in: ChatCreate) -> Chat:
    """Create a new chat session."""
    chat = Chat(
        user_id=user_id,
        workspace_id=chat_in.workspace_id,
        folder_id=chat_in.folder_id,
        document_id=chat_in.document_id,
        title=chat_in.title,
        chat_mode=chat_in.chat_mode,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_chats(db: Session, user_id: UUID, workspace_id: UUID | None = None) -> list[Chat]:
    """List chats for the user, optionally filtered by workspace."""
    query = db.query(Chat).filter(Chat.user_id == user_id)
    if workspace_id:
        query = query.filter(Chat.workspace_id == workspace_id)
    return query.order_by(Chat.updated_at.desc()).all()


def get_chat(db: Session, user_id: UUID, chat_id: UUID) -> Chat:
    """Get a chat by ID, ensuring user ownership."""
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise ChatError("Chat not found", status_code=404)
    return chat


def send_message(db: Session, user_id: UUID, chat_id: UUID, msg_in: ChatMessageCreate) -> ChatMessageResponse:
    """
    1. Save user message.
    2. Retrieve context via FTS.
    3. Build prompt and call Gemini.
    4. Save AI message.
    """
    chat = get_chat(db, user_id, chat_id)

    # 1. Save User Message
    user_msg = ChatMessage(
        chat_id=chat.id,
        role=MessageRole.USER,
        content=msg_in.content,
    )
    db.add(user_msg)
    chat.message_count += 1
    db.commit()

    # 2. Retrieve Context (FTS)
    search_results = search_documents(
        db=db,
        user_id=user_id,
        query=msg_in.content,
        workspace_id=chat.workspace_id,
        limit=5, # Top 5 chunks
    )
    
    retrieved_chunk_count = len(search_results)

    # 3. Build Prompt
    context_text = ""
    if search_results:
        context_parts = []
        for i, res in enumerate(search_results):
            context_parts.append(
                f"[Source {i+1}: {res.document_name}, Page {res.page_number or '?'}]\n"
                f"{res.content}"
            )
        context_text = "\n\n".join(context_parts)
    
    system_instruction = (
        "You are a helpful AI assistant in DevHub AI. "
        "Answer the user's question based ONLY on the provided context if it exists. "
        "If you don't know the answer, say that you don't know based on the provided context."
    )
    
    prompt = f"User Question:\n{msg_in.content}\n"
    if context_text:
        prompt = f"Context Information:\n{context_text}\n\n{prompt}"

    # Load recent history (last 10 messages for context)
    history = db.query(ChatMessage).filter(ChatMessage.chat_id == chat.id).order_by(ChatMessage.created_at.asc()).limit(10).all()
    
    # Exclude the just-saved user message from history for Gemini context (we send it as current message)
    gemini_history = []
    for h in history[:-1]:
        role = "user" if h.role == MessageRole.USER else "model"
        gemini_history.append({"role": role, "parts": [h.content]})

    # Call Gemini API
    ai_content = ""
    try:
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction
        )
        gemini_chat = model.start_chat(history=gemini_history)
        response = gemini_chat.send_message(prompt)
        ai_content = response.text
    except Exception as e:
        ai_content = f"Sorry, I encountered an error communicating with the AI service: {str(e)}"

    # 4. Save AI Message
    ai_msg = ChatMessage(
        chat_id=chat.id,
        role=MessageRole.ASSISTANT,
        content=ai_content,
    )
    db.add(ai_msg)
    chat.message_count += 1
    db.commit()
    db.refresh(ai_msg)

    # 4.5 Save Citations
    citation_responses = []
    if search_results:
        for res in search_results:
            citation = Citation(
                message_id=ai_msg.id,
                document_id=res.document_id,
                chunk_id=res.chunk_id,
                source_name=res.document_name,
                source_type=CitationSourceType.DOCUMENT,
                page_number=res.page_number,
                line_start=res.line_start,
                line_end=res.line_end,
                excerpt=res.content
            )
            db.add(citation)
            citation_responses.append(
                CitationResponse(
                    document_name=res.document_name,
                    page_number=res.page_number,
                    line_start=res.line_start,
                    line_end=res.line_end,
                )
            )
        db.commit()

    # 5. Return Response
    return ChatMessageResponse(
        id=ai_msg.id,
        chat_id=ai_msg.chat_id,
        role=ai_msg.role,
        content=ai_msg.content,
        created_at=ai_msg.created_at,
        retrieved_chunk_count=retrieved_chunk_count,
        citations=citation_responses,
    )
