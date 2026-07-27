import {
  FolderOpen,
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
      title: "Knowledge Base",
      value: statistics.total_workspaces,
      description: "Workspaces tri thức",
      footer: "Đến Workspaces →",
      icon: FolderOpen,
      color: "text-blue-500",
      bgColor: "bg-blue-500/10",
      preview: `${statistics.total_workspaces} Workspace đang quản lý`,
    },
    {
      key: "kanban",
      title: "Documents",
      value: statistics.total_documents,
      description: "Tổng tài liệu lưu trữ",
      footer: "Mở Kanban →",
      icon: FileText,
      color: "text-indigo-500",
      bgColor: "bg-indigo-500/10",
      preview: `Tài liệu gốc: ${statistics.total_documents}`,
    },
    {
      key: "kanban",
      title: "Total Chunks",
      value: statistics.total_chunks ?? 0,
      description: "Đoạn văn bản Vectorized",
      footer: "Xem Chunks →",
      icon: Layers,
      color: "text-purple-500",
      bgColor: "bg-purple-500/10",
      preview: `${statistics.total_chunks ?? 0} chunks đã sẵn sàng RAG`,
    },
    {
      key: "kanban",
      title: "Indexed Documents",
      value: statistics.indexed_documents ?? statistics.documents_processed,
      description: "Đã xử lý & Lập chỉ mục",
      footer: "Chi tiết RAG →",
      icon: CheckCircle2,
      color: "text-emerald-500",
      bgColor: "bg-emerald-500/10",
      preview: `Tỷ lệ: ${Math.round(((statistics.indexed_documents ?? statistics.documents_processed) / (statistics.total_documents || 1)) * 100)}% hoành thành`,
    },
    {
      key: "kanban",
      title: "Embedding Status",
      value: statistics.embedding_status ?? "Healthy",
      description: "Trạng thái nhúng Vector",
      footer: "Kiểm tra RAG →",
      icon: UploadCloud,
      color: statistics.failed_documents ? "text-amber-500" : "text-teal-500",
      bgColor: statistics.failed_documents ? "bg-amber-500/10" : "bg-teal-500/10",
      preview: statistics.failed_documents ? `${statistics.failed_documents} tài liệu lỗi` : "Tất cả Vector Pipeline hoàn hảo",
    },
    {
      key: "chats",
      title: "Search Health",
      value: statistics.search_health ?? "100% Operational",
      description: "Độ tin cậy Tra cứu",
      footer: "Mở Chat RAG →",
      icon: MessageSquare,
      color: "text-cyan-500",
      bgColor: "bg-cyan-500/10",
      preview: `Độ trễ trung bình: ${statistics.avg_retrieval_time_ms ?? 120}ms`,
    },
    {
      key: "analytics",
      title: "Learning Streak",
      value: `${statistics.learning_streak_days} ngày`,
      description: "Phong độ học tập",
      footer: "Xem Analytics →",
      icon: Flame,
      color: "text-orange-500",
      bgColor: "bg-orange-500/10",
      preview: statistics.learning_streak_days > 0 ? "Chuỗi học tập đang duy trì!" : "Bắt đầu học tập hôm nay",
    },
    {
      key: "chats",
      title: "Tương tác AI",
      value: statistics.total_messages,
      description: "Tin nhắn thảo luận",
      footer: "Xem lịch sử →",
      icon: MessageCircle,
      color: "text-rose-500",
      bgColor: "bg-rose-500/10",
      preview: `${statistics.total_conversations} phiên thảo luận AI`,
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
