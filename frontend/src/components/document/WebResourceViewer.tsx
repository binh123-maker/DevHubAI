import { useState } from "react"
import { ExternalLink, Globe, BookOpen, Clock, User, Calendar, FileText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface WebResourceViewerProps {
  urlResource: {
    id: string
    original_url: string
    title?: string | null
    description?: string | null
    preview_image_url?: string | null
    parsed_markdown?: string | null
    fetched_html?: string | null
    metadata_json?: any
    created_at: string
  }
  chunks: any[]
  targetChunk?: number
}

export function WebResourceViewer({ urlResource, chunks, targetChunk = 0 }: WebResourceViewerProps) {
  const [viewMode, setViewMode] = useState<"reader" | "chunks">("reader")

  const meta = urlResource.metadata_json || {}
  const domain = new URL(urlResource.original_url).hostname

  return (
    <div className="space-y-4 w-full max-w-5xl mx-auto">
      {/* 1. Header Card: Edge Reader Metadata (Part 22) */}
      <Card className="border-border/60 bg-card/90 shadow-lg overflow-hidden">
        {urlResource.preview_image_url && (
          <div className="h-48 w-full overflow-hidden bg-slate-900 relative">
            <img
              src={urlResource.preview_image_url}
              alt={urlResource.title || "Website Preview"}
              className="w-full h-full object-cover opacity-85 hover:opacity-100 transition-opacity"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-background via-transparent to-transparent" />
          </div>
        )}

        <CardHeader className="pb-3">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-2">
            <div className="flex items-center gap-2">
              {meta.favicon ? (
                <img src={meta.favicon} alt="Favicon" className="h-5 w-5 rounded shrink-0" />
              ) : (
                <Globe className="h-5 w-5 text-emerald-500 shrink-0" />
              )}
              <span className="text-xs font-mono font-bold text-muted-foreground truncate">{domain}</span>
              <Badge variant="outline" className="text-[10px] uppercase">{meta.language || "VI"}</Badge>
            </div>

            <div className="flex items-center gap-2">
              <Button
                variant={viewMode === "reader" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("reader")}
                className="h-8 text-xs gap-1 font-bold"
              >
                <BookOpen className="h-3.5 w-3.5" />
                <span>Reading Mode</span>
              </Button>
              <Button
                variant={viewMode === "chunks" ? "default" : "outline"}
                size="sm"
                onClick={() => setViewMode("chunks")}
                className="h-8 text-xs gap-1 font-bold"
              >
                <FileText className="h-3.5 w-3.5" />
                <span>Extracted Chunks ({chunks.length})</span>
              </Button>

              {/* Open Website Button: target="_blank" rel="noopener noreferrer" (Part 6) */}
              <a
                href={urlResource.original_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="secondary" size="sm" className="h-8 text-xs gap-1 font-bold border border-primary/30 text-primary">
                  <span>Open Website</span>
                  <ExternalLink className="h-3.5 w-3.5" />
                </Button>
              </a>
            </div>
          </div>

          <CardTitle className="text-xl md:text-2xl leading-snug">{urlResource.title || urlResource.original_url}</CardTitle>
          {urlResource.description && (
            <p className="text-sm text-muted-foreground mt-1 leading-relaxed">
              {urlResource.description}
            </p>
          )}
        </CardHeader>

        <CardContent className="pt-0">
          <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground border-t border-border/40 pt-3">
            {meta.author && (
              <span className="flex items-center gap-1">
                <User className="h-3.5 w-3.5 text-primary" />
                <span>{meta.author}</span>
              </span>
            )}
            {meta.published_date && (
              <span className="flex items-center gap-1">
                <Calendar className="h-3.5 w-3.5 text-blue-500" />
                <span>{meta.published_date}</span>
              </span>
            )}
            {meta.reading_time && (
              <span className="flex items-center gap-1 font-mono">
                <Clock className="h-3.5 w-3.5 text-amber-500" />
                <span>{meta.reading_time}</span>
              </span>
            )}
            {meta.canonical_url && (
              <span className="truncate max-w-xs text-[11px] font-mono opacity-80" title={meta.canonical_url}>
                Canonical: {meta.canonical_url}
              </span>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 2. Content View: Reader Mode vs Extracted Chunks (Part 21) */}
      <Card className="border-border/60 bg-card/90 shadow-md">
        <CardContent className="p-6">
          {viewMode === "reader" ? (
            <div className="prose prose-sm dark:prose-invert max-w-none space-y-4 font-sans leading-relaxed">
              {urlResource.parsed_markdown ? (
                <div className="whitespace-pre-wrap font-sans text-sm leading-relaxed text-foreground">
                  {urlResource.parsed_markdown}
                </div>
              ) : (
                <p className="text-muted-foreground text-sm">No reader mode text extracted.</p>
              )}
            </div>
          ) : (
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
                    <span>Chunk #{idx} • {c.heading || "General Content"}</span>
                  </div>
                  <div className="text-xs leading-relaxed font-mono whitespace-pre-wrap text-foreground">
                    {c.content_markdown || c.content}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
