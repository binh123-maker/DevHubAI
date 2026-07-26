import { useState } from "react"
import { Menu, Search, Bell, User, LogOut, Settings, Keyboard, HelpCircle, Info, CheckCheck, Trash2, Globe } from "lucide-react"
import { useNavigate, Link } from "react-router-dom"
import { useAuth } from "@/contexts/AuthContext"
import { useNavigation } from "@/contexts/NavigationContext"
import { useGlobalSearch } from "@/contexts/GlobalSearchContext"
import { Breadcrumb } from "./Breadcrumb"
import { ThemeToggle } from "./ThemeToggle"
import { KeyboardShortcutsModal } from "./KeyboardShortcutsModal"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface NotificationItem {
  id: string
  title: string
  time: string
  read: boolean
}

export function AppHeader() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const { setIsMobileOpen } = useNavigation()
  const { open: openSearch } = useGlobalSearch()
  const [shortcutsOpen, setShortcutsOpen] = useState(false)

  const [notifications, setNotifications] = useState<NotificationItem[]>([
    { id: "1", title: "Tài liệu 'DevHub Architecture' đã xử lý RAG thành công", time: "5 phút trước", read: false },
    { id: "2", title: "Bạn đã duy trì chuỗi học tập 3 ngày liên tiếp!", time: "1 giờ trước", read: false },
    { id: "3", title: "Workspace 'Computer Science' vừa được cập nhật", time: "Hôm qua", read: true },
  ])

  const unreadCount = notifications.filter((n) => !n.read).length

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })))
  }

  const clearAllNotifications = () => {
    setNotifications([])
  }

  const handleLogout = async () => {
    await logout()
    navigate("/login", { replace: true })
  }

  return (
    <>
      <header className="sticky top-0 z-40 flex h-14 items-center justify-between border-b border-border/40 bg-background/80 px-4 backdrop-blur-md shadow-xs">
        {/* Left: Mobile Drawer Trigger, Logo, & Breadcrumb */}
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsMobileOpen(true)}
            className="md:hidden h-8 w-8 text-muted-foreground"
            title="Mở menu"
          >
            <Menu className="h-5 w-5" />
          </Button>

          <div className="hidden sm:flex items-center gap-2 mr-2">
            <Breadcrumb />
          </div>
        </div>

        {/* Right: Global Search, Notifications, Theme Toggle, User Avatar Dropdown */}
        <div className="flex items-center gap-2">
          {/* Global Search Button */}
          <button
            onClick={openSearch}
            className="flex items-center gap-2 rounded-lg border border-border/60 bg-muted/30 px-3 py-1.5 text-xs text-muted-foreground hover:border-primary/40 hover:bg-accent hover:text-foreground transition-all"
          >
            <Search className="h-3.5 w-3.5" />
            <span className="hidden sm:inline font-medium">Tìm kiếm...</span>
            <kbd className="hidden sm:inline-flex items-center rounded border border-border/80 bg-muted px-1.5 text-[10px] font-mono text-muted-foreground">
              Ctrl K
            </kbd>
          </button>

          {/* Notifications Dropdown */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                size="icon"
                className="relative h-9 w-9 text-muted-foreground hover:text-foreground"
                title="Thông báo"
              >
                <Bell className="h-4 w-4" />
                {unreadCount > 0 && (
                  <span className="absolute top-2 right-2 flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-primary opacity-75" />
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-primary" />
                  </span>
                )}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-80 p-0 border border-border/60 bg-popover text-popover-foreground shadow-2xl rounded-2xl">
              <div className="flex items-center justify-between p-3 border-b border-border/40">
                <span className="text-xs font-bold flex items-center gap-1.5">
                  <Bell className="h-3.5 w-3.5 text-primary" />
                  Thông báo hệ thống ({unreadCount})
                </span>
                <div className="flex items-center gap-1">
                  {unreadCount > 0 && (
                    <button
                      onClick={markAllAsRead}
                      className="text-[11px] text-primary hover:underline flex items-center gap-1 font-semibold"
                    >
                      <CheckCheck className="h-3 w-3" />
                      Đọc tất cả
                    </button>
                  )}
                  {notifications.length > 0 && (
                    <button
                      onClick={clearAllNotifications}
                      className="text-[11px] text-muted-foreground hover:text-destructive flex items-center gap-1 ml-2"
                    >
                      <Trash2 className="h-3 w-3" />
                      Xóa
                    </button>
                  )}
                </div>
              </div>

              <div className="max-h-64 overflow-y-auto p-2 space-y-1 scrollbar-thin">
                {notifications.length === 0 ? (
                  <p className="p-4 text-center text-xs text-muted-foreground">Không có thông báo nào mới</p>
                ) : (
                  notifications.map((n) => (
                    <div
                      key={n.id}
                      className={`p-2.5 rounded-lg text-xs space-y-1 transition-colors ${
                        n.read ? "bg-card/40 opacity-70" : "bg-primary/5 font-medium border-l-2 border-primary"
                      }`}
                    >
                      <p className="text-foreground leading-snug">{n.title}</p>
                      <p className="text-[10px] text-muted-foreground font-mono">{n.time}</p>
                    </div>
                  ))
                )}
              </div>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* Theme Toggle */}
          <ThemeToggle />

          {/* User Avatar Dropdown Menu */}
          {user && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" className="h-9 w-9 rounded-full ring-2 ring-primary/20 hover:ring-primary/40">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-xs">
                    {user.full_name?.charAt(0) || user.email.charAt(0).toUpperCase()}
                  </div>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56 p-1 border border-border/60 bg-popover text-popover-foreground shadow-2xl rounded-2xl">
                <DropdownMenuLabel className="font-normal p-2">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-semibold leading-none">{user.full_name || "User"}</p>
                    <p className="text-xs leading-none text-muted-foreground">{user.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild className="cursor-pointer text-xs gap-2 py-2">
                  <Link to="/profile">
                    <User className="h-4 w-4 text-primary" />
                    <span>Hồ sơ cá nhân</span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild className="cursor-pointer text-xs gap-2 py-2">
                  <Link to="/profile">
                    <Settings className="h-4 w-4 text-muted-foreground" />
                    <span>Cài đặt hệ thống</span>
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => setShortcutsOpen(true)} className="cursor-pointer text-xs gap-2 py-2">
                  <Keyboard className="h-4 w-4 text-indigo-500" />
                  <span>Bảng Phím tắt (?)</span>
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer text-xs gap-2 py-2">
                  <Globe className="h-4 w-4 text-emerald-500" />
                  <span>Ngôn ngữ: Tiếng Việt</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="cursor-pointer text-xs gap-2 py-2 text-muted-foreground">
                  <HelpCircle className="h-4 w-4" />
                  <span>Trung tâm Trợ giúp</span>
                </DropdownMenuItem>
                <DropdownMenuItem className="cursor-pointer text-xs gap-2 py-2 text-muted-foreground">
                  <Info className="h-4 w-4" />
                  <span>Về DevHub AI (v1.0)</span>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-xs gap-2 py-2 text-destructive focus:bg-destructive/10">
                  <LogOut className="h-4 w-4" />
                  <span>Đăng xuất</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </header>

      {/* Keyboard Shortcuts Modal */}
      <KeyboardShortcutsModal open={shortcutsOpen} onOpenChange={setShortcutsOpen} />
    </>
  )
}
