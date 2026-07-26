import React, { useState } from "react"
import { Plus, MessageSquarePlus, Trash2 } from "lucide-react"
import { SearchConversation } from "./SearchConversation"
import { ConversationList } from "./ConversationList"
import { ConversationSkeleton } from "./ConversationSkeleton"
import { ConversationTagPicker } from "./ConversationTagPicker"
import { Button } from "@/components/ui/button"
import type { Chat } from "@/types/chat.types"

interface ChatSidebarProps {
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

export const ChatSidebar = React.memo(function ChatSidebar({
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
  isLoading = false,
}: ChatSidebarProps) {
  const [selectedTag, setSelectedTag] = useState<string | undefined>()

  const filteredByTagChats = selectedTag
    ? chats.filter((c) => c.title.toLowerCase().includes(selectedTag.toLowerCase()))
    : chats

  return (
    <aside className="h-full w-[280px] lg:w-[320px] 2xl:w-[360px] shrink-0 border-r border-border/60 bg-card/60 backdrop-blur-md flex flex-col justify-between overflow-hidden z-20">
      {/* Sticky Header: New Chat, Search & Tags */}
      <div className="p-3 border-b border-border/40 space-y-2 bg-card/80 shrink-0">
        <Button
          onClick={onNewChatClick}
          className="w-full gap-2 text-xs font-bold h-9 shadow-sm"
        >
          <Plus className="h-4 w-4" />
          <MessageSquarePlus className="h-4 w-4" />
          Tạo cuộc trò chuyện mới
        </Button>

        <SearchConversation query={searchQuery} onQueryChange={onSearchChange} />

        {/* Tag Filter Pills */}
        <ConversationTagPicker
          tags={["Spring", "Flutter", "Database", "React", "Python"]}
          selectedTag={selectedTag}
          onSelectTag={setSelectedTag}
        />
      </div>

      {/* Scrollable Conversation History List */}
      <div className="flex-1 overflow-y-auto scrollbar-hover contain-layout-paint">
        {isLoading ? (
          <ConversationSkeleton />
        ) : (
          <ConversationList
            chats={filteredByTagChats}
            activeChatId={activeChatId}
            searchQuery={searchQuery}
            onSelectChat={onSelectChat}
            onRenameChat={onRenameChat}
            onDuplicateChat={onDuplicateChat}
            onToggleFavoriteChat={onToggleFavoriteChat}
            onExportChat={onExportChat}
            onDeleteChat={onDeleteChat}
          />
        )}
      </div>

      {/* Footer Clear All */}
      {chats.length > 0 && onClearAllChats && (
        <div className="p-2 border-t border-border/40 bg-muted/20 shrink-0">
          <Button
            variant="ghost"
            size="sm"
            onClick={onClearAllChats}
            className="w-full h-8 text-xs text-muted-foreground hover:text-destructive gap-1.5"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Xóa toàn bộ lịch sử trò chuyện
          </Button>
        </div>
      )}
    </aside>
  )
})

