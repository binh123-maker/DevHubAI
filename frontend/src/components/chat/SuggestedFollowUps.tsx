import { Sparkles, ArrowRight } from "lucide-react"

interface SuggestedFollowUpsProps {
  onFollowUpClick: (question: string) => void
}

export function SuggestedFollowUps({ onFollowUpClick }: SuggestedFollowUpsProps) {
  const followUps = [
    "Khái niệm này hoạt động như thế nào trong thực tế?",
    "Cho ví dụ minh họa cụ thể bằng code Java/React.",
    "So sánh với các phương pháp và kiến trúc khác.",
  ]

  return (
    <div className="pt-2 space-y-1.5 border-t border-border/30">
      <p className="text-[10px] font-bold text-muted-foreground uppercase tracking-wider flex items-center gap-1">
        <Sparkles className="h-3 w-3 text-primary" />
        Gợi ý câu hỏi tiếp theo (Follow-up Questions):
      </p>
      <div className="flex flex-wrap gap-1.5">
        {followUps.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onFollowUpClick(q)}
            className="inline-flex items-center gap-1.5 rounded-lg border border-primary/20 bg-primary/5 px-2.5 py-1 text-xs text-foreground hover:bg-primary/10 hover:border-primary/40 cursor-pointer transition-all active:scale-95"
          >
            <span>{q}</span>
            <ArrowRight className="h-3 w-3 text-primary shrink-0" />
          </button>
        ))}
      </div>
    </div>
  )
}
