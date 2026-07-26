import { CheckCircle2, Clock, Layers, FileText, FolderOpen } from "lucide-react"

interface AnswerSourcesSummaryProps {
  documentCount?: number
  chunkCount?: number
  workspaceCount?: number
  searchTimeMs?: number
}

export function AnswerSourcesSummary({
  documentCount = 3,
  chunkCount = 8,
  workspaceCount = 1,
  searchTimeMs = 380,
}: AnswerSourcesSummaryProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-emerald-500/30 bg-emerald-500/5 px-3 py-2 text-xs font-semibold text-emerald-600 dark:text-emerald-400">
      <div className="flex items-center gap-3 flex-wrap">
        <span className="flex items-center gap-1 font-bold">
          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
          Nguồn kiến thức (RAG):
        </span>
        <span className="flex items-center gap-1 text-[11px] font-medium text-foreground">
          <FileText className="h-3 w-3 text-blue-500" />
          {documentCount} Tài liệu
        </span>
        <span className="flex items-center gap-1 text-[11px] font-medium text-foreground">
          <Layers className="h-3 w-3 text-purple-500" />
          {chunkCount} Đoạn văn bản
        </span>
        <span className="flex items-center gap-1 text-[11px] font-medium text-foreground">
          <FolderOpen className="h-3 w-3 text-amber-500" />
          {workspaceCount} Workspaces
        </span>
      </div>

      <div className="flex items-center gap-1 text-[10px] text-muted-foreground font-mono">
        <Clock className="h-3 w-3 text-muted-foreground" />
        <span>Thời gian tra cứu: {searchTimeMs}ms</span>
      </div>
    </div>
  )
}
