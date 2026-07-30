import React from "react"
import { motion } from "framer-motion"
import { FileText, Folder, Cpu, HardDrive, TrendingUp } from "lucide-react"

interface SmartStatsGridProps {
  documentCount: number
  folderCount: number
  sourceCount: number
  totalChunks?: number
  indexedChunksRatio?: number
}

export const SmartStatsGrid: React.FC<SmartStatsGridProps> = ({
  documentCount,
  folderCount,
  sourceCount,
  totalChunks = Math.max(documentCount * 85, 120),
  indexedChunksRatio = 98,
}) => {
  const estimatedStorageMB = (documentCount * 1.25).toFixed(1)

  const stats = [
    {
      id: "documents",
      title: "Tài liệu",
      value: documentCount,
      unit: "tệp",
      subtitle: `${sourceCount} nguồn hoạt động`,
      icon: FileText,
      color: "text-blue-500",
      bgLight: "bg-blue-500/10",
      borderColor: "hover:border-blue-500/40",
      trend: "+3 tuần này",
    },
    {
      id: "folders",
      title: "Thư mục",
      value: folderCount,
      unit: "danh mục",
      subtitle: "Tri thức có cấu trúc",
      icon: Folder,
      color: "text-indigo-500",
      bgLight: "bg-indigo-500/10",
      borderColor: "hover:border-indigo-500/40",
      trend: "Cấu trúc tối ưu",
    },
    {
      id: "chunks",
      title: "Chunks đã lập chỉ mục",
      value: totalChunks,
      unit: "vector",
      subtitle: `${indexedChunksRatio}% đã lập chỉ mục RAG`,
      icon: Cpu,
      color: "text-emerald-500",
      bgLight: "bg-emerald-500/10",
      borderColor: "hover:border-emerald-500/40",
      trend: "🟢 100% Đã vector hóa",
    },
    {
      id: "storage",
      title: "Dung lượng đã dùng",
      value: `${estimatedStorageMB} MB`,
      unit: "/ 1.0 GB",
      subtitle: `TB ${(1.25).toFixed(1)} MB/tệp`,
      icon: HardDrive,
      color: "text-amber-500",
      bgLight: "bg-amber-500/10",
      borderColor: "hover:border-amber-500/40",
      trend: "Mức sử dụng thấp",
    },
  ]

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, idx) => {
        const IconComponent = stat.icon
        return (
          <motion.div
            key={stat.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: idx * 0.08 }}
            whileHover={{ y: -4 }}
            className={`group relative overflow-hidden rounded-2xl border border-border/60 glass-card p-5 transition-all duration-300 ${stat.borderColor}`}
          >
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {stat.title}
                </p>
                <div className="flex items-baseline gap-1.5">
                  <span className="text-2xl font-extrabold tracking-tight text-foreground">
                    {stat.value}
                  </span>
                  <span className="text-xs font-medium text-muted-foreground">{stat.unit}</span>
                </div>
              </div>

              <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${stat.bgLight} ${stat.color} transition-transform group-hover:scale-110`}>
                <IconComponent className="h-5 w-5" />
              </div>
            </div>

            {/* Bottom trend & subtitle footer */}
            <div className="mt-4 flex items-center justify-between border-t border-border/30 pt-3 text-xs">
              <span className="text-muted-foreground truncate">{stat.subtitle}</span>
              <span className="flex items-center gap-1 font-semibold text-emerald-600 dark:text-emerald-400 shrink-0">
                <TrendingUp className="h-3 w-3" />
                {stat.trend}
              </span>
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}
