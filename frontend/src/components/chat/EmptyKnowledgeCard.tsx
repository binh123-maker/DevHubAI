import { HelpCircle, UploadCloud, Globe } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface EmptyKnowledgeCardProps {
  onUploadClick?: () => void
  onExpandScopeClick?: () => void
}

export function EmptyKnowledgeCard({ onUploadClick, onExpandScopeClick }: EmptyKnowledgeCardProps) {
  return (
    <Card className="border border-amber-500/30 bg-amber-500/5 backdrop-blur-xs my-3 shadow-xs">
      <CardContent className="p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-amber-500/10 text-amber-500">
            <HelpCircle className="h-5 w-5" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-foreground">Không tìm thấy kiến thức phù hợp (No Relevant Knowledge Found)</h4>
            <p className="text-[11px] text-muted-foreground mt-0.5 max-w-md">
              Hệ thống không tìm thấy đoạn văn bản RAG khớp với câu hỏi trong phạm vi hiện tại.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 self-stretch sm:self-center">
          {onExpandScopeClick && (
            <Button variant="outline" size="sm" onClick={onExpandScopeClick} className="h-7 text-xs gap-1 border-amber-500/30">
              <Globe className="h-3 w-3 text-emerald-500" />
              Mở rộng Global Scope
            </Button>
          )}
          {onUploadClick && (
            <Button size="sm" onClick={onUploadClick} className="h-7 text-xs gap-1 shadow-xs">
              <UploadCloud className="h-3 w-3" />
              Tải thêm tài liệu
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
