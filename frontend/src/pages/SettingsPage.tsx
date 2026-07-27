import { useSearchParams } from "react-router-dom"
import {
  User,
  Sliders,
  Shield,
  Bell,
  CreditCard,
  SunMoon,
  Save,
  Lock,
} from "lucide-react"

import ProfilePage from "./ProfilePage"
import { Button } from "@/components/ui/button"
import { useTheme } from "@/contexts/ThemeContext"

export default function SettingsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const activeTab = searchParams.get("tab") || "profile"
  const { theme, setTheme } = useTheme()

  const tabs = [
    { id: "profile", label: "Hồ sơ cá nhân", icon: User },
    { id: "general", label: "Cấu hình chung", icon: Sliders },
    { id: "security", label: "Bảo mật tài khoản", icon: Shield },
    { id: "notifications", label: "Thông báo", icon: Bell },
    { id: "appearance", label: "Giao diện", icon: SunMoon },
    { id: "billing", label: "Gói cước & Billing", icon: CreditCard },
  ]

  const handleTabChange = (tabId: string) => {
    setSearchParams({ tab: tabId })
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto p-4 sm:p-6 animate-in fade-in duration-300">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">Cài đặt & Tài khoản</h1>
        <p className="text-xs sm:text-sm text-muted-foreground">
          Quản lý thông tin cá nhân, bảo mật, thông báo và tùy chỉnh trải nghiệm AI Workspace của bạn.
        </p>
      </div>

      {/* Tabs Layout */}
      <div className="flex flex-col md:flex-row gap-6 items-start">
        {/* Tab Navigation Sidebar */}
        <div className="w-full md:w-64 bg-card/50 backdrop-blur-md rounded-2xl border border-border/60 p-2 space-y-1 shrink-0">
          {tabs.map((t) => {
            const Icon = t.icon
            const isActive = activeTab === t.id
            return (
              <button
                key={t.id}
                onClick={() => handleTabChange(t.id)}
                className={`flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-xs sm:text-sm font-medium transition-all ${
                  isActive
                    ? "bg-primary text-primary-foreground font-bold shadow-xs"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{t.label}</span>
              </button>
            )
          })}
        </div>

        {/* Tab Content Area */}
        <div className="flex-1 w-full bg-card/30 rounded-2xl border border-border/40 p-4 sm:p-6 min-h-[500px]">
          {activeTab === "profile" && <ProfilePage embedded />}

          {activeTab === "general" && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold">Cấu hình chung hệ thống</h2>
              <div className="space-y-4 max-w-xl">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold">Ngôn ngữ giao diện</label>
                  <select className="flex h-10 w-full rounded-xl border border-input bg-background px-3 text-xs">
                    <option value="vi">Tiếng Việt (Mặc định)</option>
                    <option value="en">English (US)</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-semibold">Mô hình AI mặc định</label>
                  <select className="flex h-10 w-full rounded-xl border border-input bg-background px-3 text-xs">
                    <option value="gemini-1.5-pro">Gemini 1.5 Pro (RAG Nâng cao)</option>
                    <option value="gemini-1.5-flash">Gemini 1.5 Flash (Tốc độ cao)</option>
                  </select>
                </div>

                <Button className="rounded-xl text-xs font-bold gap-2">
                  <Save className="h-3.5 w-3.5" /> Lưu cài đặt chung
                </Button>
              </div>
            </div>
          )}

          {activeTab === "security" && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold">Bảo mật tài khoản</h2>
              <div className="space-y-4 max-w-md">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold">Mật khẩu hiện tại</label>
                  <input type="password" className="flex h-10 w-full rounded-xl border border-input bg-background px-3 text-xs" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold">Mật khẩu mới</label>
                  <input type="password" className="flex h-10 w-full rounded-xl border border-input bg-background px-3 text-xs" />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold">Xác nhận mật khẩu mới</label>
                  <input type="password" className="flex h-10 w-full rounded-xl border border-input bg-background px-3 text-xs" />
                </div>
                <Button className="rounded-xl text-xs font-bold gap-2">
                  <Lock className="h-3.5 w-3.5" /> Đổi mật khẩu
                </Button>
              </div>
            </div>
          )}

          {activeTab === "notifications" && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold">Cài đặt Thông báo</h2>
              <div className="space-y-3">
                <label className="flex items-center gap-3 p-3 rounded-xl border border-border/60 bg-card cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded text-primary" />
                  <div>
                    <p className="text-xs font-bold">Thông báo xử lý tài liệu RAG</p>
                    <p className="text-[11px] text-muted-foreground">Nhận thông báo khi tài liệu RAG vectorization hoàn tất.</p>
                  </div>
                </label>
                <label className="flex items-center gap-3 p-3 rounded-xl border border-border/60 bg-card cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded text-primary" />
                  <div>
                    <p className="text-xs font-bold">Báo cáo chuỗi học tập hàng tuần</p>
                    <p className="text-[11px] text-muted-foreground">Nhận tổng kết hoạt động và gợi ý bài kiểm tra.</p>
                  </div>
                </label>
              </div>
            </div>
          )}

          {activeTab === "appearance" && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold">Chế độ hiển thị Giao diện</h2>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 max-w-lg">
                <button
                  onClick={() => setTheme("light")}
                  className={`p-4 rounded-2xl border text-center space-y-2 transition-all ${
                    theme === "light" ? "border-primary bg-primary/10 ring-2 ring-primary/30" : "border-border/60 bg-card"
                  }`}
                >
                  <div className="h-10 w-10 mx-auto rounded-xl bg-amber-500/20 text-amber-500 flex items-center justify-center font-bold">
                    ☀️
                  </div>
                  <p className="text-xs font-bold">Sáng (Light)</p>
                </button>

                <button
                  onClick={() => setTheme("dark")}
                  className={`p-4 rounded-2xl border text-center space-y-2 transition-all ${
                    theme === "dark" ? "border-primary bg-primary/10 ring-2 ring-primary/30" : "border-border/60 bg-card"
                  }`}
                >
                  <div className="h-10 w-10 mx-auto rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center font-bold">
                    🌙
                  </div>
                  <p className="text-xs font-bold">Tối (Dark)</p>
                </button>
              </div>
            </div>
          )}

          {activeTab === "billing" && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold">Gói cước & Hạn mức (Billing)</h2>
              <div className="p-4 rounded-2xl border border-primary/40 bg-primary/5 space-y-3 max-w-lg">
                <div className="flex justify-between items-center">
                  <span className="text-xs font-bold text-primary uppercase">DevHub AI Pro Plan</span>
                  <span className="text-[10px] font-bold bg-emerald-500/20 text-emerald-500 px-2 py-0.5 rounded-full">
                    Đang hoạt động
                  </span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Bạn có quyền truy cập không giới hạn Workspace RAG, Gemini 1.5 Pro, và trích xuất tài liệu nâng cao.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
