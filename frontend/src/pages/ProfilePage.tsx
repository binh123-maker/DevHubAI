import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import {
  Calendar,
  FileText,
  FolderOpen,
  Mail,
  MessageSquare,
  Sparkles,
  Trash2,
  User,
  Activity,
  Layers,
  ArrowRight,
} from "lucide-react"
import React, { useState } from "react"
import { Link, useNavigate } from "react-router-dom"

import { useAuth } from "@/contexts/AuthContext"
import { profileApi } from "@/api/profile.api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

export default function ProfilePage() {
  const { logout } = useAuth()
  const navigate = useNavigate()
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
    }
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
    }
  })

  async function handleLogout() {
    await logout()
    navigate("/login", { replace: true })
  }

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
    if (!dateString) return "Không rõ"
    const date = new Date(dateString)
    return date.toLocaleDateString("vi-VN", {
      year: "numeric",
      month: "long",
      day: "numeric",
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
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-10 w-48 bg-muted rounded" />
        <div className="grid gap-6 md:grid-cols-3">
          <div className="h-64 bg-muted rounded md:col-span-1" />
          <div className="space-y-6 md:col-span-2">
            <div className="grid gap-4 grid-cols-2 md:grid-cols-4">
              <div className="h-28 bg-muted rounded" />
              <div className="h-28 bg-muted rounded" />
              <div className="h-28 bg-muted rounded" />
              <div className="h-28 bg-muted rounded" />
            </div>
            <div className="h-64 bg-muted rounded" />
          </div>
        </div>
      </div>
    )
  }

  if (fetchError || !dashboard) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-center space-y-4">
        <div className="p-3 bg-destructive/10 text-destructive rounded-full">
          <Activity className="h-8 w-8" />
        </div>
        <h2 className="text-xl font-bold">Không thể tải thông tin bảng điều khiển</h2>
        <p className="text-muted-foreground max-w-md">
          Đã có lỗi xảy ra khi kết nối tới máy chủ. Vui lòng tải lại trang hoặc thử lại sau.
        </p>
        <Button onClick={() => void queryClient.invalidateQueries({ queryKey: ["dashboardData"] })}>
          Thử lại
        </Button>
      </div>
    )
  }

  const { profile, statistics, activity_chart, recent_activity, favorite_workspace } = dashboard
  const maxChatsCount = Math.max(...activity_chart.chats_per_day.map((d) => d.count), 1)

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Bảng điều khiển cá nhân</h1>
        <p className="text-muted-foreground">
          Tổng quan hoạt động và thông tin tài khoản của bạn tại DevHub AI
        </p>
      </div>

      {error && (
        <div className="p-4 bg-destructive/15 text-destructive rounded-lg text-sm font-medium">
          {error}
        </div>
      )}

      {/* Main Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Side: Profile Info & Fav Workspace */}
        <div className="space-y-6 lg:col-span-1">
          {/* User Info Card */}
          <Card className="overflow-hidden">
            <div className="h-20 bg-gradient-to-r from-primary/80 to-primary relative" />
            <CardContent className="pt-0 relative">
              <div className="flex justify-center -mt-10 mb-4">
                <div className="h-20 w-20 rounded-full border-4 border-background bg-muted flex items-center justify-center text-primary font-bold text-2xl shadow-sm">
                  {profile.full_name ? profile.full_name.charAt(0).toUpperCase() : profile.email.charAt(0).toUpperCase()}
                </div>
              </div>
              <div className="text-center space-y-1 mb-6">
                <h3 className="font-semibold text-lg">{profile.full_name || "Chưa cập nhật tên"}</h3>
                <p className="text-xs text-muted-foreground capitalize bg-primary/10 text-primary px-2 py-0.5 rounded-full inline-block font-medium">
                  {profile.role}
                </p>
              </div>

              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-3 text-muted-foreground">
                  <Mail className="h-4 w-4 text-primary" />
                  <span className="truncate">{profile.email}</span>
                </div>
                <div className="flex items-center gap-3 text-muted-foreground">
                  <User className="h-4 w-4 text-primary" />
                  <span>
                    Giới tính:{" "}
                    {profile.gender === "male"
                      ? "Nam"
                      : profile.gender === "female"
                      ? "Nữ"
                      : "Khác"}
                  </span>
                </div>
                <div className="flex items-center gap-3 text-muted-foreground">
                  <Calendar className="h-4 w-4 text-primary" />
                  <span>Tham gia: {formatJoinDate(profile.created_at)}</span>
                </div>
              </div>

              <Button
                variant="outline"
                size="sm"
                className="mt-6 w-full text-xs"
                onClick={openEditDialog}
              >
                Chỉnh sửa hồ sơ
              </Button>
            </CardContent>
          </Card>

          {/* Favorite Workspace Card */}
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-amber-500" />
                Workspace hoạt động nhất
              </CardTitle>
            </CardHeader>
            <CardContent>
              {favorite_workspace ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div
                      className="w-10 h-10 rounded-lg flex items-center justify-center text-white font-bold"
                      style={{ backgroundColor: favorite_workspace.color }}
                    >
                      {favorite_workspace.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h4 className="font-medium text-sm">{favorite_workspace.name}</h4>
                      <p className="text-xs text-muted-foreground">
                        {favorite_workspace.chat_count} cuộc trò chuyện
                      </p>
                    </div>
                  </div>
                  <Button variant="outline" size="sm" className="w-full text-xs" asChild>
                    <Link to={`/workspaces/${favorite_workspace.id}`}>
                      Đi tới Workspace <ArrowRight className="ml-1 h-3.5 w-3.5" />
                    </Link>
                  </Button>
                </div>
              ) : (
                <div className="text-center py-6 text-muted-foreground text-xs space-y-1">
                  <Layers className="h-8 w-8 mx-auto mb-2 text-muted-foreground/50" />
                  <p>Chưa có dữ liệu Workspace</p>
                  <p className="text-[10px]">Tạo workspace và bắt đầu chat để ghi nhận</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Side: Stats & Activity Chart & Recent Timeline */}
        <div className="lg:col-span-2 space-y-6">
          {/* Statistics Grid */}
          <div className="grid gap-4 grid-cols-2 sm:grid-cols-4">
            <Card>
              <CardContent className="p-4 flex flex-col justify-between h-24">
                <p className="text-xs text-muted-foreground">Workspaces</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-2xl font-bold">{statistics.total_workspaces}</span>
                  <FolderOpen className="h-4 w-4 text-blue-500 opacity-85" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 flex flex-col justify-between h-24">
                <p className="text-xs text-muted-foreground">Chats</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-2xl font-bold">{statistics.total_chats}</span>
                  <MessageSquare className="h-4 w-4 text-indigo-500 opacity-85" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 flex flex-col justify-between h-24">
                <p className="text-xs text-muted-foreground">Tài liệu tải lên</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-2xl font-bold">{statistics.total_documents}</span>
                  <FileText className="h-4 w-4 text-emerald-500 opacity-85" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4 flex flex-col justify-between h-24">
                <p className="text-xs text-muted-foreground">Câu hỏi AI</p>
                <div className="flex items-center justify-between mt-2">
                  <span className="text-2xl font-bold">{statistics.total_ai_questions}</span>
                  <Sparkles className="h-4 w-4 text-amber-500 opacity-85" />
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Activity Chart & Month stats */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-semibold flex items-center justify-between">
                <span>Tần suất hoạt động</span>
                <span className="text-xs text-muted-foreground bg-muted px-2 py-1 rounded">
                  Tháng này: {activity_chart.total_activity_this_month} hoạt động
                </span>
              </CardTitle>
              <p className="text-xs text-muted-foreground">Số cuộc trò chuyện mới được tạo trong 7 ngày qua</p>
            </CardHeader>
            <CardContent>
              {/* Pure CSS Bar Chart */}
              <div className="flex items-end justify-between gap-3 h-40 pt-6">
                {activity_chart.chats_per_day.map((day) => {
                  const percent = (day.count / maxChatsCount) * 100
                  return (
                    <div key={day.date} className="flex-1 flex flex-col items-center group relative h-full justify-end">
                      {/* Tooltip */}
                      <div className="absolute bottom-full mb-1 hidden group-hover:block bg-slate-900 text-slate-100 text-[10px] rounded px-2 py-0.5 shadow-md z-10 whitespace-nowrap">
                        {day.count} cuộc trò chuyện
                      </div>
                      {/* Bar */}
                      <div
                        className="w-full bg-primary/20 hover:bg-primary/30 rounded-t transition-all duration-300 relative overflow-hidden"
                        style={{ height: `${Math.max(percent, 4)}%` }}
                      >
                        {day.count > 0 && (
                          <div className="absolute inset-x-0 bottom-0 top-0 bg-primary" />
                        )}
                      </div>
                      {/* Date label */}
                      <span className="text-[10px] text-muted-foreground mt-2 font-mono whitespace-nowrap">
                        {day.label}
                      </span>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base font-semibold">Hoạt động gần đây</CardTitle>
              <p className="text-xs text-muted-foreground">Lịch sử tương tác của bạn</p>
            </CardHeader>
            <CardContent>
              {recent_activity.length > 0 ? (
                <div className="space-y-4 relative before:absolute before:inset-y-1 before:left-3.5 before:w-0.5 before:bg-muted">
                  {recent_activity.map((item) => {
                    const isChat = item.type === "chat_created"
                    const isDoc = item.type === "document_uploaded"

                    return (
                      <div key={item.id} className="flex items-start gap-4 relative">
                        <div
                          className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 z-10 border-4 border-background ${
                            isChat
                              ? "bg-indigo-100 text-indigo-600"
                              : isDoc
                              ? "bg-emerald-100 text-emerald-600"
                              : "bg-amber-100 text-amber-600"
                          }`}
                        >
                          {isChat ? (
                            <MessageSquare className="h-3 w-3" />
                          ) : isDoc ? (
                            <FileText className="h-3 w-3" />
                          ) : (
                            <FolderOpen className="h-3 w-3" />
                          )}
                        </div>
                        <div className="flex-1 space-y-1 pt-1">
                          <div className="text-sm font-medium leading-none text-muted-foreground">
                            {isChat ? (
                              <span>Bắt đầu cuộc hội thoại: <span className="font-semibold text-foreground">{item.title}</span></span>
                            ) : isDoc ? (
                              <span>Đã tải lên tài liệu: <span className="font-semibold text-foreground">{item.title}</span></span>
                            ) : (
                              <span>Đã tạo workspace mới: <span className="font-semibold text-foreground">{item.title}</span></span>
                            )}
                          </div>
                          <p className="text-xs text-muted-foreground">
                            {formatActivityTime(item.created_at)}
                          </p>
                        </div>
                      </div>
                    )
                  })}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground text-sm space-y-2">
                  <Activity className="h-10 w-10 mx-auto text-muted-foreground/30" />
                  <p>Chưa có ghi nhận hoạt động nào gần đây.</p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Danger Zone */}
          <Card className="border-destructive/50">
            <CardHeader>
              <CardTitle className="text-base font-semibold text-destructive">Vùng nguy hiểm</CardTitle>
              <p className="text-xs text-muted-foreground">
                Các thao tác dọn dẹp hoặc cấu hình hệ thống
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center border-b pb-4">
                <div>
                  <h4 className="text-sm font-medium">Xóa tất cả các cuộc trò chuyện</h4>
                  <p className="text-xs text-muted-foreground">
                    Hành động này sẽ xóa vĩnh viễn toàn bộ lịch sử hội thoại của bạn.
                  </p>
                </div>
                <Button
                  variant="destructive"
                  onClick={() => setDeleteDialogOpen(true)}
                  className="shrink-0 text-xs"
                >
                  <Trash2 className="h-4 w-4 mr-2" /> Xóa tất cả cuộc trò chuyện
                </Button>
              </div>
              
              <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
                <div>
                  <h4 className="text-sm font-medium">Đăng xuất khỏi hệ thống</h4>
                  <p className="text-xs text-muted-foreground">
                    Đăng xuất phiên làm việc hiện tại trên thiết bị này.
                  </p>
                </div>
                <Button
                  variant="outline"
                  onClick={() => void handleLogout()}
                  className="shrink-0 text-xs text-destructive hover:text-destructive hover:bg-destructive/10"
                >
                  Đăng xuất
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-destructive">
              <Trash2 className="h-5 w-5" />
              Xác nhận xóa toàn bộ cuộc trò chuyện?
            </DialogTitle>
            <DialogDescription>
              Bạn có chắc chắn muốn xóa vĩnh viễn tất cả các cuộc trò chuyện? Lịch sử tin nhắn của bạn sẽ bị dọn sạch và không thể khôi phục. Tài liệu tải lên và Workspace của bạn sẽ không bị ảnh hưởng.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              disabled={isDeleting}
              className="text-xs"
            >
              Hủy
            </Button>
            <Button
              type="button"
              variant="destructive"
              onClick={() => void handleDeleteChats()}
              disabled={isDeleting}
              className="text-xs"
            >
              {isDeleting ? "Đang xóa..." : "Tôi hiểu, tiến hành xóa"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Profile Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Chỉnh sửa hồ sơ</DialogTitle>
            <p className="text-xs text-muted-foreground">
              Cập nhật thông tin cá nhân của bạn. Nhấn lưu khi hoàn tất.
            </p>
          </DialogHeader>

          {successMessage && (
            <div className="p-3 bg-emerald-50 text-emerald-700 rounded-lg text-xs font-medium border border-emerald-250">
              {successMessage}
            </div>
          )}

          <form onSubmit={(e) => void handleSaveProfile(e)} className="space-y-4 py-4">
            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">Địa chỉ Email</label>
              <input
                type="text"
                disabled
                value={profile.email}
                className="flex h-10 w-full rounded-md border border-input bg-muted px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-80"
              />
              <p className="text-[10px] text-muted-foreground">Email không thể thay đổi</p>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">Họ và tên</label>
              <input
                type="text"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="Nhập họ và tên"
                required
              />
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">Giới tính</label>
              <select
                value={editGender}
                onChange={(e) => setEditGender(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              >
                <option value="male">Nam</option>
                <option value="female">Nữ</option>
                <option value="other">Khác</option>
                <option value="prefer_not_to_say">Không muốn tiết lộ</option>
              </select>
            </div>

            <div className="space-y-1">
              <label className="text-xs font-medium text-muted-foreground">Avatar URL (Tùy chọn)</label>
              <input
                type="text"
                value={editAvatarUrl}
                onChange={(e) => setEditAvatarUrl(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                placeholder="https://example.com/avatar.png"
              />
            </div>

            <DialogFooter className="pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setEditDialogOpen(false)}
                disabled={isSavingProfile}
                className="text-xs"
              >
                Hủy
              </Button>
              <Button
                type="submit"
                disabled={isSavingProfile}
                className="text-xs"
              >
                {isSavingProfile ? "Đang lưu..." : "Lưu thay đổi"}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  )
}
