import React from "react"
import { Upload, Sparkles, FolderPlus, MessageSquare, Clock, Activity } from "lucide-react"

interface ActivityTimelineProps {
  workspaceId?: string
}

export const ActivityTimeline: React.FC<ActivityTimelineProps> = () => {
  const activities = [
    {
      id: "1",
      action: "Đã tải lên architecture_v2.pdf",
      user: "Senior Architect",
      time: "10 phút trước",
      icon: Upload,
      color: "text-blue-500",
      bgColor: "bg-blue-500/10",
    },
    {
      id: "2",
      action: "Đã vector hóa 142 chunks ngữ nghĩa cho RAG",
      user: "DevHub AI Engine",
      time: "12 phút trước",
      icon: Sparkles,
      color: "text-emerald-500",
      bgColor: "bg-emerald-500/10",
    },
    {
      id: "3",
      action: "Đã tạo thư mục API Specs",
      user: "Lead Developer",
      time: "2 giờ trước",
      icon: FolderPlus,
      color: "text-indigo-500",
      bgColor: "bg-indigo-500/10",
    },
    {
      id: "4",
      action: "Khởi tạo phiên AI Chat",
      user: "Lead Developer",
      time: "5 giờ trước",
      icon: MessageSquare,
      color: "text-purple-500",
      bgColor: "bg-purple-500/10",
    },
  ]

  return (
    <div className="space-y-4 rounded-3xl border border-border/60 glass-card p-6">
      <div className="flex items-center justify-between border-b border-border/40 pb-3">
        <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
          <Activity className="h-4 w-4 text-primary" />
          Nhật ký hoạt động gần đây
        </h3>
        <span className="text-xs text-muted-foreground">Trực tiếp</span>
      </div>

      <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-border/60">
        {activities.map((act) => {
          const IconComponent = act.icon
          return (
            <div key={act.id} className="relative flex items-start gap-4">
              <div className={`absolute -left-6 flex h-6 w-6 items-center justify-center rounded-full ${act.bgColor} ${act.color} ring-4 ring-background`}>
                <IconComponent className="h-3 w-3" />
              </div>

              <div className="flex-1 space-y-0.5">
                <p className="text-xs font-bold text-foreground">{act.action}</p>
                <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
                  <span>{act.user}</span>
                  <span>•</span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    {act.time}
                  </span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
