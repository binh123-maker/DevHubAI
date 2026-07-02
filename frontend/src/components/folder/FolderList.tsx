import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { Folder as FolderIcon, FileText, Briefcase, Book, Image as ImageIcon, Archive, MessageSquare, MoreVertical, Pencil, Trash2 } from "lucide-react"
import { useState } from "react"

import { getApiErrorMessage } from "@/api/axios"
import { type Folder, type FolderCreatePayload, type FolderUpdatePayload, folderApi } from "@/api/folder.api"
import { DeleteFolderDialog } from "./DeleteFolderDialog"
import { FolderFormDialog } from "./FolderFormDialog"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

const ICONS: Record<string, React.ElementType> = {
  folder: FolderIcon,
  file: FileText,
  briefcase: Briefcase,
  book: Book,
  image: ImageIcon,
  archive: Archive,
  message: MessageSquare,
}

interface FolderListProps {
  workspaceId: string
}

export function FolderList({ workspaceId }: FolderListProps) {
  const queryClient = useQueryClient()
  const [formOpen, setFormOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [selectedFolder, setSelectedFolder] = useState<Folder | null>(null)
  const [error, setError] = useState<string | null>(null)

  const { data: folders = [], isLoading } = useQuery({
    queryKey: ["folders", workspaceId],
    queryFn: async () => {
      const response = await folderApi.list(workspaceId)
      return response.data
    },
  })

  const createMutation = useMutation({
    mutationFn: (payload: FolderCreatePayload) => folderApi.create(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["folders", workspaceId] })
      setError(null)
      setFormOpen(false)
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể tạo thư mục.")),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: FolderUpdatePayload }) => folderApi.update(id, payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["folders", workspaceId] })
      setError(null)
      setFormOpen(false)
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể cập nhật thư mục.")),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => folderApi.delete(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["folders", workspaceId] })
      setError(null)
      setDeleteOpen(false)
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể xóa thư mục.")),
  })

  const handleCreate = () => {
    setSelectedFolder(null)
    setFormOpen(true)
  }

  const handleEdit = (folder: Folder) => {
    setSelectedFolder(folder)
    setFormOpen(true)
  }

  const handleDelete = (folder: Folder) => {
    setSelectedFolder(folder)
    setDeleteOpen(true)
  }

  const handleFormSubmit = async (payload: any) => {
    if (selectedFolder) {
      await updateMutation.mutateAsync({ id: selectedFolder.id, payload })
    } else {
      await createMutation.mutateAsync(payload)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Thư mục</h3>
        <Button onClick={handleCreate} size="sm">
          Tạo thư mục
        </Button>
      </div>

      {error && (
        <div className="rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {isLoading ? (
        <p className="text-sm text-muted-foreground">Đang tải...</p>
      ) : folders.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center">
          <FolderIcon className="mb-2 h-10 w-10 text-muted-foreground" />
          <h3 className="mb-1 font-medium">Chưa có thư mục nào</h3>
          <p className="text-sm text-muted-foreground">Tạo thư mục để sắp xếp tài liệu của bạn</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          {folders.map((folder) => {
            const Icon = ICONS[folder.icon] || FolderIcon;
            return (
            <Card key={folder.id} className="group relative overflow-hidden hover:border-primary/50 hover:bg-muted/50 transition-colors" style={{ borderTop: `3px solid ${folder.color}` }}>
              <CardContent className="p-4 flex items-start justify-between">
                <div className="flex items-start gap-3 overflow-hidden">
                  <div className="p-2 rounded-lg shrink-0 mt-0.5" style={{ backgroundColor: `${folder.color}15` }}>
                    <Icon className="h-5 w-5" style={{ color: folder.color }} />
                  </div>
                  <div className="overflow-hidden">
                    <p className="truncate font-medium leading-none" title={folder.name}>
                      {folder.name}
                    </p>
                    {folder.description && (
                      <p className="mt-1 truncate text-xs text-muted-foreground" title={folder.description}>
                        {folder.description}
                      </p>
                    )}
                  </div>
                </div>
                
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon" className="h-8 w-8 -mr-2 -mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreVertical className="h-4 w-4" />
                      <span className="sr-only">Menu</span>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => handleEdit(folder)}>
                      <Pencil className="mr-2 h-4 w-4" />
                      Chỉnh sửa
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleDelete(folder)} className="text-destructive focus:text-destructive">
                      <Trash2 className="mr-2 h-4 w-4" />
                      Xóa
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </CardContent>
            </Card>
            )
          })}
        </div>
      )}

      <FolderFormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        folder={selectedFolder}
        workspaceId={workspaceId}
        onSubmit={handleFormSubmit}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
      />

      {selectedFolder && (
        <DeleteFolderDialog
          open={deleteOpen}
          onOpenChange={setDeleteOpen}
          folderName={selectedFolder.name}
          onConfirm={async () => {
            await deleteMutation.mutateAsync(selectedFolder.id)
          }}
          isDeleting={deleteMutation.isPending}
        />
      )}
    </div>
  )
}
