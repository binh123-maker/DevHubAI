import React, { useState } from "react"
import { FileText, Globe, ExternalLink, BookOpen } from "lucide-react"
import type { Citation } from "@/types/chat.types"

interface InlineCitationPopoverProps {
  index: number
  citation: Citation
  onOpenDock?: () => void
}

export const InlineCitationPopover = React.memo(function InlineCitationPopover({
  index,
  citation,
  onOpenDock,
}: InlineCitationPopoverProps) {
  const [showPopover, setShowPopover] = useState(false)

  return (
    <span className="relative inline-block mx-0.5">
      <button
        onClick={onOpenDock}
        onMouseEnter={() => setShowPopover(true)}
        onMouseLeave={() => setShowPopover(false)}
        className="inline-flex items-center justify-center h-5 px-1.5 rounded bg-primary/10 hover:bg-primary/20 text-primary font-mono text-[10px] font-bold border border-primary/30 transition-all cursor-pointer shadow-2xs"
        title="Xem nguồn trích dẫn"
      >
        [{index}]
      </button>

      {/* Hover Card Popover */}
      {showPopover && (
        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-64 p-3 rounded-xl border border-border/80 bg-popover/95 text-popover-foreground shadow-2xl backdrop-blur-md z-50 animate-in fade-in zoom-in-95 duration-150 space-y-2 pointer-events-none">
          <div className="flex items-center justify-between border-b border-border/40 pb-1.5">
            <div className="flex items-center gap-1.5 text-xs font-bold truncate">
              {citation.url ? (
                <Globe className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
              ) : (
                <FileText className="h-3.5 w-3.5 text-blue-500 shrink-0" />
              )}
              <span className="truncate">{citation.document_name}</span>
            </div>
            <span className="text-[10px] font-mono font-bold text-primary bg-primary/10 px-1 rounded">
              Nguồn #{index}
            </span>
          </div>

          <div className="flex items-center gap-2 text-[10px] text-muted-foreground">
            <span className="font-semibold text-foreground">Loại: {citation.source_type || "RAG Chunk"}</span>
            {citation.page_number && (
              <span className="rounded bg-muted px-1 font-mono">Trang {citation.page_number}</span>
            )}
          </div>

          <p className="text-[11px] text-muted-foreground line-clamp-3 leading-snug italic bg-muted/30 p-2 rounded-lg border border-border/30">
            &ldquo;{citation.excerpt || "Đoạn văn bản trích xuất từ chỉ mục tài liệu..."}&rdquo;
          </p>

          <div className="flex items-center justify-between pt-1 text-[10px] font-semibold text-primary">
            <span className="flex items-center gap-1">
              <BookOpen className="h-3 w-3" />
              Click để xem chi tiết
            </span>
            {citation.url && <ExternalLink className="h-3 w-3" />}
          </div>
        </div>
      )}
    </span>
  )
})
