import { useState } from "react"
import { useParams, useNavigate, Link } from "react-router-dom"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { ArrowLeft, ChevronRight, FolderOpen } from "lucide-react"

import { workspaceApi, type WorkspaceUpdatePayload } from "@/api/workspace.api"
import { folderApi, type Folder, type FolderCreatePayload, type FolderUpdatePayload } from "@/api/folder.api"
import { documentApi } from "@/api/document.api"
import { chatApi } from "@/api/chat.api"
import { getApiErrorMessage } from "@/api/axios"

// Redesigned AI Knowledge Hub components
import { WorkspaceHero } from "@/components/workspace/redesign/WorkspaceHero"
import { SmartStatsGrid } from "@/components/workspace/redesign/SmartStatsGrid"
import { FolderSectionRedesign } from "@/components/workspace/redesign/FolderSectionRedesign"
import { DocumentEngine } from "@/components/workspace/redesign/DocumentEngine"
import { AIKnowledgeDrawer } from "@/components/workspace/redesign/AIKnowledgeDrawer"
import { ActivityTimeline } from "@/components/workspace/redesign/ActivityTimeline"

// Dialogs
import { WorkspaceFormDialog } from "@/components/workspace/WorkspaceFormDialog"
import { DeleteWorkspaceDialog } from "@/components/workspace/DeleteWorkspaceDialog"
import { FolderFormDialog } from "@/components/folder/FolderFormDialog"
import { DeleteFolderDialog } from "@/components/folder/DeleteFolderDialog"
import { UploadDocumentModal } from "@/components/document/UploadDocumentModal"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

export default function WorkspaceDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  // State controls
  const [activeFolder, setActiveFolder] = useState<Folder | null>(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Dialog open states
  const [workspaceFormOpen, setWorkspaceFormOpen] = useState(false)
  const [deleteWorkspaceOpen, setDeleteWorkspaceOpen] = useState(false)
  const [folderFormOpen, setFolderFormOpen] = useState(false)
  const [folderToEdit, setFolderToEdit] = useState<Folder | null>(null)
  const [deleteFolderOpen, setDeleteFolderOpen] = useState(false)
  const [folderToDelete, setFolderToDelete] = useState<Folder | null>(null)
  const [uploadModalOpen, setUploadModalOpen] = useState(false)

  // Handler: Start or open existing AI Chat for current Workspace
  const handleStartChat = async () => {
    if (!workspace) return
    try {
      const existingChats = await chatApi.getChats(workspace.id)
      if (existingChats && existingChats.length > 0) {
        navigate(`/history/${existingChats[0].id}`)
      } else {
        const newChat = await chatApi.createChat(
          `AI Chat - ${workspace.name}`,
          workspace.id,
          undefined,
          undefined,
          "workspace"
        )
        navigate(`/history/${newChat.id}`)
      }
    } catch (err) {
      console.error("Không thể tạo hoặc mở AI Chat:", err)
      navigate("/history")
    }
  }

  // Queries
  const { data: workspace, isLoading: isWorkspaceLoading, isError } = useQuery({
    queryKey: ["workspaces", id],
    queryFn: async () => {
      const response = await workspaceApi.get(id!)
      return response.data
    },
    enabled: Boolean(id),
  })

  const { data: folders = [], isLoading: isFoldersLoading } = useQuery({
    queryKey: ["folders", id],
    queryFn: async () => {
      const response = await folderApi.list(id!)
      return response.data
    },
    enabled: Boolean(id),
  })

  const { data: documents = [], isLoading: isDocsLoading } = useQuery({
    queryKey: ["documents", id, activeFolder?.id],
    queryFn: async () => {
      const response = await documentApi.list(id!, activeFolder?.id || undefined)
      return response.data
    },
    enabled: Boolean(id),
  })

  // Mutations
  const updateWorkspaceMutation = useMutation({
    mutationFn: (payload: WorkspaceUpdatePayload) => workspaceApi.update(id!, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workspaces"] })
      void queryClient.invalidateQueries({ queryKey: ["workspaces", id] })
      setError(null)
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể cập nhật workspace.")),
  })

  const deleteWorkspaceMutation = useMutation({
    mutationFn: () => workspaceApi.delete(id!),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["workspaces"] })
      navigate("/workspaces", { replace: true })
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể xóa workspace.")),
  })

  const createFolderMutation = useMutation({
    mutationFn: (payload: FolderCreatePayload) => folderApi.create(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["folders", id] })
      void queryClient.invalidateQueries({ queryKey: ["workspaces", id] })
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể tạo thư mục.")),
  })

  const updateFolderMutation = useMutation({
    mutationFn: ({ folderId, payload }: { folderId: string; payload: FolderUpdatePayload }) =>
      folderApi.update(folderId, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["folders", id] })
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể cập nhật thư mục.")),
  })

  const deleteFolderMutation = useMutation({
    mutationFn: (folderId: string) => folderApi.delete(folderId),
    onSuccess: () => {
      setActiveFolder(null)
      void queryClient.invalidateQueries({ queryKey: ["folders", id] })
      void queryClient.invalidateQueries({ queryKey: ["documents", id] })
      void queryClient.invalidateQueries({ queryKey: ["workspaces", id] })
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể xóa thư mục.")),
  })

  const deleteDocumentMutation = useMutation({
    mutationFn: (docId: string) => documentApi.delete(docId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["documents", id] })
      void queryClient.invalidateQueries({ queryKey: ["workspaces", id] })
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể xóa tài liệu.")),
  })

  const bulkDeleteDocumentsMutation = useMutation({
    mutationFn: (docIds: string[]) => documentApi.bulkDelete(docIds),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["documents", id] })
      void queryClient.invalidateQueries({ queryKey: ["workspaces", id] })
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể xóa các tài liệu đã chọn.")),
  })

  // Loading skeleton state
  if (isWorkspaceLoading) {
    return (
      <div className="space-y-8 p-6 max-w-[1600px] mx-auto">
        <div className="h-40 w-full bg-muted/60 animate-pulse rounded-3xl" />
        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-muted/40 animate-pulse rounded-2xl" />
          ))}
        </div>
      </div>
    )
  }

  // Error state
  if (isError || !workspace) {
    return (
      <div className="space-y-4 p-6 max-w-2xl mx-auto">
        <Button variant="outline" asChild>
          <Link to="/workspaces">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Quay lại Workspaces
          </Link>
        </Button>
        <Card className="border-destructive/30 bg-destructive/5 rounded-3xl">
          <CardContent className="py-8 text-center space-y-3">
            <p className="text-destructive font-semibold">Workspace không tồn tại hoặc bạn không có quyền truy cập.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background text-foreground space-y-8 p-6 md:p-8 max-w-[1600px] mx-auto">
      {/* Top Breadcrumb Navigation */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Button variant="ghost" size="sm" asChild className="gap-1.5 rounded-xl hover:text-foreground">
            <Link to="/workspaces">
              <ArrowLeft className="h-4 w-4" />
              Workspaces
            </Link>
          </Button>
          <ChevronRight className="h-3.5 w-3.5" />
          <span className="font-bold text-foreground">{workspace.name}</span>
          {activeFolder && (
            <>
              <ChevronRight className="h-3.5 w-3.5" />
              <span className="font-medium text-primary flex items-center gap-1">
                <FolderOpen className="h-3.5 w-3.5" />
                {activeFolder.name}
              </span>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="rounded-2xl border border-destructive/40 bg-destructive/10 px-4 py-3 text-xs font-semibold text-destructive">
          {error}
        </div>
      )}

      {/* 1. Hero Card */}
      <WorkspaceHero
        workspace={workspace}
        onUploadClick={() => setUploadModalOpen(true)}
        onCreateFolderClick={() => {
          setFolderToEdit(null)
          setFolderFormOpen(true)
        }}
        onStartChatClick={() => void handleStartChat()}
        onToggleDrawer={() => setIsDrawerOpen((prev) => !prev)}
        onEditClick={() => setWorkspaceFormOpen(true)}
        onDeleteClick={() => setDeleteWorkspaceOpen(true)}
      />

      {/* 2. Smart Statistics Grid */}
      <SmartStatsGrid
        documentCount={documents.length || workspace.document_count}
        folderCount={folders.length || workspace.folder_count}
        sourceCount={workspace.source_count || 1}
      />

      {/* 4. Main Split View: Content & AI Knowledge Side Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        <main className={`${isDrawerOpen ? "lg:col-span-8 xl:col-span-9" : "lg:col-span-12"} space-y-8 transition-all duration-300`}>
          {/* Folders Section */}
          <FolderSectionRedesign
            folders={folders}
            activeFolderId={activeFolder?.id}
            onSelectFolder={(folder) => setActiveFolder(folder)}
            onCreateFolderClick={() => {
              setFolderToEdit(null)
              setFolderFormOpen(true)
            }}
            onEditFolderClick={(folder) => {
              setFolderToEdit(folder)
              setFolderFormOpen(true)
            }}
            onDeleteFolderClick={(folder) => {
              setFolderToDelete(folder)
              setDeleteFolderOpen(true)
            }}
            isLoading={isFoldersLoading}
          />

          {/* Document Management Engine */}
          <DocumentEngine
            documents={documents}
            workspaceId={workspace.id}
            folderId={activeFolder?.id}
            onUploadClick={() => setUploadModalOpen(true)}
            onViewDocClick={(docId) => navigate(`/documents/${docId}`)}
            onDeleteDocClick={(docId) => deleteDocumentMutation.mutate(docId)}
            onBulkDeleteClick={(selectedIds) => bulkDeleteDocumentsMutation.mutate(selectedIds)}
            isLoading={isDocsLoading}
          />

          {/* Recent Activity Feed */}
          <ActivityTimeline workspaceId={workspace.id} />
        </main>

        {/* AI Knowledge Side Drawer */}
        {isDrawerOpen && (
          <aside className="lg:col-span-4 xl:col-span-3 sticky top-6 space-y-6">
            <AIKnowledgeDrawer
              workspaceId={workspace.id}
              onClose={() => setIsDrawerOpen(false)}
            />
          </aside>
        )}
      </div>

      {/* Dialog Modals */}
      <WorkspaceFormDialog
        open={workspaceFormOpen}
        onOpenChange={setWorkspaceFormOpen}
        workspace={workspace}
        onSubmit={async (payload) => {
          await updateWorkspaceMutation.mutateAsync(payload)
        }}
        isSubmitting={updateWorkspaceMutation.isPending}
      />

      <DeleteWorkspaceDialog
        open={deleteWorkspaceOpen}
        onOpenChange={setDeleteWorkspaceOpen}
        workspaceName={workspace.name}
        onConfirm={async () => {
          await deleteWorkspaceMutation.mutateAsync()
        }}
        isDeleting={deleteWorkspaceMutation.isPending}
      />

      <FolderFormDialog
        open={folderFormOpen}
        onOpenChange={setFolderFormOpen}
        folder={folderToEdit}
        workspaceId={workspace.id}
        onSubmit={async (payload) => {
          if (folderToEdit) {
            await updateFolderMutation.mutateAsync({ folderId: folderToEdit.id, payload })
          } else {
            await createFolderMutation.mutateAsync(payload)
          }
        }}
        isSubmitting={createFolderMutation.isPending || updateFolderMutation.isPending}
      />

      <DeleteFolderDialog
        open={deleteFolderOpen}
        onOpenChange={setDeleteFolderOpen}
        folderName={folderToDelete?.name ?? ""}
        onConfirm={async () => {
          if (folderToDelete) {
            await deleteFolderMutation.mutateAsync(folderToDelete.id)
          }
        }}
        isDeleting={deleteFolderMutation.isPending}
      />

      <UploadDocumentModal
        open={uploadModalOpen}
        onOpenChange={setUploadModalOpen}
        workspaceId={workspace.id}
        folderId={activeFolder?.id}
      />
    </div>
  )
}
