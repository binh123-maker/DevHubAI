import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { format } from "date-fns"
import { vi } from "date-fns/locale"
import { FileText, MoreHorizontal, Trash2, Pencil, Loader2, AlertCircle, CheckCircle, ExternalLink, X, Search, Filter, ArrowDownUp, ArrowUp, ArrowDown } from "lucide-react"
import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

import { getApiErrorMessage } from "@/api/axios"
import { type Document, documentApi } from "@/api/document.api"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { UploadDocumentModal } from "./UploadDocumentModal"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface DocumentListProps {
  workspaceId: string
  folderId?: string
}

export function DocumentList({ workspaceId, folderId }: DocumentListProps) {
  const queryClient = useQueryClient()
  const [uploadOpen, setUploadOpen] = useState(false)
  const [docToDelete, setDocToDelete] = useState<Document | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // ── Search, Filter & Sort state ──────────────────────────────────────────
  const [searchQuery, setSearchQuery] = useState("")
  const [typeFilter, setTypeFilter] = useState("all")
  const [sortBy, setSortBy] = useState<"name" | "date" | "size" | "status">("date")
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc")

  // ── Rename state ──────────────────────────────────────────────────────────
  const [docToRename, setDocToRename] = useState<Document | null>(null)
  const [renameTitle, setRenameTitle] = useState("")
  const [renameDescription, setRenameDescription] = useState("")
  const [titleError, setTitleError] = useState<string | null>(null)

  function openRenameModal(doc: Document) {
    setDocToRename(doc)
    setRenameTitle(doc.title)
    setRenameDescription(doc.description ?? "")
    setTitleError(null)
    setError(null)
    setSuccessMessage(null)
  }

  function closeRenameModal() {
    setDocToRename(null)
    setTitleError(null)
  }

  // ── Selection state ──────────────────────────────────────────────────────
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())
  const [bulkDeleteOpen, setBulkDeleteOpen] = useState(false)

  // Auto-dismiss success banner after 4 seconds
  useEffect(() => {
    if (!successMessage) return
    const timer = setTimeout(() => setSuccessMessage(null), 4000)
    return () => clearTimeout(timer)
  }, [successMessage])

  const { data: documents = [], isLoading } = useQuery({
    queryKey: ["documents", workspaceId, folderId],
    queryFn: async () => {
      const response = await documentApi.list(workspaceId, folderId)
      return response.data
    },
    // Poll every 3 seconds if there are documents currently processing
    refetchInterval: (query) => {
      const docs = query.state.data as Document[] | undefined;
      const needsPolling = docs?.some((d) => d.status === "UPLOADING" || d.status === "PROCESSING")
      return needsPolling ? 3000 : false
    },
  })

  // ── Single delete mutation (unchanged) ───────────────────────────────────
  const deleteMutation = useMutation({
    mutationFn: (id: string) => documentApi.delete(id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["documents", workspaceId] })
      void queryClient.invalidateQueries({ queryKey: ["workspaces", workspaceId] })
      setDocToDelete(null)
      setError(null)
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể xóa tài liệu.")),
  })

  // ── Rename mutation ───────────────────────────────────────────────────────
  const renameMutation = useMutation({
    mutationFn: ({ id, title, description }: { id: string; title: string; description: string | null }) =>
      documentApi.update(id, { title, description }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["documents", workspaceId] })
      closeRenameModal()
      setError(null)
      setSuccessMessage("Tên tài liệu đã được cập nhật thành công.")
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể đổi tên tài liệu.")),
  })

  function handleRenameSave() {
    const trimmed = renameTitle.trim()
    if (!trimmed) {
      setTitleError("Tên không được để trống.")
      return
    }
    if (trimmed.length > 255) {
      setTitleError("Tên không được vượt quá 255 ký tự.")
      return
    }
    setTitleError(null)
    if (!docToRename) return
    renameMutation.mutate({
      id: docToRename.id,
      title: trimmed,
      description: renameDescription.trim() || null,
    })
  }

  // ── Bulk delete mutation ─────────────────────────────────────────────────
  const bulkDeleteMutation = useMutation({
    mutationFn: (ids: string[]) => documentApi.bulkDelete(ids),
    onSuccess: (_data, ids) => {
      void queryClient.invalidateQueries({ queryKey: ["documents", workspaceId] })
      void queryClient.invalidateQueries({ queryKey: ["workspaces", workspaceId] })
      setSelectedIds(new Set())
      setBulkDeleteOpen(false)
      setError(null)
      setSuccessMessage(`${ids.length} tài liệu đã được xóa thành công.`)
    },
    onError: (err) => setError(getApiErrorMessage(err, "Không thể xóa các tài liệu đã chọn.")),
  })

  // ── Data Processing (Filter & Sort) ──────────────────────────────────────
  const uniqueFileTypes = Array.from(new Set(documents.map(d => d.file_type.toLowerCase()))).sort()

  const filteredAndSortedDocuments = documents
    .filter((doc) => {
      const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        doc.file_name.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesType = typeFilter === "all" || doc.file_type.toLowerCase() === typeFilter
      return matchesSearch && matchesType
    })
    .sort((a, b) => {
      let comparison = 0
      if (sortBy === "name") {
        comparison = a.title.localeCompare(b.title)
      } else if (sortBy === "date") {
        comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      } else if (sortBy === "size") {
        comparison = a.file_size - b.file_size
      } else if (sortBy === "status") {
        comparison = a.status.localeCompare(b.status)
      }
      return sortOrder === "asc" ? comparison : -comparison
    })

  // ── Selection helpers ────────────────────────────────────────────────────
  const allSelected = filteredAndSortedDocuments.length > 0 && selectedIds.size === filteredAndSortedDocuments.length
  const someSelected = selectedIds.size > 0 && !allSelected

  function toggleSelectAll() {
    setSuccessMessage(null)
    if (allSelected) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(filteredAndSortedDocuments.map((d) => d.id)))
    }
  }

  function toggleRow(id: string) {
    setSuccessMessage(null)
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  function clearSelection() {
    setSelectedIds(new Set())
  }

  // ── Utilities (unchanged) ────────────────────────────────────────────────
  function formatBytes(bytes: number, decimals = 2) {
    if (!+bytes) return '0 Bytes'
    const k = 1024
    const dm = decimals < 0 ? 0 : decimals
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "UPLOADING":
        return <Badge variant="outline" className="bg-yellow-50 text-yellow-600 border-yellow-200"><Loader2 className="mr-1 h-3 w-3 animate-spin" /> Đang tải lên</Badge>
      case "PROCESSING":
        return <Badge variant="outline" className="bg-blue-50 text-blue-600 border-blue-200"><Loader2 className="mr-1 h-3 w-3 animate-spin" /> Đang xử lý</Badge>
      case "PROCESSED":
        return <Badge variant="outline" className="bg-green-50 text-green-600 border-green-200"><CheckCircle className="mr-1 h-3 w-3" /> Đã xử lý</Badge>
      case "FAILED":
        return <Badge variant="destructive"><AlertCircle className="mr-1 h-3 w-3" /> Thất bại</Badge>
      default:
        return <Badge variant="secondary">{status}</Badge>
    }
  }

  const selectedCount = selectedIds.size

  return (
    <div className="space-y-4">
      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Tài liệu</h3>
        <Button onClick={() => setUploadOpen(true)} size="sm">
          Tải lên tài liệu
        </Button>
      </div>

      {/* ── Error banner ───────────────────────────────────────────────── */}
      {error && (
        <div className="rounded-md border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {/* ── Success banner (auto-dismisses after 4 s) ──────────────────── */}
      {successMessage && (
        <div className="rounded-md border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700 animate-in fade-in slide-in-from-top-1 duration-200">
          <CheckCircle className="mr-2 inline-block h-4 w-4" />
          {successMessage}
        </div>
      )}

      {/* ── Search, Filter & Sort Toolbar ──────────────────────────────── */}
      {documents.length > 0 && (
        <div className="flex flex-col md:flex-row gap-3 items-start md:items-center justify-between bg-muted/20 p-3 rounded-lg border border-border/50">
          <div className="relative w-full md:w-64 shrink-0">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Tìm kiếm tài liệu..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-8 bg-background h-9"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
            <div className="flex items-center gap-2 text-sm border rounded-md bg-background px-3 h-9 shrink-0 focus-within:ring-1 focus-within:ring-ring">
              <Filter className="h-4 w-4 text-muted-foreground" />
              <select
                className="bg-transparent outline-none text-sm cursor-pointer w-full"
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
              >
                <option value="all">Tất cả định dạng</option>
                {uniqueFileTypes.map(type => (
                  <option key={type} value={type}>{type.toUpperCase()}</option>
                ))}
              </select>
            </div>

            <div className="flex items-center gap-2 text-sm border rounded-md bg-background px-3 h-9 shrink-0 focus-within:ring-1 focus-within:ring-ring">
              <ArrowDownUp className="h-4 w-4 text-muted-foreground" />
              <select
                className="bg-transparent outline-none text-sm cursor-pointer w-full"
                value={sortBy}
                onChange={(e: any) => setSortBy(e.target.value)}
              >
                <option value="date">Ngày tải lên</option>
                <option value="name">Tên tài liệu</option>
                <option value="size">Kích thước</option>
                <option value="status">Trạng thái</option>
              </select>
            </div>

            <Button
              variant="outline"
              size="icon"
              className="h-9 w-9 shrink-0"
              onClick={() => setSortOrder(prev => prev === "asc" ? "desc" : "asc")}
              title={sortOrder === "asc" ? "Tăng dần" : "Giảm dần"}
            >
              {sortOrder === "asc" ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />}
            </Button>
          </div>
        </div>
      )}

      {/* ── Selection toolbar ──────────────────────────────────────────── */}
      {selectedCount > 0 && (
        <div className="flex items-center justify-between rounded-md border border-primary/20 bg-primary/5 px-4 py-2 text-sm animate-in fade-in slide-in-from-top-1 duration-200">
          <span className="font-medium text-primary">
            {selectedCount} tài liệu được chọn
          </span>
          <div className="flex items-center gap-2">
            <Button
              variant="destructive"
              size="sm"
              onClick={() => setBulkDeleteOpen(true)}
              disabled={bulkDeleteMutation.isPending}
            >
              <Trash2 className="mr-1.5 h-3.5 w-3.5" />
              Xóa đã chọn
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={clearSelection}
              disabled={bulkDeleteMutation.isPending}
            >
              <X className="mr-1.5 h-3.5 w-3.5" />
              Huỷ chọn
            </Button>
          </div>
        </div>
      )}

      {/* ── Document table / empty state ───────────────────────────────── */}
      {isLoading ? (
        <p className="text-sm text-muted-foreground">Đang tải tài liệu...</p>
      ) : documents.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center">
          <FileText className="mb-2 h-10 w-10 text-muted-foreground" />
          <h3 className="mb-1 font-medium">Chưa có tài liệu nào</h3>
          <p className="text-sm text-muted-foreground mb-4">Tải lên các file PDF, DOCX, TXT để bắt đầu.</p>
          <Button variant="outline" onClick={() => setUploadOpen(true)}>Tải lên ngay</Button>
        </div>
      ) : filteredAndSortedDocuments.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center bg-muted/10">
          <Search className="mb-2 h-10 w-10 text-muted-foreground/50" />
          <h3 className="mb-1 font-medium">Không tìm thấy kết quả</h3>
          <p className="text-sm text-muted-foreground mb-4">Thử thay đổi từ khóa hoặc bộ lọc của bạn.</p>
          <Button variant="outline" onClick={() => { setSearchQuery(""); setTypeFilter("all") }}>Xóa bộ lọc</Button>
        </div>
      ) : (
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                {/* Select-all checkbox */}
                <TableHead className="w-[44px] pr-0">
                  <input
                    type="checkbox"
                    aria-label="Chọn tất cả"
                    checked={allSelected}
                    disabled={filteredAndSortedDocuments.length === 0}
                    ref={(el) => { if (el) el.indeterminate = someSelected }}
                    onChange={toggleSelectAll}
                    className="h-4 w-4 cursor-pointer rounded border-input accent-primary disabled:cursor-not-allowed disabled:opacity-40"
                  />
                </TableHead>
                <TableHead>Tên tài liệu</TableHead>
                <TableHead>Trạng thái</TableHead>
                <TableHead>Loại</TableHead>
                <TableHead>Kích thước</TableHead>
                <TableHead>Ngày tải lên</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAndSortedDocuments.map((doc) => (
                <TableRow
                  key={doc.id}
                  data-state={selectedIds.has(doc.id) ? "selected" : undefined}
                  className={selectedIds.has(doc.id) ? "bg-primary/5" : undefined}
                >
                  {/* Per-row checkbox */}
                  <TableCell className="pr-0">
                    <input
                      type="checkbox"
                      aria-label={`Chọn ${doc.title}`}
                      checked={selectedIds.has(doc.id)}
                      onChange={() => toggleRow(doc.id)}
                      className="h-4 w-4 cursor-pointer rounded border-input accent-primary"
                    />
                  </TableCell>
                  <TableCell className="font-medium">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
                      <Link
                        to={`/documents/${doc.id}`}
                        className="truncate max-w-[200px] md:max-w-[300px] hover:underline hover:text-primary"
                        title={doc.title}
                      >
                        {doc.title}
                      </Link>
                    </div>
                  </TableCell>
                  <TableCell>
                    {getStatusBadge(doc.status)}
                  </TableCell>
                  <TableCell className="uppercase text-xs font-semibold text-muted-foreground">
                    {doc.file_type}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {formatBytes(doc.file_size)}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {format(new Date(doc.created_at), "dd MMM yyyy, HH:mm", { locale: vi })}
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem asChild>
                          <Link to={`/documents/${doc.id}`}>
                            <ExternalLink className="mr-2 h-4 w-4" />
                            Xem chi tiết
                          </Link>
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          onClick={() => openRenameModal(doc)}
                        >
                          <Pencil className="mr-2 h-4 w-4" />
                          Đổi tên
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-destructive focus:text-destructive"
                          onClick={() => setDocToDelete(doc)}
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Xóa
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}

      <UploadDocumentModal
        open={uploadOpen}
        onOpenChange={setUploadOpen}
        workspaceId={workspaceId}
        folderId={folderId}
      />

      {/* ── Rename modal ─────────────────────────────────────────────────── */}
      <Dialog open={!!docToRename} onOpenChange={(open) => !open && closeRenameModal()}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Đổi tên tài liệu</DialogTitle>
            <DialogDescription>
              Cập nhật tên và mô tả cho tài liệu này.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-2">
            <div className="space-y-1.5">
              <Label htmlFor="rename-title">Tên tài liệu <span className="text-destructive">*</span></Label>
              <Input
                id="rename-title"
                value={renameTitle}
                maxLength={255}
                onChange={(e) => {
                  setRenameTitle(e.target.value)
                  if (titleError) setTitleError(null)
                }}
                onKeyDown={(e) => e.key === "Enter" && handleRenameSave()}
                disabled={renameMutation.isPending}
                placeholder="Tên tài liệu"
                autoFocus
              />
              {titleError && (
                <p className="text-xs text-destructive">{titleError}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="rename-description">Mô tả <span className="text-muted-foreground text-xs">(tùy chọn)</span></Label>
              <Input
                id="rename-description"
                value={renameDescription}
                onChange={(e) => setRenameDescription(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleRenameSave()}
                disabled={renameMutation.isPending}
                placeholder="Mô tả ngắn về tài liệu"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={closeRenameModal} disabled={renameMutation.isPending}>
              Huỷ
            </Button>
            <Button onClick={handleRenameSave} disabled={renameMutation.isPending}>
              {renameMutation.isPending ? "Đang lưu..." : "Lưu"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Single delete confirm dialog (unchanged behaviour) ─────────── */}
      <Dialog open={!!docToDelete} onOpenChange={(open) => !open && setDocToDelete(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Xóa tài liệu</DialogTitle>
            <DialogDescription>
              Bạn có chắc chắn muốn xóa tài liệu <strong className="text-foreground">{docToDelete?.title}</strong>?{" "}
              Hành động này không thể hoàn tác và file vật lý cũng sẽ bị xóa.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDocToDelete(null)} disabled={deleteMutation.isPending}>
              Huỷ
            </Button>
            <Button
              variant="destructive"
              onClick={() => docToDelete && deleteMutation.mutate(docToDelete.id)}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? "Đang xóa..." : "Xóa tài liệu"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* ── Bulk delete confirm dialog ─────────────────────────────────── */}
      <Dialog open={bulkDeleteOpen} onOpenChange={(open) => !open && setBulkDeleteOpen(false)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Xóa {selectedCount} tài liệu</DialogTitle>
            <DialogDescription>
              Bạn có chắc chắn muốn xóa <strong className="text-foreground">{selectedCount} tài liệu</strong> đã chọn?{" "}
              Hành động này không thể hoàn tác và các file vật lý cũng sẽ bị xóa.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setBulkDeleteOpen(false)}
              disabled={bulkDeleteMutation.isPending}
            >
              Huỷ
            </Button>
            <Button
              variant="destructive"
              onClick={() => bulkDeleteMutation.mutate([...selectedIds])}
              disabled={bulkDeleteMutation.isPending}
            >
              {bulkDeleteMutation.isPending ? "Đang xóa..." : `Xóa ${selectedCount} tài liệu`}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
