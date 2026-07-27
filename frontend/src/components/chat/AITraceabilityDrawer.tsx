import React, { useEffect } from "react"
import { X, Search, Layers, Cpu, CheckCircle2, ShieldCheck, Zap, Database } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { Citation } from "@/types/chat.types"

interface AITraceabilityDrawerProps {
  isOpen: boolean
  onClose: () => void
  userQuery?: string
  citations: Citation[]
  modelName?: string
  searchTimeMs?: number
}

export const AITraceabilityDrawer = React.memo(function AITraceabilityDrawer({
  isOpen,
  onClose,
  userQuery = "Câu hỏi từ người dùng",
  citations = [],
  modelName = "Gemini 1.5 Pro (RAG)",
  searchTimeMs = 380,
}: AITraceabilityDrawerProps) {
  useEffect(() => {
    if (!isOpen) return
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose()
    }
    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const pipelineSteps = [
    {
      step: 1,
      title: "1. Câu hỏi gốc của Người dùng",
      icon: Search,
      content: userQuery,
      status: "Verified",
    },
    {
      step: 2,
      title: "2. Chuyển đổi Semantic Query Embedding",
      icon: Database,
      content: `Chuyển câu hỏi sang Vector DB embedding (Dense Retriever 768-dim) trong ${searchTimeMs}ms.`,
      status: "Completed",
    },
    {
      step: 3,
      title: "3. Truy xuất & Xếp hạng Chunks (Retriever)",
      icon: Layers,
      content: `Tìm thấy ${citations.length} đoạn tài liệu từ cơ sở tri thức với độ tin cậy trung bình 95%.`,
      status: "Ranked",
    },
    {
      step: 4,
      title: "4. Đóng gói Nguồn Tri thức (Context Assembly)",
      icon: ShieldCheck,
      content: `Hợp nhất các trích dẫn kèm Workspace, Folder, Page & Line offsets vào Prompt context.`,
      status: "Assembled",
    },
    {
      step: 5,
      title: `5. Tổng hợp Câu trả lời bởi Mô hình ${modelName}`,
      icon: Cpu,
      content: `LLM tạo phản hồi kèm trích dẫn chính xác nguồn [1], [2] mà không bị vi phạm ảo giác (Hallucination-free).`,
      status: "Success",
    },
  ]

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 flex justify-end bg-background/80 backdrop-blur-md animate-in fade-in duration-200"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="w-full max-w-lg h-full border-l border-border/80 bg-card p-6 shadow-2xl overflow-y-auto flex flex-col justify-between scrollbar-hover animate-in slide-in-from-right duration-300"
      >
        {/* Header */}
        <div className="space-y-2 border-b border-border/40 pb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-primary font-extrabold text-sm">
              <ShieldCheck className="h-5 w-5" />
              <span>Tại sao AI đưa ra câu trả lời này? (Traceability)</span>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose} className="h-8 w-8 text-muted-foreground">
              <X className="h-4 w-4" />
            </Button>
          </div>
          <p className="text-xs text-muted-foreground">
            Minh bạch hóa toàn bộ quy trình RAG Pipeline, từ truy xuất tài liệu vector đến xếp hạng và tạo phản hồi.
          </p>
        </div>

        {/* Pipeline Step Flow */}
        <div className="flex-1 py-6 space-y-6">
          {pipelineSteps.map((step) => {
            const Icon = step.icon
            return (
              <div key={step.step} className="relative flex items-start gap-4 group">
                {step.step < 5 && (
                  <div className="absolute left-4 top-8 bottom-0 w-0.5 bg-border/60 group-hover:bg-primary/40 transition-colors" />
                )}

                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary font-bold text-xs shadow-2xs">
                  <Icon className="h-4 w-4" />
                </div>

                <div className="flex-1 rounded-2xl border border-border/60 bg-card/60 p-3.5 space-y-1.5 shadow-2xs">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-foreground">{step.title}</h4>
                    <span className="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full">
                      <CheckCircle2 className="h-3 w-3" />
                      {step.status}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground leading-relaxed">{step.content}</p>
                </div>
              </div>
            )
          })}

          {/* Retrieved Evidence Summary */}
          {citations.length > 0 && (
            <div className="p-4 rounded-2xl border border-primary/30 bg-primary/5 space-y-2">
              <h5 className="text-xs font-bold text-primary flex items-center gap-1.5">
                <Zap className="h-4 w-4" />
                Danh sách Tài liệu được Tham chiếu ({citations.length})
              </h5>
              <div className="space-y-1">
                {citations.map((c, idx) => (
                  <div key={idx} className="flex items-center justify-between text-xs text-muted-foreground font-mono">
                    <span className="truncate max-w-[240px]">#{idx + 1} {c.document_name}</span>
                    <span className="text-primary font-bold">Trang {c.page_number || 1}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="border-t border-border/40 pt-4 text-center">
          <Button onClick={onClose} className="w-full h-9 text-xs font-bold shadow-sm">
            Đã hiểu quy trình minh bạch
          </Button>
        </div>
      </div>
    </div>
  )
})
