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
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import type { DashboardStatistics } from "@/api/dashboard.api"

interface DashboardStatsGridProps {
  statistics: DashboardStatistics
}

export function DashboardStatsGrid({ statistics }: DashboardStatsGridProps) {
  const statItems = [
    {
      title: "Workspaces",
      value: statistics.total_workspaces,
      description: "Không gian học tập",
      icon: FolderOpen,
      color: "text-blue-500",
      bgColor: "bg-blue-500/10",
    },
    {
      title: "Thư mục",
      value: statistics.total_folders,
      description: "Phân loại kiến thức",
      icon: Folder,
      color: "text-amber-500",
      bgColor: "bg-amber-500/10",
    },
    {
      title: "Tài liệu",
      value: statistics.total_documents,
      description: "Tài nguyên đã lưu",
      icon: FileText,
      color: "text-indigo-500",
      bgColor: "bg-indigo-500/10",
    },
    {
      title: "Cuộc trò chuyện",
      value: statistics.total_conversations,
      description: "Phiên chat AI",
      icon: MessageSquare,
      color: "text-emerald-500",
      bgColor: "bg-emerald-500/10",
    },
    {
      title: "Tin nhắn AI",
      value: statistics.total_messages,
      description: "Tương tác với AI",
      icon: MessageCircle,
      color: "text-purple-500",
      bgColor: "bg-purple-500/10",
    },
    {
      title: "Tài liệu tải lên",
      value: statistics.total_uploads,
      description: "Tổng file gốc",
      icon: UploadCloud,
      color: "text-cyan-500",
      bgColor: "bg-cyan-500/10",
    },
    {
      title: "Đã xử lý",
      value: statistics.documents_processed,
      description: "Sẵn sàng tra cứu RAG",
      icon: CheckCircle2,
      color: "text-teal-500",
      bgColor: "bg-teal-500/10",
    },
    {
      title: "Chuỗi học tập",
      value: `${statistics.learning_streak_days} ngày`,
      description: "Giữ vững phong độ",
      icon: Flame,
      color: "text-orange-500",
      bgColor: "bg-orange-500/10",
    },
  ]

  return (
    <div className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statItems.map((item) => {
          const Icon = item.icon
          return (
            <Card key={item.title} className="relative overflow-hidden border border-border/50 bg-card/60 backdrop-blur-sm transition-all hover:shadow-md hover:border-primary/30">
              <CardContent className="p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">{item.title}</p>
                    <h3 className="mt-1 text-2xl font-bold tracking-tight">{item.value}</h3>
                    <p className="mt-1 text-xs text-muted-foreground">{item.description}</p>
                  </div>
                  <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${item.bgColor} ${item.color}`}>
                    <Icon className="h-5 w-5" />
                  </div>
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
