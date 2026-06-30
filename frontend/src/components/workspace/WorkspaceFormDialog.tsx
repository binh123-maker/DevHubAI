import { FormEvent, useEffect, useState } from "react"

import { type Workspace, type WorkspaceCreatePayload, type WorkspaceUpdatePayload } from "@/api/workspace.api"
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

const COLOR_PRESETS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]

interface WorkspaceFormDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  workspace?: Workspace | null
  onSubmit: (payload: WorkspaceCreatePayload | WorkspaceUpdatePayload) => Promise<void>
  isSubmitting?: boolean
}

export function WorkspaceFormDialog({
  open,
  onOpenChange,
  workspace,
  onSubmit,
  isSubmitting = false,
}: WorkspaceFormDialogProps) {
  const isEditing = Boolean(workspace)
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [color, setColor] = useState("#3B82F6")
  const [errors, setErrors] = useState<{ name?: string; color?: string }>({})

  useEffect(() => {
    if (!open) {
      return
    }
    setName(workspace?.name ?? "")
    setDescription(workspace?.description ?? "")
    setColor(workspace?.color ?? "#3B82F6")
    setErrors({})
  }, [open, workspace])

  function validate() {
    const nextErrors: { name?: string; color?: string } = {}
    if (!name.trim()) {
      nextErrors.name = "Tên workspace là bắt buộc"
    }
    if (!/^#[0-9A-Fa-f]{6}$/.test(color)) {
      nextErrors.color = "Màu phải là mã hex hợp lệ (ví dụ: #3B82F6)"
    }
    setErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!validate()) {
      return
    }

    const payload = {
      name: name.trim(),
      description: description.trim() || null,
      color: color.toUpperCase(),
      icon: workspace?.icon ?? "folder",
    }

    await onSubmit(payload)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{isEditing ? "Chỉnh sửa workspace" : "Tạo workspace mới"}</DialogTitle>
          <DialogDescription>
            {isEditing
              ? "Cập nhật thông tin workspace của bạn."
              : "Tạo workspace để tổ chức tài liệu và trò chuyện AI."}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={(event) => void handleSubmit(event)} className="space-y-4" noValidate>
          <div className="space-y-2">
            <Label htmlFor="workspace-name">Tên workspace</Label>
            <Input
              id="workspace-name"
              value={name}
              onChange={(event) => setName(event.target.value)}
              placeholder="Ví dụ: ReactJS"
            />
            {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
          </div>

          <div className="space-y-2">
            <Label htmlFor="workspace-description">Mô tả</Label>
            <Input
              id="workspace-description"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Mô tả ngắn (tuỳ chọn)"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="workspace-color">Màu</Label>
            <div className="flex flex-wrap gap-2">
              {COLOR_PRESETS.map((preset) => (
                <button
                  key={preset}
                  type="button"
                  className="h-8 w-8 rounded-full border-2 transition-transform hover:scale-105"
                  style={{
                    backgroundColor: preset,
                    borderColor: color.toUpperCase() === preset ? "#111827" : "transparent",
                  }}
                  aria-label={`Chọn màu ${preset}`}
                  onClick={() => setColor(preset)}
                />
              ))}
            </div>
            <Input
              id="workspace-color"
              value={color}
              onChange={(event) => setColor(event.target.value)}
              placeholder="#3B82F6"
            />
            {errors.color && <p className="text-sm text-destructive">{errors.color}</p>}
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isSubmitting}>
              Huỷ
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Đang lưu..." : isEditing ? "Lưu thay đổi" : "Tạo workspace"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
