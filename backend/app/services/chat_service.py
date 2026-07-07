import google.generativeai as genai
from sqlalchemy.orm import Session
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.models.chat import Chat, ChatMessage, Citation
from app.models.workspace import Workspace, Folder
from app.models.document import Document
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from app.models.enums import MessageRole, ChatMode, CitationSourceType
from app.services.search_service import search_documents
from app.schemas.chat import ChatCreate, ChatMessageCreate, ChatMessageResponse, CitationResponse, ChatUpdate, ChatResponse
 
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


def get_chats(db: Session, user_id: UUID, workspace_id: UUID | None = None) -> list[ChatResponse]:
    """List chats for the user, optionally filtered by workspace. Includes metadata."""
    query = (
        db.query(
            Chat,
            Workspace.name.label("workspace_name"),
            Folder.name.label("folder_name"),
            Document.title.label("document_name"),
        )
        .outerjoin(Workspace, Chat.workspace_id == Workspace.id)
        .outerjoin(Folder, Chat.folder_id == Folder.id)
        .outerjoin(Document, Chat.document_id == Document.id)
        .filter(Chat.user_id == user_id)
    )
    
    if workspace_id:
        query = query.filter(Chat.workspace_id == workspace_id)
        
    results = query.order_by(Chat.updated_at.desc()).all()
    
    responses = []
    for chat, w_name, f_name, d_name in results:
        last_msg = db.query(ChatMessage).filter(ChatMessage.chat_id == chat.id).order_by(desc(ChatMessage.created_at)).first()
        responses.append(ChatResponse(
            id=chat.id,
            workspace_id=chat.workspace_id,
            folder_id=chat.folder_id,
            document_id=chat.document_id,
            title=chat.title,
            chat_mode=chat.chat_mode,
            is_favorite=getattr(chat, 'is_favorite', False),
            status=getattr(chat, 'status', "completed"),
            message_count=chat.message_count,
            created_at=chat.created_at,
            updated_at=chat.updated_at,
            workspace_name=w_name,
            folder_name=f_name,
            document_name=d_name,
            last_message_content=last_msg.content if last_msg else None,
        ))
    return responses


def get_chat(db: Session, user_id: UUID, chat_id: UUID) -> Chat:
    """Get a chat by ID, ensuring user ownership."""
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == user_id).first()
    if not chat:
        raise ChatError("Chat not found", status_code=404)
    return chat


def update_chat(db: Session, user_id: UUID, chat_id: UUID, chat_in: ChatUpdate) -> Chat:
    chat = get_chat(db, user_id, chat_id)
    if chat_in.title is not None:
        chat.title = chat_in.title
    if chat_in.is_favorite is not None:
        chat.is_favorite = chat_in.is_favorite
    db.commit()
    db.refresh(chat)
    return chat


def delete_chat(db: Session, user_id: UUID, chat_id: UUID) -> None:
    chat = get_chat(db, user_id, chat_id)
    db.delete(chat)
    db.commit()


def get_chat_messages(db: Session, user_id: UUID, chat_id: UUID) -> list[ChatMessageResponse]:
    """Get all messages for a specific chat, including citations."""
    chat = get_chat(db, user_id, chat_id)
    
    messages = (
        db.query(ChatMessage)
        .options(joinedload(ChatMessage.citations))
        .filter(ChatMessage.chat_id == chat.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    
    responses = []
    for msg in messages:
        citations = []
        for cit in msg.citations:
            citations.append(
                CitationResponse(
                    document_name=cit.source_name,
                    source_type=cit.source_type.value,
                    page_number=cit.page_number,
                    line_start=cit.line_start,
                    line_end=cit.line_end,
                    heading=None, # Heading is not currently stored in DB, keeping schema compatible
                    url=cit.url,
                )
            )
            
        responses.append(
            ChatMessageResponse(
                id=msg.id,
                chat_id=msg.chat_id,
                role=msg.role.value,
                content=msg.content,
                created_at=msg.created_at,
                retrieved_chunk_count=len(citations) if citations else None,
                citations=citations,
            )
        )
    return responses


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
    # Auto-generate title if this is the first message and title is default
    if chat.message_count == 0 and chat.title == "Cuộc trò chuyện mới":
        words = msg_in.content.split()
        chat.title = " ".join(words[:6]) + ("..." if len(words) > 6 else "")

    chat.message_count += 1
    db.commit()

    # 2. Retrieve Context (FTS)
    search_results = search_documents(
        db=db,
        user_id=user_id,
        query=msg_in.content,
        workspace_id=chat.workspace_id,
        folder_id=chat.folder_id,
        document_id=chat.document_id,
        chat_mode=chat.chat_mode,
        limit=5, # Top 5 chunks
    )
    
    retrieved_chunk_count = len(search_results)

    # 3. Build Prompt and Call AI
    if not search_results and chat.chat_mode != ChatMode.GLOBAL:
        ai_content = "Tôi không tìm thấy tài liệu nào trong workspace hiện tại có chứa thông tin để trả lời câu hỏi của bạn. Vui lòng tải lên tài liệu liên quan hoặc điều chỉnh lại câu hỏi."
    else:
        context_parts = []
        for i, res in enumerate(search_results):
            heading_info = f", Section: {res.heading}" if res.heading else ""
            page_info = f", Page {res.page_number}" if res.page_number else ""
            context_parts.append(
                f"[Source {i+1}: {res.document_name}{page_info}{heading_info}]\n"
                f"{res.content}"
            )
        context_text = "\n\n".join(context_parts)
        
        system_instruction = (
            "You are a helpful AI assistant for DevHub AI. "
            "You MUST answer the user's question based ONLY on the provided Context Information from their workspace. "
            "NEVER use external knowledge or hallucinate facts. "
            "If the provided context does not contain the answer, you MUST say exactly: "
            "'Tài liệu hiện tại không chứa đủ thông tin để tôi trả lời câu hỏi này.'"
        )
        
        prompt = f"Context Information:\n{context_text}\n\nUser Question:\n{msg_in.content}\n"
        
        logger.info(f"[DEBUG RAG] Final context passed into Gemini:\n{context_text}")

        # Load recent history (last 10 messages for context)
        history = db.query(ChatMessage).filter(ChatMessage.chat_id == chat.id).order_by(ChatMessage.created_at.asc()).limit(10).all()
        
        # Exclude the just-saved user message from history for Gemini context (we send it as current message)
        gemini_history = []
        for h in history[:-1]:
            role = "user" if h.role == MessageRole.USER else "model"
            gemini_history.append({"role": role, "parts": [h.content]})

        # Call Gemini API
        try:
            model = genai.GenerativeModel(
                model_name=settings.gemini_model,
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
            source_type = CitationSourceType.WEBSITE if res.source_url else CitationSourceType.DOCUMENT
            citation = Citation(
                message_id=ai_msg.id,
                document_id=res.document_id,
                chunk_id=res.chunk_id,
                source_name=res.document_name,
                source_type=source_type,
                page_number=res.page_number,
                line_start=res.line_start,
                line_end=res.line_end,
                url=res.source_url,
                excerpt=res.content
            )
            db.add(citation)
            citation_responses.append(
                CitationResponse(
                    document_name=res.document_name,
                    source_type=source_type.value,
                    page_number=res.page_number,
                    line_start=res.line_start,
                    line_end=res.line_end,
                    heading=res.heading,
                    url=res.source_url,
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


def delete_all_chats(db: Session, user_id: UUID) -> None:
    """Delete all chats for a user in a single transaction."""
    try:
        chats = db.query(Chat).filter(Chat.user_id == user_id).all()
        for chat in chats:
            db.delete(chat)
        db.commit()
    except Exception as e:
        db.rollback()
        raise e

