import { apiClient } from './axios';
import { Chat, ChatMessage } from '../types/chat.types';

export const chatApi = {
  getChats: async (workspaceId?: string) => {
    const params = workspaceId ? { workspace_id: workspaceId } : {};
    const { data } = await apiClient.get<Chat[]>('/chats', { params });
    return data;
  },

  createChat: async (
    title: string,
    workspaceId?: string,
    folderId?: string,
    documentId?: string,
    chatMode: string = 'global'
  ) => {
    const { data } = await apiClient.post<Chat>('/chats', {
      title,
      workspace_id: workspaceId,
      folder_id: folderId,
      document_id: documentId,
      chat_mode: chatMode,
    });
    return data;
  },

  getChat: async (chatId: string) => {
    const { data } = await apiClient.get<Chat>(`/chats/${chatId}`);
    return data;
  },

  getChatMessages: async (chatId: string) => {
    const { data } = await apiClient.get<ChatMessage[]>(`/chats/${chatId}/messages`);
    return data;
  },

  sendMessage: async (chatId: string, content: string) => {
    const { data } = await apiClient.post<ChatMessage>(`/chats/${chatId}/messages`, {
      content,
    });
    return data;
  },

  updateChat: async (chatId: string, payload: { title?: string; is_favorite?: boolean }) => {
    const { data } = await apiClient.patch<Chat>(`/chats/${chatId}`, payload);
    return data;
  },

  deleteChat: async (chatId: string) => {
    await apiClient.delete(`/chats/${chatId}`);
  },
};
