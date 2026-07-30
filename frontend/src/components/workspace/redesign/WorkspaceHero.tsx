import React from "react"
import { format } from "date-fns"
import { motion } from "framer-motion"
import { 
  Sparkles, 
  Upload, 
  MessageSquare, 
  FolderPlus, 
  BarChart3, 
  MoreVertical, 
  Pencil, 
  Trash2, 
  Calendar, 
  Clock, 
  CheckCircle2, 
  Layers 
} from "lucide-react"
import { type Workspace } from "@/api/workspace.api"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface WorkspaceHeroProps {
  workspace: Workspace
  onUploadClick: () => void
  onCreateFolderClick: () => void
  onStartChatClick: () => void
  onToggleDrawer: () => void
  onEditClick: () => void
  onDeleteClick: () => void
  aiReadinessScore?: number
}

export const WorkspaceHero: React.FC<WorkspaceHeroProps> = ({
  workspace,
  onUploadClick,
  onCreateFolderClick,
  onStartChatClick,
  onToggleDrawer,
  onEditClick,
  onDeleteClick,
  aiReadinessScore = 96,
}) => {
  const formattedCreated = format(new Date(workspace.created_at), "dd MMM yyyy")
  const formattedUpdated = format(new Date(workspace.updated_at), "dd MMM yyyy")

  // Calculate SVG Circle values for AI Readiness Ring
  const radius = 28
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (aiReadinessScore / 100) * circumference

  return (
    <div className="relative overflow-hidden rounded-3xl border border-border/60 glass-card bg-hero-gradient p-6 md:p-8 shadow-xl">
      {/* Ambient background glow orb */}
      <div 
        className="absolute -right-16 -top-16 h-64 w-64 rounded-full opacity-20 blur-3xl pointer-events-none"
        style={{ backgroundColor: workspace.color || "#3B82F6" }}
      />

      <div className="relative z-10 flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
        {/* Left identity section */}
        <div className="space-y-4 max-w-3xl">
          <div className="flex flex-wrap items-center gap-3">
            {/* Color Accent Badge & Icon */}
            <div 
              className="flex h-12 w-12 items-center justify-center rounded-2xl text-2xl shadow-lg border border-white/20"
              style={{ backgroundColor: workspace.color || "#3B82F6", color: "#FFFFFF" }}
            >
              {workspace.icon || "🤖"}
            </div>

            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-foreground">
                  {workspace.name}
                </h1>
                <Badge variant="outline" className="gap-1.5 border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-medium px-2.5 py-0.5 rounded-full text-xs">
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  AI Sẵn sàng
                </Badge>
              </div>

              {/* Meta details */}
              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-1 text-xs text-muted-foreground">
                <span className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5" />
                  Tạo ngày {formattedCreated}
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-3.5 w-3.5" />
                  Cập nhật {formattedUpdated}
                </span>
                <span className="flex items-center gap-1 font-medium text-foreground">
                  <Layers className="h-3.5 w-3.5 text-primary" />
                  {workspace.document_count} Tài liệu • {workspace.folder_count} Thư mục
                </span>
              </div>
            </div>
          </div>

          <p className="text-sm leading-relaxed text-muted-foreground line-clamp-2 md:line-clamp-none">
            {workspace.description || "Chưa có mô tả cho Workspace. Thêm tài liệu và ghi chú để cung cấp tri thức cho AI RAG."}
          </p>
        </div>

        {/* Right Section: AI Score Ring & Action Button Bar */}
        <div className="flex flex-wrap items-center gap-4 lg:justify-end border-t border-border/40 pt-4 lg:border-t-0 lg:pt-0">
          {/* AI Knowledge Score Ring */}
          <div className="flex items-center gap-3 bg-background/50 backdrop-blur-md px-4 py-2.5 rounded-2xl border border-border/50 shadow-sm">
            <div className="relative flex items-center justify-center">
              <svg className="h-16 w-16 -rotate-90 transform">
                <circle
                  cx="32"
                  cy="32"
                  r={radius}
                  stroke="currentColor"
                  strokeWidth="5"
                  className="text-muted/40"
                  fill="transparent"
                />
                <motion.circle
                  cx="32"
                  cy="32"
                  r={radius}
                  stroke={workspace.color || "#3B82F6"}
                  strokeWidth="5"
                  strokeDasharray={circumference}
                  initial={{ strokeDashoffset: circumference }}
                  animate={{ strokeDashoffset }}
                  transition={{ duration: 1.2, ease: "easeOut" }}
                  strokeLinecap="round"
                  fill="transparent"
                />
              </svg>
              <span className="absolute text-xs font-bold text-foreground">
                {aiReadinessScore}%
              </span>
            </div>
            <div className="flex flex-col">
              <span className="text-xs font-semibold text-foreground flex items-center gap-1">
                <Sparkles className="h-3.5 w-3.5 text-amber-500 animate-pulse" />
                Sức khỏe tri thức
              </span>
              <span className="text-[11px] text-muted-foreground">Chỉ mục RAG đang hoạt động</span>
            </div>
          </div>

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center gap-2">
            <Button 
              onClick={onUploadClick} 
              className="gap-2 rounded-xl bg-primary shadow-md hover:shadow-lg transition-all hover:scale-[1.02]"
            >
              <Upload className="h-4 w-4" />
              Tải lên
            </Button>

            <Button 
              variant="outline" 
              onClick={onStartChatClick} 
              className="gap-2 rounded-xl border-border/80 hover:border-primary/50 hover:bg-primary/5 transition-all"
            >
              <MessageSquare className="h-4 w-4 text-primary" />
              AI Chat
            </Button>

            <Button 
              variant="ghost" 
              size="icon" 
              onClick={onToggleDrawer}
              title="Bảng chỉ số tri thức"
              className="rounded-xl hover:bg-muted/80"
            >
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="rounded-xl hover:bg-muted/80">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-48 rounded-xl p-1.5">
                <DropdownMenuItem onClick={onCreateFolderClick} className="gap-2 rounded-lg cursor-pointer">
                  <FolderPlus className="h-4 w-4 text-blue-500" />
                  Tạo thư mục mới
                </DropdownMenuItem>
                <DropdownMenuItem onClick={onEditClick} className="gap-2 rounded-lg cursor-pointer">
                  <Pencil className="h-4 w-4 text-slate-500" />
                  Chỉnh sửa Workspace
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={onDeleteClick} className="gap-2 rounded-lg text-destructive cursor-pointer">
                  <Trash2 className="h-4 w-4" />
                  Xóa Workspace
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </div>
    </div>
  )
}
