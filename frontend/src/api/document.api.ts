import { apiClient } from "./axios"

export interface Document {
  id: string
  workspace_id: string
  folder_id: string | null
  title: string
  description: string | null
  file_name: string
  file_type: string
  file_size: number
  status: string
  view_count: number
  created_at: string
  updated_at: string
}

export const documentApi = {
  list: (workspaceId: string, folderId?: string) => {
    let url = `/documents?workspace_id=${workspaceId}`
    if (folderId) {
      url += `&folder_id=${folderId}`
    }
    return apiClient.get<Document[]>(url)
  },
  
  get: (id: string) => apiClient.get<Document>(`/documents/${id}`),
  
  delete: (id: string) => apiClient.delete<{ message: string }>(`/documents/${id}`),

  bulkDelete: (ids: string[]) =>
    apiClient.delete<{ message: string }>("/documents/bulk", {
      data: { document_ids: ids },
    }),

    upload: (
    workspaceId: string,
    file: File,
    onProgress?: (progress: number) => void,
    folderId?: string,
    title?: string,
    description?: string,
    signal?: AbortSignal
  ) => {
    const formData = new FormData()
    formData.append("workspace_id", workspaceId)
    formData.append("file", file)
    
    if (folderId) formData.append("folder_id", folderId)
    if (title) formData.append("title", title)
    if (description) formData.append("description", description)

    return apiClient.post<Document>("/documents/upload", formData, {
      signal,
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
  },
}
