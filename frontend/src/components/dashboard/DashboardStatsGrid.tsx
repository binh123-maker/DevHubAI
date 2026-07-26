import {
  FolderOpen,
  Folder,
  FileText,
  MessageSquare,
  MessageCircle,
  UploadCloud,
  CheckCircle2,
  Flame,
  Layers,
  HelpCircle,
  ArrowRight,
} from "lucide-react"
import { useNavigate, useLocation } from "react-router-dom"
import { useNavigation } from "@/contexts/NavigationContext"
import { handleTargetNavigation } from "@/utils/routeMapping"
import { Card, CardContent } from "@/components/ui/card"
import type { DashboardStatistics } from "@/api/dashboard.api"

interface DashboardStatsGridProps {
  statistics: DashboardStatistics
  onUploadClick?: () => void
}

export function DashboardStatsGrid({ statistics, onUploadClick }: DashboardStatsGridProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const { scrollToSection } = useNavigation()

  const handleCardClick = (targetKey: string) => {
    if (targetKey === "uploads" && onUploadClick) {
      onUploadClick()
      return
    }
    handleTargetNavigation(targetKey, navigate, location.pathname, scrollToSection)
  }

  const handleKeyDown = (e: React.KeyboardEvent, targetKey: string) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault()
      handleCardClick(targetKey)
    }
  }

  const statItems = [
    {
      key: "workspaces",
      title: "Workspaces",
      value: statistics.total_workspaces,
      description: "Không gian học tập",
      footer: "Đến Workspaces →",
      icon: FolderOpen,
      color: "text-blue-500",
      bgColor: "bg-blue-500/10",
      preview: `${statistics.total_workspaces} Workspace đang quản lý`,
    },
    {
      key: "workspaces",
      title: "Thư mục",
      value: statistics.total_folders,
      description: "Phân loại kiến thức",
      footer: "Quản lý thư mục →",
      icon: Folder,
      color: "text-amber-500",
      bgColor: "bg-amber-500/10",
      preview: `${statistics.total_folders} Thư mục tài nguyên`,
    },
    {
      key: "kanban",
      title: "Tài liệu",
      value: statistics.total_documents,
      description: "Tài nguyên đã lưu",
      footer: "Mở Kanban →",
      icon: FileText,
      color: "text-indigo-500",
      bgColor: "bg-indigo-500/10",
      preview: `Đã xử lý: ${statistics.documents_processed} / ${statistics.total_documents}`,
    },
    {
      key: "chats",
      title: "Cuộc trò chuyện",
      value: statistics.total_conversations,
      description: "Phiên chat AI",
      footer: "Xem lịch sử Chat →",
      icon: MessageSquare,
      color: "text-emerald-500",
      bgColor: "bg-emerald-500/10",
      preview: `${statistics.total_conversations} phiên thảo luận AI`,
    },
    {
      key: "chats",
      title: "Tin nhắn AI",
      value: statistics.total_messages,
      description: "Tương tác với AI",
      footer: "Xem tin nhắn →",
      icon: MessageCircle,
      color: "text-purple-500",
      bgColor: "bg-purple-500/10",
      preview: `Trung bình ~${Math.round(statistics.total_messages / (statistics.total_conversations || 1))} tin/chat`,
    },
    {
      key: "uploads",
      title: "Tài liệu tải lên",
      value: statistics.total_uploads,
      description: "Tổng file gốc",
      footer: "Tải lên ngay →",
      icon: UploadCloud,
      color: "text-cyan-500",
      bgColor: "bg-cyan-500/10",
      preview: "Bấm để tải thêm tệp tin PDF, DOCX, TXT",
    },
    {
      key: "kanban",
      title: "Đã xử lý RAG",
      value: statistics.documents_processed,
      description: "Sẵn sàng tra cứu RAG",
      footer: "Mở tài liệu RAG →",
      icon: CheckCircle2,
      color: "text-teal-500",
      bgColor: "bg-teal-500/10",
      preview: `${statistics.documents_processed} tài liệu đã lập chỉ mục vector`,
    },
    {
      key: "analytics",
      title: "Chuỗi học tập",
      value: `${statistics.learning_streak_days} ngày`,
      description: "Giữ vững phong độ",
      footer: "Xem Analytics →",
      icon: Flame,
      color: "text-orange-500",
      bgColor: "bg-orange-500/10",
      preview: statistics.learning_streak_days > 0 ? "Chuỗi học tập đang hoạt động!" : "Học tập ngay hôm nay!",
    },
  ]

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statItems.map((item) => {
          const Icon = item.icon
          return (
            <Card
              key={item.title + item.key}
              tabIndex={0}
              role="button"
              aria-label={`${item.title}: ${item.value}. Bấm để ${item.footer}`}
              onClick={() => handleCardClick(item.key)}
              onKeyDown={(e) => handleKeyDown(e, item.key)}
              className="group relative cursor-pointer overflow-hidden border border-border/50 bg-card/60 backdrop-blur-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-md hover:border-primary/40 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary active:scale-[0.98]"
            >
              <CardContent className="p-5 flex flex-col justify-between h-full space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{item.title}</p>
                    <h3 className="mt-1 text-2xl font-bold tracking-tight">{item.value}</h3>
                    <p className="mt-1 text-xs text-muted-foreground">{item.description}</p>
                  </div>
                  <div className={`flex h-11 w-11 items-center justify-center rounded-xl transition-transform group-hover:scale-110 ${item.bgColor} ${item.color}`}>
                    <Icon className="h-5 w-5" />
                  </div>
                </div>

                {/* Footer Link & Tooltip Preview */}
                <div className="flex items-center justify-between pt-2 border-t border-border/40 text-xs font-semibold text-primary">
                  <span className="truncate text-[11px] font-normal text-muted-foreground/80 group-hover:text-foreground transition-colors">
                    {item.preview}
                  </span>
                  <span className="flex items-center gap-1 shrink-0 group-hover:translate-x-0.5 transition-transform">
                    {item.footer}
                    <ArrowRight className="h-3 w-3" />
                  </span>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Extensible slots for future Flashcards & Quizzes */}
      <div className="grid gap-3 sm:grid-cols-2">
        <div className="flex items-center gap-3 rounded-lg border border-dashed border-border/60 bg-muted/20 px-4 py-3 text-xs text-muted-foreground">
          <Layers className="h-4 w-4 text-primary/60" />
          <span>Flashcards (Thẻ ghi nhớ) &mdash; <span className="font-medium text-foreground/80">Sắp ra mắt</span></span>
        </div>
        <div className="flex items-center gap-3 rounded-lg border border-dashed border-border/60 bg-muted/20 px-4 py-3 text-xs text-muted-foreground">
          <HelpCircle className="h-4 w-4 text-purple-500/60" />
          <span>Quizzes (Trắc nghiệm kiến thức) &mdash; <span className="font-medium text-foreground/80">Sắp ra mắt</span></span>
        </div>
      </div>
    </div>
  )
}
