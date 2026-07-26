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

export interface UserDashboardOverviewResponse {
  statistics: DashboardStatistics
  learning_analytics: LearningAnalytics
  heatmap: HeatmapDay[]
  recent_activities: RecentActivityItem[]
}

export const dashboardApi = {
  getOverview: () => apiClient.get<UserDashboardOverviewResponse>("/dashboard/overview"),
  getHeatmap: (days: number = 90) => apiClient.get<HeatmapDay[]>(`/dashboard/heatmap?days=${days}`),
}
