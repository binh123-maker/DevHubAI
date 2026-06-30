import { apiClient } from './axios';
import { Chat, ChatMessage } from '../types/chat.types';

export const chatApi = {
  getChats: async (workspaceId?: string) => {
    const params = workspaceId ? { workspace_id: workspaceId } : {};
    const { data } = await apiClient.get<Chat[]>('/chats', { params });
    return data;
  },

  createChat: async (title: string, workspaceId?: string, chatMode: string = 'global') => {
    const { data } = await apiClient.post<Chat>('/chats', {
      title,
      workspace_id: workspaceId,
      chat_mode: chatMode,
    });
    return data;
  },

  getChat: async (chatId: string) => {
    const { data } = await apiClient.get<Chat>(`/chats/${chatId}`);
    return data;
  },

  sendMessage: async (chatId: string, content: string) => {
    const { data } = await apiClient.post<ChatMessage>(`/chats/${chatId}/messages`, {
      content,
    });
    return data;
  },
};
