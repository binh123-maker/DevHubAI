import { useState } from "react"
import { UploadCloud, Link as LinkIcon, Image, X, FileText, CheckCircle2, Loader2, Plus } from "lucide-react"
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { documentApi } from "@/api/document.api"
import { workspaceApi } from "@/api/workspace.api"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"

interface DocumentUploadDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  defaultWorkspaceId?: string
}

export function DocumentUploadDialog({
  open,
  onOpenChange,
  defaultWorkspaceId,
}: DocumentUploadDialogProps) {
  const queryClient = useQueryClient()
  const [tab, setTab] = useState<"file" | "url" | "ocr">("file")
  const [selectedWorkspaceId, setSelectedWorkspaceId] = useState(defaultWorkspaceId || "")
  const [files, setFiles] = useState<File[]>([])
  const [url, setUrl] = useState("")
  const [urlTitle, setUrlTitle] = useState("")
  const [progress, setProgress] = useState<number>(0)
  const [isSuccess, setIsSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch Workspaces
  const { data: workspaces = [] } = useQuery({
    queryKey: ["workspaces"],
    queryFn: async () => (await workspaceApi.list()).data,
    enabled: open,
  })

  // File Upload Mutation
  const uploadFileMutation = useMutation({
    mutationFn: async () => {
      const wsId = selectedWorkspaceId || (workspaces[0]?.id || "")
      if (!wsId) throw new Error("Vui lòng chọn hoặc tạo Workspace trước khi tải tài liệu.")
      if (files.length === 0) throw new Error("Vui lòng chọn ít nhất một tệp tin.")

      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        await documentApi.upload(wsId, file, (p) => setProgress(Math.round(((i + p / 100) / files.length) * 100)))
      }
    },
    onSuccess: () => {
      setIsSuccess(true)
      void queryClient.invalidateQueries({ queryKey: ["documents"] })
      void queryClient.invalidateQueries({ queryKey: ["dashboardOverview"] })
      void queryClient.invalidateQueries({ queryKey: ["workspaces"] })
      void queryClient.invalidateQueries({ queryKey: ["search"] })
      setTimeout(() => {
        setIsSuccess(false)
        setFiles([])
        setProgress(0)
        onOpenChange(false)
      }, 1200)
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail || err.message || "Tải tài liệu thất bại.")
    },
  })

  // URL Import Mutation
  const uploadUrlMutation = useMutation({
    mutationFn: async () => {
      const wsId = selectedWorkspaceId || (workspaces[0]?.id || "")
      if (!wsId) throw new Error("Vui lòng chọn Workspace trước.")
      if (!url.trim()) throw new Error("Vui lòng nhập đường dẫn URL hợp lệ.")

      return await documentApi.uploadUrl({
        workspace_id: wsId,
        url,
        title: urlTitle || undefined,
      })
    },
    onSuccess: () => {
      setIsSuccess(true)
      void queryClient.invalidateQueries({ queryKey: ["documents"] })
      void queryClient.invalidateQueries({ queryKey: ["dashboardOverview"] })
      void queryClient.invalidateQueries({ queryKey: ["workspaces"] })
      void queryClient.invalidateQueries({ queryKey: ["search"] })
      setTimeout(() => {
        setIsSuccess(false)
        setUrl("")
        setUrlTitle("")
        onOpenChange(false)
      }, 1200)
    },
    onError: (err: any) => {
      setError(err?.response?.data?.detail || err.message || "Nhập URL thất bại.")
    },
  })

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFiles(Array.from(e.dataTransfer.files))
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFiles(Array.from(e.target.files))
    }
  }

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index))
  }

  const isUploading = uploadFileMutation.isPending || uploadUrlMutation.isPending

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md p-0 overflow-hidden border border-border/60 bg-card text-card-foreground shadow-2xl rounded-2xl">
        <DialogHeader className="p-5 border-b border-border/40 pb-4">
          <DialogTitle className="text-lg font-bold flex items-center gap-2">
            <UploadCloud className="h-5 w-5 text-primary" />
            Tải tài liệu vào Kho kiến thức
          </DialogTitle>
        </DialogHeader>

        <div className="p-5 space-y-4">
          {/* Workspace Selector */}
          <div className="space-y-1.5">
            <Label className="text-xs font-semibold">Chọn Workspace lưu trữ</Label>
            <Select value={selectedWorkspaceId} onValueChange={setSelectedWorkspaceId}>
              <SelectTrigger className="h-9 text-xs bg-background">
                <SelectValue placeholder="Chọn Workspace..." />
              </SelectTrigger>
              <SelectContent>
                {workspaces.map((ws) => (
                  <SelectItem key={ws.id} value={ws.id}>
                    {ws.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Tab Selector */}
          <div className="flex rounded-lg bg-muted p-1 text-xs">
            <button
              onClick={() => setTab("file")}
              className={`flex-1 py-1.5 font-medium rounded-md transition-all flex items-center justify-center gap-1.5 ${
                tab === "file" ? "bg-background text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <FileText className="h-3.5 w-3.5" />
              Tải tệp tin
            </button>
            <button
              onClick={() => setTab("url")}
              className={`flex-1 py-1.5 font-medium rounded-md transition-all flex items-center justify-center gap-1.5 ${
                tab === "url" ? "bg-background text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <LinkIcon className="h-3.5 w-3.5" />
              Nhập từ URL
            </button>
            <button
              onClick={() => setTab("ocr")}
              className={`flex-1 py-1.5 font-medium rounded-md transition-all flex items-center justify-center gap-1.5 ${
                tab === "ocr" ? "bg-background text-foreground shadow-xs" : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Image className="h-3.5 w-3.5" />
              Tải ảnh (OCR)
            </button>
          </div>

          {error && (
            <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-3 text-xs text-destructive">
              {error}
            </div>
          )}

          {isSuccess ? (
            <div className="py-8 text-center space-y-2">
              <CheckCircle2 className="h-10 w-10 text-emerald-500 mx-auto animate-bounce" />
              <p className="text-sm font-bold text-foreground">Tải tài liệu thành công!</p>
              <p className="text-xs text-muted-foreground">Tài liệu đã được lưu và đưa vào xử lý RAG.</p>
            </div>
          ) : tab === "file" ? (
            <div className="space-y-3">
              {/* Drag & Drop Zone */}
              <div
                onDragOver={(e) => e.preventDefault()}
                onDrop={handleFileDrop}
                className="flex flex-col items-center justify-center border-2 border-dashed border-border/60 hover:border-primary/50 bg-muted/20 hover:bg-primary/5 rounded-xl p-6 transition-all text-center cursor-pointer relative"
              >
                <input
                  type="file"
                  multiple
                  accept=".pdf,.docx,.txt,.md"
                  onChange={handleFileSelect}
                  className="absolute inset-0 opacity-0 cursor-pointer"
                />
                <UploadCloud className="h-8 w-8 text-primary/70 mb-2" />
                <p className="text-xs font-semibold text-foreground">Kéo thả tệp tin vào đây hoặc bấm để chọn</p>
                <p className="text-[11px] text-muted-foreground mt-1">Hỗ trợ PDF, DOCX, TXT, MD (Tối đa 50MB)</p>
              </div>

              {/* Selected Files Preview List */}
              {files.length > 0 && (
                <div className="space-y-1.5 max-h-36 overflow-y-auto pr-1 scrollbar-thin">
                  {files.map((file, idx) => (
                    <div key={idx} className="flex items-center justify-between p-2 rounded-lg border border-border/40 bg-card text-xs">
                      <div className="flex items-center gap-2 truncate">
                        <FileText className="h-4 w-4 text-blue-500 shrink-0" />
                        <span className="truncate font-medium">{file.name}</span>
                        <span className="text-[10px] text-muted-foreground font-mono">({(file.size / 1024).toFixed(0)} KB)</span>
                      </div>
                      <button onClick={() => removeFile(idx)} className="text-muted-foreground hover:text-destructive">
                        <X className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  ))}
                </div>
              )}

              {/* Progress */}
              {isUploading && progress > 0 && (
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px] font-medium text-muted-foreground">
                    <span>Đang tải lên...</span>
                    <span>{progress}%</span>
                  </div>
                  <Progress value={progress} className="h-1.5" />
                </div>
              )}
            </div>
          ) : tab === "url" ? (
            <div className="space-y-3">
              <div className="space-y-1">
                <Label className="text-xs">Địa chỉ trang web (URL)</Label>
                <Input
                  placeholder="https://example.com/article"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="h-9 text-xs"
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Tiêu đề tùy chọn</Label>
                <Input
                  placeholder="Ví dụ: Bài viết học tập Python"
                  value={urlTitle}
                  onChange={(e) => setUrlTitle(e.target.value)}
                  className="h-9 text-xs"
                />
              </div>
            </div>
          ) : (
            <div className="p-6 border border-dashed border-border/60 rounded-xl text-center space-y-2 bg-muted/10">
              <Image className="h-8 w-8 mx-auto text-purple-500/70" />
              <p className="text-xs font-semibold text-foreground">Tải ảnh chụp tài liệu (OCR Pipeline)</p>
              <p className="text-[11px] text-muted-foreground">
                Tải ảnh PNG/JPG để AI tự động trích xuất văn bản & chuyển đổi thành Markdown.
              </p>
            </div>
          )}
        </div>

        <DialogFooter className="p-4 border-t border-border/40 bg-muted/20 gap-2">
          <Button variant="outline" size="sm" onClick={() => onOpenChange(false)} className="h-9 text-xs">
            Hủy
          </Button>
          <Button
            size="sm"
            disabled={isUploading || (tab === "file" && files.length === 0) || (tab === "url" && !url)}
            onClick={() => {
              setError(null)
              if (tab === "file") uploadFileMutation.mutate()
              else if (tab === "url") uploadUrlMutation.mutate()
            }}
            className="h-9 text-xs gap-1.5"
          >
            {isUploading ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Đang xử lý...
              </>
            ) : (
              <>
                <Plus className="h-3.5 w-3.5" />
                Bắt đầu tải lên
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
