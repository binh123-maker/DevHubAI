import { useState } from "react"
import { Plus, FileText, FolderPlus, Folder, Globe } from "lucide-react"



interface KanbanSpeedDialProps {
  onUploadClick: () => void
  onCreateWorkspaceClick: () => void
  onCreateFolderClick?: () => void
  onImportUrlClick: () => void
}

export function KanbanSpeedDial({
  onUploadClick,
  onCreateWorkspaceClick,
  onCreateFolderClick,
  onImportUrlClick,
}: KanbanSpeedDialProps) {
  const [isOpen, setIsOpen] = useState(false)

  const handleAction = (action: () => void) => {
    setIsOpen(false)
    action()
  }

  return (
    <div className="fixed bottom-6 right-6 z-40 flex flex-col items-end gap-2.5">
      {/* Expanded Speed Dial Actions */}
      {isOpen && (
        <div className="flex flex-col items-end gap-2 animate-in slide-in-from-bottom-5 duration-200">
          <button
            onClick={() => handleAction(onUploadClick)}
            className="flex items-center gap-2.5 rounded-full bg-card border border-border/80 px-3.5 py-2 text-xs font-semibold shadow-lg text-foreground hover:bg-accent hover:border-primary/40 transition-all active:scale-95"
          >
            <span>Tải lên Tài liệu</span>
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-blue-500/10 text-blue-500">
              <FileText className="h-3.5 w-3.5" />
            </div>
          </button>

          <button
            onClick={() => handleAction(onImportUrlClick)}
            className="flex items-center gap-2.5 rounded-full bg-card border border-border/80 px-3.5 py-2 text-xs font-semibold shadow-lg text-foreground hover:bg-accent hover:border-primary/40 transition-all active:scale-95"
          >
            <span>Nhập từ URL</span>
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-emerald-500/10 text-emerald-500">
              <Globe className="h-3.5 w-3.5" />
            </div>
          </button>

          <button
            onClick={() => handleAction(onCreateWorkspaceClick)}
            className="flex items-center gap-2.5 rounded-full bg-card border border-border/80 px-3.5 py-2 text-xs font-semibold shadow-lg text-foreground hover:bg-accent hover:border-primary/40 transition-all active:scale-95"
          >
            <span>Tạo Workspace</span>
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-amber-500/10 text-amber-500">
              <FolderPlus className="h-3.5 w-3.5" />
            </div>
          </button>

          {onCreateFolderClick && (
            <button
              onClick={() => handleAction(onCreateFolderClick)}
              className="flex items-center gap-2.5 rounded-full bg-card border border-border/80 px-3.5 py-2 text-xs font-semibold shadow-lg text-foreground hover:bg-accent hover:border-primary/40 transition-all active:scale-95"
            >
              <span>Tạo Thư mục</span>
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-purple-500/10 text-purple-500">
                <Folder className="h-3.5 w-3.5" />
              </div>
            </button>
          )}
        </div>
      )}

      {/* Main Floating Trigger Button */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        aria-label="Thao tác nhanh Kanban"
        className={`flex h-12 w-12 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-xl transition-all duration-200 hover:scale-110 active:scale-95 ring-4 ring-primary/20 ${
          isOpen ? "rotate-45 bg-destructive text-destructive-foreground ring-destructive/20" : ""
        }`}
      >
        <Plus className="h-6 w-6" />
      </button>
    </div>
  )
}
