import { useState } from "react"
import { Download, FileText, Printer, Check } from "lucide-react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"

interface ExportDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onExportMarkdown: (includeCitations: boolean) => void
  onExportTxt: (includeCitations: boolean) => void
  onPrintPdf: () => void
}

export function ExportDialog({
  open,
  onOpenChange,
  onExportMarkdown,
  onExportTxt,
  onPrintPdf,
}: ExportDialogProps) {
  const [includeCitations, setIncludeCitations] = useState(true)
  const [exportFormat, setExportFormat] = useState<"md" | "txt" | "pdf">("md")

  const handleExport = () => {
    if (exportFormat === "md") {
      onExportMarkdown(includeCitations)
    } else if (exportFormat === "txt") {
      onExportTxt(includeCitations)
    } else {
      onPrintPdf()
    }
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-xs p-0 overflow-hidden border border-border/60 bg-card text-card-foreground shadow-2xl rounded-2xl">
        <DialogHeader className="p-4 border-b border-border/40 pb-3">
          <DialogTitle className="text-sm font-bold flex items-center gap-2">
            <Download className="h-4 w-4 text-primary" />
            Xuất cuộc trò chuyện (Export Chat)
          </DialogTitle>
        </DialogHeader>

        <div className="p-4 space-y-4 text-xs">
          {/* Format selection */}
          <div className="space-y-2">
            <Label className="text-xs font-semibold">Định dạng file</Label>
            <div className="grid grid-cols-3 gap-1.5">
              <div
                onClick={() => setExportFormat("md")}
                className={`flex flex-col items-center justify-center p-2.5 rounded-xl border cursor-pointer transition-all ${
                  exportFormat === "md" ? "bg-primary/10 border-primary/50 text-primary font-bold" : "bg-muted/20 border-border/60 text-muted-foreground"
                }`}
              >
                <FileText className="h-4 w-4 mb-1" />
                <span>Markdown (.md)</span>
              </div>
              <div
                onClick={() => setExportFormat("txt")}
                className={`flex flex-col items-center justify-center p-2.5 rounded-xl border cursor-pointer transition-all ${
                  exportFormat === "txt" ? "bg-primary/10 border-primary/50 text-primary font-bold" : "bg-muted/20 border-border/60 text-muted-foreground"
                }`}
              >
                <FileText className="h-4 w-4 mb-1" />
                <span>Text (.txt)</span>
              </div>
              <div
                onClick={() => setExportFormat("pdf")}
                className={`flex flex-col items-center justify-center p-2.5 rounded-xl border cursor-pointer transition-all ${
                  exportFormat === "pdf" ? "bg-primary/10 border-primary/50 text-primary font-bold" : "bg-muted/20 border-border/60 text-muted-foreground"
                }`}
              >
                <Printer className="h-4 w-4 mb-1" />
                <span>PDF Print</span>
              </div>
            </div>
          </div>

          {/* Options */}
          <div className="flex items-center gap-2 pt-1">
            <input
              type="checkbox"
              id="citations"
              checked={includeCitations}
              onChange={(e) => setIncludeCitations(e.target.checked)}
              className="rounded border-border text-primary focus:ring-primary h-4 w-4 cursor-pointer"
            />
            <Label htmlFor="citations" className="text-xs cursor-pointer">
              Bao gồm nguồn trích dẫn RAG (Citations)
            </Label>
          </div>
        </div>

        <DialogFooter className="p-3 border-t border-border/40 bg-muted/20 gap-2">
          <Button variant="outline" size="sm" onClick={() => onOpenChange(false)} className="h-8 text-xs">
            Hủy
          </Button>
          <Button size="sm" onClick={handleExport} className="h-8 text-xs gap-1 shadow-sm font-bold">
            <Check className="h-3.5 w-3.5" />
            Tải về
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
