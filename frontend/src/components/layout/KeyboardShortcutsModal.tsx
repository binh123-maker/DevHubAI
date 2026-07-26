import { Keyboard } from "lucide-react"
import { useKeyboardShortcut } from "@/hooks/useKeyboardShortcut"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"

interface KeyboardShortcutsModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function KeyboardShortcutsModal({ open, onOpenChange }: KeyboardShortcutsModalProps) {
  // Global keybinding `?`
  useKeyboardShortcut("?", () => onOpenChange(true))

  const shortcuts = [
    { key: "Ctrl + K / Cmd + K", description: "Mở tìm kiếm nhanh toàn hệ thống (Global Search)" },
    { key: "?", description: "Mở bảng phím tắt này" },
    { key: "ESC", description: "Đóng cửa sổ Modal / Mobile Drawer / Tìm kiếm" },
    { key: "Tab / Shift + Tab", description: "Di chuyển tiêu điểm (Focus) giữa các phần tử" },
    { key: "Enter / Space", description: "Kích hoạt thẻ KPI hoặc nút hành động" },
    { key: "Arrow Up / Down", description: "Di chuyển trong danh sách tìm kiếm" },
  ]

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md p-0 overflow-hidden border border-border/60 bg-card text-card-foreground shadow-2xl rounded-2xl">
        <DialogHeader className="p-5 border-b border-border/40 pb-4">
          <DialogTitle className="text-base font-bold flex items-center gap-2">
            <Keyboard className="h-5 w-5 text-primary" />
            Danh sách Phím tắt (Keyboard Shortcuts)
          </DialogTitle>
        </DialogHeader>

        <div className="p-5 space-y-3 max-h-[350px] overflow-y-auto scrollbar-thin">
          {shortcuts.map((sc, idx) => (
            <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg border border-border/40 bg-muted/20 text-xs">
              <span className="text-muted-foreground">{sc.description}</span>
              <kbd className="rounded border border-border/80 bg-muted px-2 py-0.5 text-[11px] font-mono font-bold text-foreground shrink-0 ml-2">
                {sc.key}
              </kbd>
            </div>
          ))}
        </div>
      </DialogContent>
    </Dialog>
  )
}
