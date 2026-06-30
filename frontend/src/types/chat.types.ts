export interface Citation {
  document_name: string;
  page_number?: number;
  line_start?: number;
  line_end?: number;
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
  title: string;
  chat_mode: 'global' | 'workspace' | 'folder' | 'document';
  message_count: number;
  created_at: string;
  updated_at: string;
}
