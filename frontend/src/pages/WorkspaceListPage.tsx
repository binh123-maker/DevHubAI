import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { FolderOpen, Pencil, Plus, Trash2 } from "lucide-react"
import { useState } from "react"
import { Link } from "react-router-dom"

import { getApiErrorMessage } from "@/api/axios"
import {
  type Workspace,
  type WorkspaceCreatePayload,
  type WorkspaceUpdatePayload,
  workspaceApi,
} from "@/api/workspace.api"
import { DeleteWorkspaceDialog } from "@/components/workspace/DeleteWorkspaceDialog"
import { WorkspaceFormDialog } from "@/components/workspace/WorkspaceFormDialog"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function WorkspaceListPage() {
  const queryClient = useQueryClient()
  const [formOpen, setFormOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [selectedWorkspace, setSelectedWorkspace] = useState<Workspace | null>(null)
  const [error, setError] = useState<string | null>(null)

  const { data: workspaces = [], isLoading } = useQuery({
    queryKey: ["workspaces"],
    queryFn: async () => {
      const response = await workspaceApi.list()
      return response.data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: WorkspaceCreatePayload) => workspaceApi.create(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workspaces"] })
      setError(null)
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể tạo workspace.")),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: WorkspaceUpdatePayload }) =>
      workspaceApi.update(id, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workspaces"] })
      setError(null)
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể cập nhật workspace.")),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => workspaceApi.delete(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workspaces"] })
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
    if (!selectedWorkspace) {
      return
    }
    await deleteMutation.mutateAsync(selectedWorkspace.id)
  }

  const isSubmitting = createMutation.isPending || updateMutation.isPending

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Workspaces</h1>
          <p className="text-sm text-muted-foreground">Quản lý không gian tri thức của bạn</p>
        </div>
        <Button onClick={openCreateDialog}>
          <Plus className="h-4 w-4" />
          Tạo workspace
        </Button>
      </div>

      {error && (
        <div className="rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {isLoading ? (
        <Card>
          <CardContent className="py-8">
            <p className="text-muted-foreground">Đang tải workspaces...</p>
          </CardContent>
        </Card>
      ) : workspaces.length === 0 ? (
        <Card>
          <CardHeader>
            <CardTitle>Chưa có workspace</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Tạo workspace đầu tiên để bắt đầu tổ chức tài liệu và chat AI.
            </p>
            <Button onClick={openCreateDialog}>
              <Plus className="h-4 w-4" />
              Tạo workspace
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {workspaces.map((workspace) => (
            <Card key={workspace.id} className="overflow-hidden">
              <div className="h-1.5" style={{ backgroundColor: workspace.color }} />
              <CardHeader className="space-y-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <div
                      className="flex h-10 w-10 items-center justify-center rounded-md"
                      style={{ backgroundColor: `${workspace.color}20`, color: workspace.color }}
                    >
                      <FolderOpen className="h-5 w-5" />
                    </div>
                    <div>
                      <CardTitle className="text-lg">
                        <Link to={`/workspaces/${workspace.id}`} className="hover:underline">
                          {workspace.name}
                        </Link>
                      </CardTitle>
                      {workspace.description && (
                        <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{workspace.description}</p>
                      )}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => openEditDialog(workspace)}>
                  <Pencil className="h-4 w-4" />
                  Sửa
                </Button>
                <Button variant="destructive" size="sm" onClick={() => openDeleteDialog(workspace)}>
                  <Trash2 className="h-4 w-4" />
                  Xóa
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

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
