import { Flame, FolderOpen, TrendingUp, CalendarDays } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { LearningAnalytics as LearningAnalyticsType } from "@/api/dashboard.api"

interface LearningAnalyticsProps {
  analytics: LearningAnalyticsType
}

export function LearningAnalytics({ analytics }: LearningAnalyticsProps) {
  const { learning_streak_days, most_active_workspace, weekly_activity_count, monthly_activity_count } = analytics

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
      {/* Learning Streak */}
      <Card className="border border-border/50 bg-card/60 backdrop-blur-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-24 h-24 bg-gradient-to-br from-orange-500/10 to-transparent rounded-bl-full pointer-events-none" />
        <CardHeader className="pb-2">
          <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center justify-between">
            <span>Chuỗi học tập</span>
            <Flame className="h-4 w-4 text-orange-500 animate-pulse" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-extrabold text-orange-500 flex items-baseline gap-2">
            <span>{learning_streak_days}</span>
            <span className="text-sm font-semibold text-muted-foreground">ngày liên tiếp</span>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            {learning_streak_days > 0
              ? "Tuyệt vời! Hãy tiếp tục duy trì thói quen học tập."
              : "Bắt đầu chuỗi học tập bằng cách tạo chat hoặc tải tài liệu hôm nay."}
          </p>
        </CardContent>
      </Card>

      {/* Most Active Workspace */}
      <Card className="border border-border/50 bg-card/60 backdrop-blur-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center justify-between">
            <span>Workspace tích cực nhất</span>
            <FolderOpen className="h-4 w-4 text-blue-500" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          {most_active_workspace ? (
            <div>
              <div className="flex items-center gap-2">
                <div
                  className="h-3 w-3 rounded-full"
                  style={{ backgroundColor: most_active_workspace.color }}
                />
                <span className="text-base font-bold truncate">{most_active_workspace.name}</span>
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                <span className="font-semibold text-foreground">{most_active_workspace.activity_count}</span> tài liệu & hoạt động
              </p>
            </div>
          ) : (
            <p className="text-xs text-muted-foreground py-2">Chưa có dữ liệu workspace</p>
          )}
        </CardContent>
      </Card>

      {/* Weekly Activity */}
      <Card className="border border-border/50 bg-card/60 backdrop-blur-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center justify-between">
            <span>Hoạt động tuần này</span>
            <TrendingUp className="h-4 w-4 text-emerald-500" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-extrabold text-foreground">
            {weekly_activity_count}
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Tương tác & cập nhật trong 7 ngày qua
          </p>
        </CardContent>
      </Card>

      {/* Monthly Activity */}
      <Card className="border border-border/50 bg-card/60 backdrop-blur-sm">
        <CardHeader className="pb-2">
          <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center justify-between">
            <span>Hoạt động tháng này</span>
            <CalendarDays className="h-4 w-4 text-purple-500" />
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-extrabold text-foreground">
            {monthly_activity_count}
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Tổng đóng góp trong tháng hiện tại
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
