import { useState } from "react"

import { MoreVertical, Pencil, Copy, Pin, PinOff, Download, Trash2, Loader2 } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface ConversationMenuProps {
  chatId: string
  currentTitle: string
  isFavorite: boolean
  onRename: (newTitle: string) => Promise<void>
  onDuplicate: () => Promise<void>
  onToggleFavorite: () => Promise<void>
  onExport: () => Promise<void>
  onDelete: () => Promise<void>
}

export function ConversationMenu({
  currentTitle,
  isFavorite,
  onRename,
  onDuplicate,
  onToggleFavorite,
  onExport,
  onDelete,
}: ConversationMenuProps) {
  const [renameOpen, setRenameOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [newTitle, setNewTitle] = useState(currentTitle)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleRenameSubmit = async () => {
    if (!newTitle.trim()) return
    setIsSubmitting(true)
    try {
      await onRename(newTitle.trim())
      setRenameOpen(false)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleDeleteSubmit = async () => {
    setIsSubmitting(true)
    try {
      await onDelete()
      setDeleteOpen(false)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button
            variant="ghost"
            size="icon"
            onClick={(e) => e.stopPropagation()}
            className="h-7 w-7 text-muted-foreground hover:text-foreground opacity-80 group-hover:opacity-100 transition-opacity"
            title="Thao tác"
          >
            <MoreVertical className="h-4 w-4" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-48 p-1 border border-border/60 bg-popover text-popover-foreground shadow-xl rounded-xl">
          <DropdownMenuItem
            onClick={(e) => {
              e.stopPropagation()
              setNewTitle(currentTitle)
              setRenameOpen(true)
            }}
            className="cursor-pointer text-xs gap-2 py-2"
          >
            <Pencil className="h-3.5 w-3.5 text-blue-500" />
            <span>Đổi tên cuộc trò chuyện</span>
          </DropdownMenuItem>

          <DropdownMenuItem
            onClick={(e) => {
              e.stopPropagation()
              onToggleFavorite()
            }}
            className="cursor-pointer text-xs gap-2 py-2"
          >
            {isFavorite ? (
              <>
                <PinOff className="h-3.5 w-3.5 text-amber-500" />
                <span>Bỏ ghim</span>
              </>
            ) : (
              <>
                <Pin className="h-3.5 w-3.5 text-amber-500" />
                <span>Ghim cuộc trò chuyện</span>
              </>
            )}
          </DropdownMenuItem>

          <DropdownMenuItem
            onClick={(e) => {
              e.stopPropagation()
              onDuplicate()
            }}
            className="cursor-pointer text-xs gap-2 py-2"
          >
            <Copy className="h-3.5 w-3.5 text-purple-500" />
            <span>Tạo bản sao (Duplicate)</span>
          </DropdownMenuItem>

          <DropdownMenuItem
            onClick={(e) => {
              e.stopPropagation()
              onExport()
            }}
            className="cursor-pointer text-xs gap-2 py-2"
          >
            <Download className="h-3.5 w-3.5 text-emerald-500" />
            <span>Xuất file Markdown</span>
          </DropdownMenuItem>

          <DropdownMenuSeparator />

          <DropdownMenuItem
            onClick={(e) => {
              e.stopPropagation()
              setDeleteOpen(true)
            }}
            className="cursor-pointer text-xs gap-2 py-2 text-destructive focus:bg-destructive/10"
          >
            <Trash2 className="h-3.5 w-3.5" />
            <span>Xóa cuộc trò chuyện</span>
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Rename Dialog */}
      <Dialog open={renameOpen} onOpenChange={setRenameOpen}>
        <DialogContent className="max-w-xs p-5 border border-border/60 bg-card shadow-2xl rounded-2xl">
          <DialogHeader className="pb-2">
            <DialogTitle className="text-sm font-bold">Đổi tên cuộc trò chuyện</DialogTitle>
          </DialogHeader>
          <Input
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            className="h-9 text-xs"
            autoFocus
          />
          <DialogFooter className="pt-2 gap-2">
            <Button variant="outline" size="sm" onClick={() => setRenameOpen(false)} className="h-8 text-xs">
              Hủy
            </Button>
            <Button size="sm" onClick={handleRenameSubmit} disabled={isSubmitting || !newTitle.trim()} className="h-8 text-xs">
              {isSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Lưu"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent className="max-w-xs p-5 border border-border/60 bg-card shadow-2xl rounded-2xl">
          <DialogHeader className="pb-2">
            <DialogTitle className="text-sm font-bold text-destructive">Xác nhận xóa</DialogTitle>
          </DialogHeader>
          <p className="text-xs text-muted-foreground">
            Bạn có chắc chắn muốn xóa cuộc trò chuyện &quot;<span className="font-semibold text-foreground">{currentTitle}</span>&quot;? Hành động này không thể hoàn tác.
          </p>
          <DialogFooter className="pt-3 gap-2">
            <Button variant="outline" size="sm" onClick={() => setDeleteOpen(false)} className="h-8 text-xs">
              Hủy
            </Button>
            <Button variant="destructive" size="sm" onClick={handleDeleteSubmit} disabled={isSubmitting} className="h-8 text-xs">
              {isSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : "Xóa vĩnh viễn"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
