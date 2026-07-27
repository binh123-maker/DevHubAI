import React from "react"
import { Layers, FileText, ChevronRight } from "lucide-react"
import type { Citation } from "@/types/chat.types"
import { CitationConfidenceBadge } from "./CitationConfidenceBadge"
import { useCitationNavigation } from "@/hooks/useCitationNavigation"

interface EvidenceTimelineProps {
  citations: Citation[]
  onSelectCitation?: (citation: Citation) => void
}

export const EvidenceTimeline = React.memo(function EvidenceTimeline({
  citations,
  onSelectCitation,
}: EvidenceTimelineProps) {
  const { navigateToCitation } = useCitationNavigation()

  if (citations.length === 0) {
    return (
      <div className="py-8 text-center text-xs text-muted-foreground space-y-1">
        <Layers className="h-7 w-7 mx-auto text-muted-foreground/40 mb-1" />
        <p className="font-semibold text-foreground">Chưa có dòng thời gian bằng chứng</p>
        <p>Gửi câu hỏi để AI truy xuất các đoạn tài liệu RAG.</p>
      </div>
    )
  }

  return (
    <div className="space-y-3 p-1">
      <div className="flex items-center justify-between text-[11px] font-bold uppercase tracking-wider text-muted-foreground border-b border-border/40 pb-1.5">
        <span>Timeline Truy xuất ({citations.length} Chunks)</span>
        <span>Xếp hạng Retriever</span>
      </div>

      <div className="relative border-l-2 border-primary/30 pl-4 ml-2 space-y-4">
        {citations.map((cit, idx) => (
          <div
            key={idx}
            onClick={() => onSelectCitation ? onSelectCitation(cit) : navigateToCitation(cit)}
            className="group relative flex flex-col gap-1.5 rounded-xl border border-border/60 bg-card/60 hover:bg-accent/80 p-3 transition-all cursor-pointer shadow-2xs hover:border-primary/50"
          >
            {/* Timeline Node Dot */}
            <div className="absolute -left-[23px] top-3 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[9px] font-bold text-primary-foreground shadow-xs">
              {idx + 1}
            </div>

            <div className="flex items-center justify-between gap-2">
              <div className="flex items-center gap-1.5 text-xs font-bold text-foreground truncate">
                <FileText className="h-3.5 w-3.5 text-primary shrink-0" />
                <span className="truncate group-hover:text-primary transition-colors">{cit.document_name}</span>
              </div>
              <CitationConfidenceBadge confidence={cit.confidence} level={cit.confidence_level} />
            </div>

            <div className="flex items-center justify-between text-[10px] text-muted-foreground font-mono">
              <span>Trang {cit.page_number || 1} • Chunk #{cit.chunk_index || 0}</span>
              <span className="text-primary font-semibold flex items-center gap-0.5 group-hover:underline">
                Xem nguồn <ChevronRight className="h-3 w-3" />
              </span>
            </div>

            <p className="text-[11px] text-muted-foreground line-clamp-2 italic bg-muted/30 p-2 rounded-lg border border-border/30">
              &ldquo;{cit.excerpt || "Nội dung văn bản trích dẫn từ vector DB..."}&rdquo;
            </p>
          </div>
        ))}
      </div>
    </div>
  )
})
