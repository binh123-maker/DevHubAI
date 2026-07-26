import { useState, useEffect, useRef, useCallback } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"
import "katex/dist/katex.min.css"
import { ArrowDown } from "lucide-react"

import { chatApi } from "@/api/chat.api"
import type { Chat, ChatMessage, Citation } from "@/types/chat.types"
import { ChatLayout } from "@/components/chat/ChatLayout"
import { ChatHeader } from "@/components/chat/ChatHeader"
import { ChatComposer } from "@/components/chat/ChatComposer"
import { WelcomeChatState } from "@/components/chat/WelcomeChatState"
import { CitationDock } from "@/components/chat/CitationDock"
import { StreamingStatusIndicator } from "@/components/chat/StreamingStatusIndicator"
import { ConversationMetadataDialog } from "@/components/chat/ConversationMetadataDialog"
import { NewChatScopeDialog, ScopeSelection } from "@/components/chat/NewChatScopeDialog"
import { MessageSkeleton } from "@/components/chat/ConversationSkeleton"
import { VirtualMessageList } from "@/components/chat/VirtualMessageList"
import { EmptyKnowledgeCard } from "@/components/chat/EmptyKnowledgeCard"
import { ExportDialog } from "@/components/chat/ExportDialog"
import { DragDropOverlay } from "@/components/chat/DragDropOverlay"
import { ChatErrorBoundary } from "@/components/chat/ChatErrorBoundary"
import { useKeyboardShortcut } from "@/hooks/useKeyboardShortcut"
import { generateAutoTitle } from "@/utils/autoRename"
import { Button } from "@/components/ui/button"

export default function ChatHistoryPage() {
  const { chatId } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [chats, setChats] = useState<Chat[]>([])
  const [searchQuery, setSearchQuery] = useState("")
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isRestoring, setIsRestoring] = useState(false)
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [metadataOpen, setMetadataOpen] = useState(false)
  const [exportOpen, setExportOpen] = useState(false)
  const [citationDockOpen, setCitationDockOpen] = useState(false)
  const [activeChat, setActiveChat] = useState<Chat | null>(null)

  // Scroll lock & floating new messages button state
  const [showScrollToBottom, setShowScrollToBottom] = useState(false)
  const [isDraggingFile, setIsDraggingFile] = useState(false)
  const [attachedFiles, setAttachedFiles] = useState<File[]>([])

  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const scrollPositionsRef = useRef<Record<string, number>>({})
  const abortControllerRef = useRef<AbortController | null>(null)

  const scrollToBottom = useCallback((smooth = true) => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({
        top: scrollContainerRef.current.scrollHeight,
        behavior: smooth ? "smooth" : "auto",
      })
    }
  }, [])

  // Auto scroll to bottom during messaging if user is near bottom (<120px)
  useEffect(() => {
    if (!scrollContainerRef.current) return
    const { scrollHeight, scrollTop, clientHeight } = scrollContainerRef.current
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight

    if (distanceFromBottom < 120 || !showScrollToBottom) {
      scrollToBottom(true)
    }
  }, [messages, isLoading, showScrollToBottom, scrollToBottom])

  // Handle user scrolling inside message stream
  const handleScroll = () => {
    if (!scrollContainerRef.current) return
    const { scrollHeight, scrollTop, clientHeight } = scrollContainerRef.current
    const distanceFromBottom = scrollHeight - scrollTop - clientHeight

    if (distanceFromBottom > 120) {
      setShowScrollToBottom(true)
    } else {
      setShowScrollToBottom(false)
    }

    // Save scroll position for active chat
    if (chatId) {
      scrollPositionsRef.current[chatId] = scrollTop
    }
  }

  // Restore scroll position when switching active chat
  useEffect(() => {
    if (chatId && scrollContainerRef.current) {
      const savedPosition = scrollPositionsRef.current[chatId]
      if (savedPosition !== undefined) {
        scrollContainerRef.current.scrollTop = savedPosition
      } else {
        scrollToBottom(false)
      }
    }
  }, [chatId, scrollToBottom])

  // Drag & drop handlers
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDraggingFile(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.relatedTarget === null) {
      setIsDraggingFile(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDraggingFile(false)

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const filesArr = Array.from(e.dataTransfer.files)
      setAttachedFiles((prev) => [...prev, ...filesArr])
    }
  }

  // Keyboard Shortcuts
  useKeyboardShortcut("n", () => setIsDialogOpen(true), { ctrlKey: true, metaKey: true })

  const loadChats = useCallback(async () => {
    try {
      const data = await chatApi.getChats()
      setChats(data)
      if (chatId) {
        const found = data.find((c) => c.id === chatId)
        if (found) setActiveChat(found)
      }
    } catch (e) {
      console.error(e)
    }
  }, [chatId])

  const loadMessages = useCallback(
    async (id: string) => {
      try {
        setIsRestoring(true)
        const data = await chatApi.getChatMessages(id)
        setMessages(data)
      } catch (e: any) {
        console.error(e)
        if (e.response?.status === 404 || e.response?.status === 403) {
          navigate("/history")
        }
      } finally {
        setIsRestoring(false)
      }
    },
    [navigate]
  )

  useEffect(() => {
    loadChats()
  }, [loadChats])

  useEffect(() => {
    if (chatId) {
      loadMessages(chatId)
    } else {
      setMessages([])
      setActiveChat(null)
    }
  }, [chatId, loadMessages])

  const allCitations = messages.reduce<Citation[]>((acc, msg) => {
    if (msg.citations && msg.citations.length > 0) {
      return [...acc, ...msg.citations]
    }
    return acc
  }, [])

  const handleStartChatFromDialog = async (selection: ScopeSelection) => {
    try {
      const newChat = await chatApi.createChat(
        selection.chatName,
        selection.workspaceId,
        selection.folderId,
        selection.selectedDocumentIds ? selection.selectedDocumentIds[0] : undefined,
        selection.chatMode
      )
      setChats((prev) => [newChat, ...prev])
      navigate(`/history/${newChat.id}`)
    } catch (e) {
      console.error("Không thể tạo chat:", e)
    }
  }

  const handleSendMessage = async (customContent?: string) => {
    const textToSend = customContent || input
    if (!textToSend.trim() || isLoading) return

    setInput("")
    setIsLoading(true)
    setShowScrollToBottom(false)

    let currentChatId = chatId

    try {
      if (!currentChatId) {
        const autoTitle = generateAutoTitle(textToSend)
        const newChat = await chatApi.createChat(
          autoTitle,
          undefined,
          undefined,
          undefined,
          "global"
        )
        currentChatId = newChat.id
        setChats((prev) => [newChat, ...prev])
        navigate(`/history/${newChat.id}`, { replace: true })
      }

      const tempUserMsg: ChatMessage = {
        id: Date.now().toString(),
        chat_id: currentChatId,
        role: "user",
        content: textToSend,
        created_at: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, tempUserMsg])
      scrollToBottom(true)

      const aiResponse = await chatApi.sendMessage(currentChatId, textToSend)

      setMessages((prev) => [...prev, aiResponse])
      scrollToBottom(true)

      // Auto-rename chat title after 3 messages
      if (messages.length === 2 && currentChatId) {
        const autoTitle = generateAutoTitle(messages[0]?.content || textToSend)
        void chatApi.updateChat(currentChatId, { title: autoTitle })
      }

      void queryClient.invalidateQueries({ queryKey: ["dashboardOverview"] })
      void loadChats()
    } catch (e) {
      console.error("Lỗi khi gửi tin nhắn:", e)
    } finally {
      setIsLoading(false)
      setAttachedFiles([])
    }
  }

  const handleStopGeneration = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
      abortControllerRef.current = null
    }
    setIsLoading(false)
  }

  const handleRegenerate = async () => {
    if (messages.length < 2 || isLoading) return
    const lastUserMsg = [...messages].reverse().find((m) => m.role === "user")
    if (lastUserMsg) {
      setMessages((prev) => prev.slice(0, prev.length - 1))
      await handleSendMessage(lastUserMsg.content)
    }
  }

  const handleRenameChat = async (id: string, newTitle: string) => {
    await chatApi.updateChat(id, { title: newTitle })
    setChats((prev) => prev.map((c) => (c.id === id ? { ...c, title: newTitle } : c)))
    if (activeChat?.id === id) {
      setActiveChat((prev) => (prev ? { ...prev, title: newTitle } : null))
    }
  }

  const handleDuplicateChat = async (id: string) => {
    const duplicated = await chatApi.duplicateChat(id)
    setChats((prev) => [duplicated, ...prev])
    navigate(`/history/${duplicated.id}`)
  }

  const handleToggleFavoriteChat = async (id: string, isFavorite: boolean) => {
    await chatApi.updateChat(id, { is_favorite: isFavorite })
    setChats((prev) => prev.map((c) => (c.id === id ? { ...c, is_favorite: isFavorite } : c)))
  }

  const handleExportMarkdown = async (includeCitations: boolean) => {
    if (!chatId) return
    let markdownContent = await chatApi.exportChat(chatId)
    if (!includeCitations) {
      markdownContent = markdownContent.replace(/--- Trích dẫn[\s\S]*$/, "")
    }
    const blob = new Blob([markdownContent], { type: "text/markdown;charset=utf-8;" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.setAttribute("download", `DevHub_Chat_${chatId.slice(0, 8)}.md`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleExportTxt = async (includeCitations: boolean) => {
    if (!chatId) return
    let markdownContent = await chatApi.exportChat(chatId)
    if (!includeCitations) {
      markdownContent = markdownContent.replace(/--- Trích dẫn[\s\S]*$/, "")
    }
    const plainText = markdownContent.replace(/[#*`_]/g, "")
    const blob = new Blob([plainText], { type: "text/plain;charset=utf-8;" })
    const url = URL.createObjectURL(blob)
    const link = document.createElement("a")
    link.href = url
    link.setAttribute("download", `DevHub_Chat_${chatId.slice(0, 8)}.txt`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handlePrintPdf = () => {
    window.print()
  }

  const handleDeleteChat = async (id: string) => {
    await chatApi.deleteChat(id)
    setChats((prev) => prev.filter((c) => c.id !== id))
    if (chatId === id) {
      navigate("/history")
    }
  }

  const handleClearAllChats = async () => {
    await chatApi.clearAllChats()
    setChats([])
    setMessages([])
    navigate("/history")
  }

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className="h-full w-full flex flex-col overflow-hidden relative"
    >
      {/* Drag & Drop File Overlay */}
      <DragDropOverlay isVisible={isDraggingFile} />

      <ChatLayout
        chats={chats}
        activeChatId={chatId}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onNewChatClick={() => setIsDialogOpen(true)}
        onSelectChat={(id) => navigate(`/history/${id}`)}
        onRenameChat={handleRenameChat}
        onDuplicateChat={handleDuplicateChat}
        onToggleFavoriteChat={handleToggleFavoriteChat}
        onExportChat={async () => setExportOpen(true)}
        onDeleteChat={handleDeleteChat}
        onClearAllChats={handleClearAllChats}
      >
        {/* 1. Fixed Height 72px Chat Header */}
        <ChatHeader
          chatMode={(activeChat?.chat_mode as any) || "global"}
          title={activeChat?.title}
          workspaceName={activeChat?.workspace_name}
          citationCount={allCitations.length}
          onOpenMetadata={() => setMetadataOpen(true)}
          onToggleCitationDock={() => setCitationDockOpen((prev) => !prev)}
        />

        {/* 2. Scrollable Message Stream & Active Welcome State */}
        <div
          ref={scrollContainerRef}
          onScroll={handleScroll}
          className="flex-1 overflow-y-auto pt-3 pb-3 px-4 sm:px-6 space-y-4 scrollbar-hover contain-layout-paint relative"
        >
          <ChatErrorBoundary fallbackText="Lỗi hiển thị dòng tin nhắn">
            {isRestoring ? (
              <MessageSkeleton />
            ) : !chatId || messages.length === 0 ? (
              <WelcomeChatState
                chatMode={(activeChat?.chat_mode as any) || "global"}
                workspaceName={activeChat?.workspace_name}
                onPromptClick={(text) => handleSendMessage(text)}
              />
            ) : (
              <VirtualMessageList
                messages={messages}
                activeChatMode={activeChat?.chat_mode}
                workspaceName={activeChat?.workspace_name}
                onSendActionPrompt={(prompt) => handleSendMessage(prompt)}
                onRegenerate={handleRegenerate}
              />
            )}
          </ChatErrorBoundary>

          {/* Empty Knowledge Card if no citations retrieved on assistant message */}
          {messages.length > 0 &&
            messages[messages.length - 1]?.role !== "user" &&
            (!messages[messages.length - 1]?.citations || messages[messages.length - 1]?.citations?.length === 0) && (
              <EmptyKnowledgeCard
                onUploadClick={() => navigate("/workspaces")}
                onExpandScopeClick={() => navigate("/history")}
              />
            )}

          {/* RAG Streaming Indicator */}
          {isLoading && (
            <div className="py-2 max-w-[900px] mx-auto">
              <StreamingStatusIndicator />
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Floating "↓ Tin nhắn mới" Jump to Bottom Button */}
        {showScrollToBottom && (
          <div className="absolute bottom-24 left-1/2 -translate-x-1/2 z-30 animate-in fade-in zoom-in-95 duration-200">
            <Button
              size="sm"
              onClick={() => {
                setShowScrollToBottom(false)
                scrollToBottom(true)
              }}
              className="h-8 px-3 text-xs gap-1.5 shadow-xl rounded-full bg-primary text-primary-foreground font-bold hover:bg-primary/90 transition-all border border-primary-foreground/20"
            >
              <ArrowDown className="h-3.5 w-3.5" />
              <span>↓ Tin nhắn mới</span>
            </Button>
          </div>
        )}

        {/* 3. Bottom Pinned Active Chat Composer */}
        <div className="border-t border-border/40 bg-card/60 backdrop-blur-md shadow-lg shrink-0 z-10">
          <ChatComposer
            input={input}
            setInput={setInput}
            onSend={() => handleSendMessage()}
            activeChatId={chatId || "global"}
            isLoading={isLoading}
            onStop={handleStopGeneration}
            showChips={!chatId || messages.length === 0}
            onPromptChipClick={(chip) => handleSendMessage(chip)}
            attachedFiles={attachedFiles}
            onAttachFiles={(files) => setAttachedFiles((prev) => [...prev, ...files])}
            onRemoveFile={(idx) => setAttachedFiles((prev) => prev.filter((_, i) => i !== idx))}
          />
        </div>

        {/* Dialogs & Right Resizable Citation Drawer */}
        <NewChatScopeDialog
          open={isDialogOpen}
          onOpenChange={setIsDialogOpen}
          onStartChat={handleStartChatFromDialog}
        />

        <ConversationMetadataDialog
          open={metadataOpen}
          onOpenChange={setMetadataOpen}
          chat={activeChat}
          messageCount={messages.length}
          citationCount={allCitations.length}
        />

        <ExportDialog
          open={exportOpen}
          onOpenChange={setExportOpen}
          onExportMarkdown={handleExportMarkdown}
          onExportTxt={handleExportTxt}
          onPrintPdf={handlePrintPdf}
        />

        <CitationDock
          isOpen={citationDockOpen}
          onClose={() => setCitationDockOpen(false)}
          citations={allCitations}
        />
      </ChatLayout>
    </div>
  )
}

