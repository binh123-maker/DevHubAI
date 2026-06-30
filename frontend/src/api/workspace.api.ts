import { apiClient } from "./axios"

export interface Workspace {
  id: string
  name: string
  description: string | null
  color: string
  icon: string
  created_at: string
  updated_at: string
}

export interface WorkspaceCreatePayload {
  name: string
  description?: string | null
  color?: string
  icon?: string
}

export interface WorkspaceUpdatePayload {
  name?: string
  description?: string | null
  color?: string
  icon?: string
}

export const workspaceApi = {
  list: () => apiClient.get<Workspace[]>("/workspaces"),
  get: (id: string) => apiClient.get<Workspace>(`/workspaces/${id}`),
  create: (payload: WorkspaceCreatePayload) => apiClient.post<Workspace>("/workspaces", payload),
  update: (id: string, payload: WorkspaceUpdatePayload) => apiClient.put<Workspace>(`/workspaces/${id}`, payload),
  delete: (id: string) => apiClient.delete<{ message: string }>(`/workspaces/${id}`),
}
