export interface Citation {
  document_id?: string;
  document_name: string;
  workspace_id?: string;
  workspace_name?: string;
  folder_id?: string;
  folder_name?: string;
  page_number?: number;
  heading?: string;
  chunk_id?: string;
  chunk_index?: number;
  confidence?: number;
  confidence_level?: 'High' | 'Medium' | 'Fair' | 'Low';
  source_type: string;
  excerpt?: string;
  url?: string;
  document_url?: string;
  line_start?: number;
  line_end?: number;
  start_offset?: number;
  end_offset?: number;
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
