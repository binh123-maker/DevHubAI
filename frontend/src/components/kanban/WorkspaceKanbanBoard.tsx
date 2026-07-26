import { useState, useMemo, useEffect } from "react"

import { DragDropContext, DropResult } from "@hello-pangea/dnd"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { KanbanColumn, COLUMN_CONFIGS } from "./KanbanColumn"
import { KanbanFilterBar, SortOption } from "./KanbanFilterBar"
import { documentApi, Document, KanbanStatus } from "@/api/document.api"
import { FileUp, RotateCcw, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"

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
}

export function WorkspaceKanbanBoard({
  documents,
  workspaces,
  folders,
  onUploadClick,
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

    // Optimistically update local state immediately
    const nowIso = new Date().toISOString()
    const updatedDocs = localDocs.map((doc) => {
      if (doc.id === draggableId) {
        return {
          ...doc,
          kanban_status: toStatus,
          kanban_updated_at: nowIso,
        }
      }
      return doc
    })

    setLocalDocs(updatedDocs)

    // Show Toast with Undo Callback
    setToast({
      id: Date.now().toString(),
      documentId: draggableId,
      docTitle: targetDoc.title,
      fromStatus,
      toStatus,
    })

    // Perform API update
    updateKanbanMutation.mutate({ id: draggableId, status: toStatus })
  }


  // Undo status change handler
  const handleUndo = () => {
    if (!toast) return

    const { documentId, fromStatus } = toast
    // Revert local state
    setLocalDocs((prev) =>
      prev.map((doc) => {
        if (doc.id === documentId) {
          return {
            ...doc,
            kanban_status: fromStatus,
            kanban_updated_at: new Date().toISOString(),
          }
        }
        return doc
      })
    )

    // Revert API state
    updateKanbanMutation.mutate({ id: documentId, status: fromStatus })
    setToast(null)
  }

  // Filter & Sort Logic
  const filteredDocuments = useMemo(() => {
    return localDocs
      .filter((doc) => {
        // Workspace filter
        if (selectedWorkspaceId !== "all" && doc.workspace_id !== selectedWorkspaceId) {
          return false
        }
        // Folder filter
        if (selectedFolderId !== "all" && doc.folder_id !== selectedFolderId) {
          return false
        }
        // Search query
        if (searchQuery.trim() !== "") {
          const q = searchQuery.toLowerCase()
          const matchTitle = doc.title.toLowerCase().includes(q)
          const matchDesc = doc.description?.toLowerCase().includes(q) || false
          if (!matchTitle && !matchDesc) return false
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
          const timeA = new Date(a.kanban_updated_at || a.updated_at).getTime()
          const timeB = new Date(b.kanban_updated_at || b.updated_at).getTime()
          return timeB - timeA
        }
        if (sortBy === "alphabetical") {
          return a.title.localeCompare(b.title)
        }
        return 0
      })
  }, [localDocs, selectedWorkspaceId, selectedFolderId, searchQuery, sortBy])

  // Group by Kanban Status
  const columnsData = useMemo(() => {
    const columns: Record<KanbanStatus, Document[]> = {
      new: [],
      learning: [],
      completed: [],
      archived: [],
    }

    filteredDocuments.forEach((doc) => {
      const status = doc.kanban_status || "new"
      if (columns[status]) {
        columns[status].push(doc)
      } else {
        columns.new.push(doc)
      }
    })

    return columns
  }, [filteredDocuments])

  const totalFilteredCount = filteredDocuments.length

  return (
    <div className="space-y-4">
      {/* Filter & Search Controls */}
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

      {/* Toast Notification with Undo */}
      {toast && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center justify-between gap-4 rounded-xl border border-primary/40 bg-card p-4 shadow-2xl backdrop-blur-md animate-in slide-in-from-bottom-5 duration-200">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-primary">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <p className="text-xs font-semibold text-foreground">
                Đã chuyển &quot;{toast.docTitle}&quot; sang{" "}
                <span className="text-primary font-bold">
                  {COLUMN_CONFIGS[toast.toStatus].title}
                </span>
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleUndo}
              className="h-8 gap-1 text-xs border-primary/30 hover:bg-primary/10"
            >
              <RotateCcw className="h-3.5 w-3.5" />
              Hoàn tác
            </Button>
            <button
              onClick={() => setToast(null)}
              className="text-xs text-muted-foreground hover:text-foreground px-1"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      {/* Main Empty State if 0 documents overall */}
      {localDocs.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 px-4 text-center rounded-2xl border border-dashed border-border/60 bg-card/40 backdrop-blur-sm">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-primary mb-4">
            <FileUp className="h-8 w-8" />
          </div>
          <h3 className="text-xl font-bold tracking-tight">Chưa có tài liệu nào</h3>
          <p className="mt-2 text-sm text-muted-foreground max-w-md">
            Tải lên tài liệu đầu tiên của bạn để bắt đầu tổ chức kiến thức trên bảng Kanban.
          </p>
          {onUploadClick && (
            <Button onClick={onUploadClick} className="mt-6 gap-2">
              <FileUp className="h-4 w-4" />
              Tải lên tài liệu ngay
            </Button>
          )}
        </div>
      ) : totalFilteredCount === 0 ? (
        <div className="flex flex-col items-center justify-center py-12 px-4 text-center rounded-xl border border-border/50 bg-card/40">
          <p className="text-sm font-medium text-muted-foreground">Không tìm thấy tài liệu phù hợp với bộ lọc</p>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSearchQuery("")
              setSelectedWorkspaceId("all")
              setSelectedFolderId("all")
            }}
            className="mt-2 text-xs"
          >
            Xóa các bộ lọc tìm kiếm
          </Button>

        </div>
      ) : (
        /* Responsive Kanban Board Layout */
        <DragDropContext onDragEnd={handleDragEnd}>
          <div className="overflow-x-auto pb-4 scrollbar-thin">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 min-w-full lg:min-w-[1000px]">
              {(["new", "learning", "completed", "archived"] as KanbanStatus[]).map((statusKey) => (
                <KanbanColumn
                  key={statusKey}
                  columnId={statusKey}
                  documents={columnsData[statusKey]}
                  workspaceMap={workspaceMap}
                  folderMap={folderMap}
                />
              ))}
            </div>
          </div>
        </DragDropContext>
      )}
    </div>
  )
}
