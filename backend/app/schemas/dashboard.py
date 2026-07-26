from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class DashboardStatistics(BaseModel):
    total_workspaces: int
    total_folders: int
    total_documents: int
    total_conversations: int
    total_messages: int
    total_uploads: int
    documents_processed: int
    learning_streak_days: int


class MostActiveWorkspace(BaseModel):
    id: UUID
    name: str
    color: str
    icon: str
    activity_count: int


class LearningAnalytics(BaseModel):
    learning_streak_days: int
    most_active_workspace: MostActiveWorkspace | None = None
    weekly_activity_count: int
    monthly_activity_count: int


class HeatmapDay(BaseModel):
    date: str
    count: int


class RecentActivityItem(BaseModel):
    id: str
    type: str  # e.g., 'document_uploaded', 'document_processed', 'workspace_created', 'chat_created', 'kanban_moved'
    title: str
    description: str
    created_at: datetime
    meta: dict | None = None


class UserDashboardOverviewResponse(BaseModel):
    statistics: DashboardStatistics
    learning_analytics: LearningAnalytics
    heatmap: list[HeatmapDay]
    recent_activities: list[RecentActivityItem]
