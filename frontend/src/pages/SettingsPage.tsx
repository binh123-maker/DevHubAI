import { useEffect, useState } from "react"
import { useSearchParams } from "react-router-dom"
import {
  User,
  Sliders,
  Shield,
  Bell,
  CreditCard,
  SunMoon,
  Lock,
  Link2,
  Trash2,
} from "lucide-react"

import ProfilePage from "./ProfilePage"
import { authApi, type GoogleOAuthStatusResponse } from "@/api/auth.api"
import { getApiErrorMessage } from "@/api/axios"
import { Button } from "@/components/ui/button"
import { useTheme } from "@/contexts/ThemeContext"

export default function SettingsPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const activeTab = searchParams.get("tab") || "profile"
  const { theme, setTheme } = useTheme()

  const [googleStatus, setGoogleStatus] = useState<GoogleOAuthStatusResponse | null>(null)
  const [unlinkError, setUnlinkError] = useState<string | null>(null)
  const [isUnlinking, setIsUnlinking] = useState(false)

  const tabs = [
    { id: "profile", label: "Hồ sơ cá nhân", icon: User },
    { id: "general", label: "Cấu hình chung", icon: Sliders },
    { id: "security", label: "Bảo mật tài khoản", icon: Shield },
    { id: "notifications", label: "Thông báo", icon: Bell },
    { id: "appearance", label: "Giao diện", icon: SunMoon },
    { id: "billing", label: "Gói cước & Billing", icon: CreditCard },
  ]

  useEffect(() => {
    if (activeTab === "security") {
      void fetchGoogleStatus()
    }
  }, [activeTab])

  async function fetchGoogleStatus() {
    try {
      const { data } = await authApi.getGoogleStatus()
      setGoogleStatus(data)
    } catch {
      // Ignore load failure if unauthenticated
    }
  }

  async function handleDisconnectGoogle() {
    setUnlinkError(null)
    setIsUnlinking(true)
    try {
      await authApi.disconnectGoogle()
      await fetchGoogleStatus()
    } catch (err) {
      setUnlinkError(getApiErrorMessage(err, "Không thể ngắt kết nối tài khoản Google."))
    } finally {
      setIsUnlinking(false)
    }
  }

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
                className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:bg-accent hover:text-foreground"
                }`}
              >
                <Icon className="h-4 w-4 shrink-0" />
                {t.label}
              </button>
            )
          })}
        </div>

        {/* Tab Content Panel */}
        <div className="flex-1 w-full bg-card/50 backdrop-blur-md rounded-2xl border border-border/60 p-4 sm:p-6">
          {activeTab === "profile" && <ProfilePage />}

          {activeTab === "general" && (
            <div className="space-y-6">
              <h2 className="text-lg font-bold">Cấu hình hệ thống</h2>
              <p className="text-xs text-muted-foreground">
                Các thiết lập liên quan đến ngôn ngữ hiển thị và ngôn ngữ mặc định của AI Model.
              </p>
            </div>
          )}

          {activeTab === "security" && (
            <div className="space-y-8">
              <div>
                <h2 className="text-lg font-bold">Bảo mật & Đổi mật khẩu</h2>
                <div className="space-y-4 max-w-md mt-4">
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

              {/* Google Authentication Card (ADR 8) */}
              <div className="pt-6 border-t border-border/60 space-y-4">
                <div>
                  <h2 className="text-lg font-bold flex items-center gap-2">
                    <Link2 className="h-5 w-5 text-primary" /> Google Authentication
                  </h2>
                  <p className="text-xs text-muted-foreground">
                    Quản lý liên kết tài khoản Google Identity với tài khoản DevHub AI của bạn.
                  </p>
                </div>

                {unlinkError && (
                  <p className="text-xs font-semibold text-destructive bg-destructive/10 p-3 rounded-xl">
                    {unlinkError}
                  </p>
                )}

                <div className="space-y-3">
                  {!googleStatus || !googleStatus.connected ? (
                    <div className="p-4 rounded-2xl border border-dashed border-border/80 flex items-center justify-between bg-card/40">
                      <div>
                        <p className="text-xs font-bold text-foreground">Chưa kết nối tài khoản Google</p>
                        <p className="text-[11px] text-muted-foreground">Liên kết Google để đăng nhập nhanh 1-click vào DevHub AI.</p>
                      </div>
                      <Button
                        size="sm"
                        onClick={async () => {
                          const redirectUri = `${window.location.origin}/auth/callback/google`
                          const { data } = await authApi.getGoogleOAuthUrl(redirectUri)
                          sessionStorage.setItem("oauth_state", data.state)
                          window.location.href = data.url
                        }}
                        className="rounded-xl text-xs font-bold gap-1.5"
                      >
                        Kết nối Google
                      </Button>
                    </div>
                  ) : (
                    <div className="p-4 rounded-2xl border border-border/60 bg-card space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {googleStatus.avatar_url ? (
                            <img
                              src={googleStatus.avatar_url}
                              alt="Google Avatar"
                              className="h-10 w-10 rounded-xl object-cover ring-2 ring-primary/20"
                            />
                          ) : (
                            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-primary/10 text-primary font-bold text-sm">
                              G
                            </div>
                          )}
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-bold text-foreground">
                                {googleStatus.display_name || "Google Account"}
                              </span>
                              <span className="text-[10px] font-bold bg-emerald-500/10 text-emerald-500 px-2 py-0.5 rounded-full">
                                Connected
                              </span>
                            </div>
                            <p className="text-xs text-muted-foreground">{googleStatus.email}</p>
                            {googleStatus.linked_at && (
                              <p className="text-[10px] text-muted-foreground/70 font-mono">
                                Liên kết: {new Date(googleStatus.linked_at).toLocaleDateString("vi-VN")}
                              </p>
                            )}
                          </div>
                        </div>

                        <Button
                          variant="outline"
                          size="sm"
                          disabled={isUnlinking || !googleStatus.can_disconnect}
                          onClick={handleDisconnectGoogle}
                          className="rounded-xl text-xs font-semibold text-destructive hover:bg-destructive/10 hover:text-destructive border-destructive/30 gap-1.5"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                          {isUnlinking ? "Đang hủy..." : "Ngắt kết nối"}
                        </Button>
                      </div>

                      {!googleStatus.can_disconnect && (
                        <div className="p-2.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-600 dark:text-amber-400 text-[11px] font-medium">
                          ⚠️ Bạn cần tạo mật khẩu trước khi ngắt kết nối tài khoản Google.
                        </div>
                      )}
                    </div>
                  )}
                </div>
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
              <h2 className="text-lg font-bold">Gói cước & Thanh toán</h2>
              <p className="text-xs text-muted-foreground">Gói hiện tại: DevHub Pro MVP Version.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
