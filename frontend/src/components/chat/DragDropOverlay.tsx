import React from "react"
import { UploadCloud, FileText } from "lucide-react"

interface DragDropOverlayProps {
  isVisible: boolean
}

export const DragDropOverlay = React.memo(function DragDropOverlay({ isVisible }: DragDropOverlayProps) {
  if (!isVisible) return null

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-background/80 backdrop-blur-md border-4 border-dashed border-primary/60 p-8 text-center animate-in fade-in duration-200 pointer-events-none">
      <div className="flex h-20 w-20 items-center justify-center rounded-3xl bg-primary/10 text-primary shadow-inner mb-4 animate-bounce">
        <UploadCloud className="h-10 w-10 text-primary" />
      </div>
      <h2 className="text-2xl font-extrabold tracking-tight text-foreground">
        Thả tập tin để tải lên AI Chat
      </h2>
      <p className="mt-2 text-sm text-muted-foreground max-w-md">
        Hỗ trợ tài liệu PDF, DOCX, TXT, Markdown. Hệ thống sẽ tự động trích xuất chỉ mục RAG cho cuộc trò chuyện này.
      </p>
      <div className="mt-4 inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/5 px-4 py-1.5 text-xs font-semibold text-primary">
        <FileText className="h-4 w-4" />
        <span>Hỗ trợ batch upload nhiều tệp cùng lúc</span>
      </div>
    </div>
  )
})
