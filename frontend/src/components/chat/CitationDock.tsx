import React, { useState, useMemo, useEffect, useRef } from "react"
import { X, BookOpen, Layers, GripVertical, Clock, LayoutGrid } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Citation } from "@/types/chat.types"
import { CitationCard } from "./CitationCard"
import { EvidenceTimeline } from "./EvidenceTimeline"

interface CitationDockProps {
  isOpen: boolean
  onClose: () => void
  citations: Citation[]
  onCompareClick?: (citation: Citation) => void
}

const STORAGE_KEY = "devhub_citation_dock_width"
const MIN_WIDTH = 320
const MAX_WIDTH = 600
const DEFAULT_WIDTH = 380

export const CitationDock = React.memo(function CitationDock({ isOpen, onClose, citations, onCompareClick }: CitationDockProps) {
  const [viewMode, setViewMode] = useState<"cards" | "timeline">("cards")
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
      return list.sort((a, b) => (b.confidence || 0.9) - (a.confidence || 0.9))
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
      <div className="p-3.5 border-b border-border/40 bg-card/80 space-y-2.5 shrink-0">
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

        {/* Mode Toggle & Sorting */}
        <div className="flex items-center justify-between gap-2 pt-1 border-t border-border/30">
          <div className="flex items-center gap-1 rounded-lg bg-muted p-0.5 text-xs">
            <button
              onClick={() => setViewMode("cards")}
              className={`flex items-center gap-1 px-2 py-0.5 rounded-md font-semibold text-[11px] transition-all ${
                viewMode === "cards" ? "bg-background text-foreground shadow-2xs" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <LayoutGrid className="h-3 w-3" />
              <span>Cards</span>
            </button>
            <button
              onClick={() => setViewMode("timeline")}
              className={`flex items-center gap-1 px-2 py-0.5 rounded-md font-semibold text-[11px] transition-all ${
                viewMode === "timeline" ? "bg-background text-foreground shadow-2xs" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Clock className="h-3 w-3" />
              <span>Timeline</span>
            </button>
          </div>

          <Select value={sortBy} onValueChange={(val: any) => setSortBy(val)}>
            <SelectTrigger className="h-7 w-32 text-xs bg-background">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="confidence">Confidence</SelectItem>
              <SelectItem value="newest">Newest</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Citation Content View */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3 scrollbar-hover contain-layout-paint">
        {viewMode === "timeline" ? (
          <EvidenceTimeline citations={sortedCitations} />
        ) : sortedCitations.length === 0 ? (
          <div className="py-12 text-center text-xs text-muted-foreground space-y-1">
            <Layers className="h-8 w-8 mx-auto text-muted-foreground/40 mb-2" />
            <p className="font-semibold text-foreground">Chưa có trích dẫn nào</p>
            <p>Gửi câu hỏi để AI tra cứu RAG và hiển thị nguồn tài liệu ở đây.</p>
          </div>
        ) : (
          sortedCitations.map((cit, idx) => (
            <CitationCard
              key={idx}
              citation={cit}
              rankIndex={idx}
              onCompareClick={onCompareClick}
            />
          ))
        )}
      </div>
    </aside>
  )
})

