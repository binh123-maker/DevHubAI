import { useState } from "react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { FolderOpen, Pencil, Plus, Trash2, LayoutDashboard, Kanban, Layers, Zap } from "lucide-react"
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

import { useScrollSpy } from "@/hooks/useScrollSpy"
import { DeleteWorkspaceDialog } from "@/components/workspace/DeleteWorkspaceDialog"
import { WorkspaceFormDialog } from "@/components/workspace/WorkspaceFormDialog"
import { DocumentUploadDialog } from "@/components/document/DocumentUploadDialog"
import { DashboardStatsGrid } from "@/components/dashboard/DashboardStatsGrid"
import { LearningAnalytics } from "@/components/dashboard/LearningAnalytics"
import { GitHubContributionHeatmap } from "@/components/dashboard/GitHubContributionHeatmap"
import { RecentActivityList } from "@/components/dashboard/RecentActivityList"
import { WorkspaceKanbanBoard } from "@/components/kanban/WorkspaceKanbanBoard"
import { QuickActions } from "@/components/dashboard/QuickActions"
import { AnimatedSection } from "@/components/dashboard/AnimatedSection"
import { DashboardWidget } from "@/components/dashboard/DashboardWidget"

// Skeleton Loaders
import { StatsGridSkeleton } from "@/components/dashboard/skeletons/StatsGridSkeleton"
import { HeatmapSkeleton } from "@/components/dashboard/skeletons/HeatmapSkeleton"
import { AnalyticsSkeleton } from "@/components/dashboard/skeletons/AnalyticsSkeleton"
import { RecentActivitySkeleton } from "@/components/dashboard/skeletons/RecentActivitySkeleton"
import { KanbanSkeleton } from "@/components/dashboard/skeletons/KanbanSkeleton"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const SECTION_IDS = [
  "overview",
  "statistics",
  "analytics",
  "heatmap",
  "activity",
  "kanban",
  "workspaces",
]

export default function WorkspaceListPage() {
  const queryClient = useQueryClient()
  const [formOpen, setFormOpen] = useState(false)
  const [uploadOpen, setUploadOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [selectedWorkspace, setSelectedWorkspace] = useState<Workspace | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Initialize IntersectionObserver Scroll Spy
  useScrollSpy(SECTION_IDS)

  // Fetch Dashboard Overview
  const { data: dashboard, isLoading: isDashboardLoading } = useQuery({
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
    <div className="space-y-8 pb-16">
      {/* 1. Overview Header */}
      <AnimatedSection id="overview">
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
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => setUploadOpen(true)} className="gap-2 shadow-xs">
              Tải lên tài liệu
            </Button>
            <Button onClick={openCreateDialog} className="gap-2 shadow-xs">
              <Plus className="h-4 w-4" />
              Tạo Workspace mới
            </Button>
          </div>
        </div>
      </AnimatedSection>

      {error && (
        <div className="rounded-xl border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive font-medium">
          {error}
        </div>
      )}

      {/* 2. Quick Actions Onboarding Section */}
      <section className="space-y-3">
        <h2 className="text-xs font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
          <Zap className="h-4 w-4 text-amber-500" />
          Thao tác nhanh (Quick Actions)
        </h2>
        <QuickActions
          onUploadClick={() => setUploadOpen(true)}
          onCreateWorkspaceClick={openCreateDialog}
        />
      </section>

      {/* 3. Dashboard Statistics KPI Cards */}
      <AnimatedSection id="statistics">
        <section className="space-y-3">
          <h2 className="text-lg font-bold flex items-center gap-2">
            <Layers className="h-5 w-5 text-indigo-500" />
            Tổng quan chỉ số học tập
          </h2>
          <DashboardWidget title="Statistics KPI Grid">
            {isDashboardLoading || !dashboard ? (
              <StatsGridSkeleton />
            ) : (
              <DashboardStatsGrid
                statistics={dashboard.statistics}
                onUploadClick={() => setUploadOpen(true)}
              />
            )}
          </DashboardWidget>
        </section>
      </AnimatedSection>

      {/* 4. Learning Analytics Cards */}
      <AnimatedSection id="analytics">
        <section className="space-y-3">
          <DashboardWidget title="Learning Analytics">
            {isDashboardLoading || !dashboard ? (
              <AnalyticsSkeleton />
            ) : (
              <LearningAnalytics analytics={dashboard.learning_analytics} />
            )}
          </DashboardWidget>
        </section>
      </AnimatedSection>

      {/* 5. Heatmap & Recent Activity Timeline */}
      <div className="grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <AnimatedSection id="heatmap">
            <DashboardWidget title="Contribution Heatmap">
              {isDashboardLoading || !dashboard ? (
                <HeatmapSkeleton />
              ) : (
                <GitHubContributionHeatmap data={dashboard.heatmap} days={90} />
              )}
            </DashboardWidget>
          </AnimatedSection>
        </div>

        <div>
          <AnimatedSection id="activity">
            <DashboardWidget title="Recent Activity">
              {isDashboardLoading || !dashboard ? (
                <RecentActivitySkeleton />
              ) : (
                <RecentActivityList activities={dashboard.recent_activities} />
              )}
            </DashboardWidget>
          </AnimatedSection>
        </div>
      </div>

      {/* 6. Document Kanban Board Section */}
      <AnimatedSection id="kanban">
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

          <DashboardWidget title="Document Kanban Board">
            {isDocumentsLoading ? (
              <KanbanSkeleton />
            ) : (
              <WorkspaceKanbanBoard
                documents={documents}
                workspaces={workspaces.map((w) => ({ id: w.id, name: w.name }))}
                folders={[]}
                onUploadClick={() => setUploadOpen(true)}
                onCreateWorkspaceClick={openCreateDialog}
              />
            )}
          </DashboardWidget>
        </section>
      </AnimatedSection>

      {/* 7. Workspaces Grid */}
      <AnimatedSection id="workspaces">
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
      </AnimatedSection>

      {/* Dialogs */}
      <WorkspaceFormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        workspace={selectedWorkspace}
        onSubmit={handleFormSubmit}
        isSubmitting={isSubmitting}
      />

      <DocumentUploadDialog
        open={uploadOpen}
        onOpenChange={setUploadOpen}
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
