import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface DeleteWorkspaceDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  workspaceName?: string
  onConfirm: () => Promise<void>
  isDeleting?: boolean
}

export function DeleteWorkspaceDialog({
  open,
  onOpenChange,
  workspaceName,
  onConfirm,
  isDeleting = false,
}: DeleteWorkspaceDialogProps) {
  async function handleConfirm() {
    await onConfirm()
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Xóa workspace</DialogTitle>
          <DialogDescription>
            Bạn có chắc chắn muốn xóa workspace{" "}
            <span className="font-medium text-foreground">{workspaceName}</span>? Hành động này không thể hoàn tác.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={isDeleting}>
            Huỷ
          </Button>
          <Button type="button" variant="destructive" onClick={() => void handleConfirm()} disabled={isDeleting}>
            {isDeleting ? "Đang xóa..." : "Xóa workspace"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
