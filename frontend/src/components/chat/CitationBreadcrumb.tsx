import React from "react"
import { ChevronRight, FolderOpen, Layers, FileText } from "lucide-react"

interface CitationBreadcrumbProps {
  workspaceName?: string
  folderName?: string
  documentName?: string
  heading?: string
  pageNumber?: number
  chunkIndex?: number
  onNavigateCrumb?: (type: "workspace" | "folder" | "document" | "page") => void
}

export const CitationBreadcrumb = React.memo(function CitationBreadcrumb({
  workspaceName = "Backend",
  folderName = "Spring",
  documentName = "IOC.pdf",
  heading = "Dependency Injection",
  pageNumber = 18,
  chunkIndex = 92,
  onNavigateCrumb,
}: CitationBreadcrumbProps) {
  return (
    <nav className="flex items-center gap-1.5 overflow-x-auto text-xs font-semibold text-muted-foreground py-1.5 px-3 rounded-xl border border-border/60 bg-card/60 backdrop-blur-md scrollbar-none shadow-2xs">
      <button
        onClick={() => onNavigateCrumb && onNavigateCrumb("workspace")}
        className="flex items-center gap-1 hover:text-primary transition-colors shrink-0"
      >
        <FolderOpen className="h-3.5 w-3.5 text-amber-500" />
        <span>{workspaceName}</span>
      </button>

      <ChevronRight className="h-3 w-3 text-muted-foreground/40 shrink-0" />

      <button
        onClick={() => onNavigateCrumb && onNavigateCrumb("folder")}
        className="flex items-center gap-1 hover:text-primary transition-colors shrink-0"
      >
        <Layers className="h-3.5 w-3.5 text-blue-500" />
        <span>{folderName}</span>
      </button>

      <ChevronRight className="h-3 w-3 text-muted-foreground/40 shrink-0" />

      <button
        onClick={() => onNavigateCrumb && onNavigateCrumb("document")}
        className="flex items-center gap-1 hover:text-primary transition-colors font-bold text-foreground shrink-0"
      >
        <FileText className="h-3.5 w-3.5 text-primary" />
        <span>{documentName}</span>
      </button>

      {heading && (
        <>
          <ChevronRight className="h-3 w-3 text-muted-foreground/40 shrink-0" />
          <span className="text-primary truncate max-w-[140px] shrink-0">📍 {heading}</span>
        </>
      )}

      {pageNumber !== undefined && (
        <>
          <ChevronRight className="h-3 w-3 text-muted-foreground/40 shrink-0" />
          <button
            onClick={() => onNavigateCrumb && onNavigateCrumb("page")}
            className="rounded bg-primary/10 px-1.5 py-0.5 font-mono text-[10px] font-bold text-primary hover:bg-primary/20 transition-all shrink-0"
          >
            Trang {pageNumber}
          </button>
        </>
      )}

      {chunkIndex !== undefined && (
        <>
          <ChevronRight className="h-3 w-3 text-muted-foreground/40 shrink-0" />
          <span className="rounded bg-muted px-1.5 py-0.5 font-mono text-[10px] font-bold text-muted-foreground shrink-0">
            Chunk #{chunkIndex}
          </span>
        </>
      )}
    </nav>
  )
})
