import { useState, useEffect, useRef } from "react"
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  ChevronLeft,
  ChevronRight,
  Search,
  List,
  Bookmark,
  FileText,
  Sparkles,
  Download,
  Eye,
  Layout,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"

interface PdfDocumentViewerProps {
  documentId: string
  fileUrl: string
  fileTitle: string
  chunks: any[]
  targetPage?: number
  targetChunk?: number
  highlightText?: string
  shouldHighlight?: boolean
}

export function PdfDocumentViewer({
  documentId,
  fileUrl,
  fileTitle,
  chunks,
  targetPage = 1,
  targetChunk = 0,
  shouldHighlight = false,
}: PdfDocumentViewerProps) {
  const [zoom, setZoom] = useState<number>(100)
  const [currentPage, setCurrentPage] = useState<number>(targetPage)
  const [activeTab, setActiveTab] = useState<"reader" | "preview" | "outline" | "thumbnails">("reader")
  const [searchQuery, setSearchQuery] = useState<string>("")
  const [isHighlighted, setIsHighlighted] = useState<boolean>(shouldHighlight)
  const targetChunkRef = useRef<HTMLDivElement>(null)

  // Viewer State Persistence (Part 17)
  useEffect(() => {
    const savedState = localStorage.getItem(`devhub_viewer_pdf_${documentId}`)
    if (savedState) {
      try {
        const parsed = JSON.parse(savedState)
        if (parsed.zoom) setZoom(parsed.zoom)
        if (parsed.activeTab) setActiveTab(parsed.activeTab)
      } catch (e) {
        console.error("Failed restoring PDF viewer state:", e)
      }
    }
  }, [documentId])

  useEffect(() => {
    localStorage.setItem(
      `devhub_viewer_pdf_${documentId}`,
      JSON.stringify({ zoom, activeTab, currentPage })
    )
  }, [documentId, zoom, activeTab, currentPage])

  // Handle citation page change & scroll
  useEffect(() => {
    if (targetPage) {
      setCurrentPage(targetPage)
    }
    if (shouldHighlight) {
      setIsHighlighted(true)
      if (targetChunkRef.current) {
        targetChunkRef.current.scrollIntoView({ behavior: "smooth", block: "center" })
      }
    }
  }, [targetPage, targetChunk, shouldHighlight])

  // Dismiss highlight on click/interaction (Part 19)
  const handleUserInteraction = () => {
    if (isHighlighted) {
      setIsHighlighted(false)
    }
  }

  // Keyboard Shortcuts (Part 18): Ctrl++, Ctrl+-, Ctrl+F
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey || e.metaKey) {
        if (e.key === "=" || e.key === "+") {
          e.preventDefault()
          setZoom((z) => Math.min(250, z + 15))
        } else if (e.key === "-") {
          e.preventDefault()
          setZoom((z) => Math.max(50, z - 15))
        }
      }
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [])

  const filteredChunks = searchQuery.trim()
    ? chunks.filter((c) =>
        (c.content_markdown || c.content || "")
          .toLowerCase()
          .includes(searchQuery.toLowerCase())
      )
    : chunks

  const totalPages = Math.max(
    1,
    ...chunks.map((c) => c.page_number || 1)
  )

  return (
    <div
      onClick={handleUserInteraction}
      className="flex flex-col h-[78vh] w-full rounded-2xl border border-border/60 bg-card/80 shadow-lg overflow-hidden contain-layout"
    >
      {/* 1. PDF Control Toolbar (Zoom, Page Nav, Search, Fit Width, Shortcuts) */}
      <div className="flex flex-wrap items-center justify-between gap-2 px-4 py-2 border-b border-border/50 bg-muted/40 shrink-0">
        <div className="flex items-center gap-1.5">
          <Button
            variant={activeTab === "reader" ? "secondary" : "ghost"}
            size="sm"
            onClick={() => setActiveTab("reader")}
            className="h-8 text-xs gap-1 font-semibold"
          >
            <Eye className="h-3.5 w-3.5 text-primary" />
            <span>Structured Reader</span>
          </Button>
          <Button
            variant={activeTab === "preview" ? "secondary" : "ghost"}
            size="sm"
            onClick={() => setActiveTab("preview")}
            className="h-8 text-xs gap-1 font-semibold"
          >
            <FileText className="h-3.5 w-3.5 text-blue-500" />
            <span>Native PDF Stream</span>
          </Button>
          <Button
            variant={activeTab === "thumbnails" ? "secondary" : "ghost"}
            size="sm"
            onClick={() => setActiveTab("thumbnails")}
            className="h-8 text-xs gap-1"
          >
            <Layout className="h-3.5 w-3.5 text-amber-500" />
            <span>Thumbnails</span>
          </Button>
          <Button
            variant={activeTab === "outline" ? "secondary" : "ghost"}
            size="sm"
            onClick={() => setActiveTab("outline")}
            className="h-8 text-xs gap-1"
          >
            <List className="h-3.5 w-3.5 text-purple-500" />
            <span>Outline ({totalPages} Pages)</span>
          </Button>
        </div>

        {/* Center: Page Controls */}
        <div className="flex items-center gap-1 font-mono text-xs">
          <Button
            variant="ghost"
            size="icon"
            disabled={currentPage <= 1}
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            className="h-7 w-7"
            title="Trang trước"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="font-bold px-1">
            Trang {currentPage} / {totalPages}
          </span>
          <Button
            variant="ghost"
            size="icon"
            disabled={currentPage >= totalPages}
            onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
            className="h-7 w-7"
            title="Trang sau"
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>

        {/* Right: Zoom & Search */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1 bg-background/80 rounded-lg p-0.5 border border-border/50">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setZoom((z) => Math.max(50, z - 15))}
              className="h-6 w-6 text-xs"
              title="Thu nhỏ (Ctrl+-)"
            >
              <ZoomOut className="h-3.5 w-3.5" />
            </Button>
            <span className="text-[11px] font-mono font-bold px-1 text-primary">
              {zoom}%
            </span>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setZoom((z) => Math.min(250, z + 15))}
              className="h-6 w-6 text-xs"
              title="Phóng to (Ctrl++)"
            >
              <ZoomIn className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setZoom(100)}
              className="h-6 w-6 text-xs"
              title="Khôi phục kích thước 100%"
            >
              <Maximize2 className="h-3 w-3" />
            </Button>
          </div>

          <a href={fileUrl} target="_blank" rel="noopener noreferrer" download>
            <Button variant="outline" size="sm" className="h-8 text-xs gap-1">
              <Download className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Tải PDF</span>
            </Button>
          </a>
        </div>
      </div>

      {/* 2. Main PDF Viewer Content Area */}
      <div className="flex flex-1 min-h-0 w-full overflow-hidden bg-muted/20">
        {/* Left Side Panel: Outline or Thumbnails */}
        {(activeTab === "outline" || activeTab === "thumbnails") && (
          <div className="w-64 border-r border-border/50 bg-card/60 p-3 overflow-y-auto shrink-0 space-y-2">
            <div className="relative mb-2">
              <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
              <Input
                placeholder="Tìm từ khóa (Ctrl+F)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 text-xs h-8"
              />
            </div>

            {activeTab === "outline" ? (
              <div className="space-y-1">
                <p className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-2">
                  Danh sách mục & trích dẫn
                </p>
                {filteredChunks.map((c, idx) => (
                  <button
                    key={c.id || idx}
                    onClick={() => setCurrentPage(c.page_number || 1)}
                    className={`w-full text-left p-2 rounded-lg text-xs transition-colors flex items-center justify-between ${
                      currentPage === (c.page_number || 1)
                        ? "bg-primary/15 text-primary font-bold border border-primary/30"
                        : "hover:bg-accent/60 text-muted-foreground"
                    }`}
                  >
                    <span className="truncate pr-2">
                      {c.heading || `Mục Trang ${c.page_number || 1}`}
                    </span>
                    <span className="font-mono text-[10px] shrink-0 bg-muted px-1.5 py-0.5 rounded">
                      P.{c.page_number || 1}
                    </span>
                  </button>
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-2">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((pg) => (
                  <button
                    key={pg}
                    onClick={() => setCurrentPage(pg)}
                    className={`p-3 rounded-xl border text-center font-mono text-xs transition-all ${
                      currentPage === pg
                        ? "bg-primary text-primary-foreground font-bold border-primary shadow-sm scale-105"
                        : "bg-card hover:border-primary/50 text-muted-foreground"
                    }`}
                  >
                    <div className="h-10 border border-dashed rounded mb-1 flex items-center justify-center text-[10px]">
                      PDF P.{pg}
                    </div>
                    <span>Trang {pg}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Native PDF Iframe Mode */}
        {activeTab === "preview" && (
          <div className="flex-1 h-full w-full bg-slate-900 flex items-center justify-center">
            <iframe
              src={`${fileUrl}#page=${currentPage}`}
              title={fileTitle}
              className="w-full h-full border-0"
            />
          </div>
        )}

        {/* Structured PDF Reader Mode (Default high performance) */}
        {activeTab !== "preview" && (
          <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 scrollbar-hover contain-layout">
            {isHighlighted && (
              <div className="sticky top-0 z-10 flex items-center justify-between p-2.5 rounded-xl bg-amber-500/20 border border-amber-500/40 text-amber-700 dark:text-amber-300 text-xs font-semibold backdrop-blur-md shadow-md animate-pulse">
                <span className="flex items-center gap-1.5">
                  <Sparkles className="h-4 w-4 text-amber-500" />
                  Đang làm nổi bật đoạn trích dẫn RAG tại Trang {targetPage}, Chunk #{targetChunk}
                </span>
                <span className="text-[10px] opacity-80">(Nhấp vào màn hình để tắt làm nổi bật)</span>
              </div>
            )}

            <div
              style={{ zoom: `${zoom}%` }}
              className="space-y-4 transition-all duration-200 mx-auto max-w-4xl"
            >
              {chunks
                .filter((c) => (currentPage ? (c.page_number || 1) === currentPage : true))
                .map((c, idx) => {
                  const isTarget = idx === targetChunk || (targetPage > 0 && (c.page_number || 1) === targetPage)
                  return (
                    <div
                      key={c.id || idx}
                      ref={isTarget ? targetChunkRef : null}
                      className={`p-5 rounded-2xl border transition-all duration-300 relative ${
                        isTarget && isHighlighted
                          ? "bg-amber-400/25 dark:bg-amber-500/20 border-amber-500 ring-2 ring-amber-500/50 shadow-xl scale-[1.01]"
                          : "bg-card border-border/50 hover:border-border"
                      }`}
                    >
                      <div className="flex items-center justify-between text-[11px] font-mono font-bold text-muted-foreground mb-3 pb-2 border-b border-border/30">
                        <span className="flex items-center gap-1.5 text-primary">
                          <Bookmark className="h-3.5 w-3.5" />
                          {c.heading || `Trang ${c.page_number || 1} • Chunk #${c.chunk_index ?? idx}`}
                        </span>
                        <Badge variant="outline" className="font-mono text-[10px]">
                          Trang {c.page_number || 1}
                        </Badge>
                      </div>

                      <div className="text-xs leading-relaxed font-mono whitespace-pre-wrap text-foreground select-text">
                        {c.content_markdown || c.content}
                      </div>
                    </div>
                  )
                })}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
