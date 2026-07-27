import React from "react"
import { CitationService } from "@/services/citation.service"
import { Zap } from "lucide-react"

interface CitationConfidenceBadgeProps {
  confidence?: number
  level?: string
}

export const CitationConfidenceBadge = React.memo(function CitationConfidenceBadge({
  confidence,
  level,
}: CitationConfidenceBadgeProps) {
  const badgeInfo = CitationService.getConfidenceBadge(confidence, level)

  return (
    <div
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider border shadow-2xs ${badgeInfo.bgClass} ${badgeInfo.colorClass} ${badgeInfo.borderClass}`}
      title={`Độ tin cậy của thuật toán RAG Retriever: ${badgeInfo.scorePercent}% (${badgeInfo.level})`}
    >
      <Zap className="h-3 w-3" />
      <span>{badgeInfo.scorePercent}% {badgeInfo.level} Relevance</span>
    </div>
  )
})
