import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  Calendar,
  FileText,
  FolderOpen,
  Mail,
  MessageSquare,
  Sparkles,
  Trash2,
  Activity,
  Layers,
  ArrowRight,
  ShieldCheck,
  Edit3,
  TrendingUp,
} from "lucide-react"
import { Link } from "react-router-dom"

import { profileApi } from "@/api/profile.api"
import { Button } from "@/components/ui/button"
import { ProfilePageSkeleton } from "@/components/ui/SkeletonLoaders"
import { EmptyState } from "@/components/ui/EmptyState"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface ProfilePageProps {
  embedded?: boolean
}

export default function ProfilePage({ embedded = false }: ProfilePageProps) {
  const queryClient = useQueryClient()

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [isDeleting, setIsDeleting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Edit Profile form states
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [editName, setEditName] = useState("")
  const [editGender, setEditGender] = useState("")
  const [editAvatarUrl, setEditAvatarUrl] = useState("")
  const [isSavingProfile, setIsSavingProfile] = useState(false)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // Fetch Dashboard Data
  const { data: dashboard, isLoading, error: fetchError } = useQuery({
    queryKey: ["dashboardData"],
    queryFn: async () => {
      const response = await profileApi.getDashboardData()
      return response.data
    },
  })

  // Delete All Chats Mutation
  const deleteChatsMutation = useMutation({
    mutationFn: () => profileApi.deleteAllChats(),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["dashboardData"] })
      void queryClient.invalidateQueries({ queryKey: ["chats"] })
      setDeleteDialogOpen(false)
      setError(null)
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail || "Không thể xóa các cuộc trò chuyện.")
    },
    onSettled: () => {
      setIsDeleting(false)
    },
  })

  // Update Profile Mutation
  const updateProfileMutation = useMutation({
    mutationFn: (payload: { full_name: string; gender: string; avatar_url: string }) =>
      profileApi.updateProfile(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["dashboardData"] })
      setSuccessMessage("Hồ sơ của bạn đã được cập nhật thành công!")
      setError(null)
      setTimeout(() => {
        setSuccessMessage(null)
        setEditDialogOpen(false)
      }, 1500)
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail || "Không thể cập nhật hồ sơ.")
    },
    onSettled: () => {
      setIsSavingProfile(false)
    },
  })

  async function handleDeleteChats() {
    setIsDeleting(true)
    await deleteChatsMutation.mutateAsync()
  }

  const openEditDialog = () => {
    if (!dashboard) return
    setEditName(dashboard.profile.full_name || "")
    setEditGender(dashboard.profile.gender || "prefer_not_to_say")
    setEditAvatarUrl(dashboard.profile.avatar_url || "")
    setSuccessMessage(null)
    setError(null)
    setEditDialogOpen(true)
  }

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editName.trim()) {
      setError("Họ và tên không được để trống")
      return
    }
    setIsSavingProfile(true)
    await updateProfileMutation.mutateAsync({
      full_name: editName,
      gender: editGender,
      avatar_url: editAvatarUrl,
    })
  }

  const formatJoinDate = (dateString?: string) => {
    if (!dateString) return "Tháng 7, 2026"
    const date = new Date(dateString)
    return date.toLocaleDateString("vi-VN", {
      year: "numeric",
      month: "long",
    })
  }

  const formatActivityTime = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
      day: "2-digit",
      month: "2-digit",
    })
  }

  if (isLoading) {
    return <ProfilePageSkeleton />
  }

  if (fetchError || !dashboard) {
    return (
      <EmptyState
        icon={Activity}
        title="Không thể tải thông tin bảng điều khiển"
        description="Đã có lỗi xảy ra khi kết nối máy chủ. Vui lòng thử lại."
        actionLabel="Tải lại dữ liệu"
        onAction={() => void queryClient.invalidateQueries({ queryKey: ["dashboardData"] })}
      />
    )
  }

  const { profile, statistics, activity_chart, recent_activity, favorite_workspace } = dashboard

  // Generate GitHub-style 28-day contribution heatmap cells
  const heatmapData = activity_chart.chats_per_day || []

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* 1. Header (If not embedded) */}
      {!embedded && (
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/40 pb-4">
          <div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight">Hồ sơ cá nhân & Workspace</h1>
            <p className="text-xs sm:text-sm text-muted-foreground">
              Tổng quan thông tin tài khoản và nhật ký hoạt động tri thức DevHub AI
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={openEditDialog} className="rounded-xl text-xs font-semibold gap-1.5 shrink-0">
            <Edit3 className="h-3.5 w-3.5 text-primary" /> Chỉnh sửa hồ sơ
          </Button>
        </div>
      )}

      {error && (
        <div className="p-3 bg-destructive/10 text-destructive rounded-xl text-xs font-semibold border border-destructive/20">
          {error}
        </div>
      )}

      {/* 2. Hero Card (Horizontal Seamless Glass Banner) */}
      <div className="relative overflow-hidden rounded-[24px] border border-border/60 bg-gradient-to-br from-card/90 via-card/60 to-primary/5 p-6 shadow-md backdrop-blur-md">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          {/* Avatar & User Info Horizontal Group */}
          <div className="flex items-center gap-5">
            <div className="relative shrink-0">
              <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-tr from-primary to-indigo-600 text-primary-foreground font-extrabold text-3xl shadow-lg ring-4 ring-background">
                {profile.full_name ? profile.full_name.charAt(0).toUpperCase() : profile.email.charAt(0).toUpperCase()}
              </div>
              <span className="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-emerald-500 ring-2 ring-background text-[10px] font-bold text-white" title="Hoạt động">
                ✓
              </span>
            </div>

            <div className="space-y-1.5 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <h2 className="text-xl sm:text-2xl font-extrabold tracking-tight text-foreground truncate">
                  {profile.full_name || "Binh"}
                </h2>
                <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-0.5 text-[11px] font-bold text-primary border border-primary/20 uppercase tracking-wider">
                  <ShieldCheck className="h-3 w-3" />
                  {profile.role || "User"}
                </span>
              </div>

              <div className="flex items-center gap-4 text-xs text-muted-foreground flex-wrap">
                <span className="flex items-center gap-1">
                  <Mail className="h-3.5 w-3.5 text-primary" />
                  {profile.email}
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5 text-primary" />
                  Joined {formatJoinDate(profile.created_at)}
                </span>
              </div>
            </div>
          </div>

          {/* Quick Metrics Badges Horizontal */}
          <div className="flex items-center gap-4 sm:gap-6 border-t md:border-t-0 md:border-l border-border/40 pt-4 md:pt-0 md:pl-6">
            <div className="text-center">
              <p className="text-2xl font-extrabold text-foreground">{statistics.total_workspaces || 0}</p>
              <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">Workspaces</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-extrabold text-foreground">{statistics.total_chats || 0}</p>
              <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">Chats</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-extrabold text-foreground">{statistics.total_documents || 0}</p>
              <p className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider">Files</p>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Main Grid: Activity Heatmap & Recent Timeline */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left 2 Cols: Activity Heatmap & Top Workspace */}
        <div className="lg:col-span-2 space-y-6">
          {/* GitHub Contribution Heatmap */}
          <div className="rounded-[20px] border border-border/50 bg-card/60 p-5 space-y-4 shadow-2xs backdrop-blur-md">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <h3 className="text-base font-bold flex items-center gap-2">
                  <TrendingUp className="h-4 w-4 text-primary" />
                  Activity Heatmap (Tần suất đóng góp RAG)
                </h3>
                <p className="text-xs text-muted-foreground">
                  Số cuộc trò chuyện và câu hỏi AI xử lý trong tuần vừa qua
                </p>
              </div>
              <span className="text-[11px] font-mono text-emerald-500 bg-emerald-500/10 px-2 py-0.5 rounded-full font-bold">
                Tháng này: {activity_chart.total_activity_this_month} chats
              </span>
            </div>

            {/* Heatmap Grid Cells */}
            <div className="p-3 bg-muted/20 rounded-xl border border-border/40">
              <div className="grid grid-cols-7 gap-2 sm:gap-3 text-center">
                {heatmapData.map((day, idx) => {
                  const count = day.count
                  const intensityClass =
                    count === 0
                      ? "bg-muted/60 text-muted-foreground"
                      : count === 1
                        ? "bg-primary/20 text-primary font-bold"
                        : count <= 3
                          ? "bg-primary/50 text-white font-bold"
                          : "bg-primary text-white font-extrabold shadow-sm"

                  return (
                    <div
                      key={idx}
                      className={`flex flex-col items-center justify-center p-2.5 rounded-xl transition-all duration-200 hover:-translate-y-0.5 group relative ${intensityClass}`}
                    >
                      <span className="text-[10px] font-mono opacity-80">{day.label}</span>
                      <span className="text-sm font-bold">{count}</span>

                      {/* Tooltip */}
                      <div className="absolute bottom-full mb-1.5 hidden group-hover:block bg-slate-900 text-slate-100 text-[10px] font-medium rounded-md px-2 py-1 shadow-xl z-20 whitespace-nowrap">
                        {day.date}: {count} cuộc hội thoại AI
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          {/* Top Active Workspace Card */}
          <div className="rounded-[20px] border border-border/50 bg-card/60 p-5 space-y-3 shadow-2xs backdrop-blur-md">
            <h3 className="text-sm font-bold text-muted-foreground flex items-center gap-2 uppercase tracking-wider">
              <Sparkles className="h-4 w-4 text-amber-500" />
              Workspace Hoạt động cao nhất
            </h3>

            {favorite_workspace ? (
              <div className="flex items-center justify-between p-4 rounded-xl border border-border/60 bg-card/80 hover:border-primary/40 transition-all">
                <div className="flex items-center gap-3">
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center text-white font-extrabold shadow-sm"
                    style={{ backgroundColor: favorite_workspace.color || "#3B82F6" }}
                  >
                    {favorite_workspace.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h4 className="font-bold text-sm text-foreground">{favorite_workspace.name}</h4>
                    <p className="text-xs text-muted-foreground">
                      {favorite_workspace.chat_count} cuộc trò chuyện đang hoạt động
                    </p>
                  </div>
                </div>

                <Button size="sm" variant="ghost" asChild className="text-xs font-bold text-primary gap-1">
                  <Link to={`/workspaces/${favorite_workspace.id}`}>
                    Mở <ArrowRight className="h-3.5 w-3.5" />
                  </Link>
                </Button>
              </div>
            ) : (
              <div className="text-center py-6 text-xs text-muted-foreground space-y-1">
                <Layers className="h-8 w-8 mx-auto text-muted-foreground/40 mb-1" />
                <p>Chưa có thông tin Workspace chính</p>
              </div>
            )}
          </div>
        </div>

        {/* Right 1 Col: Recent Activity Vertical Timeline */}
        <div className="rounded-[20px] border border-border/50 bg-card/60 p-5 space-y-4 shadow-2xs backdrop-blur-md">
          <div className="space-y-0.5">
            <h3 className="text-base font-bold text-foreground">Lịch sử Hoạt động (Timeline)</h3>
            <p className="text-xs text-muted-foreground">Nhật ký sự kiện tri thức gần nhất</p>
          </div>

          {recent_activity && recent_activity.length > 0 ? (
            <div className="space-y-4 relative before:absolute before:inset-y-1 before:left-3.5 before:w-0.5 before:bg-border/60">
              {recent_activity.map((item) => {
                const isChat = item.type === "chat_created"
                const isDoc = item.type === "document_uploaded"

                return (
                  <div key={item.id} className="flex items-start gap-3.5 relative group">
                    <div
                      className={`w-7 h-7 rounded-xl flex items-center justify-center shrink-0 z-10 ring-4 ring-background shadow-xs ${isChat
                          ? "bg-indigo-500/10 text-indigo-500"
                          : isDoc
                            ? "bg-emerald-500/10 text-emerald-500"
                            : "bg-amber-500/10 text-amber-500"
                        }`}
                    >
                      {isChat ? (
                        <MessageSquare className="h-3.5 w-3.5" />
                      ) : isDoc ? (
                        <FileText className="h-3.5 w-3.5" />
                      ) : (
                        <FolderOpen className="h-3.5 w-3.5" />
                      )}
                    </div>

                    <div className="flex-1 space-y-0.5 pt-0.5">
                      <p className="text-xs font-semibold text-foreground leading-snug">
                        {isChat
                          ? `Tạo hội thoại: ${item.title}`
                          : isDoc
                            ? `Tải tài liệu: ${item.title}`
                            : `Tạo Workspace: ${item.title}`}
                      </p>
                      <p className="text-[10px] text-muted-foreground font-mono">{formatActivityTime(item.created_at)}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <EmptyState
              icon={Activity}
              title="Chưa có nhật ký hoạt động"
              description="Các tương tác RAG và chat của bạn sẽ hiển thị tại đây."
            />
          )}

          {/* Quick Clear All Chats Action */}
          <div className="border-t border-border/40 pt-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setDeleteDialogOpen(true)}
              className="w-full rounded-xl text-xs text-destructive hover:text-destructive hover:bg-destructive/10 border-destructive/30"
            >
              <Trash2 className="h-3.5 w-3.5 mr-1.5" /> Xóa lịch sử trò chuyện
            </Button>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent className="rounded-2xl sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-destructive">
              <Trash2 className="h-5 w-5" />
              Xác nhận xóa toàn bộ cuộc trò chuyện?
            </DialogTitle>
            <DialogDescription className="text-xs">
              Hành động này sẽ xóa vĩnh viễn tất cả cuộc trò chuyện. Tài liệu và Workspace của bạn không bị ảnh hưởng.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2">
            <Button variant="outline" size="sm" onClick={() => setDeleteDialogOpen(false)} disabled={isDeleting} className="rounded-xl text-xs">
              Hủy
            </Button>
            <Button variant="destructive" size="sm" onClick={() => void handleDeleteChats()} disabled={isDeleting} className="rounded-xl text-xs font-bold">
              {isDeleting ? "Đang xóa..." : "Tiến hành xóa"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Profile Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="sm:max-w-[425px] rounded-2xl">
          <DialogHeader>
            <DialogTitle>Chỉnh sửa hồ sơ cá nhân</DialogTitle>
            <p className="text-xs text-muted-foreground">Cập nhật thông tin hiển thị của bạn tại DevHub AI.</p>
          </DialogHeader>

          {successMessage && (
            <div className="p-3 bg-emerald-500/10 text-emerald-500 rounded-xl text-xs font-semibold border border-emerald-500/20">
              {successMessage}
            </div>
          )}

          <form onSubmit={(e) => void handleSaveProfile(e)} className="space-y-4 py-2">
            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground">Địa chỉ Email</label>
              <input
                type="text"
                disabled
                value={profile.email}
                className="flex h-10 w-full rounded-xl border border-input bg-muted px-3 text-xs text-muted-foreground cursor-not-allowed"
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground">Họ và tên</label>
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                className="flex h-10 w-full rounded-xl border border-input bg-background px-3 text-xs focus:ring-2 focus:ring-primary/40"
                placeholder="Nhập họ tên"
                required
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-semibold text-muted-foreground">Giới tính</label>
              <select
                value={editGender}
                onChange={(e) => setEditGender(e.target.value)}
                className="flex h-10 w-full rounded-xl border border-input bg-background px-3 text-xs"
              >
                <option value="male">Nam</option>
                <option value="female">Nữ</option>
                <option value="other">Khác</option>
                <option value="prefer_not_to_say">Không tiết lộ</option>
              </select>
            </div>

            <DialogFooter className="pt-2 gap-2">
              <Button type="button" variant="outline" size="sm" onClick={() => setEditDialogOpen(false)} disabled={isSavingProfile} className="rounded-xl text-xs">
                Hủy
              </Button>
              <Button type="submit" size="sm" disabled={isSavingProfile} className="rounded-xl text-xs font-bold">
                {isSavingProfile ? "Đang lưu..." : "Lưu thay đổi"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
