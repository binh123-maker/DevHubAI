import re
import difflib
from collections import defaultdict
from app.services.ai import AIOrchestrator
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
from app.services.query_rewriter import rewrite_query
from app.schemas.chat import ChatCreate, ChatMessageCreate, ChatMessageResponse, CitationResponse, ChatUpdate, ChatResponse


def _is_noisy_chunk(content: str) -> bool:
    stripped = content.strip()
    if not stripped:
        return True
    
    # 1. Less than 30 alphanumeric characters
    useful_chars = [c for c in stripped if c.isalnum()]
    if len(useful_chars) < 30:
        return True
        
    # 2. Table of contents keywords or pattern
    lower_content = stripped.lower()
    if "mục lục" in lower_content or "table of contents" in lower_content:
        return True
    if len(re.findall(r'\.{5,}', stripped)) > 0 or len(re.findall(r'-{5,}', stripped)) > 0:
        return True
        
    # 3. Only page numbers (e.g. "Trang 12" or "Page 12" or only digits)
    if re.match(r'^(trang|page)?\s*\d+\s*$', lower_content):
        return True
        
    # 4. Only heading: e.g. starts with # and has no newline
    if stripped.startswith('#') and '\n' not in stripped:
        return True
        
    return False


def _clean_text(content: str) -> str:
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
        
        lower_line = stripped_line.lower()
        # Strip SaveLikeReport, Download, AI tóm tắt
        if "savelikereport" in lower_line or "download" in lower_line or "ai tóm tắt" in lower_line:
            continue
        if "save" in lower_line and "like" in lower_line and "report" in lower_line:
            continue
            
        # Strip search URLs
        if "/tim-kiem" in lower_line:
            continue
            
        # Strip lines composed entirely of Markdown links
        if re.match(r'^(\s*\[[^\]]+\]\([^)]+\)\s*)+$', stripped_line):
            continue
            
        # Clean inline links: [text](url) -> text
        stripped_line = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', stripped_line)
        
        # Strip HTML tags
        stripped_line = re.sub(r'<[^>]+>', '', stripped_line)
        
        # Strip empty headings
        if re.match(r'^#+\s*$', stripped_line):
            continue
            
        cleaned_lines.append(stripped_line)
        
    return "\n".join(cleaned_lines)


def _normalize_whitespace(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def _extract_relevant_passages(cleaned_content: str, query: str) -> list[dict]:
    keywords = set(tok for tok in query.lower().split() if tok.isalnum())
    paragraphs = [p.strip() for p in cleaned_content.split('\n') if p.strip()]
    
    if not keywords:
        # Fallback to returning normalized text if no keywords are matched
        fallback_text = "\n".join(paragraphs[:2]).strip()
        if len(fallback_text) > 400:
            fallback_text = fallback_text[:400] + '...'
        return [{"text": fallback_text, "matched_keywords": [], "reason": "Fallback to first paragraphs"}]
        
    selected_passages = []
    for idx, para in enumerate(paragraphs):
        para_lower = para.lower()
        matched = [kw for kw in keywords if kw in para_lower]
        if matched:
            # Context window: 1 paragraph before, matching paragraph, 1 paragraph after
            start_idx = max(0, idx - 1)
            end_idx = min(len(paragraphs), idx + 2)
            window = paragraphs[start_idx:end_idx]
            
            # Merge and normalize whitespace inside the merged passage
            merged = _normalize_whitespace(" ".join(window))
            
            # Limit passage to 400 characters cleanly at word boundary
            if len(merged) > 400:
                truncated = merged[:400]
                last_space = truncated.rfind(' ')
                if last_space > 300:
                    merged = truncated[:last_space] + '...'
                else:
                    merged = truncated + '...'
                    
            selected_passages.append({
                "text": merged,
                "matched_keywords": matched,
                "reason": f"Paragraph {idx} matches terms: {', '.join(matched)}"
            })
            
    return selected_passages


def _are_passages_similar(p1: str, p2: str) -> bool:
    return difflib.SequenceMatcher(None, p1.lower(), p2.lower()).ratio() > 0.90


def _build_grounded_context(db: Session, search_results: list, query: str) -> tuple[str, list]:
    from app.services.context_builder import ContextBuilder
    builder = ContextBuilder()
    context_str, mapping = builder.build_context(db, search_results)
    
    # Map back to expected structure by the caller: list of search result elements that were selected.
    selected_chunk_ids = {m["chunk_id"] for m in mapping}
    citation_targets = [res for res in search_results if res.chunk_id in selected_chunk_ids]
    return context_str, citation_targets


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

    # 2. Retrieve Context (FTS) with query rewriting + automatic fallback
    rewritten = rewrite_query(msg_in.content)
    logger.info("[QUERY REWRITER] original=%r  rewritten=%r", msg_in.content, rewritten)

    search_results = search_documents(
        db=db,
        user_id=user_id,
        query=rewritten,
        workspace_id=chat.workspace_id,
        folder_id=chat.folder_id,
        document_id=chat.document_id,
        chat_mode=chat.chat_mode,
        limit=10,  # Top 10 chunks
    )

    # Fallback: if the rewritten query returned nothing and it actually
    # differs from the original, retry with the raw user message.
    if not search_results and rewritten != msg_in.content.lower().strip():
        logger.info("[QUERY REWRITER] rewritten query returned 0 results, falling back to original")
        search_results = search_documents(
            db=db,
            user_id=user_id,
            query=msg_in.content,
            workspace_id=chat.workspace_id,
            folder_id=chat.folder_id,
            document_id=chat.document_id,
            chat_mode=chat.chat_mode,
            limit=10,
        )

    retrieved_chunk_count = len(search_results)

    # 3. Build Prompt and Call AI
    context_text, citation_targets = _build_grounded_context(db, search_results, rewritten)
    
    if not context_text and chat.chat_mode != ChatMode.GLOBAL:
        ai_content = "Tôi không tìm thấy tài liệu nào trong workspace hiện tại có chứa thông tin để trả lời câu hỏi của bạn. Vui lòng tải lên tài liệu liên quan hoặc điều chỉnh lại câu hỏi."
    else:
        system_instruction = (
            "You are a helpful AI assistant for DevHub AI.\n"
            "You must answer the user's question based strictly on the provided Context Information from their workspace.\n"
            "Never invent facts or use external knowledge not present in the context.\n"
            "If the context contains enough information, provide the best and most accurate answer possible.\n"
            "If the context only partially answers the question, answer using the available information and explicitly state what details are missing.\n"
            "Only refuse to answer when absolutely no relevant context or information is present, in which case you must say exactly:\n"
            "'Tài liệu hiện tại không chứa đủ thông tin để tôi trả lời câu hỏi này.'\n\n"
            "Format your response as clean, plain educational text. Follow these rendering rules strictly:\n"
            "1. Do not expose reasoning and never output <think> blocks.\n"
            "2. Normal educational text must be plain text. Do NOT use Markdown headings (#, ##, etc.), bold (**text**), italic (*text*), or Markdown tables (unless explicitly requested).\n"
            "3. You are ONLY allowed to use Markdown for fenced code blocks (e.g. ```python ... ```) and inline code (e.g. `code`).\n"
            "4. Output all mathematical formulas in LaTeX: enclose block equations in $$...$$ and inline formulas in $...$.\n"
            "5. Preserve mathematical notations and Unicode symbols when appropriate. Keep answers concise and readable."
        )
        
        prompt = f"Context Information:\n{context_text}\n\nUser Question:\n{msg_in.content}\n"
        
        logger.info(f"[DEBUG RAG] Final context passed into Gemini:\n{context_text}")

        # Load recent history (last 10 messages for context)
        history = db.query(ChatMessage).filter(ChatMessage.chat_id == chat.id).order_by(ChatMessage.created_at.asc()).limit(10).all()
        
        # Call AIOrchestrator
        try:
            response = AIOrchestrator.generate_response(
                user_message=msg_in.content,
                context_text=context_text,
                history_messages=history[:-1],
                system_instruction=system_instruction,
                temperature=settings.ai_temperature,
                max_tokens=settings.ai_max_tokens
            )
            ai_content = response.content
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
    if citation_targets:
        for res in citation_targets:
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

