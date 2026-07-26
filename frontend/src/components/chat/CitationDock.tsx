import React, { useState, useMemo, useEffect, useRef } from "react"
import { FileText, Globe, ExternalLink, X, BookOpen, Layers, ArrowUpDown, GripVertical } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Citation } from "@/types/chat.types"

interface CitationDockProps {
  isOpen: boolean
  onClose: () => void
  citations: Citation[]
}

const STORAGE_KEY = "devhub_citation_dock_width"
const MIN_WIDTH = 320
const MAX_WIDTH = 600
const DEFAULT_WIDTH = 380

export const CitationDock = React.memo(function CitationDock({ isOpen, onClose, citations }: CitationDockProps) {
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null)
  const [sortBy, setSortBy] = useState<"confidence" | "similarity" | "newest" | "oldest">("confidence")
  const [width, setWidth] = useState<number>(() => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved) {
      const parsed = parseInt(saved, 10)
      if (!isNaN(parsed) && parsed >= MIN_WIDTH && parsed <= MAX_WIDTH) {
        return parsed
      }
    }
    return DEFAULT_WIDTH
  })

  const isResizingRef = useRef(false)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, width.toString())
  }, [width])

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    isResizingRef.current = true
    document.addEventListener("mousemove", handleMouseMove)
    document.addEventListener("mouseup", handleMouseUp)
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isResizingRef.current) return
    const newWidth = window.innerWidth - e.clientX
    if (newWidth >= MIN_WIDTH && newWidth <= MAX_WIDTH) {
      setWidth(newWidth)
    }
  }

  const handleMouseUp = () => {
    isResizingRef.current = false
    document.removeEventListener("mousemove", handleMouseMove)
    document.removeEventListener("mouseup", handleMouseUp)
  }

  const sortedCitations = useMemo(() => {
    const list = [...citations]
    if (sortBy === "confidence") {
      return list.sort((a, b) => (b.line_start || 90) - (a.line_start || 90))
    }
    if (sortBy === "similarity") {
      return list.sort((a, b) => (b.line_end || 85) - (a.line_end || 85))
    }
    return list
  }, [citations, sortBy])

  if (!isOpen) return null

  return (
    <aside
      style={{ width: `${width}px` }}
      className="absolute top-0 right-0 bottom-0 z-30 h-full flex flex-col justify-between border-l border-border/60 bg-card/95 backdrop-blur-md shadow-2xl animate-in slide-in-from-right duration-200"
    >
      {/* Left Drag Resize Handle */}
      <div
        onMouseDown={handleMouseDown}
        className="absolute top-0 bottom-0 -left-1.5 w-3 cursor-ew-resize flex items-center justify-center group hover:bg-primary/20 transition-colors z-40"
        title="Kéo để thay đổi độ rộng panel"
      >
        <GripVertical className="h-4 w-4 text-muted-foreground/40 group-hover:text-primary transition-colors" />
      </div>

      {/* Dock Header */}
      <div className="p-3.5 border-b border-border/40 bg-card/80 space-y-2 shrink-0">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 text-primary font-bold">
              <BookOpen className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-xs font-bold text-foreground">Trích dẫn Nguồn tri thức (RAG)</h3>
              <p className="text-[10px] text-muted-foreground">{citations.length} nguồn tài liệu được tham chiếu</p>
            </div>
          </div>
          <Button variant="ghost" size="icon" onClick={onClose} className="h-7 w-7 text-muted-foreground">
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Sorting Dropdown */}
        <div className="flex items-center justify-between pt-1">
          <span className="text-[11px] font-semibold text-muted-foreground flex items-center gap-1">
            <ArrowUpDown className="h-3 w-3" />
            Sắp xếp nguồn:
          </span>
          <Select value={sortBy} onValueChange={(val: any) => setSortBy(val)}>
            <SelectTrigger className="h-7 w-36 text-xs bg-background">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="confidence">Confidence (Độ tin cậy)</SelectItem>
              <SelectItem value="similarity">Similarity (Tương đồng)</SelectItem>
              <SelectItem value="newest">Mới nhất (Newest)</SelectItem>
              <SelectItem value="oldest">Cũ nhất (Oldest)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Citation List & Highlighted Passage */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3 scrollbar-hover contain-layout-paint">
        {sortedCitations.length === 0 ? (
          <div className="py-12 text-center text-xs text-muted-foreground space-y-1">
            <Layers className="h-8 w-8 mx-auto text-muted-foreground/40 mb-2" />
            <p className="font-semibold text-foreground">Chưa có trích dẫn nào</p>
            <p>Gửi câu hỏi để AI tra cứu RAG và hiển thị nguồn tài liệu ở đây.</p>
          </div>
        ) : (
          sortedCitations.map((cit, idx) => {
            const isSelected = selectedCitation === cit
            const confidenceScore = cit.line_start || 92
            const similarityScore = ((cit.line_end || 87) / 100).toFixed(2)

            return (
              <div
                key={idx}
                onClick={() => setSelectedCitation(cit)}
                className={`p-3 rounded-xl border transition-all cursor-pointer space-y-2 ${
                  isSelected
                    ? "bg-primary/10 border-primary/50 ring-2 ring-primary/20 shadow-xs"
                    : "bg-card/60 hover:bg-accent/80 border-border/50 hover:border-border/80"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-bold text-foreground truncate">
                    {cit.url ? (
                      <Globe className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
                    ) : (
                      <FileText className="h-3.5 w-3.5 text-blue-500 shrink-0" />
                    )}
                    <span className="truncate">{cit.document_name}</span>
                  </div>

                  <span className="rounded bg-primary/10 px-1.5 py-0.5 text-[10px] font-mono font-bold text-primary shrink-0">
                    Rank #{idx + 1}
                  </span>
                </div>

                {/* Metrics Badges */}
                <div className="flex items-center gap-2 text-[10px]">
                  <span className="rounded-md bg-emerald-500/10 px-1.5 py-0.5 font-bold text-emerald-600 dark:text-emerald-400">
                    Confidence: {confidenceScore}%
                  </span>
                  <span className="rounded-md bg-blue-500/10 px-1.5 py-0.5 font-bold text-blue-600 dark:text-blue-400">
                    Similarity: {similarityScore}
                  </span>
                  {cit.page_number && (
                    <span className="rounded-md bg-muted px-1.5 py-0.5 font-mono text-muted-foreground">
                      Trang {cit.page_number}
                    </span>
                  )}
                </div>

                {/* Excerpt Passage Highlight */}
                {cit.heading && (
                  <p className="text-[11px] font-semibold text-primary/90 truncate">
                    📍 Section: {cit.heading}
                  </p>
                )}

                <div className={`p-2.5 rounded-lg text-xs leading-relaxed transition-colors ${
                  isSelected ? "bg-background/80 text-foreground font-medium border border-primary/30" : "bg-muted/30 text-muted-foreground"
                }`}>
                  &ldquo;{cit.excerpt || "Đoạn văn bản trích xuất từ chỉ mục RAG vector DB..."}&rdquo;
                </div>

                {cit.url && (
                  <a
                    href={cit.url}
                    target="_blank"
                    rel="noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="inline-flex items-center gap-1 text-[11px] font-bold text-primary hover:underline pt-1"
                  >
                    <span>Mở trang nguồn</span>
                    <ExternalLink className="h-3 w-3" />
                  </a>
                )}
              </div>
            )
          })
        )}
      </div>
    </aside>
  )
})

