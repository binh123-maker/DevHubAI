import React, { useState, useMemo } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { 
  FileText, 
  Search, 
  Filter, 
  LayoutGrid, 
  List as ListIcon, 
  Maximize2, 
  CheckSquare, 
  Square, 
  Trash2, 
  Eye, 
  FileCode, 
  FileCheck, 
  File, 
  Globe, 
  Upload, 
  AlertCircle, 
  Clock, 
  Layers
} from "lucide-react"
import { type Document } from "@/api/document.api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface DocumentEngineProps {
  documents: Document[]
  workspaceId?: string
  folderId?: string | null
  onUploadClick: () => void
  onViewDocClick: (docId: string) => void
  onDeleteDocClick: (docId: string) => void
  onBulkDeleteClick: (selectedIds: string[]) => void
  isLoading?: boolean
}

export const DocumentEngine: React.FC<DocumentEngineProps> = ({
  documents,
  onUploadClick,
  onViewDocClick,
  onDeleteDocClick,
  onBulkDeleteClick,
  isLoading = false,
}) => {
  const [searchQuery, setSearchQuery] = useState("")
  const [fileTypeFilter, setFileTypeFilter] = useState<string>("all")
  const [viewMode, setViewMode] = useState<"grid" | "list" | "compact">("grid")
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [sortBy] = useState<"recent" | "name" | "size">("recent")

  // Helper file extension icon picker
  const getFileIcon = (fileType: string, fileName: string) => {
    const ext = fileName.split(".").pop()?.toLowerCase() || ""
    if (ext === "pdf" || fileType.includes("pdf")) return <FileText className="h-5 w-5 text-red-500" />
    if (ext === "md" || ext === "markdown") return <FileCheck className="h-5 w-5 text-blue-500" />
    if (ext === "py" || ext === "ts" || ext === "js" || ext === "json" || ext === "html" || ext === "css") {
      return <FileCode className="h-5 w-5 text-emerald-500" />
    }
    if (fileType.includes("url") || fileName.startsWith("http")) return <Globe className="h-5 w-5 text-purple-500" />
    return <File className="h-5 w-5 text-slate-500" />
  }

  // Format File Size
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 B"
    const k = 1024
    const sizes = ["B", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i]
  }

  // Status Badge chip renderer
  const renderStatusBadge = (status: string) => {
    const s = status.toLowerCase()
    if (s === "completed" || s === "indexed") {
      return (
        <Badge variant="outline" className="gap-1 border-emerald-500/30 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-[11px]">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
          Đã chỉ mục
        </Badge>
      )
    }
    if (s === "processing" || s === "parsing" || s === "chunking") {
      return (
        <Badge variant="outline" className="gap-1 border-amber-500/30 bg-amber-500/10 text-amber-600 dark:text-amber-400 text-[11px]">
          <Clock className="h-3 w-3 animate-spin" />
          Đang xử lý
        </Badge>
      )
    }
    if (s === "error" || s === "failed") {
      return (
        <Badge variant="outline" className="gap-1 border-rose-500/30 bg-rose-500/10 text-rose-600 dark:text-rose-400 text-[11px]">
          <AlertCircle className="h-3 w-3" />
          Lỗi
        </Badge>
      )
    }
    return (
      <Badge variant="outline" className="gap-1 border-slate-500/30 bg-slate-500/10 text-slate-600 text-[11px]">
        Chờ xử lý
      </Badge>
    )
  }

  // Filter & Sort Logic
  const filteredDocuments = useMemo(() => {
    return documents
      .filter((doc) => {
        const matchesSearch = doc.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                              doc.file_name.toLowerCase().includes(searchQuery.toLowerCase())
        if (fileTypeFilter === "all") return matchesSearch
        if (fileTypeFilter === "pdf") return matchesSearch && doc.file_name.endsWith(".pdf")
        if (fileTypeFilter === "md") return matchesSearch && (doc.file_name.endsWith(".md") || doc.file_name.endsWith(".markdown"))
        if (fileTypeFilter === "code") return matchesSearch && (doc.file_name.endsWith(".ts") || doc.file_name.endsWith(".py") || doc.file_name.endsWith(".js") || doc.file_name.endsWith(".json"))
        return matchesSearch
      })
      .sort((a, b) => {
        if (sortBy === "name") return a.title.localeCompare(b.title)
        if (sortBy === "size") return b.file_size - a.file_size
        return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
      })
  }, [documents, searchQuery, fileTypeFilter, sortBy])

  // Selection toggle handlers
  const toggleSelectDoc = (id: string) => {
    setSelectedIds((prev) => 
      prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]
    )
  }

  const toggleSelectAll = () => {
    if (selectedIds.length === filteredDocuments.length) {
      setSelectedIds([])
    } else {
      setSelectedIds(filteredDocuments.map((d) => d.id))
    }
  }

  return (
    <div className="space-y-4">
      {/* Header bar */}
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-base font-bold text-foreground flex items-center gap-2">
            <Layers className="h-4 w-4 text-blue-500" />
            Tài liệu tri thức Workspace
          </h2>
          <Badge variant="secondary" className="rounded-full text-xs font-semibold px-2 py-0.5">
            {filteredDocuments.length}
          </Badge>
        </div>

        {/* Filters & View Switches */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Search bar */}
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Tìm kiếm tài liệu..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 h-9 rounded-xl border-border/60 bg-background/50 text-xs focus:bg-background"
            />
          </div>

          {/* Filter Pills */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm" className="h-9 gap-1.5 rounded-xl border-border/60 text-xs font-semibold">
                <Filter className="h-3.5 w-3.5 text-muted-foreground" />
                {fileTypeFilter === "all" ? "Tất cả tệp" : fileTypeFilter.toUpperCase()}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-36 rounded-xl p-1">
              <DropdownMenuItem onClick={() => setFileTypeFilter("all")} className="text-xs cursor-pointer">Tất cả tệp</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setFileTypeFilter("pdf")} className="text-xs cursor-pointer">Tài liệu PDF</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setFileTypeFilter("md")} className="text-xs cursor-pointer">Markdown</DropdownMenuItem>
              <DropdownMenuItem onClick={() => setFileTypeFilter("code")} className="text-xs cursor-pointer">Code & JSON</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          {/* View Switchers */}
          <div className="flex items-center rounded-xl border border-border/60 bg-muted/30 p-1">
            <Button
              variant="ghost"
              size="icon"
              className={`h-7 w-7 rounded-lg ${viewMode === "grid" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground"}`}
              onClick={() => setViewMode("grid")}
              title="Chế độ lưới"
            >
              <LayoutGrid className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={`h-7 w-7 rounded-lg ${viewMode === "list" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground"}`}
              onClick={() => setViewMode("list")}
              title="Chế độ danh sách"
            >
              <ListIcon className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={`h-7 w-7 rounded-lg ${viewMode === "compact" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground"}`}
              onClick={() => setViewMode("compact")}
              title="Chế độ thu gọn"
            >
              <Maximize2 className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </div>

      {/* Floating Multi-Select Bulk Action Bar */}
      <AnimatePresence>
        {selectedIds.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.98 }}
            className="flex items-center justify-between rounded-2xl border border-primary/40 bg-primary/10 backdrop-blur-md p-3 shadow-lg"
          >
            <div className="flex items-center gap-3">
              <Badge className="bg-primary text-primary-foreground font-bold px-2.5 py-0.5 rounded-lg text-xs">
                Đã chọn {selectedIds.length}
              </Badge>
              <span className="text-xs font-medium text-foreground hidden sm:inline">
                Sẵn sàng thao tác hàng loạt
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Button
                size="sm"
                variant="destructive"
                onClick={() => {
                  onBulkDeleteClick(selectedIds)
                  setSelectedIds([])
                }}
                className="gap-1.5 rounded-xl h-8 text-xs shadow-sm"
              >
                <Trash2 className="h-3.5 w-3.5" />
                Xóa hàng loạt
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setSelectedIds([])}
                className="h-8 text-xs rounded-xl"
              >
                Bỏ chọn
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Empty State */}
      {filteredDocuments.length === 0 && !isLoading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="flex flex-col items-center justify-center rounded-3xl border border-dashed border-border/80 glass-card p-10 text-center"
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10 text-primary mb-4 shadow-inner">
            <Upload className="h-8 w-8 animate-bounce" />
          </div>
          <h3 className="text-base font-bold text-foreground">Chưa có tài liệu nào</h3>
          <p className="text-xs text-muted-foreground max-w-md mt-1 mb-4">
            Tải lên các tệp PDF, DOCX, Markdown hoặc Code để cung cấp cơ sở tri thức cho DevHub AI.
          </p>
          <div className="flex items-center gap-3">
            <Button onClick={onUploadClick} className="gap-2 rounded-xl bg-primary shadow-sm">
              <Upload className="h-4 w-4" />
              Tải lên tài liệu
            </Button>
          </div>
        </motion.div>
      )}

      {/* Document Grid / List / Compact Rendering */}
      {filteredDocuments.length > 0 && (
        <AnimatePresence mode="wait">
          {viewMode === "grid" && (
            <motion.div
              key="grid"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4"
            >
              {filteredDocuments.map((doc) => {
                const isSelected = selectedIds.includes(doc.id)
                return (
                  <motion.div
                    key={doc.id}
                    whileHover={{ y: -3 }}
                    onClick={() => onViewDocClick(doc.id)}
                    className={`group relative flex flex-col justify-between overflow-hidden rounded-2xl border glass-card p-4 transition-all duration-200 cursor-pointer ${
                      isSelected 
                        ? "border-primary bg-primary/5 ring-2 ring-primary/20 shadow-md" 
                        : "border-border/60 hover:border-primary/40 hover:shadow-lg"
                    }`}
                  >
                    <div>
                      {/* Top bar with selection checkbox & status */}
                      <div className="flex items-center justify-between mb-3">
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            toggleSelectDoc(doc.id)
                          }}
                          className="text-muted-foreground hover:text-primary transition-colors"
                        >
                          {isSelected ? (
                            <CheckSquare className="h-4 w-4 text-primary" />
                          ) : (
                            <Square className="h-4 w-4 opacity-40 group-hover:opacity-100" />
                          )}
                        </button>
                        {renderStatusBadge(doc.status)}
                      </div>

                      {/* File Info */}
                      <div className="flex items-start gap-3">
                        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-muted/60 shadow-inner">
                          {getFileIcon(doc.file_type, doc.file_name)}
                        </div>
                        <div className="overflow-hidden">
                          <h4 className="text-sm font-bold text-foreground truncate group-hover:text-primary transition-colors">
                            {doc.title}
                          </h4>
                          <p className="text-[11px] text-muted-foreground truncate font-mono mt-0.5">
                            {doc.file_name}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Bottom Metadata & Actions */}
                    <div className="mt-4 flex items-center justify-between border-t border-border/30 pt-3 text-[11px] text-muted-foreground">
                      <span className="font-semibold text-foreground">{formatBytes(doc.file_size)}</span>
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 rounded-lg hover:text-primary"
                          onClick={(e) => {
                            e.stopPropagation()
                            onViewDocClick(doc.id)
                          }}
                        >
                          <Eye className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 rounded-lg hover:text-destructive"
                          onClick={(e) => {
                            e.stopPropagation()
                            onDeleteDocClick(doc.id)
                          }}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  </motion.div>
                )
              })}
            </motion.div>
          )}

          {viewMode === "list" && (
            <motion.div
              key="list"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="overflow-hidden rounded-2xl border border-border/60 glass-card"
            >
              <div className="grid grid-cols-12 gap-4 border-b border-border/60 bg-muted/40 px-4 py-3 text-xs font-bold text-muted-foreground uppercase tracking-wider">
                <div className="col-span-1 flex items-center">
                  <button onClick={toggleSelectAll}>
                    {selectedIds.length === filteredDocuments.length ? (
                      <CheckSquare className="h-4 w-4 text-primary" />
                    ) : (
                      <Square className="h-4 w-4 opacity-60" />
                    )}
                  </button>
                </div>
                <div className="col-span-5">Tên tài liệu</div>
                <div className="col-span-2">Kích thước</div>
                <div className="col-span-2">Trạng thái</div>
                <div className="col-span-2 text-right">Thao tác</div>
              </div>

              <div className="divide-y divide-border/40">
                {filteredDocuments.map((doc) => {
                  const isSelected = selectedIds.includes(doc.id)
                  return (
                    <div
                      key={doc.id}
                      onClick={() => onViewDocClick(doc.id)}
                      className={`grid grid-cols-12 gap-4 items-center px-4 py-3 text-xs transition-colors cursor-pointer ${
                        isSelected ? "bg-primary/10" : "hover:bg-muted/40"
                      }`}
                    >
                      <div className="col-span-1" onClick={(e) => e.stopPropagation()}>
                        <button onClick={() => toggleSelectDoc(doc.id)}>
                          {isSelected ? (
                            <CheckSquare className="h-4 w-4 text-primary" />
                          ) : (
                            <Square className="h-4 w-4 opacity-40 hover:opacity-100" />
                          )}
                        </button>
                      </div>
                      <div className="col-span-5 flex items-center gap-2.5 overflow-hidden">
                        {getFileIcon(doc.file_type, doc.file_name)}
                        <span className="font-bold text-foreground truncate">{doc.title}</span>
                      </div>
                      <div className="col-span-2 font-mono text-muted-foreground">
                        {formatBytes(doc.file_size)}
                      </div>
                      <div className="col-span-2">{renderStatusBadge(doc.status)}</div>
                      <div className="col-span-2 flex items-center justify-end gap-1" onClick={(e) => e.stopPropagation()}>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 rounded-lg hover:text-primary"
                          onClick={() => onViewDocClick(doc.id)}
                        >
                          <Eye className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-7 w-7 rounded-lg hover:text-destructive"
                          onClick={() => onDeleteDocClick(doc.id)}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    </div>
                  )
                })}
              </div>
            </motion.div>
          )}

          {viewMode === "compact" && (
            <motion.div
              key="compact"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="divide-y divide-border/30 rounded-2xl border border-border/60 glass-card overflow-hidden"
            >
              {filteredDocuments.map((doc) => (
                <div
                  key={doc.id}
                  onClick={() => onViewDocClick(doc.id)}
                  className="flex items-center justify-between px-4 py-2 text-xs hover:bg-muted/40 transition-colors cursor-pointer"
                >
                  <div className="flex items-center gap-3 overflow-hidden">
                    {getFileIcon(doc.file_type, doc.file_name)}
                    <span className="font-semibold text-foreground truncate">{doc.title}</span>
                    <span className="text-[11px] text-muted-foreground font-mono">({formatBytes(doc.file_size)})</span>
                  </div>
                  <div className="flex items-center gap-3">
                    {renderStatusBadge(doc.status)}
                    <Button variant="ghost" size="icon" className="h-6 w-6" onClick={(e) => { e.stopPropagation(); onDeleteDocClick(doc.id) }}>
                      <Trash2 className="h-3 w-3 text-muted-foreground hover:text-destructive" />
                    </Button>
                  </div>
                </div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>
      )}
    </div>
  )
}
