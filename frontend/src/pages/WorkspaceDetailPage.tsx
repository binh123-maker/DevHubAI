import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { format } from "date-fns"
import { ArrowLeft, ChevronRight, FolderOpen, Pencil, Trash2 } from "lucide-react"
import { useState } from "react"
import { Link, useNavigate, useParams } from "react-router-dom"

import { getApiErrorMessage } from "@/api/axios"
import { type WorkspaceUpdatePayload, workspaceApi } from "@/api/workspace.api"
import { DeleteWorkspaceDialog } from "@/components/workspace/DeleteWorkspaceDialog"
import { WorkspaceFormDialog } from "@/components/workspace/WorkspaceFormDialog"
import { DocumentList } from "@/components/document/DocumentList"
import { FolderList } from "@/components/folder/FolderList"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export default function WorkspaceDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [formOpen, setFormOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // ── Folder navigation state ──────────────────────────────────────────────
  const [activeFolder, setActiveFolder] = useState<{ id: string; name: string } | null>(null)

  const { data: workspace, isLoading, isError } = useQuery({
    queryKey: ["workspaces", id],
    queryFn: async () => {
      const response = await workspaceApi.get(id!)
      return response.data
    },
    enabled: Boolean(id),
  })

  const updateMutation = useMutation({
    mutationFn: (payload: WorkspaceUpdatePayload) => workspaceApi.update(id!, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workspaces"] })
      void queryClient.invalidateQueries({ queryKey: ["workspaces", id] })
      setError(null)
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể cập nhật workspace.")),
  })

  const deleteMutation = useMutation({
    mutationFn: () => workspaceApi.delete(id!),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workspaces"] })
      navigate("/workspaces", { replace: true })
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể xóa workspace.")),
  })

  if (isLoading) {
    return <p className="text-muted-foreground">Đang tải workspace...</p>
  }

  if (isError || !workspace) {
    return (
      <div className="space-y-4">
        <Button variant="outline" asChild>
          <Link to="/workspaces">
            <ArrowLeft className="h-4 w-4" />
            Quay lại
          </Link>
        </Button>
        <Card>
          <CardContent className="py-8">
            <p className="text-destructive">Không tìm thấy workspace hoặc bạn không có quyền truy cập.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-4">
        <Button variant="outline" asChild>
          <Link to="/workspaces">
            <ArrowLeft className="h-4 w-4" />
            Quay lại
          </Link>
        </Button>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setFormOpen(true)}>
            <Pencil className="h-4 w-4" />
            Sửa
          </Button>
          <Button variant="destructive" onClick={() => setDeleteOpen(true)}>
            <Trash2 className="h-4 w-4" />
            Xóa
          </Button>
        </div>
      </div>

      {error && (
        <div className="rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      <Card className="overflow-hidden">
        <div className="h-2" style={{ backgroundColor: workspace.color }} />
        <CardHeader className="pb-4">
          <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
            <div>
              <CardTitle className="text-2xl mb-2">{workspace.name}</CardTitle>
            </div>
            <div className="text-sm text-muted-foreground whitespace-nowrap">
              Updated {format(new Date(workspace.updated_at), "dd MMM yyyy")}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-8 md:grid-cols-2">
            <div>
              <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">Workspace Overview</h4>
              <div className="space-y-1">
                <p className="text-sm font-medium">Description</p>
                <p className="text-sm text-muted-foreground">
                  {workspace.description || "No description yet."}
                </p>
              </div>
            </div>
            <div>
              <h4 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3">Statistics</h4>
              <div className="flex gap-6">
                <div className="flex flex-col">
                  <span className="text-2xl font-bold">{workspace.document_count}</span>
                  <span className="text-sm text-muted-foreground">Documents</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-2xl font-bold">{workspace.folder_count}</span>
                  <span className="text-sm text-muted-foreground">Folders</span>
                </div>
                <div className="flex flex-col">
                  <span className="text-2xl font-bold">{workspace.source_count}</span>
                  <span className="text-sm text-muted-foreground">Sources</span>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Folder List */}
      <FolderList
        workspaceId={workspace.id}
        activeFolderId={activeFolder?.id}
        onFolderClick={(folder) => setActiveFolder({ id: folder.id, name: folder.name })}
        onFolderDeleted={() => {
          setActiveFolder(null)
          void queryClient.invalidateQueries({ queryKey: ["documents", workspace.id] })
        }}
      />

      {/* Document List with breadcrumb */}
      <div className="mt-8 space-y-3">
        {/* Breadcrumb */}
        <div className="flex items-center gap-1.5 text-sm text-muted-foreground">
          <button
            onClick={() => setActiveFolder(null)}
            className="hover:text-foreground transition-colors font-medium flex items-center gap-1"
          >
            <FolderOpen className="h-4 w-4" />
            {workspace.name}
          </button>
          {activeFolder && (
            <>
              <ChevronRight className="h-3.5 w-3.5 shrink-0" />
              <span className="font-medium text-foreground truncate">{activeFolder.name}</span>
            </>
          )}
        </div>

        <DocumentList workspaceId={workspace.id} folderId={activeFolder?.id} />
      </div>

      <WorkspaceFormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        workspace={workspace}
        onSubmit={(payload) => updateMutation.mutateAsync(payload)}
        isSubmitting={updateMutation.isPending}
      />

      <DeleteWorkspaceDialog
        open={deleteOpen}
        onOpenChange={setDeleteOpen}
        workspaceName={workspace.name}
        onConfirm={() => deleteMutation.mutateAsync()}
        isDeleting={deleteMutation.isPending}
      />
    </div>
  )
}
