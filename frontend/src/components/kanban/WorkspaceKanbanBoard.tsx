import { useState, useMemo, useEffect } from "react"
import { DragDropContext, DropResult } from "@hello-pangea/dnd"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { KanbanColumn, COLUMN_CONFIGS } from "./KanbanColumn"
import { KanbanFilterBar, SortOption } from "./KanbanFilterBar"
import { KanbanSpeedDial } from "./KanbanSpeedDial"
import { documentApi, Document, KanbanStatus } from "@/api/document.api"
import { FileUp, RotateCcw, FolderPlus, Globe, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"

interface ToastInfo {
  id: string
  documentId: string
  docTitle: string
  fromStatus: KanbanStatus
  toStatus: KanbanStatus
}

interface WorkspaceKanbanBoardProps {
  documents: Document[]
  workspaces: Array<{ id: string; name: string }>
  folders: Array<{ id: string; name: string; workspace_id: string }>
  onUploadClick?: () => void
  onCreateWorkspaceClick?: () => void
}

export function WorkspaceKanbanBoard({
  documents,
  workspaces,
  folders,
  onUploadClick,
  onCreateWorkspaceClick,
}: WorkspaceKanbanBoardProps) {
  const queryClient = useQueryClient()

  // Client-side filter & sort states
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState("all")
  const [selectedFolderId, setSelectedFolderId] = useState("all")
  const [sortBy, setSortBy] = useState<SortOption>("newest")

  // Local optimistic override for documents
  const [localDocs, setLocalDocs] = useState<Document[]>(documents)

  // Sync props to localDocs when documents prop updates from query
  useEffect(() => {
    setLocalDocs(documents)
  }, [documents])

  // Toast state with Undo action
  const [toast, setToast] = useState<ToastInfo | null>(null)

  // Maps for workspace and folder names
  const workspaceMap = useMemo(() => {
    const map: Record<string, string> = {}
    workspaces.forEach((w) => {
      map[w.id] = w.name
    })
    return map
  }, [workspaces])

  const folderMap = useMemo(() => {
    const map: Record<string, string> = {}
    folders.forEach((f) => {
      map[f.id] = f.name
    })
    return map
  }, [folders])

  // Update Kanban Status Mutation
  const updateKanbanMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: KanbanStatus }) =>
      documentApi.updateKanbanStatus(id, status),

    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["documents"] })
      void queryClient.invalidateQueries({ queryKey: ["dashboardOverview"] })
    },
    onError: () => {
      // Revert local state on error
      setLocalDocs(documents)
    },
  })

  // Handle Drag & Drop End
  const handleDragEnd = (result: DropResult) => {
    const { destination, source, draggableId } = result

    if (!destination) return
    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return
    }

    const fromStatus = source.droppableId as KanbanStatus
    const toStatus = destination.droppableId as KanbanStatus
    const targetDoc = localDocs.find((d) => d.id === draggableId)

    if (!targetDoc) return

    // 1. Optimistically update local state immediately
    const updatedDocs = localDocs.map((doc) => {
      if (doc.id === draggableId) {
        return {
          ...doc,
          kanban_status: toStatus,
          kanban_updated_at: new Date().toISOString(),
        }
      }
      return doc
    })

    setLocalDocs(updatedDocs)

    // 2. Trigger API call in background
    updateKanbanMutation.mutate({ id: draggableId, status: toStatus })

    // 3. Show Toast notification with Undo action
    setToast({

      id: Date.now().toString(),
      documentId: draggableId,
      docTitle: targetDoc.title,
      fromStatus,
      toStatus,
    })
  }

  // Handle Undo
  const handleUndo = () => {
    if (!toast) return

    // Revert local state
    const revertedDocs = localDocs.map((doc) => {
      if (doc.id === toast.documentId) {
        return {
          ...doc,
          kanban_status: toast.fromStatus,
          kanban_updated_at: new Date().toISOString(),
        }
      }
      return doc
    })

    setLocalDocs(revertedDocs)

    // Trigger API call to revert status in backend
    updateKanbanMutation.mutate({ id: toast.documentId, status: toast.fromStatus })

    // Clear Toast
    setToast(null)
  }

  // Filter & Sort Logic
  const filteredAndSortedDocs = useMemo(() => {
    return localDocs
      .filter((doc) => {
        // Search query
        if (searchQuery.trim() !== "") {
          const q = searchQuery.toLowerCase()
          const matchesTitle = doc.title.toLowerCase().includes(q)
          const matchesDesc = doc.description?.toLowerCase().includes(q)
          if (!matchesTitle && !matchesDesc) return false
        }

        // Workspace filter
        if (selectedWorkspaceId !== "all" && doc.workspace_id !== selectedWorkspaceId) {
          return false
        }

        // Folder filter
        if (selectedFolderId !== "all" && doc.folder_id !== selectedFolderId) {
          return false
        }

        return true
      })
      .sort((a, b) => {
        if (sortBy === "newest") {
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        }
        if (sortBy === "oldest") {
          return new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        }
        if (sortBy === "recently_updated") {
          const aTime = a.kanban_updated_at ? new Date(a.kanban_updated_at).getTime() : new Date(a.created_at).getTime()
          const bTime = b.kanban_updated_at ? new Date(b.kanban_updated_at).getTime() : new Date(b.created_at).getTime()
          return bTime - aTime
        }
        if (sortBy === "alphabetical") {
          return a.title.localeCompare(b.title)
        }
        return 0
      })
  }, [localDocs, searchQuery, selectedWorkspaceId, selectedFolderId, sortBy])

  // Group documents by KanbanStatus column
  const columnsData = useMemo(() => {
    const map: Record<KanbanStatus, Document[]> = {
      new: [],
      learning: [],
      completed: [],
      archived: [],
    }

    filteredAndSortedDocs.forEach((doc) => {
      const status = doc.kanban_status || "new"
      if (map[status]) {
        map[status].push(doc)
      } else {
        map["new"].push(doc)
      }
    })

    return map
  }, [filteredAndSortedDocs])

  return (
    <div className="space-y-4 relative">
      {/* Action Shortcuts Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-card/60 border border-border/50 rounded-xl p-3 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <Button size="sm" onClick={() => onUploadClick?.()} className="gap-1.5 text-xs shadow-xs">
            <FileUp className="h-3.5 w-3.5" />
            Tải lên Tài liệu
          </Button>
          <Button variant="outline" size="sm" onClick={() => onUploadClick?.()} className="gap-1.5 text-xs">
            <Globe className="h-3.5 w-3.5 text-emerald-500" />
            Nhập URL
          </Button>
          <Button variant="ghost" size="sm" onClick={() => onCreateWorkspaceClick?.()} className="gap-1.5 text-xs">
            <FolderPlus className="h-3.5 w-3.5 text-amber-500" />
            Tạo Workspace
          </Button>
        </div>

        {/* Filter Bar Controls */}
        <KanbanFilterBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedWorkspaceId={selectedWorkspaceId}
          onWorkspaceChange={setSelectedWorkspaceId}
          selectedFolderId={selectedFolderId}
          onFolderChange={setSelectedFolderId}
          sortBy={sortBy}
          onSortChange={setSortBy}
          workspaces={workspaces}
          folders={folders}
          onClearFilters={() => {
            setSearchQuery("")
            setSelectedWorkspaceId("all")
            setSelectedFolderId("all")
            setSortBy("newest")
          }}
        />
      </div>

      {/* Empty State when no workspace or documents exist */}
      {workspaces.length === 0 ? (
        <Card className="border-dashed border-2 border-border/80 bg-card/40 p-8 text-center">
          <CardContent className="space-y-4 py-6">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-500/10 text-amber-500 mx-auto">
              <FolderPlus className="h-7 w-7" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-bold text-foreground">Chưa có Workspace nào</h3>
              <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                Tạo Workspace đầu tiên để nhóm tài liệu và bắt đầu quản lý tiến độ học tập Kanban.
              </p>
            </div>
            <div className="flex justify-center gap-2 pt-2">
              <Button size="sm" onClick={() => onCreateWorkspaceClick?.()} className="gap-1.5 text-xs">
                <Plus className="h-4 w-4" />
                Tạo Workspace mới
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : documents.length === 0 ? (
        <Card className="border-dashed border-2 border-border/80 bg-card/40 p-8 text-center">
          <CardContent className="space-y-4 py-6">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary mx-auto">
              <FileUp className="h-7 w-7" />
            </div>
            <div className="space-y-1">
              <h3 className="text-base font-bold text-foreground">Chưa có tài liệu trong Kho tri thức</h3>
              <p className="text-xs text-muted-foreground max-w-sm mx-auto">
                Tải tệp tin PDF, DOCX, TXT hoặc bài viết URL để hiển thị trên bảng tiến độ Kanban.
              </p>
            </div>
            <div className="flex justify-center gap-2 pt-2">
              <Button size="sm" onClick={() => onUploadClick?.()} className="gap-1.5 text-xs">
                <FileUp className="h-4 w-4" />
                Tải lên tài liệu ngay
              </Button>
            </div>
          </CardContent>
        </Card>
      ) : (
        /* Drag & Drop Context */
        <DragDropContext onDragEnd={handleDragEnd}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {(Object.keys(COLUMN_CONFIGS) as KanbanStatus[]).map((status) => (
              <KanbanColumn
                key={status}
                columnId={status}
                documents={columnsData[status]}
                workspaceMap={workspaceMap}
                folderMap={folderMap}
              />
            ))}
          </div>
        </DragDropContext>
      )}


      {/* Floating Speed Dial FAB */}
      <KanbanSpeedDial
        onUploadClick={() => onUploadClick?.()}
        onImportUrlClick={() => onUploadClick?.()}
        onCreateWorkspaceClick={() => onCreateWorkspaceClick?.()}
      />

      {/* Toast Notification with Undo Action */}
      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center justify-between gap-4 rounded-xl border border-primary/40 bg-card/95 px-4 py-3 text-xs font-semibold shadow-2xl backdrop-blur-md animate-in fade-in slide-in-from-bottom-5">
          <span>
            Đã chuyển &quot;<span className="text-primary font-bold">{toast.docTitle}</span>&quot; sang cột{" "}
            <span className="font-bold">{COLUMN_CONFIGS[toast.toStatus]?.title}</span>
          </span>
          <Button
            size="sm"
            variant="ghost"
            onClick={handleUndo}
            className="h-7 gap-1 px-2.5 text-xs text-primary hover:bg-primary/10 font-bold"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            Hoàn tác (Undo)
          </Button>
        </div>
      )}
    </div>
  )
}
