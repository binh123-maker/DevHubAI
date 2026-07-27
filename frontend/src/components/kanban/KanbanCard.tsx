import { Draggable } from "@hello-pangea/dnd"
import { FileText, Calendar, Eye, FileCode, Globe, Layers, MessageSquare, ExternalLink, RefreshCw, CheckCircle2, AlertTriangle, Loader2 } from "lucide-react"
import { Link } from "react-router-dom"
import { useMutation, useQueryClient } from "@tanstack/react-query"

import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { documentApi, type Document } from "@/api/document.api"

interface KanbanCardProps {
  document: Document
  index: number
  workspaceName?: string
  folderName?: string
}

export function KanbanCard({ document, index, workspaceName, folderName }: KanbanCardProps) {
  const queryClient = useQueryClient()

  const retryMutation = useMutation({
    mutationFn: () => documentApi.retryProcessing(document.id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["documents"] })
      void queryClient.invalidateQueries({ queryKey: ["dashboardOverview"] })
    },
  })

  const getFileIcon = (fileType: string) => {
    const ft = (fileType || "").toLowerCase()
    if (ft.includes("pdf")) return <FileText className="h-4 w-4 text-red-500" />
    if (ft.includes("word") || ft.includes("docx")) return <FileText className="h-4 w-4 text-blue-500" />
    if (ft.includes("url") || ft.includes("html") || ft.includes("webpage")) return <Globe className="h-4 w-4 text-emerald-500" />
    if (ft.includes("code") || ft.includes("json")) return <FileCode className="h-4 w-4 text-amber-500" />
    return <FileText className="h-4 w-4 text-indigo-500" />
  }

  const formatSize = (bytes: number) => {
    if (!bytes) return "0 KB"
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatTime = (dateStr?: string | null) => {
    if (!dateStr) return "Chưa xem"
    try {
      const d = new Date(dateStr)
      return d.toLocaleDateString("vi-VN", { month: "short", day: "numeric" })
    } catch {
      return dateStr
    }
  }

  const getStatusBadge = (status: string) => {
    if (status === "PROCESSED") {
      return (
        <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-bold text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
          <CheckCircle2 className="h-3 w-3" />
          Ready for RAG
        </span>
      )
    }
    if (status === "PROCESSING" || status === "UPLOADING") {
      return (
        <span className="inline-flex items-center gap-1 rounded-full bg-amber-500/10 px-2 py-0.5 text-[10px] font-bold text-amber-600 dark:text-amber-400 border border-amber-500/20">
          <Loader2 className="h-3 w-3 animate-spin" />
          Processing RAG
        </span>
      )
    }
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-destructive/10 px-2 py-0.5 text-[10px] font-bold text-destructive border border-destructive/20">
        <AlertTriangle className="h-3 w-3" />
        Failed
      </span>
    )
  }

  const getLearningBadge = (ks: string) => {
    switch (ks) {
      case "learning":
        return <span className="rounded-full bg-blue-500/10 px-2 py-0.5 text-[10px] font-bold text-blue-600 border border-blue-500/20">Đang học</span>
      case "completed":
        return <span className="rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-bold text-emerald-600 border border-emerald-500/20">Hoàn thành</span>
      case "archived":
        return <span className="rounded-full bg-slate-500/10 px-2 py-0.5 text-[10px] font-bold text-slate-600 border border-slate-500/20">Đã lưu trữ</span>
      default:
        return <span className="rounded-full bg-purple-500/10 px-2 py-0.5 text-[10px] font-bold text-purple-600 border border-purple-500/20">Mới</span>
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
              {/* Header: Icon & Title & Badges */}
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-start gap-2.5 min-w-0">
                  <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-muted/60">
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

              {/* Status Badges Row */}
              <div className="flex items-center gap-1.5 flex-wrap">
                {getStatusBadge(document.status)}
                {getLearningBadge(document.kanban_status)}
                {document.total_chunks !== undefined && document.total_chunks > 0 && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-indigo-500/10 px-2 py-0.5 text-[10px] font-mono font-bold text-indigo-600 border border-indigo-500/20">
                    <Layers className="h-3 w-3" />
                    {document.total_chunks} chunks
                  </span>
                )}
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

              {/* Footer Actions & Metadata */}
              <div className="flex items-center justify-between pt-2 border-t border-border/40 text-[11px] text-muted-foreground">
                <div className="flex items-center gap-2">
                  <span>{formatSize(document.file_size)}</span>
                  <span className="flex items-center gap-0.5" title="Lượt xem / Mở">
                    <Eye className="h-3 w-3" />
                    {document.view_count}
                  </span>
                  <span className="flex items-center gap-0.5 text-[10px] font-mono" title="Ngày tải lên / mở">
                    <Calendar className="h-3 w-3" />
                    {formatTime(document.last_opened_at || document.created_at)}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  {document.status === "FAILED" && (
                    <Button
                      size="icon"
                      variant="ghost"
                      className="h-6 w-6 text-destructive hover:bg-destructive/10"
                      title="Thử lại xử lý RAG"
                      onClick={(e) => {
                        e.stopPropagation()
                        retryMutation.mutate()
                      }}
                      disabled={retryMutation.isPending}
                    >
                      <RefreshCw className={`h-3 w-3 ${retryMutation.isPending ? "animate-spin" : ""}`} />
                    </Button>
                  )}
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-6 w-6 text-muted-foreground hover:text-primary"
                    title="Mở xem tài liệu"
                    asChild
                  >
                    <Link to={`/documents/${document.id}`}>
                      <ExternalLink className="h-3 w-3" />
                    </Link>
                  </Button>
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-6 w-6 text-muted-foreground hover:text-emerald-500"
                    title="Hỏi AI về tài liệu này"
                    asChild
                  >
                    <Link to={`/history?workspace_id=${document.workspace_id}`}>
                      <MessageSquare className="h-3 w-3" />
                    </Link>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </Draggable>
  )
}
