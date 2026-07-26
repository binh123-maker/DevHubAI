import { Globe, FolderOpen, Pin } from "lucide-react"
import { formatDistanceToNow } from "date-fns"
import { vi } from "date-fns/locale"
import { ConversationMenu } from "./ConversationMenu"
import type { Chat } from "@/types/chat.types"

interface ConversationItemProps {
  chat: Chat
  isActive: boolean
  onClick: () => void
  onRename: (chatId: string, newTitle: string) => Promise<void>
  onDuplicate: (chatId: string) => Promise<void>
  onToggleFavorite: (chatId: string, isFavorite: boolean) => Promise<void>
  onExport: (chatId: string) => Promise<void>
  onDelete: (chatId: string) => Promise<void>
}

export function ConversationItem({
  chat,
  isActive,
  onClick,
  onRename,
  onDuplicate,
  onToggleFavorite,
  onExport,
  onDelete,
}: ConversationItemProps) {
  const isGlobal = chat.chat_mode === "global" || !chat.workspace_id

  const formatRelativeTime = (dateStr: string) => {
    try {
      return formatDistanceToNow(new Date(dateStr), { addSuffix: true, locale: vi })
    } catch {
      return ""
    }
  }

  return (
    <div
      onClick={onClick}
      tabIndex={0}
      role="button"
      aria-label={`Cuộc trò chuyện: ${chat.title}`}
      className={`group relative flex flex-col gap-1.5 rounded-xl p-3 text-xs transition-all duration-200 cursor-pointer select-none border ${
        isActive
          ? "bg-primary/10 border-primary/40 text-foreground font-semibold shadow-xs"
          : "bg-card/60 hover:bg-accent/80 border-border/40 hover:border-border/80 text-muted-foreground hover:text-foreground"
      }`}
    >
      {/* Active Left Indicator Bar */}
      {isActive && (
        <span className="absolute left-0 top-2 bottom-2 w-1 rounded-r-full bg-primary transition-all duration-200" />
      )}

      {/* Header Row: Scope Badge & Menu */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-1.5 truncate">
          <span
            className={`inline-flex items-center gap-1 rounded-md px-1.5 py-0.5 text-[10px] font-bold ${
              isGlobal
                ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                : "bg-amber-500/10 text-amber-600 dark:text-amber-400"
            }`}
          >
            {isGlobal ? <Globe className="h-3 w-3" /> : <FolderOpen className="h-3 w-3" />}
            <span className="truncate max-w-[120px]">
              {isGlobal ? "Global" : chat.workspace_name || "Workspace"}
            </span>
          </span>

          {chat.is_favorite && (
            <span title="Đã ghim">
              <Pin className="h-3 w-3 text-amber-500 shrink-0 fill-amber-500/20" />
            </span>
          )}
        </div>

        <ConversationMenu
          chatId={chat.id}
          currentTitle={chat.title}
          isFavorite={chat.is_favorite}
          onRename={(title) => onRename(chat.id, title)}
          onDuplicate={() => onDuplicate(chat.id)}
          onToggleFavorite={() => onToggleFavorite(chat.id, !chat.is_favorite)}
          onExport={() => onExport(chat.id)}
          onDelete={() => onDelete(chat.id)}
        />
      </div>

      {/* Title */}
      <h3 className="font-semibold text-foreground text-xs leading-snug line-clamp-1 group-hover:text-primary transition-colors">
        {chat.title}
      </h3>

      {/* Last Message Preview & Time */}
      <div className="flex items-center justify-between text-[11px] text-muted-foreground/80 pt-0.5">
        <span className="truncate max-w-[170px]">
          {chat.last_message_content || `${chat.message_count} tin nhắn`}
        </span>
        <span className="font-mono text-[10px] shrink-0">{formatRelativeTime(chat.updated_at || chat.created_at)}</span>
      </div>
    </div>
  )
}
