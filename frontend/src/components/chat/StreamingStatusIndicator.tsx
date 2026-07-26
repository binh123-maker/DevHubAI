import { useState, useEffect } from "react"
import { BookOpen, Brain, Building2, Pin, CheckCircle2 } from "lucide-react"

export function StreamingStatusIndicator() {
  const [stage, setStage] = useState<1 | 2 | 3 | 4 | 5>(1)

  useEffect(() => {
    const t1 = setTimeout(() => setStage(2), 1000)
    const t2 = setTimeout(() => setStage(3), 2200)
    const t3 = setTimeout(() => setStage(4), 3500)
    const t4 = setTimeout(() => setStage(5), 4800)

    return () => {
      clearTimeout(t1)
      clearTimeout(t2)
      clearTimeout(t3)
      clearTimeout(t4)
    }
  }, [])

  return (
    <div className="flex items-center gap-2 rounded-xl border border-primary/30 bg-primary/5 px-3.5 py-2 text-xs font-semibold text-primary animate-in fade-in duration-200">
      {stage === 1 && (
        <>
          <BookOpen className="h-4 w-4 animate-bounce text-blue-500" />
          <span>📖 Reading documents (Đang đọc tài liệu)...</span>
        </>
      )}
      {stage === 2 && (
        <>
          <Brain className="h-4 w-4 animate-pulse text-purple-500" />
          <span>🧠 Understanding context (Đang phân tích ngữ cảnh RAG)...</span>
        </>
      )}
      {stage === 3 && (
        <>
          <Building2 className="h-4 w-4 animate-spin text-amber-500" />
          <span>🏗️ Building answer (Đang xây dựng câu trả lời)...</span>
        </>
      )}
      {stage === 4 && (
        <>
          <Pin className="h-4 w-4 animate-bounce text-emerald-500" />
          <span>📌 Generating citations (Đang tạo trích dẫn nguồn)...</span>
        </>
      )}
      {stage === 5 && (
        <>
          <CheckCircle2 className="h-4 w-4 text-emerald-500" />
          <span>✅ Done (Hoàn tất)</span>
        </>
      )}
    </div>
  )
}
