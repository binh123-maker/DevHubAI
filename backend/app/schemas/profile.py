from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

class DashboardProfile(BaseModel):
    email: str
    full_name: str
    role: str
    avatar_url: str | None = None
    gender: str
    created_at: datetime

    class Config:
        from_attributes = True

class DashboardStatistics(BaseModel):
    total_workspaces: int = 0  # wait, in python we must use type hint int, not number!
    total_chats: int = 0
    total_documents: int = 0
    total_ai_questions: int = 0

class ActivityDay(BaseModel):
    date: str
    label: str
    count: int

class DashboardActivity(BaseModel):
    chats_per_day: list[ActivityDay]
    total_activity_this_month: int

class RecentActivityItem(BaseModel):
    id: str
    type: str  # chat_created, document_uploaded, workspace_created
    title: str
    created_at: datetime
    meta: dict

class FavoriteWorkspace(BaseModel):
    id: UUID
    name: str
    color: str
    icon: str
    chat_count: int

    class Config:
        from_attributes = True

class UserDashboardResponse(BaseModel):
    profile: DashboardProfile
    statistics: DashboardStatistics
    activity_chart: DashboardActivity
    recent_activity: list[RecentActivityItem]
    favorite_workspace: FavoriteWorkspace | None = None


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    gender: str | None = None
    avatar_url: str | None = None

