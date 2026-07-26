import React from "react"
import { FolderOpen, FileText, Layers } from "lucide-react"

interface MentionItem {
  id: string
  title: string
  type: "workspace" | "folder" | "document"
  description?: string
}

interface MentionPopoverProps {
  filter: string
  onSelectMention: (item: MentionItem) => void
  onClose?: () => void
}

export const MentionPopover = React.memo(function MentionPopover({
  filter,
  onSelectMention,
}: MentionPopoverProps) {
  const items: MentionItem[] = [
    { id: "ws-1", title: "Computer Science", type: "workspace", description: "Toàn bộ tài liệu Khoa học Máy tính" },
    { id: "ws-2", title: "DevHub AI Architecture", type: "workspace", description: "Sơ đồ kiến trúc & SRS DevHub" },
    { id: "f-1", title: "Backend API Docs", type: "folder", description: "Tài liệu FastAPI & Postgres Schema" },
    { id: "f-2", title: "Frontend UI Guidelines", type: "folder", description: "Thiết kế UI/UX & Tailwind system" },
    { id: "doc-1", title: "RAG_Vector_Search.pdf", type: "document", description: "Chỉ mục tìm kiếm vector DB" },
    { id: "doc-2", title: "FastAPI_Security.md", type: "document", description: "Bảo mật OAuth2 & JWT tokens" },
  ]

  const search = filter.replace(/^@/, "").toLowerCase()
  const filtered = items.filter(
    (i) => i.title.toLowerCase().includes(search) || i.type.toLowerCase().includes(search)
  )

  if (filtered.length === 0) return null

  return (
    <div className="absolute bottom-full left-0 mb-2 w-72 max-h-60 overflow-y-auto rounded-2xl border border-border/80 bg-popover/95 text-popover-foreground shadow-2xl backdrop-blur-md z-50 p-1.5 scrollbar-thin animate-in fade-in zoom-in-95 duration-150">
      <div className="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-muted-foreground border-b border-border/40 mb-1 flex items-center justify-between">
        <span>Nhắc tên Scope tri thức (@)</span>
        <span>Esc để đóng</span>
      </div>

      {filtered.map((item) => (
        <div
          key={item.id}
          onClick={() => onSelectMention(item)}
          className="flex items-center gap-2.5 p-2 rounded-xl hover:bg-accent/80 cursor-pointer transition-colors text-xs"
        >
          <div className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-lg ${
            item.type === "workspace"
              ? "bg-amber-500/10 text-amber-500"
              : item.type === "folder"
              ? "bg-blue-500/10 text-blue-500"
              : "bg-emerald-500/10 text-emerald-500"
          }`}>
            {item.type === "workspace" ? (
              <FolderOpen className="h-4 w-4" />
            ) : item.type === "folder" ? (
              <Layers className="h-4 w-4" />
            ) : (
              <FileText className="h-4 w-4" />
            )}
          </div>

          <div className="min-w-0 flex-1">
            <p className="font-bold text-foreground truncate">{item.title}</p>
            {item.description && (
              <p className="text-[10px] text-muted-foreground truncate">{item.description}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
})
