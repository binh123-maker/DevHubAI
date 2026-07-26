import { ElementType } from "react"
import { FileText, BookOpen, HelpCircle, Layers, Search, Languages } from "lucide-react"

export interface SlashCommand {
  cmd: string
  label: string
  description: string
  icon: ElementType
  template: string
}

export const SLASH_COMMANDS: SlashCommand[] = [
  {
    cmd: "/summarize",
    label: "Tóm tắt tài liệu",
    description: "Tóm tắt toàn bộ các ý chính trong phạm vi tài liệu đã chọn",
    icon: FileText,
    template: "Hãy tóm tắt ngắn gọn các điểm chính trong tài liệu này.",
  },
  {
    cmd: "/explain",
    label: "Giải thích khái niệm",
    description: "Giải thích chi tiết và cấp ví dụ minh họa về một khái niệm",
    icon: BookOpen,
    template: "Hãy giải thích chi tiết khái niệm sau kèm ví dụ minh họa: ",
  },
  {
    cmd: "/quiz",
    label: "Tạo câu hỏi trắc nghiệm",
    description: "Tạo 3 câu hỏi trắc nghiệm kiểm tra kiến thức trích xuất RAG",
    icon: HelpCircle,
    template: "Tạo 3 câu hỏi trắc nghiệm kèm đáp án dựa trên nội dung tài liệu.",
  },
  {
    cmd: "/flashcards",
    label: "Tạo thẻ ghi nhớ Flashcards",
    description: "Tạo bộ 5 thẻ ghi nhớ (Front/Back) từ kho tri thức",
    icon: Layers,
    template: "Tạo 5 thẻ ghi nhớ Flashcard (Mặt trước / Mặt sau) từ tài liệu.",
  },
  {
    cmd: "/find",
    label: "Tìm kiếm thông tin",
    description: "Tìm kiếm các đoạn văn bản chính xác nói về từ khóa",
    icon: Search,
    template: "Tìm kiếm và trích dẫn các đoạn văn bản đề cập đến: ",
  },
  {
    cmd: "/translate",
    label: "Dịch thuật sang Tiếng Việt",
    description: "Dịch lại nội dung tài liệu sang Tiếng Việt chuẩn mực",
    icon: Languages,
    template: "Hãy dịch và giải thích nội dung sau sang Tiếng Việt: ",
  },
]

interface SlashCommandPopoverProps {
  filter: string
  onSelectCommand: (command: SlashCommand) => void
  onClose?: () => void
}

export function SlashCommandPopover({ filter, onSelectCommand }: SlashCommandPopoverProps) {
  const filtered = SLASH_COMMANDS.filter(
    (c) => c.cmd.toLowerCase().includes(filter.toLowerCase()) || c.label.toLowerCase().includes(filter.toLowerCase())
  )

  if (filtered.length === 0) return null

  return (
    <div className="absolute bottom-full left-3 mb-2 w-80 rounded-xl border border-border/80 bg-popover text-popover-foreground shadow-2xl p-1.5 z-50 animate-in fade-in slide-in-from-bottom-2 duration-150">
      <p className="px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
        Lệnh điều hướng (Slash Commands)
      </p>
      <div className="space-y-0.5 max-h-56 overflow-y-auto scrollbar-thin">
        {filtered.map((c) => {
          const Icon = c.icon
          return (
            <div
              key={c.cmd}
              onClick={() => onSelectCommand(c)}
              className="flex items-center gap-2.5 rounded-lg p-2 text-xs hover:bg-accent cursor-pointer transition-colors group"
            >
              <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary group-hover:scale-110 transition-transform">
                <Icon className="h-3.5 w-3.5" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-foreground group-hover:text-primary transition-colors">
                    {c.cmd}
                  </span>
                  <span className="text-[10px] text-muted-foreground font-mono">{c.label}</span>
                </div>
                <p className="text-[11px] text-muted-foreground truncate mt-0.5">{c.description}</p>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
