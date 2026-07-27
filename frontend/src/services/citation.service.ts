import type { Citation } from "@/types/chat.types"

export interface ConfidenceBadgeInfo {
  scorePercent: number
  level: "High" | "Medium" | "Fair" | "Low"
  colorClass: string
  bgClass: string
  borderClass: string
}

export class CitationService {
  /**
   * Calculates confidence badge info based on float confidence (0.0 to 1.0) or percentage (0 to 100)
   */
  static getConfidenceBadge(confidence?: number, level?: string): ConfidenceBadgeInfo {
    const rawScore = confidence ?? 0.95
    const scorePercent = Math.round(rawScore <= 1.0 ? rawScore * 100 : rawScore)

    let calcLevel: "High" | "Medium" | "Fair" | "Low" = (level as any) || "High"
    if (!level) {
      if (scorePercent >= 95) calcLevel = "High"
      else if (scorePercent >= 80) calcLevel = "Medium"
      else if (scorePercent >= 60) calcLevel = "Fair"
      else calcLevel = "Low"
    }

    let colorClass = "text-emerald-600 dark:text-emerald-400"
    let bgClass = "bg-emerald-500/10"
    let borderClass = "border-emerald-500/30"

    if (calcLevel === "Medium") {
      colorClass = "text-blue-600 dark:text-blue-400"
      bgClass = "bg-blue-500/10"
      borderClass = "border-blue-500/30"
    } else if (calcLevel === "Fair") {
      colorClass = "text-amber-600 dark:text-amber-400"
      bgClass = "bg-amber-500/10"
      borderClass = "border-amber-500/30"
    } else if (calcLevel === "Low") {
      colorClass = "text-rose-600 dark:text-rose-400"
      bgClass = "bg-rose-500/10"
      borderClass = "border-rose-500/30"
    }

    return {
      scorePercent,
      level: calcLevel,
      colorClass,
      bgClass,
      borderClass,
    }
  }

  /**
   * Constructs deep link URL into Document Viewer
   */
  static buildDeepLinkUrl(citation: Citation): string {
    const docId = citation.document_id || "preview"
    const page = citation.page_number || 1
    const chunk = citation.chunk_index ?? 0
    const highlightParam = citation.excerpt ? `&highlight=${encodeURIComponent(citation.excerpt.slice(0, 100))}` : ""

    return `/documents/${docId}?page=${page}&chunk=${chunk}${highlightParam}`
  }

  /**
   * Builds Workspace > Folder > Document > Heading > Page > Chunk breadcrumbs
   */
  static getBreadcrumbs(citation: Citation): string[] {
    const crumbs: string[] = []
    crumbs.push(citation.workspace_name || "Workspace")
    crumbs.push(citation.folder_name || "Folder")
    crumbs.push(citation.document_name)
    if (citation.heading) crumbs.push(citation.heading)
    if (citation.page_number) crumbs.push(`Trang ${citation.page_number}`)
    if (citation.chunk_index !== undefined) crumbs.push(`Chunk #${citation.chunk_index}`)
    return crumbs
  }
}
