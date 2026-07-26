import { useMemo } from "react"
import { isToday, isYesterday, isWithinInterval, subDays } from "date-fns"
import { ConversationItem } from "./ConversationItem"
import type { Chat } from "@/types/chat.types"

interface ConversationListProps {
  chats: Chat[]
  activeChatId?: string
  searchQuery: string
  onSelectChat: (chatId: string) => void
  onRenameChat: (chatId: string, newTitle: string) => Promise<void>
  onDuplicateChat: (chatId: string) => Promise<void>
  onToggleFavoriteChat: (chatId: string, isFavorite: boolean) => Promise<void>
  onExportChat: (chatId: string) => Promise<void>
  onDeleteChat: (chatId: string) => Promise<void>
}

export function ConversationList({
  chats,
  activeChatId,
  searchQuery,
  onSelectChat,
  onRenameChat,
  onDuplicateChat,
  onToggleFavoriteChat,
  onExportChat,
  onDeleteChat,
}: ConversationListProps) {
  const filteredChats = useMemo(() => {
    if (!searchQuery.trim()) return chats
    const q = searchQuery.toLowerCase()
    return chats.filter(
      (c) =>
        c.title.toLowerCase().includes(q) ||
        c.workspace_name?.toLowerCase().includes(q) ||
        c.last_message_content?.toLowerCase().includes(q)
    )
  }, [chats, searchQuery])

  // Group chats by Pinned, Today, Yesterday, Last Week, Last Month, Older
  const groupedChats = useMemo(() => {
    const pinned: Chat[] = []
    const today: Chat[] = []
    const yesterday: Chat[] = []
    const lastWeek: Chat[] = []
    const lastMonth: Chat[] = []
    const older: Chat[] = []

    const now = new Date()
    const sevenDaysAgo = subDays(now, 7)
    const thirtyDaysAgo = subDays(now, 30)

    filteredChats.forEach((chat) => {
      if (chat.is_favorite) {
        pinned.push(chat)
        return
      }

      const date = new Date(chat.updated_at || chat.created_at)
      if (isToday(date)) {
        today.push(chat)
      } else if (isYesterday(date)) {
        yesterday.push(chat)
      } else if (isWithinInterval(date, { start: sevenDaysAgo, end: now })) {
        lastWeek.push(chat)
      } else if (isWithinInterval(date, { start: thirtyDaysAgo, end: now })) {
        lastMonth.push(chat)
      } else {
        older.push(chat)
      }
    })

    return [
      { title: "📌 Đã ghim", items: pinned },
      { title: "📅 Hôm nay", items: today },
      { title: "📆 Hôm qua", items: yesterday },
      { title: "🗓️ 7 ngày qua", items: lastWeek },
      { title: "📅 30 ngày qua", items: lastMonth },
      { title: "🗄️ Cũ hơn", items: older },
    ].filter((g) => g.items.length > 0)
  }, [filteredChats])

  if (filteredChats.length === 0) {
    return (
      <div className="p-6 text-center text-xs text-muted-foreground space-y-1">
        <p className="font-semibold text-foreground">Không tìm thấy cuộc trò chuyện nào</p>
        <p>Thử tìm kiếm từ khóa khác hoặc tạo cuộc trò chuyện mới.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4 p-2">
      {groupedChats.map((group) => (
        <div key={group.title} className="space-y-1.5">
          <p className="px-2 text-[11px] font-bold uppercase tracking-wider text-muted-foreground/80">
            {group.title} ({group.items.length})
          </p>
          <div className="space-y-1">
            {group.items.map((chat) => (
              <ConversationItem
                key={chat.id}
                chat={chat}
                isActive={chat.id === activeChatId}
                onClick={() => onSelectChat(chat.id)}
                onRename={onRenameChat}
                onDuplicate={onDuplicateChat}
                onToggleFavorite={onToggleFavoriteChat}
                onExport={onExportChat}
                onDelete={onDeleteChat}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}
