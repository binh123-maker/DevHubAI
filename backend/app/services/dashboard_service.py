from datetime import datetime, timedelta, timezone
from sqlalchemy import func, desc
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workspace import Workspace, Folder
from app.models.chat import Chat, ChatMessage
from app.models.document import Document, DocumentChunk
from app.models.enums import DocumentStatus
from app.schemas.dashboard import (
    UserDashboardOverviewResponse,
    DashboardStatistics,
    LearningAnalytics,
    MostActiveWorkspace,
    HeatmapDay,
    RecentActivityItem,
    DocumentSummaryItem,
    RecentWorkspaceItem,
)


def get_dashboard_overview(db: Session, user: User) -> UserDashboardOverviewResponse:
    user_id = user.id

    # 1. KPI Statistics
    total_workspaces = db.query(func.count(Workspace.id)).filter(Workspace.user_id == user_id).scalar() or 0
    
    total_folders = (
        db.query(func.count(Folder.id))
        .join(Workspace, Folder.workspace_id == Workspace.id)
        .filter(Workspace.user_id == user_id)
        .scalar() or 0
    )
    
    total_documents = db.query(func.count(Document.id)).filter(Document.user_id == user_id).scalar() or 0
    total_conversations = db.query(func.count(Chat.id)).filter(Chat.user_id == user_id).scalar() or 0
    
    total_messages = (
        db.query(func.count(ChatMessage.id))
        .join(Chat, ChatMessage.chat_id == Chat.id)
        .filter(Chat.user_id == user_id)
        .scalar() or 0
    )
    
    total_uploads = total_documents
    documents_processed = (
        db.query(func.count(Document.id))
        .filter(Document.user_id == user_id, Document.status == DocumentStatus.PROCESSED)
        .scalar() or 0
    )
    failed_documents = (
        db.query(func.count(Document.id))
        .filter(Document.user_id == user_id, Document.status == DocumentStatus.FAILED)
        .scalar() or 0
    )
    total_chunks = (
        db.query(func.count(DocumentChunk.id))
        .join(Document, DocumentChunk.document_id == Document.id)
        .filter(Document.user_id == user_id)
        .scalar() or 0
    )
    latest_doc = (
        db.query(Document.updated_at)
        .filter(Document.user_id == user_id, Document.status == DocumentStatus.PROCESSED)
        .order_by(desc(Document.updated_at))
        .first()
    )
    latest_processing_time = latest_doc[0].isoformat() if latest_doc and latest_doc[0] else None

    # 2. 90-Day Heatmap Calculation
    now = datetime.now(timezone.utc)
    today_date = now.date()
    start_date_90 = today_date - timedelta(days=89)

    # Query chat creation activity per day
    chat_days = (
        db.query(
            func.date(Chat.created_at).label('activity_date'),
            func.count(Chat.id).label('cnt')
        )
        .filter(Chat.user_id == user_id, Chat.created_at >= start_date_90)
        .group_by(func.date(Chat.created_at))
        .all()
    )

    # Query document creation activity per day
    doc_days = (
        db.query(
            func.date(Document.created_at).label('activity_date'),
            func.count(Document.id).label('cnt')
        )
        .filter(Document.user_id == user_id, Document.created_at >= start_date_90)
        .group_by(func.date(Document.created_at))
        .all()
    )

    # Query workspace creation activity per day
    ws_days = (
        db.query(
            func.date(Workspace.created_at).label('activity_date'),
            func.count(Workspace.id).label('cnt')
        )
        .filter(Workspace.user_id == user_id, Workspace.created_at >= start_date_90)
        .group_by(func.date(Workspace.created_at))
        .all()
    )

    daily_counts: dict = {}
    for r in chat_days:
        if r.activity_date:
            daily_counts[r.activity_date] = daily_counts.get(r.activity_date, 0) + r.cnt
    for r in doc_days:
        if r.activity_date:
            daily_counts[r.activity_date] = daily_counts.get(r.activity_date, 0) + r.cnt
    for r in ws_days:
        if r.activity_date:
            daily_counts[r.activity_date] = daily_counts.get(r.activity_date, 0) + r.cnt

    heatmap_days: list[HeatmapDay] = []
    for i in range(90):
        d = start_date_90 + timedelta(days=i)
        heatmap_days.append(HeatmapDay(
            date=d.isoformat(),
            count=daily_counts.get(d, 0)
        ))

    # 3. Learning Streak Days
    streak = 0
    curr_d = today_date
    # Check today, if no activity check yesterday to keep streak unbroken
    if daily_counts.get(curr_d, 0) == 0:
        curr_d = today_date - timedelta(days=1)

    while daily_counts.get(curr_d, 0) > 0:
        streak += 1
        curr_d -= timedelta(days=1)

    # 4. Weekly & Monthly activity
    start_of_week = today_date - timedelta(days=today_date.weekday())
    start_of_month = today_date.replace(day=1)
    
    weekly_activity_count = sum(cnt for d, cnt in daily_counts.items() if d >= start_of_week)
    monthly_activity_count = sum(cnt for d, cnt in daily_counts.items() if d >= start_of_month)

    # 5. Most Active Workspace
    most_active_workspace = None
    fav_ws = (
        db.query(
            Workspace.id,
            Workspace.name,
            Workspace.color,
            Workspace.icon,
            func.count(Document.id).label('doc_count')
        )
        .outerjoin(Document, Document.workspace_id == Workspace.id)
        .filter(Workspace.user_id == user_id)
        .group_by(Workspace.id)
        .order_by(desc('doc_count'))
        .first()
    )
    if fav_ws and fav_ws[0]:
        most_active_workspace = MostActiveWorkspace(
            id=fav_ws[0],
            name=fav_ws[1],
            color=fav_ws[2],
            icon=fav_ws[3],
            activity_count=fav_ws[4] or 0
        )

    # 6. Recent Activities
    recent_chats = db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.created_at.desc()).limit(5).all()
    recent_docs = db.query(Document).filter(Document.user_id == user_id).order_by(Document.created_at.desc()).limit(5).all()
    recent_workspaces = db.query(Workspace).filter(Workspace.user_id == user_id).order_by(Workspace.created_at.desc()).limit(5).all()

    activities: list[RecentActivityItem] = []
    for c in recent_chats:
        activities.append(RecentActivityItem(
            id=str(c.id),
            type="chat_created",
            title=c.title,
            description=f"Cuộc trò chuyện mới: {c.title}",
            created_at=c.created_at,
            meta={"workspace_id": str(c.workspace_id) if c.workspace_id else None}
        ))
    for d in recent_docs:
        activities.append(RecentActivityItem(
            id=str(d.id),
            type="document_uploaded",
            title=d.title,
            description=f"Đã tải lên tài liệu {d.title}",
            created_at=d.created_at,
            meta={"workspace_id": str(d.workspace_id), "status": d.status.value, "kanban_status": d.kanban_status.value}
        ))
    for w in recent_workspaces:
        activities.append(RecentActivityItem(
            id=str(w.id),
            type="workspace_created",
            title=w.name,
            description=f"Đã tạo workspace {w.name}",
            created_at=w.created_at,
            meta={}
        ))

    activities.sort(key=lambda x: x.created_at, reverse=True)
    recent_activities = activities[:10]

    statistics = DashboardStatistics(
        total_workspaces=total_workspaces,
        total_folders=total_folders,
        total_documents=total_documents,
        total_conversations=total_conversations,
        total_messages=total_messages,
        total_uploads=total_uploads,
        documents_processed=documents_processed,
        learning_streak_days=streak,
        total_chunks=total_chunks,
        indexed_documents=documents_processed,
        failed_documents=failed_documents,
        embedding_status="Healthy" if failed_documents == 0 else "Degraded",
        search_health="100% Operational",
        latest_processing_time=latest_processing_time,
        avg_retrieval_time_ms=120,
    )

    learning_analytics = LearningAnalytics(
        learning_streak_days=streak,
        most_active_workspace=most_active_workspace,
        weekly_activity_count=weekly_activity_count,
        monthly_activity_count=monthly_activity_count,
    )

    # 7. Document Collections & Kanban Summary
    kanban_counts = (
        db.query(Document.kanban_status, func.count(Document.id))
        .filter(Document.user_id == user_id)
        .group_by(Document.kanban_status)
        .all()
    )
    kanban_summary = {"new": 0, "learning": 0, "completed": 0, "archived": 0}
    for st, count in kanban_counts:
        status_key = st.value if hasattr(st, "value") else str(st).lower()
        if status_key in kanban_summary:
            kanban_summary[status_key] = count

    ws_list = db.query(Workspace).filter(Workspace.user_id == user_id).order_by(desc(Workspace.updated_at)).limit(6).all()
    recent_workspaces_items = []
    for w in ws_list:
        cnt = db.query(func.count(Document.id)).filter(Document.workspace_id == w.id).scalar() or 0
        recent_workspaces_items.append(RecentWorkspaceItem(
            id=w.id,
            name=w.name,
            color=w.color,
            document_count=cnt,
            updated_at=w.updated_at
        ))

    def to_doc_summary(doc: Document) -> DocumentSummaryItem:
        chunk_cnt = db.query(func.count(DocumentChunk.id)).filter(DocumentChunk.document_id == doc.id).scalar() or 0
        ws = db.query(Workspace.name).filter(Workspace.id == doc.workspace_id).first()
        return DocumentSummaryItem(
            id=doc.id,
            title=doc.title,
            workspace_id=doc.workspace_id,
            workspace_name=ws[0] if ws else None,
            file_type=doc.file_type,
            file_size=doc.file_size,
            status=doc.status.value if hasattr(doc.status, "value") else str(doc.status),
            kanban_status=doc.kanban_status.value if hasattr(doc.kanban_status, "value") else str(doc.kanban_status),
            view_count=doc.view_count or 0,
            last_opened_at=doc.last_opened_at,
            total_chunks=chunk_cnt,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )

    all_user_docs = db.query(Document).filter(Document.user_id == user_id)
    recent_docs_db = all_user_docs.order_by(desc(Document.created_at)).limit(6).all()
    recently_processed_db = all_user_docs.filter(Document.status == DocumentStatus.PROCESSED).order_by(desc(Document.updated_at)).limit(6).all()
    recently_opened_db = all_user_docs.filter(Document.last_opened_at.isnot(None)).order_by(desc(Document.last_opened_at)).limit(6).all()
    favorite_docs_db = all_user_docs.order_by(desc(Document.view_count)).limit(6).all()

    recent_documents = [to_doc_summary(d) for d in recent_docs_db]
    recently_processed = [to_doc_summary(d) for d in recently_processed_db]
    recently_opened = [to_doc_summary(d) for d in recently_opened_db]
    favorite_documents = [to_doc_summary(d) for d in favorite_docs_db]

    processing_queue = db.query(func.count(Document.id)).filter(
        Document.user_id == user_id,
        Document.status.in_([DocumentStatus.UPLOADING, DocumentStatus.PROCESSING])
    ).scalar() or 0
    avg_chunks = (total_chunks // (total_documents or 1))

    knowledge_health = {
        "indexed_documents": documents_processed,
        "processing_queue": processing_queue,
        "failed_documents": failed_documents,
        "avg_retrieval_time_ms": 120,
        "avg_chunk_count": avg_chunks,
        "search_health": "100% Operational",
        "embedding_status": "Healthy" if failed_documents == 0 else "Degraded",
    }

    return UserDashboardOverviewResponse(
        statistics=statistics,
        learning_analytics=learning_analytics,
        heatmap=heatmap_days,
        recent_activities=recent_activities,
        recent_documents=recent_documents,
        recently_processed=recently_processed,
        recently_opened=recently_opened,
        favorite_documents=favorite_documents,
        recent_workspaces=recent_workspaces_items,
        kanban_summary=kanban_summary,
        knowledge_health=knowledge_health,
    )
