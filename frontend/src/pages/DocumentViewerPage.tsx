import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { AlertCircle, ArrowLeft, Loader2 } from "lucide-react"
import { Link, useParams } from "react-router-dom"

import { documentApi } from "@/api/document.api"
import { isDocumentProcessed, isDocumentProcessing } from "@/utils/documentStatus"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { useCitationNavigation } from "@/hooks/useCitationNavigation"
import { CitationBreadcrumb } from "@/components/chat/CitationBreadcrumb"
import { PdfDocumentViewer } from "@/components/document/PdfDocumentViewer"
import { WebResourceViewer } from "@/components/document/WebResourceViewer"
import { DocxDocumentViewer } from "@/components/document/DocxDocumentViewer"
import { MarkdownDocumentViewer } from "@/components/document/MarkdownDocumentViewer"
import { TextDocumentViewer } from "@/components/document/TextDocumentViewer"
import { ProcessingMonitor } from "@/components/document/ProcessingMonitor"

export default function DocumentViewerPage() {
  const { id } = useParams()
  const queryClient = useQueryClient()
  const { targetPage, targetChunk, highlightQuery, shouldHighlight } = useCitationNavigation()

  // 1. Fetch Document Metadata
  const { data: document, isLoading, isError } = useQuery({
    queryKey: ["documents", id],
    queryFn: async () => {
      const res = await documentApi.get(id!)
      return res.data
    },
    enabled: Boolean(id),
    refetchInterval: (query) => {
      const doc = query.state.data
      return doc && isDocumentProcessing(doc.status) ? 2000 : false
    },
  })

  // 2. Fetch Document Chunks
  const { data: chunks = [] } = useQuery({
    queryKey: ["chunks", id],
    queryFn: async () => {
      const res = await documentApi.getChunks(id!)
      return res.data
    },
    enabled: Boolean(id) && isDocumentProcessed(document?.status),
  })

  // 3. Fetch URL Resource details (if URL type)
  const sourceUrl = (document as any)?.source_url
  const isUrlDoc = Boolean(document?.file_type?.toLowerCase() === "md" && sourceUrl) || document?.file_name === "webpage.md"
  const { data: urlResource } = useQuery({
    queryKey: ["url-resource", id],
    queryFn: async () => {
      const res = await documentApi.getUrlResource(id!)
      return res.data
    },
    enabled: Boolean(id) && isUrlDoc,
  })

  // 4. Fetch Structure Nodes (for DOCX/PDF)
  const { data: structureNodes = [] } = useQuery({
    queryKey: ["structure", id],
    queryFn: async () => {
      const res = await documentApi.getStructure(id!)
      return res.data
    },
    enabled: Boolean(id) && isDocumentProcessed(document?.status),
  })

  // Retry processing mutation (Part 23)
  const retryMutation = useMutation({
    mutationFn: async () => {
      const res = await documentApi.retryProcessing(id!)
      return res.data
    },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["documents"] })
      void queryClient.invalidateQueries({ queryKey: ["dashboardOverview"] })
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[50vh] gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin text-primary" />
        <span className="text-sm font-semibold">Đang tải thông tin tài liệu...</span>
      </div>
    )
  }

  if (isError || !document) {
    return (
      <div className="space-y-4 max-w-xl mx-auto py-12">
        <Button variant="outline" asChild>
          <Link to="/workspaces">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Quay lại Workspaces
          </Link>
        </Button>
        <Card className="border-destructive/30">
          <CardContent className="py-8 text-center space-y-3">
            <AlertCircle className="h-8 w-8 text-destructive mx-auto" />
            <h3 className="text-base font-bold text-destructive">Không tìm thấy tài liệu hoặc nguồn không khả dụng</h3>
            <p className="text-xs text-muted-foreground">Source unavailable</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const fileType = (document.file_type || "").toLowerCase()
  const fileUrl = documentApi.getFileUrl(document.id)

  return (
    <div className="space-y-4 contain-layout">
      {/* Navigation Header & Citation Breadcrumb */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-border/40 pb-3">
        <Button variant="outline" size="sm" asChild className="w-fit">
          <Link to={`/workspaces/${document.workspace_id}`}>
            <ArrowLeft className="h-4 w-4 mr-1.5" />
            Quay lại Workspace
          </Link>
        </Button>

        <CitationBreadcrumb
          workspaceName="Workspace"
          folderName="Folder"
          documentName={document.title}
          pageNumber={targetPage}
          chunkIndex={targetChunk}
        />
      </div>

      {/* Processing Monitor for non-PROCESSED status (Parts 10, 11, 24) */}
      {!isDocumentProcessed(document.status) && (
        <ProcessingMonitor
          status={document.status}
          onRetry={() => retryMutation.mutate()}
          isRetrying={retryMutation.isPending}
        />
      )}

      {/* Smart Viewer Routing (Parts 4, 6, 7) */}
      {isDocumentProcessed(document.status) && (
        <div>
          {urlResource ? (
            <WebResourceViewer
              urlResource={urlResource}
              chunks={chunks}
              targetChunk={targetChunk}
            />
          ) : fileType === "pdf" ? (
            <PdfDocumentViewer
              documentId={document.id}
              fileUrl={fileUrl}
              fileTitle={document.title}
              chunks={chunks}
              targetPage={targetPage}
              targetChunk={targetChunk}
              highlightText={highlightQuery}
              shouldHighlight={shouldHighlight}
            />
          ) : fileType === "docx" ? (
            <DocxDocumentViewer
              title={document.title}
              chunks={chunks}
              structureNodes={structureNodes}
              targetChunk={targetChunk}
            />
          ) : fileType === "md" ? (
            <MarkdownDocumentViewer
              title={document.title}
              chunks={chunks}
              targetChunk={targetChunk}
            />
          ) : (
            <TextDocumentViewer
              title={document.title}
              chunks={chunks}
              targetChunk={targetChunk}
            />
          )}
        </div>
      )}
    </div>
  )
}
