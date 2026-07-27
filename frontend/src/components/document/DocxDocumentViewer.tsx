import { useState } from "react"
import { FileText, Layers, ChevronRight } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface DocxDocumentViewerProps {
  title: string
  chunks: any[]
  structureNodes?: any[]
  targetChunk?: number
}

export function DocxDocumentViewer({ title, chunks, structureNodes = [], targetChunk = 0 }: DocxDocumentViewerProps) {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null)

  return (
    <div className="flex flex-col md:flex-row h-[75vh] w-full gap-4">
      {/* Structural Tree Outline (Part 7) */}
      {structureNodes.length > 0 && (
        <div className="w-full md:w-72 border border-border/60 rounded-2xl p-4 bg-card/80 overflow-y-auto shrink-0 space-y-2">
          <div className="flex items-center gap-2 pb-2 border-b border-border/40 text-xs font-bold text-muted-foreground">
            <Layers className="h-4 w-4 text-primary" />
            <span>Document Outline ({structureNodes.length} Nodes)</span>
          </div>
          <div className="space-y-1">
            {structureNodes.map((node, idx) => (
              <button
                key={node.id || idx}
                onClick={() => setSelectedNodeId(node.id)}
                className={`w-full text-left p-2 rounded-xl text-xs transition-colors flex items-center gap-1.5 ${
                  selectedNodeId === node.id
                    ? "bg-primary/15 text-primary font-bold border border-primary/30"
                    : "hover:bg-accent/60 text-muted-foreground"
                }`}
              >
                <ChevronRight className="h-3 w-3 shrink-0 text-muted-foreground" />
                <span className="truncate">{node.content_text || `Node #${idx+1}`}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Main Document Content */}
      <div className="flex-1 border border-border/60 rounded-2xl p-6 bg-card/80 overflow-y-auto space-y-4">
        <div className="flex items-center gap-2 pb-3 border-b border-border/40">
          <FileText className="h-5 w-5 text-blue-500" />
          <h3 className="text-lg font-extrabold">{title}</h3>
          <Badge variant="outline" className="ml-auto font-mono text-xs">DOCX Document</Badge>
        </div>

        <div className="space-y-4">
          {chunks.map((c, idx) => (
            <div
              key={c.id || idx}
              className={`p-4 rounded-xl border transition-all ${
                idx === targetChunk
                  ? "bg-amber-500/15 border-amber-500 ring-2 ring-amber-500/30"
                  : "bg-muted/30 border-border/40"
              }`}
            >
              <div className="flex items-center justify-between text-[11px] font-mono font-bold text-muted-foreground mb-2">
                <span>{c.heading || `Section #${idx+1}`}</span>
                <span>Chunk #{idx}</span>
              </div>
              <div className="text-xs leading-relaxed font-mono whitespace-pre-wrap text-foreground">
                {c.content_markdown || c.content}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
