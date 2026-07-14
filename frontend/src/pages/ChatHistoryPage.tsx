import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQueryClient } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { chatApi } from '@/api/chat.api';
import { Chat, ChatMessage } from '@/types/chat.types';
import { CitationPanel } from '@/components/chat/CitationPanel';
import { NewChatScopeDialog, ScopeSelection } from '@/components/chat/NewChatScopeDialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { isToday, isYesterday, isWithinInterval, subDays } from 'date-fns';
import { Folder, FileText, Globe, Box, MoreVertical, Pin, Pencil, Trash, Plus, Search } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import rehypeRaw from 'rehype-raw';
import 'katex/dist/katex.min.css';

export default function ChatHistoryPage() {
  const { chatId } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const [chats, setChats] = useState<Chat[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRestoring, setIsRestoring] = useState(false);
  const [isCreatingChat, setIsCreatingChat] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [pendingScope, setPendingScope] = useState<ScopeSelection | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesRef = useRef(messages);
  const isCreatingChatRef = useRef(isCreatingChat);

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  useEffect(() => {
    isCreatingChatRef.current = isCreatingChat;
  }, [isCreatingChat]);

  const loadChats = useCallback(async () => {
    try {
      const data = await chatApi.getChats();
      setChats(data);
    } catch (e) {
      console.error(e);
    }
  }, []);

  const loadMessages = useCallback(async (id: string) => {
    console.debug('[LOG 8] loadMessages start', { timestamp: new Date().toISOString(), chatId, messagesLength: messagesRef.current.length, isCreatingChat: isCreatingChatRef.current, targetId: id });
    // Prevent loading from backend if we are in the middle of creating/sending the first message
    if (isCreatingChatRef.current) return;

    // Avoid duplicate calls if messages are already loaded for this chat
    if (messagesRef.current.length > 0 && messagesRef.current[0]?.chat_id === id) return;

    try {
      setIsRestoring(true);
      console.debug('[LOG 9] GET /messages request', { timestamp: new Date().toISOString(), chatId, messagesLength: messagesRef.current.length, isCreatingChat: isCreatingChatRef.current });
      const data = await chatApi.getChatMessages(id);
      console.debug('[LOG 10] GET /messages response received', { timestamp: new Date().toISOString(), chatId, messagesLength: messagesRef.current.length, isCreatingChat: isCreatingChatRef.current, responseLength: data.length });
      console.debug('[LOG 11] setMessages(data) call', { timestamp: new Date().toISOString(), chatId, messagesLength: messagesRef.current.length, isCreatingChat: isCreatingChatRef.current });
      setMessages(data);
    } catch (e: any) {
      console.error(e);
      if (e.response?.status === 404 || e.response?.status === 403) {
        navigate('/history');
      }
    } finally {
      setIsRestoring(false);
    }
  }, [chatId, navigate]);

  useEffect(() => {
    loadChats();
  }, [loadChats]);

  useEffect(() => {
    console.debug('[LOG 7] useEffect(chatId) triggered', { timestamp: new Date().toISOString(), chatId, messagesLength: messagesRef.current.length, isCreatingChat: isCreatingChatRef.current });
    if (chatId) {
      setPendingScope(null);
      loadMessages(chatId);
    } else {
      setMessages([]);
    }
  }, [chatId, loadMessages]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    console.debug('[LOG 1] handleSend start', { timestamp: new Date().toISOString(), chatId, messagesLength: messages.length, isCreatingChat });

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
      if (!currentChatId) {
        if (!pendingScope) {
          setIsDialogOpen(true);
          setIsLoading(false);
          return;
        }

        console.debug('[LOG 2] setIsCreatingChat(true) call', { timestamp: new Date().toISOString(), chatId, messagesLength: messages.length, isCreatingChat });
        setIsCreatingChat(true);

        // Use auto-title if empty, or pendingScope.chatName
        const title = pendingScope.chatName || "Cuộc trò chuyện mới";
        console.debug('[LOG 3] createChat request', { timestamp: new Date().toISOString(), chatId, messagesLength: messages.length, isCreatingChat });
        const newChat = await chatApi.createChat(
          title,
          pendingScope.workspaceId,
          pendingScope.folderId,
          pendingScope.documentId,
          pendingScope.chatMode
        );
        console.debug('[LOG 4] createChat resolved', { timestamp: new Date().toISOString(), chatId, messagesLength: messages.length, isCreatingChat, newChatId: newChat.id });
        const createdChatId = newChat.id;
        currentChatId = createdChatId;

        // Optimistically replace 'temp' chat_id with the real chat ID before navigation
        console.debug('[LOG 5] setMessages(temp->real) call', { timestamp: new Date().toISOString(), chatId, messagesLength: messages.length, isCreatingChat, currentChatId });
        setMessages(prev => prev.map(m => m.chat_id === 'temp' ? { ...m, chat_id: createdChatId } : m));

        console.debug('[LOG 6] navigate() call', { timestamp: new Date().toISOString(), chatId, messagesLength: messages.length, isCreatingChat, currentChatId });
        navigate(`/history/${currentChatId}`, { replace: true });
        setPendingScope(null);
        await loadChats();
      }

      if (!currentChatId) return;

      console.debug('[LOG 12] sendMessage request', { timestamp: new Date().toISOString(), chatId, messagesLength: messages.length, isCreatingChat, currentChatId });
      const aiResponse = await chatApi.sendMessage(currentChatId, userMessage.content);
      console.debug('[LOG 13] sendMessage response received', { timestamp: new Date().toISOString(), chatId, messagesLength: messages.length, isCreatingChat });

      console.debug('[LOG 14] setMessages(ai) call', { timestamp: new Date().toISOString(), chatId, messagesLength: messages.length, isCreatingChat });
      setMessages((prev) => {
        const updatedPrev = prev.map(m => m.chat_id === 'temp' ? { ...m, chat_id: currentChatId } : m);
        return [...updatedPrev, aiResponse];
      });

      await loadChats();
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      console.debug('[LOG 15] finally block', { timestamp: new Date().toISOString(), chatId, messagesLength: messages.length, isCreatingChat });
      setIsLoading(false);
      setIsCreatingChat(false);
    }
  };

  const handleStartChat = (selection: ScopeSelection) => {
    setPendingScope(selection);
    navigate('/history');
  };

  const handleRename = async (id: string, currentTitle: string) => {
    const newTitle = window.prompt("Nhập tên mới:", currentTitle);
    if (newTitle && newTitle.trim() !== currentTitle) {
      await chatApi.updateChat(id, { title: newTitle.trim() });
      loadChats();
    }
  };

  const handleDelete = async (id: string) => {
    if (window.confirm("Bạn có chắc muốn xóa cuộc trò chuyện này?")) {
      try {
        await chatApi.deleteChat(id);
        void queryClient.invalidateQueries({ queryKey: ["dashboardData"] });
        if (chatId === id) {
          setMessages([]);
          setPendingScope(null);
          navigate('/history', { replace: true });
        }
        await loadChats();
      } catch (error) {
        console.error('Failed to delete chat:', error);
      }
    }
  };

  const handleTogglePin = async (id: string, current: boolean) => {
    await chatApi.updateChat(id, { is_favorite: !current });
    loadChats();
  };

  const getScopeIcon = (mode: string) => {
    switch (mode) {
      case 'workspace': return <Box className="w-4 h-4" />;
      case 'folder': return <Folder className="w-4 h-4" />;
      case 'document': return <FileText className="w-4 h-4" />;
      default: return <Globe className="w-4 h-4" />;
    }
  };

  const filteredChats = chats.filter(c => c.title.toLowerCase().includes(searchQuery.toLowerCase()));

  const pinned = filteredChats.filter(c => c.is_favorite);
  const unpinned = filteredChats.filter(c => !c.is_favorite);

  const today = unpinned.filter(c => isToday(new Date(c.updated_at)));
  const yesterday = unpinned.filter(c => isYesterday(new Date(c.updated_at)));
  const previous7Days = unpinned.filter(c => !isToday(new Date(c.updated_at)) && !isYesterday(new Date(c.updated_at)) && isWithinInterval(new Date(c.updated_at), { start: subDays(new Date(), 7), end: new Date() }));
  const older = unpinned.filter(c => !isToday(new Date(c.updated_at)) && !isYesterday(new Date(c.updated_at)) && !isWithinInterval(new Date(c.updated_at), { start: subDays(new Date(), 7), end: new Date() }));

  const renderChatGroup = (title: string, list: Chat[]) => {
    if (list.length === 0) return null;
    return (
      <div className="mb-6">
        <h3 className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">{title}</h3>
        <div className="space-y-1">
          {list.map(c => (
            <div
              key={c.id}
              onClick={() => navigate(`/history/${c.id}`)}
              className={`group flex items-center justify-between px-3 py-2 text-sm rounded-md cursor-pointer hover:bg-accent transition-colors ${chatId === c.id ? 'bg-accent' : ''}`}
            >
              <div className="flex items-center space-x-3 overflow-hidden">
                <span className="text-muted-foreground">{getScopeIcon(c.chat_mode)}</span>
                <div className="flex flex-col overflow-hidden">
                  <span className="truncate font-medium">{c.title}</span>
                  {c.last_message_content && (
                    <span className="text-xs text-muted-foreground truncate opacity-70">
                      {c.last_message_content.length > 40 ? c.last_message_content.substring(0, 40) + '...' : c.last_message_content}
                    </span>
                  )}
                </div>
              </div>
              <div
                className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none group-hover:pointer-events-auto"
                onPointerDown={(e) => e.stopPropagation()}
                onClick={(e) => e.stopPropagation()}
              >
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-6 w-6">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onSelect={() => handleTogglePin(c.id, c.is_favorite)}>
                      <Pin className="mr-2 h-4 w-4" /> {c.is_favorite ? 'Bỏ ghim' : 'Ghim'}
                    </DropdownMenuItem>
                    <DropdownMenuItem onSelect={() => handleRename(c.id, c.title)}>
                      <Pencil className="mr-2 h-4 w-4" /> Đổi tên
                    </DropdownMenuItem>
                    <DropdownMenuItem className="text-red-600" onSelect={() => handleDelete(c.id)}>
                      <Trash className="mr-2 h-4 w-4" /> Xóa
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderScopeBadge = () => {
    if (pendingScope) {
      if (pendingScope.chatMode === 'global') return "Entire Knowledge Base";
      if (pendingScope.chatMode === 'website') return "Imported Websites";
      return `${pendingScope.chatMode.toUpperCase()} scope selected`;
    }

    if (chatId) {
      const c = chats.find(x => x.id === chatId);
      if (c) {
        if (c.chat_mode === 'global') return "Entire Knowledge Base";
        if (c.chat_mode === 'website') return "Imported Websites";
        const parts = [];
        parts.push(c.chat_mode.charAt(0).toUpperCase() + c.chat_mode.slice(1));
        if (c.workspace_name) parts.push(c.workspace_name);
        if (c.folder_name) parts.push(c.folder_name);
        if (c.document_name) parts.push(c.document_name);
        return parts.join(' • ');
      }
    }
    return null;
  };

  return (
    <div className="flex h-[calc(100vh-2rem)] gap-4">
      {/* Sidebar */}
      <Card className="w-80 flex flex-col overflow-hidden bg-background">
        <div className="p-4 border-b space-y-4">
          <Button className="w-full justify-start shadow-sm" onClick={() => setIsDialogOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Chat
          </Button>
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search history..."
              className="pl-9 bg-accent/50"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {renderChatGroup("Ghim", pinned)}
          {renderChatGroup("Hôm nay", today)}
          {renderChatGroup("Hôm qua", yesterday)}
          {renderChatGroup("7 ngày trước", previous7Days)}
          {renderChatGroup("Cũ hơn", older)}
        </div>
      </Card>

      {/* Main Chat Area */}
      <Card className="flex-1 flex flex-col overflow-hidden relative">
        {renderScopeBadge() && (
          <div className="absolute top-0 left-0 right-0 z-10 flex justify-center p-2">
            <div className="bg-muted text-muted-foreground text-xs px-3 py-1 rounded-full shadow-sm flex items-center gap-2">
              <Globe className="w-3 h-3" />
              {renderScopeBadge()}
            </div>
          </div>
        )}

        <CardContent className="flex-1 overflow-y-auto p-4 pt-12 space-y-6">
          {(!chatId && !pendingScope) ? (
            <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
              <h2 className="text-2xl font-bold text-muted-foreground">DevHub AI Chat</h2>
              <p className="text-muted-foreground max-w-sm">
                Bắt đầu một cuộc trò chuyện mới hoặc chọn một cuộc trò chuyện từ lịch sử bên trái.
              </p>
              <Button onClick={() => setIsDialogOpen(true)}>Bắt đầu trò chuyện</Button>
            </div>
          ) : isRestoring ? (
            <div className="flex items-center justify-center h-full">
              <span className="flex space-x-1">
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce"></span>
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce delay-75"></span>
                <span className="w-2 h-2 bg-primary rounded-full animate-bounce delay-150"></span>
              </span>
            </div>
          ) : (
            <>
              {messages.length === 0 && !isLoading ? (
                <div className="flex flex-col items-center justify-center h-full text-center">
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                    <Search className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-lg font-medium">Bạn cần giúp gì hôm nay?</h3>
                  <p className="text-sm text-muted-foreground mt-2 max-w-sm">
                    AI sẽ tìm kiếm và trả lời dựa trên phạm vi tài liệu bạn đã chọn.
                  </p>
                </div>
              ) : (
                messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl p-4 shadow-sm ${msg.role === 'user'
                        ? 'bg-primary text-primary-foreground rounded-br-sm'
                        : 'bg-muted text-foreground rounded-bl-sm border'
                        }`}
                    >
                      {msg.role === 'assistant' ? (
                        <ReactMarkdown
                          remarkPlugins={[remarkMath]}
                          rehypePlugins={[rehypeKatex, rehypeRaw]}
                          className="prose dark:prose-invert max-w-none text-sm leading-relaxed"
                          components={{
                            p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                            code({ className, children, ...props }) {
                              const match = /language-(\w+)/.exec(className || '');
                              return match ? (
                                <pre className="bg-accent/40 rounded-lg p-3 my-2 overflow-x-auto border border-accent">
                                  <code className={`${className || ''} text-xs`} {...props}>
                                    {children}
                                  </code>
                                </pre>
                              ) : (
                                <code className="bg-accent/40 px-1.5 py-0.5 rounded text-xs border border-accent/60 font-mono" {...props}>
                                  {children}
                                </code>
                              );
                            }
                          }}
                        >
                          {msg.content}
                        </ReactMarkdown>
                      ) : (
                        <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                      )}
                    </div>
                    {msg.role === 'assistant' && msg.citations && msg.citations.length > 0 && (
                      <div className="max-w-[80%] w-full mt-2">
                        <CitationPanel citations={msg.citations} />
                      </div>
                    )}
                  </div>
                ))
              )}
              {isLoading && (
                <div className="flex items-start">
                  <div className="bg-muted text-foreground rounded-2xl rounded-bl-sm border p-4 shadow-sm">
                    <span className="flex space-x-1">
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce"></span>
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce delay-75"></span>
                      <span className="w-2 h-2 bg-primary rounded-full animate-bounce delay-150"></span>
                    </span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </CardContent>

        {(chatId || pendingScope) && (
          <div className="p-4 bg-background border-t">
            <form onSubmit={handleSend} className="max-w-3xl mx-auto flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Nhập câu hỏi của bạn..."
                className="flex-1 rounded-full px-6 bg-accent/50 border-accent focus-visible:ring-1"
                disabled={isLoading}
              />
              <Button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="rounded-full px-6"
              >
                Gửi
              </Button>
            </form>
          </div>
        )}
      </Card>

      <NewChatScopeDialog
        open={isDialogOpen}
        onOpenChange={setIsDialogOpen}
        onStartChat={handleStartChat}
      />
    </div>
  );
}
