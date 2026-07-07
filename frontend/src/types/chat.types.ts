export interface Citation {
  document_name: string;
  source_type: string;
  page_number?: number;
  line_start?: number;
  line_end?: number;
  heading?: string;
  url?: string;
}

export interface ChatMessage {
  id: string;
  chat_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  retrieved_chunk_count?: number;
  citations?: Citation[];
}

export interface Chat {
  id: string;
  workspace_id?: string;
  folder_id?: string;
  document_id?: string;
  title: string;
  chat_mode: 'global' | 'workspace' | 'folder' | 'document' | 'website';
  is_favorite: boolean;
  status: 'active' | 'generating' | 'failed' | 'completed';
  message_count: number;
  created_at: string;
  updated_at: string;
  
  // Raw metadata from backend
  workspace_name?: string;
  folder_name?: string;
  document_name?: string;
  last_message_content?: string;
}
