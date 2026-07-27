import React from "react"
import { Sparkles, Globe, FolderOpen, FileText } from "lucide-react"

interface WelcomeChatStateProps {
  chatMode?: "global" | "workspace"
  workspaceName?: string
  onPromptClick: (promptText: string) => void
}

export const WelcomeChatState = React.memo(function WelcomeChatState({
  chatMode = "global",
  workspaceName,
  onPromptClick,
}: WelcomeChatStateProps) {
  const suggestedPrompts = [
    { icon: FileText, title: "Tóm tắt kiến thức ", text: "Tóm tắt lại các khái niệm chính trong tài liệu." },
    { icon: Sparkles, title: "Những tài liệu mới nhất", text: "Liệt kê danh sách những tài liệu vừa tải lên gần đây." },
  ]

  return (
    <div className="flex-1 flex flex-col justify-center items-center py-4 px-4 max-w-[900px] mx-auto w-full text-center space-y-3.5 my-auto animate-in fade-in zoom-in-95 duration-300">
      {/* Icon Badge */}
      <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10 text-primary shadow-inner shrink-0">
        {chatMode === "workspace" ? (
          <FolderOpen className="h-6 w-6 text-amber-500" />
        ) : (
          <Globe className="h-6 w-6 text-primary" />
        )}
      </div>

      {/* Greeting Title & Subtitle */}
      <div className="space-y-1">
        <h1 className="text-xl sm:text-2xl font-extrabold tracking-tight">
          Xin chào 👋
        </h1>
        <p className="text-xs sm:text-sm text-muted-foreground max-w-md mx-auto leading-relaxed">
          Hỏi AI bất kỳ câu hỏi nào về toàn bộ kiến thức và tài liệu trong DevHub AI.
        </p>
      </div>

      {/* Scope Badge */}
      <div className="inline-flex items-center gap-2 rounded-full border border-border/80 bg-card px-3 py-1 text-xs font-semibold shadow-2xs shrink-0">
        <span className={`h-2 w-2 rounded-full ${chatMode === "workspace" ? "bg-amber-500" : "bg-emerald-500"}`} />
        <span className="text-muted-foreground">Knowledge Scope:</span>
        <span className="text-primary font-bold">
          {chatMode === "workspace" ? `● Workspace: ${workspaceName || "Đang chọn"}` : "● All Documents (Toàn bộ tài liệu)"}
        </span>
      </div>

      {/* Suggested Prompts Grid */}
      <div className="w-full max-w-2xl pt-2 space-y-2">
        <p className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider text-left pl-1">
          Gợi ý câu hỏi bắt đầu:
        </p>
        <div className="grid gap-2 sm:grid-cols-2 text-left">
          {suggestedPrompts.map((p, idx) => {
            const Icon = p.icon
            return (
              <div
                key={idx}
                onClick={() => onPromptClick(p.text)}
                role="button"
                tabIndex={0}
                className="group flex flex-col justify-between p-3 rounded-xl border border-border/60 bg-card/60 hover:bg-accent/80 hover:border-primary/40 cursor-pointer transition-all duration-200 shadow-2xs active:scale-[0.98]"
              >
                <div className="flex items-center gap-2 font-semibold text-xs text-foreground group-hover:text-primary transition-colors">
                  <Icon className="h-3.5 w-3.5 text-primary/80 shrink-0" />
                  <span className="truncate">{p.title}</span>
                </div>
                <p className="mt-1 text-[11px] text-muted-foreground line-clamp-1">
                  &ldquo;{p.text}&rdquo;
                </p>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
})

