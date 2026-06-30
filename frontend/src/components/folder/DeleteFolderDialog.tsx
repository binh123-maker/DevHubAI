import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface DeleteFolderDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  folderName: string
  onConfirm: () => Promise<void>
  isDeleting?: boolean
}

export function DeleteFolderDialog({
  open,
  onOpenChange,
  folderName,
  onConfirm,
  isDeleting = false,
}: DeleteFolderDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Xóa thư mục</DialogTitle>
          <DialogDescription>
            Bạn có chắc chắn muốn xóa thư mục <strong className="text-foreground">{folderName}</strong>? Hành động này
            không thể hoàn tác và các tài liệu bên trong (nếu có) cũng sẽ bị xóa.
          </DialogDescription>
        </DialogHeader>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isDeleting}>
            Huỷ
          </Button>
          <Button variant="destructive" onClick={() => void onConfirm()} disabled={isDeleting}>
            {isDeleting ? "Đang xóa..." : "Xóa thư mục"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
