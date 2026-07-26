import React from "react"
import { ChatSidebar } from "./ChatSidebar"
import type { Chat } from "@/types/chat.types"

interface ChatLayoutProps {
  children: React.ReactNode
  chats: Chat[]
  activeChatId?: string
  searchQuery: string
  onSearchChange: (query: string) => void
  onNewChatClick: () => void
  onSelectChat: (chatId: string) => void
  onRenameChat: (chatId: string, newTitle: string) => Promise<void>
  onDuplicateChat: (chatId: string) => Promise<void>
  onToggleFavoriteChat: (chatId: string, isFavorite: boolean) => Promise<void>
  onExportChat: (chatId: string) => Promise<void>
  onDeleteChat: (chatId: string) => Promise<void>
  onClearAllChats?: () => Promise<void>
  isLoading?: boolean
}

export const ChatLayout = React.memo(function ChatLayout({
  children,
  chats,
  activeChatId,
  searchQuery,
  onSearchChange,
  onNewChatClick,
  onSelectChat,
  onRenameChat,
  onDuplicateChat,
  onToggleFavoriteChat,
  onExportChat,
  onDeleteChat,
  onClearAllChats,
  isLoading,
}: ChatLayoutProps) {
  return (
    <div className="flex h-full w-full bg-background text-foreground antialiased overflow-hidden relative">
      {/* Responsive Adaptive Desktop Sidebar */}
      <div className="hidden md:block h-full shrink-0">
        <ChatSidebar
          chats={chats}
          activeChatId={activeChatId}
          searchQuery={searchQuery}
          onSearchChange={onSearchChange}
          onNewChatClick={onNewChatClick}
          onSelectChat={onSelectChat}
          onRenameChat={onRenameChat}
          onDuplicateChat={onDuplicateChat}
          onToggleFavoriteChat={onToggleFavoriteChat}
          onExportChat={onExportChat}
          onDeleteChat={onDeleteChat}
          onClearAllChats={onClearAllChats}
          isLoading={isLoading}
        />
      </div>

      {/* Main Active Chat Area */}
      <main className="flex-1 flex flex-col min-w-0 h-full overflow-hidden bg-background/50 relative">
        {children}
      </main>
    </div>
  )
})

