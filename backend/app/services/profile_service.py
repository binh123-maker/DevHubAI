from datetime import datetime, timedelta, timezone
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from uuid import UUID

from app.models.user import User, UserProfile
from app.models.workspace import Workspace
from app.models.chat import Chat, ChatMessage
from app.models.document import Document
from app.models.enums import MessageRole, GenderType
from app.schemas.profile import (
    UserDashboardResponse,
    DashboardProfile,
    DashboardStatistics,
    DashboardActivity,
    ActivityDay,
    RecentActivityItem,
    FavoriteWorkspace,
    ProfileUpdateRequest,
)


def get_user_dashboard(db: Session, user: User) -> UserDashboardResponse:
    profile = user.profile
    dashboard_profile = DashboardProfile(
        email=user.email,
        full_name=profile.full_name if profile else "",
        role=user.role.value,
        avatar_url=profile.avatar_url if profile else None,
        gender=profile.gender.value if profile else "prefer_not_to_say",
        created_at=user.created_at,
    )

    # Statistics (efficient SQL aggregates)
    total_workspaces = db.query(func.count(Workspace.id)).filter(Workspace.user_id == user.id).scalar() or 0
    total_chats = db.query(func.count(Chat.id)).filter(Chat.user_id == user.id).scalar() or 0
    total_documents = db.query(func.count(Document.id)).filter(Document.user_id == user.id).scalar() or 0
    total_ai_questions = (
        db.query(func.count(ChatMessage.id))
        .join(Chat, ChatMessage.chat_id == Chat.id)
        .filter(Chat.user_id == user.id, ChatMessage.role == MessageRole.USER)
        .scalar()
    ) or 0

    statistics = DashboardStatistics(
        total_workspaces=total_workspaces,
        total_chats=total_chats,
        total_documents=total_documents,
        total_ai_questions=total_ai_questions,
    )

    # Activity chart: last 7 days
    now = datetime.now(timezone.utc)
    start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    chat_counts = (
        db.query(
            func.date_trunc('day', Chat.created_at).label('day'),
            func.count(Chat.id).label('count')
        )
        .filter(Chat.user_id == user.id, Chat.created_at >= start_date)
        .group_by('day')
        .all()
    )

    days_list = [now - timedelta(days=6-i) for i in range(7)]
    counts_dict = {r[0].date(): r[1] for r in chat_counts if r[0]}
    chats_per_day = []
    for d in days_list:
        chats_per_day.append(ActivityDay(
            date=d.date().isoformat(),
            label=d.strftime("%d/%m"),
            count=counts_dict.get(d.date(), 0)
        ))

    # Total activity this month
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    chats_month = db.query(func.count(Chat.id)).filter(Chat.user_id == user.id, Chat.created_at >= start_of_month).scalar() or 0
    docs_month = db.query(func.count(Document.id)).filter(Document.user_id == user.id, Document.created_at >= start_of_month).scalar() or 0
    workspaces_month = db.query(func.count(Workspace.id)).filter(Workspace.user_id == user.id, Workspace.created_at >= start_of_month).scalar() or 0
    total_activity_this_month = chats_month + docs_month + workspaces_month

    activity_chart = DashboardActivity(
        chats_per_day=chats_per_day,
        total_activity_this_month=total_activity_this_month,
    )

    # Recent activity timeline
    recent_chats = db.query(Chat).filter(Chat.user_id == user.id).order_by(Chat.created_at.desc()).limit(10).all()
    recent_docs = db.query(Document).filter(Document.user_id == user.id).order_by(Document.created_at.desc()).limit(10).all()
    recent_workspaces = db.query(Workspace).filter(Workspace.user_id == user.id).order_by(Workspace.created_at.desc()).limit(10).all()

    activities = []
    for c in recent_chats:
        activities.append(RecentActivityItem(
            id=str(c.id),
            type="chat_created",
            title=c.title,
            created_at=c.created_at,
            meta={"workspace_id": str(c.workspace_id) if c.workspace_id else None}
        ))
    for d in recent_docs:
        activities.append(RecentActivityItem(
            id=str(d.id),
            type="document_uploaded",
            title=d.title,
            created_at=d.created_at,
            meta={"workspace_id": str(d.workspace_id) if d.workspace_id else None}
        ))
    for w in recent_workspaces:
        activities.append(RecentActivityItem(
            id=str(w.id),
            type="workspace_created",
            title=w.name,
            created_at=w.created_at,
            meta={}
        ))

    activities.sort(key=lambda x: x.created_at, reverse=True)
    recent_activity = activities[:10]

    # Favorite Workspace based on chat counts
    fav_query = (
        db.query(
            Workspace.id,
            Workspace.name,
            Workspace.color,
            Workspace.icon,
            func.count(Chat.id).label('chat_count')
        )
        .join(Chat, Chat.workspace_id == Workspace.id)
        .filter(Workspace.user_id == user.id)
        .group_by(Workspace.id)
        .order_by(desc('chat_count'))
        .first()
    )

    favorite_workspace = None
    if fav_query:
        favorite_workspace = FavoriteWorkspace(
            id=fav_query[0],
            name=fav_query[1],
            color=fav_query[2],
            icon=fav_query[3],
            chat_count=fav_query[4],
        )

    return UserDashboardResponse(
        profile=dashboard_profile,
        statistics=statistics,
        activity_chart=activity_chart,
        recent_activity=recent_activity,
        favorite_workspace=favorite_workspace,
    )


def update_user_profile(db: Session, user: User, payload: ProfileUpdateRequest) -> UserDashboardResponse:
    profile = user.profile
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.flush()

    if payload.full_name is not None:
        name = payload.full_name.strip()
        if not name:
            raise ValueError("Họ và tên không được để trống")
        profile.full_name = name

    if payload.gender is not None:
        try:
            profile.gender = GenderType(payload.gender)
        except ValueError:
            raise ValueError(f"Giới tính không hợp lệ: {payload.gender}")

    if payload.avatar_url is not None:
        profile.avatar_url = payload.avatar_url.strip() or None

    db.commit()
    db.refresh(user)
    return get_user_dashboard(db, user)

