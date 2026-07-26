import { Draggable } from "@hello-pangea/dnd"
import { FileText, Calendar, Eye, FileCode, Globe } from "lucide-react"
import { Link } from "react-router-dom"

import { Card, CardContent } from "@/components/ui/card"
import type { Document } from "@/api/document.api"

interface KanbanCardProps {
  document: Document
  index: number
  workspaceName?: string
  folderName?: string
}

export function KanbanCard({ document, index, workspaceName, folderName }: KanbanCardProps) {
  const getFileIcon = (fileType: string) => {
    if (fileType.includes("pdf")) return <FileText className="h-4 w-4 text-red-500" />
    if (fileType.includes("word") || fileType.includes("docx")) return <FileText className="h-4 w-4 text-blue-500" />
    if (fileType.includes("url") || fileType.includes("html")) return <Globe className="h-4 w-4 text-emerald-500" />
    if (fileType.includes("code") || fileType.includes("json")) return <FileCode className="h-4 w-4 text-amber-500" />
    return <FileText className="h-4 w-4 text-indigo-500" />
  }

  const formatSize = (bytes: number) => {
    if (!bytes) return "0 KB"
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatTime = (dateStr: string) => {
    try {
      const d = new Date(dateStr)
      return d.toLocaleDateString("vi-VN", { month: "short", day: "numeric" })
    } catch {
      return dateStr
    }
  }

  return (
    <Draggable draggableId={document.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          style={provided.draggableProps.style as React.CSSProperties}
          className="mb-3"
        >

          <Card
            className={`group relative border border-border/60 bg-card/90 backdrop-blur-xs transition-all duration-200 hover:shadow-md hover:border-primary/40 ${
              snapshot.isDragging
                ? "shadow-xl ring-2 ring-primary/60 scale-[1.02] rotate-1 z-50 bg-card"
                : ""
            }`}
          >
            <CardContent className="p-3.5 space-y-2.5">
              {/* Header: Icon & Title */}
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2.5 min-w-0">
                  <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-muted/60">
                    {getFileIcon(document.file_type)}
                  </div>
                  <div className="min-w-0">
                    <Link
                      to={`/documents/${document.id}`}
                      className="text-sm font-semibold text-foreground line-clamp-2 hover:underline hover:text-primary transition-colors"
                    >
                      {document.title}
                    </Link>
                    {document.description && (
                      <p className="mt-0.5 text-xs text-muted-foreground line-clamp-1">
                        {document.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              {/* Workspace / Folder tags */}
              {(workspaceName || folderName) && (
                <div className="flex flex-wrap gap-1.5 pt-0.5">
                  {workspaceName && (
                    <span className="inline-flex items-center rounded-full bg-primary/10 px-2 py-0.5 text-[10px] font-medium text-primary border border-primary/20">
                      {workspaceName}
                    </span>
                  )}
                  {folderName && (
                    <span className="inline-flex items-center rounded-full bg-secondary px-2 py-0.5 text-[10px] font-medium text-secondary-foreground">
                      {folderName}
                    </span>
                  )}
                </div>
              )}

              {/* Footer info */}
              <div className="flex items-center justify-between pt-1 border-t border-border/40 text-[11px] text-muted-foreground">
                <div className="flex items-center gap-2">
                  <span>{formatSize(document.file_size)}</span>
                  <span className="flex items-center gap-0.5">
                    <Eye className="h-3 w-3" />
                    {document.view_count}
                  </span>
                </div>
                <span className="flex items-center gap-1 font-mono text-[10px]">
                  <Calendar className="h-3 w-3" />
                  {formatTime(document.kanban_updated_at || document.created_at)}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </Draggable>
  )
}
