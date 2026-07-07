import { apiClient } from "./axios"

export interface DashboardProfile {
  email: string
  full_name: string
  role: string
  avatar_url: string | null
  gender: string
  created_at: string
}

export interface DashboardStatistics {
  total_workspaces: number
  total_chats: number
  total_documents: number
  total_ai_questions: number
}

export interface ActivityDay {
  date: string
  label: string
  count: number
}

export interface DashboardActivity {
  chats_per_day: ActivityDay[]
  total_activity_this_month: number
}

export interface RecentActivityItem {
  id: string
  type: "chat_created" | "document_uploaded" | "workspace_created"
  title: string
  created_at: string
  meta: {
    workspace_id?: string | null
  }
}

export interface FavoriteWorkspace {
  id: string
  name: string
  color: string
  icon: string
  chat_count: number
}

export interface UserDashboardResponse {
  profile: DashboardProfile
  statistics: DashboardStatistics
  activity_chart: DashboardActivity
  recent_activity: RecentActivityItem[]
  favorite_workspace: FavoriteWorkspace | null
}

export interface ProfileUpdateRequest {
  full_name?: string
  gender?: string
  avatar_url?: string
}

export const profileApi = {
  getDashboardData: () => apiClient.get<UserDashboardResponse>("/users/me/dashboard"),
  deleteAllChats: () => apiClient.delete("/users/me/chats"),
  updateProfile: (payload: ProfileUpdateRequest) => apiClient.patch<UserDashboardResponse>("/users/me/profile", payload),
}

