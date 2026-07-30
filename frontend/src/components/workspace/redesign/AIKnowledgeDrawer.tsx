import React from "react"
import { 
  Sparkles, 
  CheckCircle2, 
  X, 
  FileCheck, 
  Lightbulb, 
  ShieldCheck, 
  TrendingUp 
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"

interface AIKnowledgeDrawerProps {
  workspaceId?: string
  onClose: () => void
  coveragePercent?: number
  chunkCount?: number
  duplicateCount?: number
  brokenCount?: number
}

export const AIKnowledgeDrawer: React.FC<AIKnowledgeDrawerProps> = ({
  onClose,
  coveragePercent = 96,
  chunkCount = 1420,
  duplicateCount = 0,
  brokenCount = 0,
}) => {
  const topSearchTopics = ["FastAPI Gateway", "Vector Embeddings", "RAG Pipeline", "JWT Auth", "PostgreSQL PGVector"]

  return (
    <div className="space-y-6 rounded-3xl border border-border/60 glass-card p-5 shadow-xl">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-border/40 pb-4">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-foreground">Sức khỏe tri thức AI</h3>
            <p className="text-[11px] text-muted-foreground">Trạng thái & Độ phủ RAG Vector</p>
          </div>
        </div>
        <Button variant="ghost" size="icon" onClick={onClose} className="h-7 w-7 rounded-lg">
          <X className="h-4 w-4" />
        </Button>
      </div>

      {/* 1. Knowledge Coverage Gauge */}
      <div className="space-y-2.5 rounded-2xl bg-muted/40 p-4 border border-border/40">
        <div className="flex items-center justify-between text-xs">
          <span className="font-bold text-foreground flex items-center gap-1.5">
            <ShieldCheck className="h-4 w-4 text-emerald-500" />
            Độ phủ tri thức
          </span>
          <span className="font-extrabold text-emerald-600 dark:text-emerald-400">
            {coveragePercent}% Tối ưu
          </span>
        </div>
        <Progress value={coveragePercent} className="h-2 rounded-full bg-muted" />
        <div className="flex justify-between text-[10px] text-muted-foreground">
          <span>{chunkCount} Chunks ngữ nghĩa</span>
          <span>Chất lượng TB 95/100</span>
        </div>
      </div>

      {/* 2. Document Health Checklist */}
      <div className="space-y-3">
        <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
          <FileCheck className="h-3.5 w-3.5 text-blue-500" />
          Toàn vẹn tài liệu
        </h4>

        <div className="space-y-2 text-xs">
          <div className="flex items-center justify-between p-2.5 rounded-xl border border-border/40 bg-background/50">
            <span className="flex items-center gap-2 text-muted-foreground">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              Tài liệu lỗi / chưa phân tích
            </span>
            <Badge variant="outline" className="border-emerald-500/30 text-emerald-600 dark:text-emerald-400 font-bold">
              {brokenCount}
            </Badge>
          </div>

          <div className="flex items-center justify-between p-2.5 rounded-xl border border-border/40 bg-background/50">
            <span className="flex items-center gap-2 text-muted-foreground">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              Tệp trùng lặp
            </span>
            <Badge variant="outline" className="border-emerald-500/30 text-emerald-600 dark:text-emerald-400 font-bold">
              {duplicateCount}
            </Badge>
          </div>
        </div>
      </div>

      {/* 3. Frequently Searched RAG Topics */}
      <div className="space-y-3">
        <h4 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
          <TrendingUp className="h-3.5 w-3.5 text-purple-500" />
          Chủ đề tra cứu hàng đầu
        </h4>
        <div className="flex flex-wrap gap-1.5">
          {topSearchTopics.map((topic, i) => (
            <Badge key={i} variant="secondary" className="rounded-lg text-[11px] font-medium py-1 px-2.5 bg-muted/60 hover:bg-primary/10 hover:text-primary transition-colors cursor-pointer">
              #{topic}
            </Badge>
          ))}
        </div>
      </div>

      {/* 4. Suggested Improvements */}
      <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-3.5 text-xs text-amber-800 dark:text-amber-300 space-y-1.5">
        <div className="flex items-center gap-1.5 font-bold">
          <Lightbulb className="h-4 w-4 text-amber-500 animate-pulse" />
          Gợi ý từ AI
        </div>
        <p className="text-[11px] leading-relaxed text-amber-900/80 dark:text-amber-200/80">
          Tải lên sơ đồ kiến trúc API hoặc OpenAPI schema để tăng độ chính xác của AI Code RAG lên đến 24%.
        </p>
      </div>
    </div>
  )
}
