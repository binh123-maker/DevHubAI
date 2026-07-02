import { FormEvent, useEffect, useState } from "react"
import { Folder as FolderIcon, FileText, Briefcase, Book, Image as ImageIcon, Archive, MessageSquare } from "lucide-react"

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

const COLOR_PRESETS = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899"]

const ICONS: Record<string, React.ElementType> = {
  folder: FolderIcon,
  file: FileText,
  briefcase: Briefcase,
  book: Book,
  image: ImageIcon,
  archive: Archive,
  message: MessageSquare,
}

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
  const [color, setColor] = useState("#3B82F6")
  const [icon, setIcon] = useState("folder")
  const [errors, setErrors] = useState<{ name?: string; color?: string }>({})

  useEffect(() => {
    if (!open) {
      return
    }
    setName(folder?.name ?? "")
    setDescription(folder?.description ?? "")
    setColor(folder?.color ?? "#3B82F6")
    setIcon(folder?.icon ?? "folder")
    setErrors({})
  }, [open, folder])

  function validate() {
    const nextErrors: { name?: string; color?: string } = {}
    if (!name.trim()) {
      nextErrors.name = "Tên thư mục là bắt buộc"
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

    const payload = isEditing 
      ? {
          name: name.trim(),
          description: description.trim() || null,
          color: color.toUpperCase(),
          icon: icon,
        }
      : {
          workspace_id: workspaceId,
          name: name.trim(),
          description: description.trim() || null,
          color: color.toUpperCase(),
          icon: icon,
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
            {errors.name && <p className="text-sm text-destructive">{errors.name}</p>}
          </div>

          <div className="space-y-2">
            <Label>Biểu tượng</Label>
            <div className="flex flex-wrap gap-2">
              {Object.entries(ICONS).map(([key, IconComponent]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => setIcon(key)}
                  className={`flex h-10 w-10 items-center justify-center rounded-md border-2 transition-all hover:bg-muted ${
                    icon === key ? "border-primary bg-primary/10 text-primary" : "border-transparent text-muted-foreground"
                  }`}
                  aria-label={`Chọn biểu tượng ${key}`}
                >
                  <IconComponent className="h-5 w-5" />
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="folder-color">Màu sắc</Label>
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
              id="folder-color"
              value={color}
              onChange={(event) => setColor(event.target.value)}
              placeholder="#3B82F6"
            />
            {errors.color && <p className="text-sm text-destructive">{errors.color}</p>}
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
