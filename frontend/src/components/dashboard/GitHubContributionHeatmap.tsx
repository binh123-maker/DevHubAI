import { useState } from "react"

import { Calendar, Info } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import type { HeatmapDay } from "@/api/dashboard.api"

interface GitHubContributionHeatmapProps {
  data: HeatmapDay[]
  days?: number
}

type RangeOption = 30 | 90 | 180 | 365

export function GitHubContributionHeatmap({ data, days: initialDays = 90 }: GitHubContributionHeatmapProps) {
  const [hoveredDay, setHoveredDay] = useState<HeatmapDay | null>(null)

  const [selectedRange, setSelectedRange] = useState<RangeOption>(() => {
    const saved = localStorage.getItem("devhub-heatmap-range")
    if (saved) {
      const parsed = parseInt(saved, 10)
      if (parsed === 30 || parsed === 90 || parsed === 180 || parsed === 365) {
        return parsed as RangeOption
      }
    }
    return (initialDays as RangeOption) || 90
  })

  const handleRangeChange = (range: RangeOption) => {
    setSelectedRange(range)
    localStorage.setItem("devhub-heatmap-range", range.toString())
  }

  const activeData = data.slice(-selectedRange)
  const totalActivity = activeData.reduce((acc, curr) => acc + curr.count, 0)

  // Helper for color intensity class
  const getIntensityClass = (count: number) => {
    if (count === 0) return "bg-muted/40 dark:bg-muted/20 border-border/30"
    if (count <= 2) return "bg-emerald-200 dark:bg-emerald-950/70 border-emerald-400/40 text-emerald-950 dark:text-emerald-100"
    if (count <= 5) return "bg-emerald-400 dark:bg-emerald-700 border-emerald-500/50 text-white"
    if (count <= 9) return "bg-emerald-500 dark:bg-emerald-600 border-emerald-600/50 text-white font-semibold"
    return "bg-emerald-600 dark:bg-emerald-500 border-emerald-700/60 text-white font-bold ring-2 ring-emerald-500/30"
  }

  const formatDate = (dateStr: string) => {
    try {
      const d = new Date(dateStr)
      return d.toLocaleDateString("vi-VN", {
        weekday: "short",
        year: "numeric",
        month: "short",
        day: "numeric",
      })
    } catch {
      return dateStr
    }
  }

  // Group into weeks
  const weeks: HeatmapDay[][] = []
  let currentWeek: HeatmapDay[] = []

  activeData.forEach((day, index) => {
    currentWeek.push(day)
    if (currentWeek.length === 7 || index === activeData.length - 1) {
      weeks.push(currentWeek)
      currentWeek = []
    }
  })

  return (
    <Card className="border border-border/50 bg-card/60 backdrop-blur-sm shadow-sm">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-3 gap-3">
        <div className="space-y-1">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Calendar className="h-4 w-4 text-emerald-500" />
            Biểu đồ đóng góp ({selectedRange} Ngày qua)
          </CardTitle>
          <p className="text-xs text-muted-foreground">
            Tổng cộng <span className="font-semibold text-foreground">{totalActivity} hoạt động</span> trong {activeData.length} ngày
          </p>
        </div>

        {/* Range Switcher Buttons */}
        <div className="flex items-center gap-1 bg-muted p-1 rounded-lg text-xs">
          {([30, 90, 180, 365] as RangeOption[]).map((r) => (
            <button
              key={r}
              onClick={() => handleRangeChange(r)}
              className={`px-2 py-1 font-medium rounded-md transition-all ${
                selectedRange === r
                  ? "bg-background text-foreground shadow-xs font-bold"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {r}D
            </button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="pt-2">
        <div className="overflow-x-auto pb-2 scrollbar-thin">
          <div className="inline-flex gap-1.5 min-w-full justify-start md:justify-center p-1">
            {weeks.map((week, weekIdx) => (
              <div key={weekIdx} className="flex flex-col gap-1.5">
                {week.map((day) => (
                  <div
                    key={day.date}
                    onMouseEnter={() => setHoveredDay(day)}
                    onMouseLeave={() => setHoveredDay(null)}
                    className={`h-3.5 w-3.5 sm:h-4 sm:w-4 rounded-sm border transition-all duration-150 hover:scale-125 hover:z-10 cursor-pointer ${getIntensityClass(
                      day.count
                    )}`}
                  />
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Interactive Tooltip bar */}
        <div className="mt-3 flex items-center justify-between border-t border-border/40 pt-2 text-xs text-muted-foreground">
          {hoveredDay ? (
            <div className="flex items-center gap-2 font-medium text-foreground">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>{formatDate(hoveredDay.date)}</span>
              <span className="rounded bg-emerald-500/10 px-1.5 py-0.5 text-emerald-600 dark:text-emerald-400 font-semibold">
                {hoveredDay.count} hoạt động
              </span>
            </div>
          ) : (
            <div className="flex items-center gap-1 text-muted-foreground/80">
              <Info className="h-3.5 w-3.5 text-muted-foreground" />
              <span>Di chuột vào từng ô vuông để xem chi tiết đóng góp</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
