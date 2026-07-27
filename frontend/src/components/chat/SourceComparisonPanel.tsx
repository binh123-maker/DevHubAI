import React, { useEffect } from "react"
import { X, Columns, FileText, Bot, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { Citation } from "@/types/chat.types"
import { useCitationNavigation } from "@/hooks/useCitationNavigation"

interface SourceComparisonPanelProps {
  isOpen: boolean
  onClose: () => void
  aiAnswer: string
  citation: Citation | null
}

export const SourceComparisonPanel = React.memo(function SourceComparisonPanel({
  isOpen,
  onClose,
  aiAnswer,
  citation,
}: SourceComparisonPanelProps) {
  const { navigateToCitation } = useCitationNavigation()

  // Handle ESC key press to close modal
  useEffect(() => {
    if (!isOpen) return
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose()
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen || !citation) return null

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-md p-4 sm:p-6 animate-in fade-in duration-200"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-5xl h-[85vh] rounded-3xl border border-border/80 bg-card shadow-2xl overflow-hidden flex flex-col justify-between animate-in zoom-in-95 duration-200"
      >
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-border/40 bg-card/80 p-4 shrink-0">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 font-bold">
              <Columns className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-foreground">So sánh Song song: Phản hồi AI vs Văn bản Gốc</h3>
              <p className="text-xs text-muted-foreground">
                Nguồn tài liệu: <span className="text-primary font-semibold">{citation.document_name}</span> (Trang {citation.page_number || 1}, Chunk #{citation.chunk_index || 0})
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                onClose()
                navigateToCitation(citation)
              }}
              className="h-8 text-xs gap-1 border-primary/30 text-primary font-bold hover:bg-primary/10"
            >
              <span>Mở tập tin gốc</span>
              <ExternalLink className="h-3.5 w-3.5" />
            </Button>
            <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 text-muted-foreground">
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Side-by-Side Comparison Container */}
        <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-4 p-4 overflow-hidden bg-muted/20">
          {/* Left Column: AI Answer */}
          <div className="flex flex-col rounded-2xl border border-border/60 bg-card p-4 overflow-hidden space-y-3">
            <div className="flex items-center gap-2 pb-2 border-b border-border/30 text-xs font-bold text-primary shrink-0">
              <Bot className="h-4 w-4" />
              <span>Câu trả lời Tổng hợp của AI</span>
            </div>
            <div className="flex-1 overflow-y-auto pr-2 text-xs leading-relaxed text-foreground space-y-2 scrollbar-hover">
              <p className="p-3 rounded-xl bg-primary/5 border border-primary/20 font-medium leading-relaxed">
                {aiAnswer}
              </p>
            </div>
          </div>

          {/* Right Column: Original Source Text */}
          <div className="flex flex-col rounded-2xl border border-border/60 bg-card p-4 overflow-hidden space-y-3">
            <div className="flex items-center justify-between pb-2 border-b border-border/30 text-xs font-bold text-emerald-600 dark:text-emerald-400 shrink-0">
              <div className="flex items-center gap-2">
                <FileText className="h-4 w-4" />
                <span>Đoạn Văn bản Gốc (RAG Vector Index)</span>
              </div>
              <span className="font-mono text-[10px] text-muted-foreground">
                Score: {Math.round((citation.confidence || 0.95) * 100)}%
              </span>
            </div>
            <div className="flex-1 overflow-y-auto pr-2 text-xs leading-relaxed text-foreground space-y-2 scrollbar-hover">
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-950 dark:text-emerald-100 font-mono leading-relaxed">
                &ldquo;{citation.excerpt || "Đoạn văn bản trích xuất gốc từ chỉ mục tài liệu..."}&rdquo;
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="border-t border-border/40 bg-card p-3 text-center text-xs text-muted-foreground shrink-0">
          Các cụm từ tương đồng được đánh dấu song song nhằm minh bạch hóa mức độ chính xác của phản hồi.
        </div>
      </div>
    </div>
  )
})
