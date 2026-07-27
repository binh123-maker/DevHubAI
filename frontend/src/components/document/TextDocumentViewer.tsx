import { FileText } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface TextDocumentViewerProps {
  title: string
  chunks: any[]
  targetChunk?: number
}

export function TextDocumentViewer({ title, chunks, targetChunk = 0 }: TextDocumentViewerProps) {
  return (
    <div className="flex flex-col h-[75vh] w-full border border-border/60 rounded-2xl bg-card/80 shadow-md overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b border-border/50 bg-muted/30 shrink-0">
        <div className="flex items-center gap-2">
          <FileText className="h-5 w-5 text-zinc-500" />
          <h3 className="text-base font-extrabold">{title}</h3>
          <Badge variant="outline" className="font-mono text-xs">TXT File</Badge>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 space-y-4 font-mono text-xs leading-relaxed scrollbar-hover">
        {chunks.map((c, idx) => (
          <div
            key={c.id || idx}
            className={`p-4 rounded-xl border transition-all ${
              idx === targetChunk
                ? "bg-amber-500/15 border-amber-500 ring-2 ring-amber-500/30"
                : "bg-muted/20 border-border/40"
            }`}
          >
            <div className="text-[10px] text-muted-foreground font-bold mb-1">Paragraph #{idx + 1}</div>
            <div className="whitespace-pre-wrap text-foreground">{c.content}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
