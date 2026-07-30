import React, { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { format } from "date-fns"
import { 
  Folder as FolderIcon, 
  FolderPlus, 
  MoreVertical, 
  Pencil, 
  Trash2, 
  ChevronRight, 
  LayoutGrid, 
  List as ListIcon
} from "lucide-react"
import { type Folder } from "@/api/folder.api"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

interface FolderSectionRedesignProps {
  folders: Folder[]
  activeFolderId?: string | null
  onSelectFolder: (folder: Folder | null) => void
  onCreateFolderClick: () => void
  onEditFolderClick: (folder: Folder) => void
  onDeleteFolderClick: (folder: Folder) => void
  isLoading?: boolean
}

export const FolderSectionRedesign: React.FC<FolderSectionRedesignProps> = ({
  folders,
  activeFolderId,
  onSelectFolder,
  onCreateFolderClick,
  onEditFolderClick,
  onDeleteFolderClick,
  isLoading = false,
}) => {
  const [folderView, setFolderView] = useState<"grid" | "list">("grid")

  if (isLoading) {
    return (
      <div className="space-y-3">
        <div className="h-6 w-32 bg-muted/60 animate-pulse rounded-md" />
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-muted/40 animate-pulse rounded-2xl border border-border/40" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header toolbar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h2 className="text-base font-bold text-foreground flex items-center gap-2">
            <FolderIcon className="h-4 w-4 text-indigo-500" />
            Thư mục tri thức
          </h2>
          <Badge variant="secondary" className="rounded-full text-xs font-semibold px-2 py-0.5">
            {folders.length}
          </Badge>
        </div>

        <div className="flex items-center gap-2">
          <div className="flex items-center rounded-xl border border-border/60 bg-muted/30 p-1">
            <Button
              variant="ghost"
              size="icon"
              className={`h-7 w-7 rounded-lg ${folderView === "grid" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground"}`}
              onClick={() => setFolderView("grid")}
            >
              <LayoutGrid className="h-3.5 w-3.5" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className={`h-7 w-7 rounded-lg ${folderView === "list" ? "bg-background shadow-sm text-foreground" : "text-muted-foreground"}`}
              onClick={() => setFolderView("list")}
            >
              <ListIcon className="h-3.5 w-3.5" />
            </Button>
          </div>

          <Button
            size="sm"
            variant="outline"
            onClick={onCreateFolderClick}
            className="gap-1.5 rounded-xl border-border/80 text-xs font-semibold hover:border-primary/50 hover:bg-primary/5"
          >
            <FolderPlus className="h-3.5 w-3.5 text-primary" />
            Tạo thư mục
          </Button>
        </div>
      </div>

      {/* Empty State */}
      {folders.length === 0 && (
        <motion.div
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center justify-center rounded-3xl border border-dashed border-border/80 glass-card p-8 text-center"
        >
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-500/10 text-indigo-500 mb-3 shadow-inner">
            <FolderPlus className="h-8 w-8" />
          </div>
          <h3 className="text-base font-bold text-foreground">Chưa có thư mục nào</h3>
          <p className="text-xs text-muted-foreground max-w-sm mt-1 mb-4">
            Phân loại tài liệu, ghi chú và đoạn mã vào các thư mục để tìm kiếm cấu trúc hiệu quả hơn.
          </p>
          <Button onClick={onCreateFolderClick} size="sm" className="gap-2 rounded-xl bg-primary shadow-sm">
            <FolderPlus className="h-4 w-4" />
            Tạo thư mục đầu tiên
          </Button>
        </motion.div>
      )}

      {/* Folders Display Grid / List */}
      {folders.length > 0 && (
        <AnimatePresence mode="wait">
          {folderView === "grid" ? (
            <motion.div 
              key="grid"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4"
            >
              {folders.map((folder) => {
                const isActive = activeFolderId === folder.id
                return (
                  <motion.div
                    key={folder.id}
                    whileHover={{ y: -3 }}
                    className={`group relative overflow-hidden rounded-2xl border glass-card p-4 transition-all duration-200 cursor-pointer ${
                      isActive 
                        ? "border-primary bg-primary/5 ring-2 ring-primary/20 shadow-md" 
                        : "border-border/60 hover:border-primary/40 hover:shadow-lg"
                    }`}
                    onClick={() => onSelectFolder(isActive ? null : folder)}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-3">
                        <div
                          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-xl shadow-sm border border-white/20"
                          style={{ backgroundColor: folder.color || "#6366F1", color: "#FFFFFF" }}
                        >
                          {folder.icon || "📂"}
                        </div>
                        <div className="overflow-hidden">
                          <h4 className="text-sm font-bold text-foreground truncate group-hover:text-primary transition-colors">
                            {folder.name}
                          </h4>
                          <p className="text-xs text-muted-foreground truncate">
                            {folder.description || "Thư mục con"}
                          </p>
                        </div>
                      </div>

                      <DropdownMenu>
                        <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                          <Button variant="ghost" size="icon" className="h-7 w-7 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                            <MoreVertical className="h-3.5 w-3.5 text-muted-foreground" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="w-40 rounded-xl p-1">
                          <DropdownMenuItem 
                            onClick={(e) => { e.stopPropagation(); onEditFolderClick(folder) }}
                            className="gap-2 rounded-lg text-xs cursor-pointer"
                          >
                            <Pencil className="h-3.5 w-3.5 text-slate-500" />
                            Đổi tên thư mục
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem 
                            onClick={(e) => { e.stopPropagation(); onDeleteFolderClick(folder) }}
                            className="gap-2 rounded-lg text-xs text-destructive cursor-pointer"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                            Xóa thư mục
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>

                    <div className="mt-3 flex items-center justify-between border-t border-border/30 pt-2.5 text-[11px] text-muted-foreground">
                      <span>Cập nhật {format(new Date(folder.updated_at), "dd MMM")}</span>
                      <span className="flex items-center gap-1 font-semibold text-primary">
                        Mở thư mục
                        <ChevronRight className="h-3 w-3" />
                      </span>
                    </div>
                  </motion.div>
                )
              })}
            </motion.div>
          ) : (
            <motion.div 
              key="list"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="divide-y divide-border/40 rounded-2xl border border-border/60 glass-card overflow-hidden"
            >
              {folders.map((folder) => {
                const isActive = activeFolderId === folder.id
                return (
                  <div
                    key={folder.id}
                    onClick={() => onSelectFolder(isActive ? null : folder)}
                    className={`flex items-center justify-between p-3.5 transition-colors cursor-pointer ${
                      isActive ? "bg-primary/10" : "hover:bg-muted/50"
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xl">{folder.icon || "📂"}</span>
                      <div>
                        <span className="text-sm font-bold text-foreground">{folder.name}</span>
                        {folder.description && (
                          <span className="text-xs text-muted-foreground ml-2">({folder.description})</span>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-muted-foreground">
                      <span>{format(new Date(folder.updated_at), "dd MMM yyyy")}</span>
                      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={(e) => { e.stopPropagation(); onEditFolderClick(folder) }}>
                        <Pencil className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                )
              })}
            </motion.div>
          )}
        </AnimatePresence>
      )}
    </div>
  )
}
