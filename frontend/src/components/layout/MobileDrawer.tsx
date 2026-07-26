import { X, Home, FolderOpen, Kanban, BarChart3, Calendar, Clock, MessageSquare, User, Sparkles } from "lucide-react"

import { useLocation, useNavigate } from "react-router-dom"
import { useNavigation } from "@/contexts/NavigationContext"
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"

export function MobileDrawer() {
  const location = useLocation()
  const navigate = useNavigate()
  const { isMobileOpen, setIsMobileOpen, scrollToSection } = useNavigation()

  const handleNav = (path?: string, sectionId?: string) => {
    setIsMobileOpen(false)
    if (path && location.pathname !== path) {
      navigate(path)
      return
    }
    if (sectionId) {
      scrollToSection(sectionId)
    }
  }

  return (
    <Dialog open={isMobileOpen} onOpenChange={setIsMobileOpen}>
      <DialogContent className="p-0 max-w-xs h-full fixed left-0 top-0 translate-x-0 rounded-none border-r border-border/60 bg-card/95 backdrop-blur-md shadow-2xl flex flex-col">
        <div className="flex items-center justify-between p-4 border-b border-border/40">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground font-extrabold shadow-sm">
              D
            </div>
            <span className="text-lg font-extrabold text-primary">DevHub AI</span>
          </div>
          <Button variant="ghost" size="icon" onClick={() => setIsMobileOpen(false)} className="h-8 w-8">
            <X className="h-4 w-4" />
          </Button>
        </div>

        <nav className="p-4 space-y-4 flex-1 overflow-y-auto">
          <div className="space-y-1">
            <p className="px-2 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Trang chủ</p>
            <button
              onClick={() => handleNav("/workspaces", "overview")}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-foreground hover:bg-accent"
            >
              <Home className="h-4 w-4 text-primary" />
              Dashboard Overview
            </button>
          </div>

          <div className="space-y-1">
            <p className="px-2 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Quản lý tri thức</p>
            <button
              onClick={() => handleNav("/workspaces", "kanban")}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-foreground hover:bg-accent"
            >
              <Kanban className="h-4 w-4 text-blue-500" />
              Document Kanban
            </button>
            <button
              onClick={() => handleNav("/workspaces", "workspaces")}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-foreground hover:bg-accent"
            >
              <FolderOpen className="h-4 w-4 text-amber-500" />
              Workspaces
            </button>
          </div>

          <div className="space-y-1">
            <p className="px-2 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">Phân tích & Thống kê</p>
            <button
              onClick={() => handleNav("/workspaces", "statistics")}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-foreground hover:bg-accent"
            >
              <BarChart3 className="h-4 w-4 text-indigo-500" />
              Chỉ số Thống kê
            </button>
            <button
              onClick={() => handleNav("/workspaces", "analytics")}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-foreground hover:bg-accent"
            >
              <Sparkles className="h-4 w-4 text-purple-500" />
              Learning Analytics
            </button>
            <button
              onClick={() => handleNav("/workspaces", "heatmap")}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-foreground hover:bg-accent"
            >
              <Calendar className="h-4 w-4 text-emerald-500" />
              Biểu đồ Đóng góp
            </button>
            <button
              onClick={() => handleNav("/workspaces", "activity")}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-foreground hover:bg-accent"
            >
              <Clock className="h-4 w-4 text-slate-500" />
              Hoạt động gần đây
            </button>
          </div>

          <div className="space-y-1">
            <p className="px-2 text-[11px] font-bold uppercase tracking-wider text-muted-foreground">AI Trợ lý & Tài khoản</p>
            <button
              onClick={() => handleNav("/history")}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-foreground hover:bg-accent"
            >
              <MessageSquare className="h-4 w-4 text-cyan-500" />
              Chat History
            </button>
            <button
              onClick={() => handleNav("/profile")}
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-foreground hover:bg-accent"
            >
              <User className="h-4 w-4 text-rose-500" />
              Hồ sơ cá nhân
            </button>
          </div>
        </nav>
      </DialogContent>
    </Dialog>
  )
}
