import { apiClient } from "./axios"

export interface Folder {
  id: string
  workspace_id: string
  parent_id: string | null
  name: string
  description: string | null
  sort_order: number
  created_at: string
  updated_at: string
}

export interface FolderCreatePayload {
  workspace_id: string
  parent_id?: string | null
  name: string
  description?: string | null
}

export interface FolderUpdatePayload {
  name?: string
  description?: string | null
  parent_id?: string | null
  sort_order?: number
}

export const folderApi = {
  list: (workspaceId: string) => apiClient.get<Folder[]>(`/folders?workspace_id=${workspaceId}`),
  get: (id: string) => apiClient.get<Folder>(`/folders/${id}`),
  create: (payload: FolderCreatePayload) => apiClient.post<Folder>("/folders", payload),
  update: (id: string, payload: FolderUpdatePayload) => apiClient.put<Folder>(`/folders/${id}`, payload),
  delete: (id: string) => apiClient.delete<{ message: string }>(`/folders/${id}`),
}
