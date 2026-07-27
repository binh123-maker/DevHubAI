import { useLocation, useNavigate } from "react-router-dom"
import {
  Home,
  FolderOpen,
  Kanban,
  BarChart3,
  Calendar,
  Clock,
  MessageSquare,
  User,
  PanelLeftClose,
  PanelLeftOpen,
  Sparkles,
  Layers,
  HelpCircle,
  Zap,
} from "lucide-react"

import { useNavigation } from "@/contexts/NavigationContext"
import { useAuth } from "@/contexts/AuthContext"
import { SidebarGroup } from "./SidebarGroup"
import { SidebarItem } from "./SidebarItem"
import { Button } from "@/components/ui/button"

export function Sidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const { user } = useAuth()
  const { isCollapsed, toggleCollapse, activeSectionId, scrollToSection } = useNavigation()

  const isDashboardPage = location.pathname === "/workspaces" || location.pathname === "/"

  const handleNavClick = (sectionId?: string, path: string = "/workspaces") => {
    if (location.pathname !== path) {
      navigate(path)
      if (sectionId) {
        setTimeout(() => scrollToSection(sectionId), 150)
      }
      return
    }
    if (sectionId) {
      scrollToSection(sectionId)
    }
  }

  return (
    <aside
      className={`sticky top-0 h-screen shrink-0 border-r border-border/40 bg-card/60 backdrop-blur-xl transition-all duration-300 z-30 flex flex-col justify-between ${
        isCollapsed ? "w-16 p-2" : "w-64 p-3 sm:p-4"
      }`}
    >
      {/* 1. Fixed Top Header & Logo */}
      <div className="flex items-center justify-between px-2 py-1 pb-3 shrink-0 border-b border-border/40 mb-3">
        {!isCollapsed && (
          <div className="flex items-center gap-2.5">
            <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-tr from-primary to-indigo-600 text-primary-foreground font-extrabold shadow-sm">
              D
            </div>
            <span className="text-base font-extrabold tracking-tight text-foreground">DevHub AI</span>
          </div>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleCollapse}
          className="h-8 w-8 rounded-xl text-muted-foreground hover:text-foreground hidden md:flex"
          title={isCollapsed ? "Mở rộng sidebar" : "Thu gọn sidebar"}
        >
          {isCollapsed ? <PanelLeftOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
        </Button>
      </div>

      {/* 2. Scrollable Navigation List */}
      <div className="space-y-4 flex-1 overflow-y-auto scrollbar-hover pr-1 contain-layout-paint">
        <nav className="space-y-1.5">
          {/* Group 1: Overview & Quick Actions */}
          <SidebarGroup title="Tổng quan" isCollapsed={isCollapsed} collapsible={false}>
            <SidebarItem
              icon={Home}
              label="Dashboard Overview"
              to="/workspaces"
              isActive={isDashboardPage && activeSectionId === "overview"}
              isCollapsed={isCollapsed}
              onClick={() => handleNavClick("overview", "/workspaces")}
            />
            <SidebarItem
              icon={Zap}
              label="Thao tác nhanh"
              isActive={isDashboardPage && activeSectionId === "quick-actions"}
              isCollapsed={isCollapsed}
              onClick={() => handleNavClick("quick-actions", "/workspaces")}
            />
          </SidebarGroup>

          {/* Group 2: Knowledge Management */}
          <SidebarGroup title="Quản lý tri thức" isCollapsed={isCollapsed}>
            <SidebarItem
              icon={FolderOpen}
              label="Workspaces"
              isActive={isDashboardPage && activeSectionId === "workspaces"}
              isCollapsed={isCollapsed}
              onClick={() => handleNavClick("workspaces", "/workspaces")}
            />
            <SidebarItem
              icon={Kanban}
              label="Document Kanban"
              isActive={isDashboardPage && activeSectionId === "kanban"}
              isCollapsed={isCollapsed}
              onClick={() => handleNavClick("kanban", "/workspaces")}
            />
          </SidebarGroup>

          {/* Group 3: Analytics & Activity */}
          <SidebarGroup title="Phân tích & Thống kê" isCollapsed={isCollapsed}>
            <SidebarItem
              icon={BarChart3}
              label="Chỉ số Tri thức KPI"
              isActive={isDashboardPage && activeSectionId === "statistics"}
              isCollapsed={isCollapsed}
              onClick={() => handleNavClick("statistics", "/workspaces")}
            />
            <SidebarItem
              icon={Sparkles}
              label="Learning Analytics"
              isActive={isDashboardPage && activeSectionId === "analytics"}
              isCollapsed={isCollapsed}
              onClick={() => handleNavClick("analytics", "/workspaces")}
            />
            <SidebarItem
              icon={Calendar}
              label="Biểu đồ Đóng góp"
              isActive={isDashboardPage && activeSectionId === "heatmap"}
              isCollapsed={isCollapsed}
              onClick={() => handleNavClick("heatmap", "/workspaces")}
            />
            <SidebarItem
              icon={Clock}
              label="Hoạt động gần đây"
              isActive={isDashboardPage && activeSectionId === "activity"}
              isCollapsed={isCollapsed}
              onClick={() => handleNavClick("activity", "/workspaces")}
            />
          </SidebarGroup>

          {/* Group 4: AI Assistant */}
          <SidebarGroup title="AI Trợ lý" isCollapsed={isCollapsed}>
            <SidebarItem
              icon={MessageSquare}
              label="Chat History"
              to="/history"
              isActive={location.pathname.startsWith("/history")}
              isCollapsed={isCollapsed}
            />
          </SidebarGroup>

          {/* Group 5: Account & Settings */}
          <SidebarGroup title="Tài khoản & Cài đặt" isCollapsed={isCollapsed}>
            <SidebarItem
              icon={User}
              label="Account & Settings"
              to="/settings"
              isActive={location.pathname === "/settings" || location.pathname === "/profile"}
              isCollapsed={isCollapsed}
            />
          </SidebarGroup>

          {/* Group 6: Extensible Learning Tools */}
          <SidebarGroup title="Công cụ học tập (Soon)" isCollapsed={isCollapsed}>
            <SidebarItem
              icon={Layers}
              label="Flashcards"
              isCollapsed={isCollapsed}
              isDisabled
              badge="Soon"
            />
            <SidebarItem
              icon={HelpCircle}
              label="Quizzes"
              isCollapsed={isCollapsed}
              isDisabled
              badge="Soon"
            />
          </SidebarGroup>
        </nav>
      </div>

      {/* User Quick Info at bottom */}
      {!isCollapsed && user && (
        <div className="border-t border-border/40 pt-3 mt-2 px-1">
          <div className="flex items-center gap-2.5 p-1.5 rounded-xl hover:bg-accent/40 transition-colors">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-primary/20 text-primary font-bold text-xs">
              {user.full_name?.charAt(0) || user.email.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="text-xs font-bold truncate">{user.full_name || "User"}</p>
              <p className="text-[10px] text-muted-foreground truncate">{user.email}</p>
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}
