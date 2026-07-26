import { FileText, MessageSquare, FolderOpen, ArrowRightLeft, Clock } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { RecentActivityItem } from "@/api/dashboard.api"

interface RecentActivityListProps {
  activities: RecentActivityItem[]
}

export function RecentActivityList({ activities }: RecentActivityListProps) {
  const getActivityIcon = (type: string) => {
    switch (type) {
      case "document_uploaded":
        return <FileText className="h-4 w-4 text-blue-500" />
      case "chat_created":
        return <MessageSquare className="h-4 w-4 text-emerald-500" />
      case "workspace_created":
        return <FolderOpen className="h-4 w-4 text-amber-500" />
      case "kanban_moved":
        return <ArrowRightLeft className="h-4 w-4 text-purple-500" />
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />
    }
  }

  const formatTimestamp = (dateStr: string) => {
    try {
      const date = new Date(dateStr)
      return date.toLocaleString("vi-VN", {
        hour: "2-digit",
        minute: "2-digit",
        day: "2-digit",
        month: "2-digit",
      })
    } catch {
      return dateStr
    }
  }

  return (
    <Card className="border border-border/50 bg-card/60 backdrop-blur-sm shadow-sm">
      <CardHeader className="pb-3">
        <CardTitle className="text-base font-semibold flex items-center gap-2">
          <Clock className="h-4 w-4 text-primary" />
          Hoạt động gần đây
        </CardTitle>
      </CardHeader>
      <CardContent>
        {activities.length === 0 ? (
          <p className="text-sm text-muted-foreground py-4 text-center">Chưa có hoạt động gần đây</p>
        ) : (
          <div className="relative border-l border-border/60 ml-3 space-y-4 py-1">
            {activities.map((item) => (
              <div key={item.id + item.created_at} className="relative pl-6 group">
                {/* Dot */}
                <div className="absolute -left-2.5 top-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-background border border-border shadow-xs group-hover:scale-110 transition-transform">
                  {getActivityIcon(item.type)}
                </div>
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">
                  <div>
                    <p className="text-sm font-medium leading-none text-foreground group-hover:text-primary transition-colors">
                      {item.title}
                    </p>
                    <p className="mt-1 text-xs text-muted-foreground">
                      {item.description}
                    </p>
                  </div>
                  <span className="text-xs text-muted-foreground/80 font-mono whitespace-nowrap">
                    {formatTimestamp(item.created_at)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
