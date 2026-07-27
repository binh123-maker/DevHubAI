import { apiClient } from "./axios"

export interface DashboardStatistics {
  total_workspaces: number
  total_folders: number
  total_documents: number
  total_conversations: number
  total_messages: number
  total_uploads: number
  documents_processed: number
  learning_streak_days: number
  total_chunks?: number
  indexed_documents?: number
  failed_documents?: number
  embedding_status?: string
  search_health?: string
  latest_processing_time?: string | null
  avg_retrieval_time_ms?: number
}

export interface MostActiveWorkspace {
  id: string
  name: string
  color: string
  icon: string
  activity_count: number
}

export interface LearningAnalytics {
  learning_streak_days: number
  most_active_workspace: MostActiveWorkspace | null
  weekly_activity_count: number
  monthly_activity_count: number
}

export interface HeatmapDay {
  date: string
  count: number
}

export interface RecentActivityItem {
  id: string
  type: string
  title: string
  description: string
  created_at: string
  meta?: Record<string, any> | null
}

export interface DocumentSummaryItem {
  id: string
  title: string
  workspace_id: string
  workspace_name?: string | null
  file_type: string
  file_size: number
  status: string
  kanban_status: string
  view_count: number
  last_opened_at?: string | null
  total_chunks?: number
  created_at: string
  updated_at: string
}

export interface RecentWorkspaceItem {
  id: string
  name: string
  color: string
  document_count: number
  updated_at: string
}

export interface UserDashboardOverviewResponse {
  statistics: DashboardStatistics
  learning_analytics: LearningAnalytics
  heatmap: HeatmapDay[]
  recent_activities: RecentActivityItem[]
  recent_documents?: DocumentSummaryItem[]
  recently_processed?: DocumentSummaryItem[]
  recently_opened?: DocumentSummaryItem[]
  favorite_documents?: DocumentSummaryItem[]
  recent_workspaces?: RecentWorkspaceItem[]
  kanban_summary?: Record<string, number>
  knowledge_health?: Record<string, any>
}

export const dashboardApi = {
  getOverview: () => apiClient.get<UserDashboardOverviewResponse>("/dashboard/overview"),
  getHeatmap: (days: number = 90) => apiClient.get<HeatmapDay[]>(`/dashboard/heatmap?days=${days}`),
}
