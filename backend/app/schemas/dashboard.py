from datetime import datetime
from typing import Any
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
    total_chunks: int = 0
    indexed_documents: int = 0
    failed_documents: int = 0
    embedding_status: str = "Healthy"
    search_health: str = "100% Operational"
    latest_processing_time: str | None = None
    avg_retrieval_time_ms: int = 120


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


class DocumentSummaryItem(BaseModel):
    id: UUID
    title: str
    workspace_id: UUID
    workspace_name: str | None = None
    file_type: str
    file_size: int
    status: str
    kanban_status: str
    view_count: int
    last_opened_at: datetime | None = None
    total_chunks: int = 0
    created_at: datetime
    updated_at: datetime


class RecentWorkspaceItem(BaseModel):
    id: UUID
    name: str
    color: str
    document_count: int
    updated_at: datetime


class UserDashboardOverviewResponse(BaseModel):
    statistics: DashboardStatistics
    learning_analytics: LearningAnalytics
    heatmap: list[HeatmapDay]
    recent_activities: list[RecentActivityItem]
    recent_documents: list[DocumentSummaryItem] = []
    recently_processed: list[DocumentSummaryItem] = []
    recently_opened: list[DocumentSummaryItem] = []
    favorite_documents: list[DocumentSummaryItem] = []
    recent_workspaces: list[RecentWorkspaceItem] = []
    kanban_summary: dict[str, int] = {"new": 0, "learning": 0, "completed": 0, "archived": 0}
    knowledge_health: dict[str, Any] = {}
