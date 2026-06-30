import { FormEvent, useEffect, useState } from "react"

import { type Folder, type FolderCreatePayload, type FolderUpdatePayload } from "@/api/folder.api"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

interface FolderFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  folder?: Folder | null
  workspaceId: string
  onSubmit: (payload: any) => Promise<void>
  isSubmitting?: boolean
}

export function FolderFormDialog({
  open,
  onOpenChange,
  folder,
  workspaceId,
  onSubmit,
  isSubmitting = false,
}: FolderFormDialogProps) {
  const isEditing = Boolean(folder)
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [error, setError] = useState("")

  useEffect(() => {
    if (!open) {
      return
    }
    setName(folder?.name ?? "")
    setDescription(folder?.description ?? "")
    setError("")
  }, [open, folder])

  function validate() {
    if (!name.trim()) {
      setError("Tên thư mục là bắt buộc")
      return false
    }
    setError("")
    return true
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!validate()) {
      return
    }

    const payload = isEditing 
      ? {
          name: name.trim(),
          description: description.trim() || null,
        }
      : {
          workspace_id: workspaceId,
          name: name.trim(),
          description: description.trim() || null,
        }

    await onSubmit(payload)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEditing ? "Chỉnh sửa thư mục" : "Tạo thư mục mới"}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? "Cập nhật thông tin thư mục."
              : "Tạo thư mục để tổ chức tài liệu gọn gàng hơn."}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={(event) => void handleSubmit(event)} className="space-y-4" noValidate>
          <div className="space-y-2">
            <Label htmlFor="folder-name">Tên thư mục</Label>
            <Input
              id="folder-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Ví dụ: Tài liệu kỹ thuật"
            />
            {error && <p className="text-sm text-destructive">{error}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="folder-description">Mô tả</Label>
            <Input
              id="folder-description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Mô tả ngắn (tuỳ chọn)"
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isSubmitting}>
              Huỷ
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Đang lưu..." : isEditing ? "Lưu thay đổi" : "Tạo thư mục"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
