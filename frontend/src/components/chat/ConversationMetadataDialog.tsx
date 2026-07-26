import { Info, Calendar, MessageSquare, BookOpen, Globe, FolderOpen, Cpu } from "lucide-react"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import type { Chat } from "@/types/chat.types"

interface ConversationMetadataDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  chat: Chat | null
  messageCount: number
  citationCount: number
}

export function ConversationMetadataDialog({
  open,
  onOpenChange,
  chat,
  messageCount,
  citationCount,
}: ConversationMetadataDialogProps) {
  if (!chat) return null

  const isGlobal = chat.chat_mode === "global" || !chat.workspace_id

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return "N/A"
    try {
      return new Date(dateStr).toLocaleString("vi-VN", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    } catch {
      return dateStr
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-sm p-0 overflow-hidden border border-border/60 bg-card text-card-foreground shadow-2xl rounded-2xl">
        <DialogHeader className="p-4 border-b border-border/40 pb-3">
          <DialogTitle className="text-sm font-bold flex items-center gap-2">
            <Info className="h-4 w-4 text-primary" />
            Thông tin & Thống kê cuộc trò chuyện
          </DialogTitle>
        </DialogHeader>

        <div className="p-4 space-y-3 text-xs">
          <div className="p-3 rounded-xl border border-border/50 bg-muted/20 space-y-2">
            <h4 className="font-bold text-foreground text-sm truncate">{chat.title}</h4>
            <div className="flex items-center gap-2">
              <span className={`inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-[10px] font-bold ${
                isGlobal ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400" : "bg-amber-500/10 text-amber-600 dark:text-amber-400"
              }`}>
                {isGlobal ? <Globe className="h-3 w-3" /> : <FolderOpen className="h-3 w-3" />}
                {isGlobal ? "Global Scope" : `Workspace: ${chat.workspace_name || "Locked"}`}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div className="p-2.5 rounded-lg border border-border/40 bg-card space-y-1">
              <span className="text-[10px] font-semibold text-muted-foreground flex items-center gap-1">
                <MessageSquare className="h-3 w-3 text-blue-500" />
                Tổng tin nhắn
              </span>
              <p className="text-sm font-bold">{messageCount}</p>
            </div>

            <div className="p-2.5 rounded-lg border border-border/40 bg-card space-y-1">
              <span className="text-[10px] font-semibold text-muted-foreground flex items-center gap-1">
                <BookOpen className="h-3 w-3 text-purple-500" />
                Nguồn tham chiếu RAG
              </span>
              <p className="text-sm font-bold">{citationCount}</p>
            </div>
          </div>

          <div className="space-y-2 pt-1 border-t border-border/40">
            <div className="flex items-center justify-between text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <Calendar className="h-3.5 w-3.5" />
                Thời gian bắt đầu:
              </span>
              <span className="font-mono text-foreground font-semibold">{formatDate(chat.created_at)}</span>
            </div>

            <div className="flex items-center justify-between text-muted-foreground">
              <span className="flex items-center gap-1.5">
                <Cpu className="h-3.5 w-3.5 text-primary" />
                Mô hình AI:
              </span>
              <span className="font-semibold text-primary">Gemini 1.5 Pro (RAG)</span>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}
