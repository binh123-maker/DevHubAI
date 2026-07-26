import { HelpCircle, Layers, Maximize2, Sparkles, Feather } from "lucide-react"

interface MessageActionsProps {
  onActionClick: (promptText: string) => void
}

export function MessageActions({ onActionClick }: MessageActionsProps) {
  const actions = [
    { label: "Giải thích đơn giản hơn", prompt: "Hãy giải thích câu trả lời trên một cách đơn giản, dễ hiểu cho người mới bắt đầu.", icon: Sparkles },
    { label: "Mở rộng câu trả lời", prompt: "Hãy mở rộng và bổ sung thêm các chi tiết nâng cao cho câu trả lời trên.", icon: Maximize2 },
    { label: "Viết tiếp", prompt: "Hãy tiếp tục viết và phát triển thêm ý cho nội dung trên.", icon: Feather },
    { label: "Tạo bài trắc nghiệm", prompt: "Tạo 3 câu hỏi trắc nghiệm RAG kiểm tra kiến thức về nội dung trên.", icon: HelpCircle },
    { label: "Tạo thẻ Flashcards", prompt: "Tạo bộ 5 thẻ ghi nhớ Flashcard (Front/Back) từ nội dung trên.", icon: Layers },
  ]

  return (
    <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none pt-1">
      {actions.map((act, idx) => {
        const Icon = act.icon
        return (
          <button
            key={idx}
            onClick={() => onActionClick(act.prompt)}
            className="inline-flex items-center gap-1 shrink-0 rounded-md border border-border/60 bg-muted/30 px-2 py-0.5 text-[11px] font-medium text-muted-foreground hover:text-foreground hover:bg-accent transition-all cursor-pointer"
          >
            <Icon className="h-3 w-3 text-primary" />
            <span>{act.label}</span>
          </button>
        )
      })}
    </div>
  )
}
