import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { chatApi } from '@/api/chat.api';
import { ChatMessage } from '@/types/chat.types';
import { CitationPanel } from '@/components/chat/CitationPanel';

export default function ChatPage() {
  const { id } = useParams();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatId, setChatId] = useState<string | null>(id || null);

  useEffect(() => {
    // If we have an id but no messages, we might want to fetch history here later
    // For now, if no ID, we'll create one on first message
  }, [id]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      chat_id: chatId || 'temp',
      role: 'user',
      content: input,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      let currentChatId = chatId;
      // Create chat if it doesn't exist
      if (!currentChatId) {
        const newChat = await chatApi.createChat('New Chat Session');
        currentChatId = newChat.id;
        setChatId(currentChatId);
      }

      const aiResponse = await chatApi.sendMessage(currentChatId, userMessage.content);
      setMessages((prev) => [...prev, aiResponse]);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Handle error visually if needed
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)]">
      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardHeader className="border-b">
          <CardTitle>{chatId ? `Chat Session` : 'Cuộc trò chuyện mới'}</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center text-muted-foreground mt-10">
              Bắt đầu cuộc trò chuyện với DevHub AI
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    msg.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{msg.content}</div>
                </div>
                {msg.role === 'assistant' && msg.citations && msg.citations.length > 0 && (
                  <div className="max-w-[80%] w-full mt-1">
                    <CitationPanel citations={msg.citations} />
                  </div>
                )}
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex items-start">
              <div className="bg-gray-100 text-gray-800 rounded-lg p-3">
                <span className="animate-pulse">Đang suy nghĩ...</span>
              </div>
            </div>
          )}
        </CardContent>
        <div className="p-4 border-t bg-white">
          <form onSubmit={handleSend} className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Nhập câu hỏi của bạn..."
              className="flex-1 px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              Gửi
            </button>
          </form>
        </div>
      </Card>
    </div>
  );
}
