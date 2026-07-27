import { Link } from "react-router-dom"
import { FileText, CheckCircle2, ExternalLink, MessageSquare, Clock, Activity, ShieldCheck, BookOpen } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import type { UserDashboardOverviewResponse } from "@/api/dashboard.api"

interface KnowledgeOverviewWidgetProps {
  dashboard: UserDashboardOverviewResponse
}

export function KnowledgeOverviewWidget({ dashboard }: KnowledgeOverviewWidgetProps) {
  const recentDocs = dashboard.recent_documents || []
  const processedDocs = dashboard.recently_processed || []
  const openedDocs = dashboard.recently_opened || []
  const kanban = dashboard.kanban_summary || { new: 0, learning: 0, completed: 0, archived: 0 }
  const health = dashboard.knowledge_health || {}

  const totalKanbanDocs = (kanban.new || 0) + (kanban.learning || 0) + (kanban.completed || 0) + (kanban.archived || 0)

  const formatSize = (bytes: number) => {
    if (!bytes) return "0 KB"
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const formatDate = (dateStr: string) => {
    try {
      return new Date(dateStr).toLocaleDateString("vi-VN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })
    } catch {
      return dateStr
    }
  }

  return (
    <div className="space-y-6">
      {/* 1. Kanban Progress Summary & Knowledge Health Row */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Kanban Workflow Summary */}
        <Card className="border border-border/60 bg-card/60 backdrop-blur-xs">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-sm font-bold flex items-center justify-between">
              <span className="flex items-center gap-2 text-foreground">
                <BookOpen className="h-4 w-4 text-primary" />
                Tiến độ Học tập (Kanban Overview)
              </span>
              <span className="text-xs font-normal text-muted-foreground">{totalKanbanDocs} tài liệu</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-2 space-y-4">
            {/* Visual Progress Bar */}
            <div className="h-2.5 w-full bg-muted/60 rounded-full overflow-hidden flex">
              <div
                className="bg-purple-500 transition-all duration-300"
                style={{ width: `${totalKanbanDocs ? ((kanban.new || 0) / totalKanbanDocs) * 100 : 0}%` }}
                title={`Mới: ${kanban.new || 0}`}
              />
              <div
                className="bg-blue-500 transition-all duration-300"
                style={{ width: `${totalKanbanDocs ? ((kanban.learning || 0) / totalKanbanDocs) * 100 : 0}%` }}
                title={`Đang học: ${kanban.learning || 0}`}
              />
              <div
                className="bg-emerald-500 transition-all duration-300"
                style={{ width: `${totalKanbanDocs ? ((kanban.completed || 0) / totalKanbanDocs) * 100 : 0}%` }}
                title={`Hoàn thành: ${kanban.completed || 0}`}
              />
              <div
                className="bg-slate-400 transition-all duration-300"
                style={{ width: `${totalKanbanDocs ? ((kanban.archived || 0) / totalKanbanDocs) * 100 : 0}%` }}
                title={`Đã lưu trữ: ${kanban.archived || 0}`}
              />
            </div>

            {/* Badges Count */}
            <div className="grid grid-cols-4 gap-2 text-center text-xs">
              <div className="rounded-lg bg-purple-500/10 p-2 border border-purple-500/20">
                <p className="text-[10px] text-purple-600 dark:text-purple-400 font-bold">MỚI</p>
                <p className="text-base font-extrabold text-purple-600 dark:text-purple-400">{kanban.new || 0}</p>
              </div>
              <div className="rounded-lg bg-blue-500/10 p-2 border border-blue-500/20">
                <p className="text-[10px] text-blue-600 dark:text-blue-400 font-bold">ĐANG HỌC</p>
                <p className="text-base font-extrabold text-blue-600 dark:text-blue-400">{kanban.learning || 0}</p>
              </div>
              <div className="rounded-lg bg-emerald-500/10 p-2 border border-emerald-500/20">
                <p className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold">HOÀN THÀNH</p>
                <p className="text-base font-extrabold text-emerald-600 dark:text-emerald-400">{kanban.completed || 0}</p>
              </div>
              <div className="rounded-lg bg-slate-500/10 p-2 border border-slate-500/20">
                <p className="text-[10px] text-slate-600 dark:text-slate-400 font-bold">LƯU TRỮ</p>
                <p className="text-base font-extrabold text-slate-600 dark:text-slate-400">{kanban.archived || 0}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Knowledge Health Monitor */}
        <Card className="border border-border/60 bg-card/60 backdrop-blur-xs">
          <CardHeader className="p-4 pb-2">
            <CardTitle className="text-sm font-bold flex items-center justify-between">
              <span className="flex items-center gap-2 text-foreground">
                <ShieldCheck className="h-4 w-4 text-emerald-500" />
                Sức khỏe Hệ thống RAG & Embedding
              </span>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500/10 px-2 py-0.5 text-[10px] font-bold text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                <Activity className="h-3 w-3" />
                {health.search_health || "100% Operational"}
              </span>
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-2">
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-muted/30 border border-border/40">
                <span className="text-muted-foreground">Vector Indexed</span>
                <span className="font-bold text-foreground">{health.indexed_documents ?? dashboard.statistics.documents_processed}</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-muted/30 border border-border/40">
                <span className="text-muted-foreground">Hàng đợi Xử lý</span>
                <span className="font-bold text-amber-500">{health.processing_queue ?? 0}</span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-muted/30 border border-border/40">
                <span className="text-muted-foreground">Tài liệu Lỗi</span>
                <span className={`font-bold ${health.failed_documents ? "text-destructive" : "text-emerald-500"}`}>
                  {health.failed_documents ?? 0}
                </span>
              </div>
              <div className="flex items-center justify-between p-2.5 rounded-lg bg-muted/30 border border-border/40">
                <span className="text-muted-foreground">Độ trễ Tra cứu</span>
                <span className="font-mono font-bold text-purple-500">{health.avg_retrieval_time_ms ?? 120}ms</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 2. Latest Uploaded Documents & Recently Processed */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Latest Documents */}
        <Card className="border border-border/60 bg-card/60 backdrop-blur-xs">
          <CardHeader className="p-4 pb-3 flex flex-row items-center justify-between">
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <FileText className="h-5 w-5 text-indigo-500" />
              Tài liệu Mới tải lên ({recentDocs.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0 space-y-3">
            {recentDocs.length === 0 ? (
              <p className="text-xs text-muted-foreground py-6 text-center">Chưa có tài liệu nào gần đây.</p>
            ) : (
              recentDocs.slice(0, 5).map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between gap-3 p-2.5 rounded-xl border border-border/40 bg-card/40 hover:bg-card/80 transition-colors group"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-500/10 text-indigo-500 font-bold text-xs">
                      <FileText className="h-4 w-4" />
                    </div>
                    <div className="min-w-0">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="text-xs font-bold text-foreground truncate hover:underline hover:text-primary block"
                      >
                        {doc.title}
                      </Link>
                      <div className="flex items-center gap-2 text-[10px] text-muted-foreground mt-0.5">
                        <span className="truncate">{doc.workspace_name || "Workspace"}</span>
                        <span>•</span>
                        <span>{formatSize(doc.file_size)}</span>
                        <span>•</span>
                        <span>{formatDate(doc.created_at)}</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-1 shrink-0">
                    <Button size="icon" variant="ghost" className="h-7 w-7 text-muted-foreground hover:text-primary" asChild title="Mở Tài liệu">
                      <Link to={`/documents/${doc.id}`}>
                        <ExternalLink className="h-3.5 w-3.5" />
                      </Link>
                    </Button>
                    <Button size="icon" variant="ghost" className="h-7 w-7 text-muted-foreground hover:text-emerald-500" asChild title="Chat RAG">
                      <Link to={`/history?workspace_id=${doc.workspace_id}`}>
                        <MessageSquare className="h-3.5 w-3.5" />
                      </Link>
                    </Button>
                  </div>
                </div>
              ))
            )}
          </CardContent>
        </Card>

        {/* Recently Processed & Ready for RAG */}
        <Card className="border border-border/60 bg-card/60 backdrop-blur-xs">
          <CardHeader className="p-4 pb-3 flex flex-row items-center justify-between">
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-emerald-500" />
              Tài liệu Đã xử lý & Sẵn sàng RAG ({processedDocs.length})
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0 space-y-3">
            {processedDocs.length === 0 ? (
              <p className="text-xs text-muted-foreground py-6 text-center">Chưa có tài liệu hoàn thành xử lý vector.</p>
            ) : (
              processedDocs.slice(0, 5).map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between gap-3 p-2.5 rounded-xl border border-emerald-500/20 bg-emerald-500/5 hover:bg-emerald-500/10 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 font-bold text-xs">
                      <CheckCircle2 className="h-4 w-4" />
                    </div>
                    <div className="min-w-0">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="text-xs font-bold text-foreground truncate hover:underline hover:text-primary block"
                      >
                        {doc.title}
                      </Link>
                      <div className="flex items-center gap-2 text-[10px] text-muted-foreground mt-0.5">
                        <span className="font-mono text-emerald-600 dark:text-emerald-400 font-bold">
                          {doc.total_chunks} Chunks RAG
                        </span>
                        <span>•</span>
                        <span className="text-emerald-600 dark:text-emerald-400 font-semibold">Ready for RAG</span>
                      </div>
                    </div>
                  </div>

                  <Button size="sm" variant="outline" className="h-7 text-[11px] gap-1 border-emerald-500/30 text-emerald-600 dark:text-emerald-400" asChild>
                    <Link to={`/documents/${doc.id}`}>
                      Xem Chunks
                    </Link>
                  </Button>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </div>

      {/* 3. Recently Opened Documents */}
      {openedDocs.length > 0 && (
        <Card className="border border-border/60 bg-card/60 backdrop-blur-xs">
          <CardHeader className="p-4 pb-3">
            <CardTitle className="text-base font-bold flex items-center gap-2">
              <Clock className="h-5 w-5 text-amber-500" />
              Tài liệu Vừa mở Gần đây
            </CardTitle>
          </CardHeader>
          <CardContent className="p-4 pt-0 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {openedDocs.slice(0, 6).map((doc) => (
              <div key={doc.id} className="p-3 rounded-xl border border-border/50 bg-background/50 hover:bg-card transition-all space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs font-bold text-foreground line-clamp-1">{doc.title}</span>
                  <span className="text-[10px] text-muted-foreground shrink-0">{doc.view_count} lượt xem</span>
                </div>
                <div className="flex items-center justify-between text-[10px] text-muted-foreground pt-1 border-t border-border/30">
                  <span className="truncate">{doc.workspace_name || "Workspace"}</span>
                  <Button size="sm" variant="ghost" className="h-6 text-[10px] px-2 text-primary" asChild>
                    <Link to={`/documents/${doc.id}`}>Mở lại →</Link>
                  </Button>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
