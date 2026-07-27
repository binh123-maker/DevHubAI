import React, { useState } from "react"
import { FileText, Globe, ExternalLink, Copy, Check, Eye, Columns, FolderOpen, Layers } from "lucide-react"
import type { Citation } from "@/types/chat.types"
import { CitationConfidenceBadge } from "./CitationConfidenceBadge"
import { useCitationNavigation } from "@/hooks/useCitationNavigation"
import { Button } from "@/components/ui/button"

interface CitationCardProps {
  citation: Citation
  rankIndex?: number
  onCompareClick?: (citation: Citation) => void
}

export const CitationCard = React.memo(function CitationCard({
  citation,
  rankIndex,
  onCompareClick,
}: CitationCardProps) {
  const { navigateToCitation } = useCitationNavigation()
  const [isCopied, setIsCopied] = useState(false)
  const [isExcerptExpanded, setIsExcerptExpanded] = useState(false)

  const handleCopyCitation = () => {
    const text = `[Trích dẫn RAG] ${citation.document_name} (${citation.workspace_name || "Workspace"} > ${citation.folder_name || "Folder"})\nTrang ${citation.page_number || 1}, Chunk #${citation.chunk_index || 0}\n"${citation.excerpt || ""}"`
    navigator.clipboard.writeText(text)
    setIsCopied(true)
    setTimeout(() => setIsCopied(false), 2000)
  }

  return (
    <div className="group rounded-2xl border border-border/60 bg-card/70 hover:bg-accent/40 p-3.5 space-y-2.5 transition-all duration-200 shadow-xs hover:shadow-md">
      {/* Top Header Row */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary font-bold shadow-2xs">
            {citation.url ? <Globe className="h-4 w-4 text-emerald-500" /> : <FileText className="h-4 w-4 text-blue-500" />}
          </div>
          <div className="min-w-0">
            <h4 className="text-xs font-bold text-foreground truncate group-hover:text-primary transition-colors">
              {citation.document_name}
            </h4>
            <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground">
              <span className="flex items-center gap-0.5">
                <FolderOpen className="h-3 w-3 text-amber-500" />
                {citation.workspace_name || "Workspace"}
              </span>
              <span>•</span>
              <span className="flex items-center gap-0.5">
                <Layers className="h-3 w-3 text-blue-500" />
                {citation.folder_name || "Root"}
              </span>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-1.5 shrink-0">
          {rankIndex !== undefined && (
            <span className="rounded-md bg-muted px-1.5 py-0.5 font-mono text-[10px] font-bold text-muted-foreground">
              Rank #{rankIndex + 1}
            </span>
          )}
          <CitationConfidenceBadge confidence={citation.confidence} level={citation.confidence_level} />
        </div>
      </div>

      {/* Heading & Page / Chunk Meta */}
      <div className="flex items-center justify-between text-[11px] font-semibold text-muted-foreground pt-0.5">
        <span className="truncate text-primary font-medium">
          📍 {citation.heading || `Mục Trang ${citation.page_number || 1}`}
        </span>
        <span className="font-mono text-[10px] shrink-0">
          Trang {citation.page_number || 1} • Chunk #{citation.chunk_index || 0}
        </span>
      </div>

      {/* Excerpt Snippet */}
      <div className={`p-2.5 rounded-xl text-xs leading-relaxed transition-all ${
        isExcerptExpanded
          ? "bg-background/90 text-foreground font-medium border border-primary/30"
          : "bg-muted/40 text-muted-foreground line-clamp-2"
      }`}>
        &ldquo;{citation.excerpt || "Đoạn văn bản trích xuất từ chỉ mục tài liệu RAG vector DB..."}&rdquo;
      </div>

      {/* Action Footer Buttons */}
      <div className="flex items-center justify-between border-t border-border/40 pt-2 text-xs">
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExcerptExpanded(!isExcerptExpanded)}
            className="h-7 px-2 text-[11px] gap-1 text-muted-foreground hover:text-foreground"
            title="Mở rộng/Thu gọn nội dung trích dẫn"
          >
            <Eye className="h-3.5 w-3.5" />
            <span>{isExcerptExpanded ? "Thu gọn" : "Xem trước"}</span>
          </Button>

          {onCompareClick && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onCompareClick(citation)}
              className="h-7 px-2 text-[11px] gap-1 text-purple-600 dark:text-purple-400 hover:bg-purple-500/10"
              title="So sánh câu trả lời AI với văn bản gốc"
            >
              <Columns className="h-3.5 w-3.5" />
              <span>So sánh nguồn</span>
            </Button>
          )}
        </div>

        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleCopyCitation}
            className="h-7 px-2 text-[11px] gap-1 text-muted-foreground hover:text-foreground"
            title="Sao chép thông tin trích dẫn"
          >
            {isCopied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
            <span>{isCopied ? "Đã sao chép" : "Copy"}</span>
          </Button>

          {citation.document_id ? (
            <Button
              variant="secondary"
              size="sm"
              onClick={() => navigateToCitation(citation)}
              className="h-7 px-2.5 text-[11px] gap-1 font-bold text-primary border border-primary/30 hover:bg-primary/10"
              title="Mở tài liệu và nhảy tới vị trí chính xác"
            >
              <span>Mở tài liệu</span>
              <ExternalLink className="h-3 w-3" />
            </Button>
          ) : (
            <span className="text-[10px] font-bold text-rose-500 bg-rose-500/10 px-2 py-1 rounded-md border border-rose-500/30">
              Source unavailable
            </span>
          )}
        </div>
      </div>
    </div>
  )
})
