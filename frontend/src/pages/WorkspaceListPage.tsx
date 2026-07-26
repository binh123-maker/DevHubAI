import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { FolderOpen, Pencil, Plus, Trash2, LayoutDashboard, Kanban, Layers } from "lucide-react"
import { Link } from "react-router-dom"


import { getApiErrorMessage } from "@/api/axios"
import {
  type Workspace,
  type WorkspaceCreatePayload,
  type WorkspaceUpdatePayload,
  workspaceApi,
} from "@/api/workspace.api"
import { documentApi } from "@/api/document.api"
import { dashboardApi } from "@/api/dashboard.api"

import { DeleteWorkspaceDialog } from "@/components/workspace/DeleteWorkspaceDialog"
import { WorkspaceFormDialog } from "@/components/workspace/WorkspaceFormDialog"
import { DashboardStatsGrid } from "@/components/dashboard/DashboardStatsGrid"
import { LearningAnalytics } from "@/components/dashboard/LearningAnalytics"
import { GitHubContributionHeatmap } from "@/components/dashboard/GitHubContributionHeatmap"
import { RecentActivityList } from "@/components/dashboard/RecentActivityList"
import { WorkspaceKanbanBoard } from "@/components/kanban/WorkspaceKanbanBoard"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function WorkspaceListPage() {
  const queryClient = useQueryClient()
  const [formOpen, setFormOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [selectedWorkspace, setSelectedWorkspace] = useState<Workspace | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Fetch Dashboard Overview
  const { data: dashboard } = useQuery({
    queryKey: ["dashboardOverview"],
    queryFn: async () => {
      const res = await dashboardApi.getOverview()
      return res.data
    },
  })


  // Fetch Workspaces
  const { data: workspaces = [], isLoading: isWorkspacesLoading } = useQuery({
    queryKey: ["workspaces"],
    queryFn: async () => {
      const response = await workspaceApi.list()
      return response.data
    },
  })

  // Fetch All User Documents for Kanban
  const { data: documents = [], isLoading: isDocumentsLoading } = useQuery({
    queryKey: ["documents"],
    queryFn: async () => {
      const response = await documentApi.listAll()
      return response.data
    },
  })

  // Create Workspace Mutation
  const createMutation = useMutation({
    mutationFn: (payload: WorkspaceCreatePayload) => workspaceApi.create(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workspaces"] })
      void queryClient.invalidateQueries({ queryKey: ["dashboardOverview"] })
      setError(null)
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể tạo workspace.")),
  })

  // Update Workspace Mutation
  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: WorkspaceUpdatePayload }) =>
      workspaceApi.update(id, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workspaces"] })
      void queryClient.invalidateQueries({ queryKey: ["dashboardOverview"] })
      setError(null)
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể cập nhật workspace.")),
  })

  // Delete Workspace Mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => workspaceApi.delete(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workspaces"] })
      void queryClient.invalidateQueries({ queryKey: ["dashboardOverview"] })
      void queryClient.invalidateQueries({ queryKey: ["documents"] })
      setError(null)
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể xóa workspace.")),
  })

  function openCreateDialog() {
    setSelectedWorkspace(null)
    setFormOpen(true)
  }

  function openEditDialog(workspace: Workspace) {
    setSelectedWorkspace(workspace)
    setFormOpen(true)
  }

  function openDeleteDialog(workspace: Workspace) {
    setSelectedWorkspace(workspace)
    setDeleteOpen(true)
  }

  async function handleFormSubmit(payload: WorkspaceCreatePayload | WorkspaceUpdatePayload) {
    if (selectedWorkspace) {
      await updateMutation.mutateAsync({ id: selectedWorkspace.id, payload })
      return
    }
    await createMutation.mutateAsync(payload as WorkspaceCreatePayload)
  }

  async function handleDeleteConfirm() {
    if (!selectedWorkspace) return
    await deleteMutation.mutateAsync(selectedWorkspace.id)
  }

  const isSubmitting = createMutation.isPending || updateMutation.isPending

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border/40 pb-5">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight flex items-center gap-3">
            <LayoutDashboard className="h-7 w-7 text-primary" />
            Knowledge Management Dashboard
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Theo dõi tiến độ học tập, quản lý tài liệu Kanban & không gian tri thức của bạn
          </p>
        </div>
        <Button onClick={openCreateDialog} className="gap-2 shadow-sm">
          <Plus className="h-4 w-4" />
          Tạo Workspace mới
        </Button>
      </div>

      {error && (
        <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive font-medium">
          {error}
        </div>
      )}

      {/* 1. Dashboard Statistics KPI Cards */}
      {dashboard && (
        <section className="space-y-3">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Layers className="h-5 w-5 text-indigo-500" />
            Tổng quan chỉ số học tập
          </h2>
          <DashboardStatsGrid statistics={dashboard.statistics} />
        </section>
      )}

      {/* 2. Learning Analytics Cards */}
      {dashboard && (
        <section className="space-y-3">
          <LearningAnalytics analytics={dashboard.learning_analytics} />
        </section>
      )}

      {/* 3. Heatmap & Recent Activity Timeline */}
      {dashboard && (
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <GitHubContributionHeatmap data={dashboard.heatmap} days={90} />
          </div>
          <div>
            <RecentActivityList activities={dashboard.recent_activities} />
          </div>
        </div>
      )}

      {/* 4. Document Kanban Board Section */}
      <section className="space-y-4 pt-4 border-t border-border/40">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold tracking-tight flex items-center gap-2">
              <Kanban className="h-5 w-5 text-primary" />
              Bảng Tiến độ Tài liệu (Document Kanban)
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Kéo thả tài liệu để phân loại trạng thái học tập (Mới &rarr; Đang học &rarr; Hoàn thành)
            </p>
          </div>
        </div>

        {isDocumentsLoading ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              Đang tải bảng Kanban...
            </CardContent>
          </Card>
        ) : (
          <WorkspaceKanbanBoard
            documents={documents}
            workspaces={workspaces.map((w) => ({ id: w.id, name: w.name }))}
            folders={[]}
            onUploadClick={openCreateDialog}
          />
        )}
      </section>

      {/* 5. Workspaces Grid */}
      <section className="space-y-4 pt-6 border-t border-border/40">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold tracking-tight flex items-center gap-2">
              <FolderOpen className="h-5 w-5 text-amber-500" />
              Danh sách Workspaces ({workspaces.length})
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              Các không gian chứa thư mục & tài liệu theo chủ đề
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={openCreateDialog} className="gap-1.5 text-xs">
            <Plus className="h-3.5 w-3.5" />
            Tạo Workspace
          </Button>
        </div>

        {isWorkspacesLoading ? (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              Đang tải danh sách workspaces...
            </CardContent>
          </Card>
        ) : workspaces.length === 0 ? (
          <Card className="border-dashed">
            <CardHeader>
              <CardTitle className="text-base">Chưa có workspace nào</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-xs text-muted-foreground">
                Tạo workspace đầu tiên để bắt đầu nhóm các tài liệu và chat AI theo dự án.
              </p>
              <Button size="sm" onClick={openCreateDialog}>
                <Plus className="h-4 w-4 mr-1" />
                Tạo workspace
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {workspaces.map((ws) => (
              <Card key={ws.id} className="overflow-hidden border border-border/60 bg-card/60 backdrop-blur-xs transition-all hover:shadow-md hover:border-primary/40">
                <div className="h-1.5" style={{ backgroundColor: ws.color }} />
                <CardHeader className="p-4 space-y-2">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div
                        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg font-bold"
                        style={{ backgroundColor: `${ws.color}20`, color: ws.color }}
                      >
                        <FolderOpen className="h-5 w-5" />
                      </div>
                      <div>
                        <CardTitle className="text-base font-semibold">
                          <Link to={`/workspaces/${ws.id}`} className="hover:underline hover:text-primary transition-colors">
                            {ws.name}
                          </Link>
                        </CardTitle>
                        {ws.description && (
                          <p className="mt-0.5 line-clamp-2 text-xs text-muted-foreground">{ws.description}</p>
                        )}
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="px-4 pb-4 pt-0 flex gap-2 justify-end border-t border-border/30 pt-3">
                  <Button variant="ghost" size="sm" onClick={() => openEditDialog(ws)} className="h-8 text-xs gap-1">
                    <Pencil className="h-3.5 w-3.5" />
                    Sửa
                  </Button>
                  <Button variant="ghost" size="sm" onClick={() => openDeleteDialog(ws)} className="h-8 text-xs gap-1 text-destructive hover:bg-destructive/10 hover:text-destructive">
                    <Trash2 className="h-3.5 w-3.5" />
                    Xóa
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </section>

      {/* Dialogs */}
      <WorkspaceFormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        workspace={selectedWorkspace}
        onSubmit={handleFormSubmit}
        isSubmitting={isSubmitting}
      />

      <DeleteWorkspaceDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        workspaceName={selectedWorkspace?.name}
        onConfirm={handleDeleteConfirm}
        isDeleting={deleteMutation.isPending}
      />
    </div>
  )
}
