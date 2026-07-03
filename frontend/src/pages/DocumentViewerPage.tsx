import { useQuery } from "@tanstack/react-query"
import { format } from "date-fns"
import { vi } from "date-fns/locale"
import { AlertCircle, ArrowLeft, CheckCircle, Clock, FileText, Loader2 } from "lucide-react"
import { Link, useParams } from "react-router-dom"

import { documentApi } from "@/api/document.api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

function formatBytes(bytes: number): string {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

function StatusBadge({ status }: { status: string }) {
  switch (status) {
    case "UPLOADING":
      return <Badge variant="outline" className="bg-yellow-50 text-yellow-600 border-yellow-200"><Loader2 className="mr-1 h-3 w-3 animate-spin" />Dang tai len</Badge>
    case "PROCESSING":
      return <Badge variant="outline" className="bg-blue-50 text-blue-600 border-blue-200"><Loader2 className="mr-1 h-3 w-3 animate-spin" />Dang xu ly</Badge>
    case "PROCESSED":
      return <Badge variant="outline" className="bg-green-50 text-green-600 border-green-200"><CheckCircle className="mr-1 h-3 w-3" />Da xu ly</Badge>
    case "FAILED":
      return <Badge variant="destructive"><AlertCircle className="mr-1 h-3 w-3" />That bai</Badge>
    default:
      return <Badge variant="secondary">{status}</Badge>
  }
}

export default function DocumentViewerPage() {
  const { id } = useParams()

  const { data: document, isLoading, isError } = useQuery({
    queryKey: ["documents", id],
    queryFn: async () => { const res = await documentApi.get(id!); return res.data },
    enabled: Boolean(id),
  })

  const canPreview =
    document?.status === "PROCESSED" &&
    ["md", "txt", "markdown"].includes((document?.file_type ?? "").toLowerCase())

  const { data: chunks = [], isLoading: chunksLoading } = useQuery({
    queryKey: ["chunks", id],
    queryFn: async () => { const res = await documentApi.getChunks(id!); return res.data },
    enabled: Boolean(id) && canPreview,
  })

  if (isLoading) return <div className="flex items-center gap-2 text-muted-foreground py-8"><Loader2 className="h-4 w-4 animate-spin" /><span>Loading...</span></div>

  if (isError || !document) return (
    <div className="space-y-4">
      <Button variant="outline" asChild><Link to="/workspaces"><ArrowLeft className="h-4 w-4" />Quay lai</Link></Button>
      <Card><CardContent className="py-8"><p className="text-destructive">Khong tim thay tai lieu.</p></CardContent></Card>
    </div>
  )

  const previewText = (chunks as any[]).map((c) => c.content_markdown || c.content || "").join("\n\n")

  return (
    <div className="space-y-6">
      <Button variant="outline" asChild>
        <Link to={`/workspaces/${document.workspace_id}`}><ArrowLeft className="h-4 w-4" />Quay lai workspace</Link>
      </Button>
      <Card>
        <CardHeader className="pb-3">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="flex items-start gap-3">
              <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-muted">
                <FileText className="h-5 w-5 text-muted-foreground" />
              </div>
              <div>
                <CardTitle className="text-xl leading-snug">{document.title}</CardTitle>
                {document.description && <p className="mt-1 text-sm text-muted-foreground">{document.description}</p>}
              </div>
            </div>
            <StatusBadge status={document.status} />
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-4 text-sm">
            <div><p className="font-medium text-muted-foreground mb-0.5">Loai file</p><p className="uppercase font-semibold">{document.file_type || "—"}</p></div>
            <div><p className="font-medium text-muted-foreground mb-0.5">Kich thuoc</p><p>{formatBytes(document.file_size)}</p></div>
            <div><p className="font-medium text-muted-foreground mb-0.5">Ten file goc</p><p className="truncate" title={document.file_name}>{document.file_name}</p></div>
            <div><p className="font-medium text-muted-foreground mb-0.5">Ngay tai len</p><p className="flex items-center gap-1"><Clock className="h-3.5 w-3.5" />{format(new Date(document.created_at), "dd MMM yyyy, HH:mm", { locale: vi })}</p></div>
          </div>
        </CardContent>
      </Card>
      {canPreview && (
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-base">Noi dung tai lieu</CardTitle></CardHeader>
          <CardContent>
            {chunksLoading ? <div className="flex items-center gap-2 text-muted-foreground py-4"><Loader2 className="h-4 w-4 animate-spin" /><span>Dang tai...</span></div>
              : chunks.length === 0 ? <p className="text-sm text-muted-foreground py-4">Khong co noi dung.</p>
                : <pre className="whitespace-pre-wrap text-sm leading-relaxed font-mono max-h-[60vh] overflow-y-auto rounded-md bg-muted/40 p-4">{previewText}</pre>
            }
          </CardContent>
        </Card>
      )}
      {document.status === "PROCESSED" && !canPreview && (
        <Card><CardContent className="py-6 text-center text-sm text-muted-foreground">
          <FileText className="mx-auto mb-2 h-8 w-8" />
          <p>Dinh dang <strong className="uppercase">{document.file_type}</strong> khong ho tro xem truoc.</p>
          <p className="mt-1">Tai lieu da duoc xu ly va san sang cho AI chat.</p>
        </CardContent></Card>
      )}
      {(document.status === "UPLOADING" || document.status === "PROCESSING") && (
        <Card><CardContent className="py-6 text-center text-sm text-muted-foreground">
          <Loader2 className="mx-auto mb-2 h-8 w-8 animate-spin" />
          <p>Tai lieu dang duoc xu ly. Noi dung se hien thi khi hoan tat.</p>
        </CardContent></Card>
      )}
    </div>
  )
}
