import { useState } from "react"
import { FileCode, Copy, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

interface MarkdownDocumentViewerProps {
  title: string
  chunks: any[]
  targetChunk?: number
}

export function MarkdownDocumentViewer({ title, chunks, targetChunk = 0 }: MarkdownDocumentViewerProps) {
  const [isCopied, setIsCopied] = useState(false)

  const fullContent = chunks.map((c) => c.content_markdown || c.content || "").join("\n\n---\n\n")

  const handleCopy = () => {
    navigator.clipboard.writeText(fullContent)
    setIsCopied(true)
    setTimeout(() => setIsCopied(false), 2000)
  }

  return (
    <div className="flex flex-col h-[75vh] w-full border border-border/60 rounded-2xl bg-card/80 shadow-md overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b border-border/50 bg-muted/30 shrink-0">
        <div className="flex items-center gap-2">
          <FileCode className="h-5 w-5 text-emerald-500" />
          <h3 className="text-base font-extrabold">{title}</h3>
          <Badge variant="outline" className="font-mono text-xs">Markdown</Badge>
        </div>

        <Button variant="outline" size="sm" onClick={handleCopy} className="h-8 text-xs gap-1">
          {isCopied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
          <span>{isCopied ? "Đã sao chép" : "Sao chép Markdown"}</span>
        </Button>
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
            <div className="text-[10px] text-muted-foreground font-bold mb-2">Chunk #{idx} • {c.heading || "Markdown Section"}</div>
            <div className="whitespace-pre-wrap text-foreground">{c.content_markdown || c.content}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
