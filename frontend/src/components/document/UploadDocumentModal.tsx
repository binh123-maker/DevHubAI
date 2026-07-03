import { useQueryClient } from "@tanstack/react-query"
import { UploadCloud, X, RefreshCw, XCircle, Link as LinkIcon, CheckCircle2, FileText } from "lucide-react"
import { useCallback, useState, useRef, useEffect } from "react"
import axios from "axios"

import { documentApi } from "@/api/document.api"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Progress } from "@/components/ui/progress"

interface UploadDocumentModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  workspaceId: string
  folderId?: string
}

type UploadStatus = "pending" | "uploading" | "success" | "error"

interface UploadItem {
  id: string
  file?: File
  url?: string
  title: string
  description: string
  progress: number
  status: UploadStatus
  error?: string
  abortController?: AbortController
}

export function UploadDocumentModal({ open, onOpenChange, workspaceId, folderId }: UploadDocumentModalProps) {
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<"file" | "url">("file")
  const [queue, setQueue] = useState<UploadItem[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)

  const queueRef = useRef<UploadItem[]>([])
  useEffect(() => {
    queueRef.current = queue
  }, [queue])

  // URL Tab State
  const [urlInput, setUrlInput] = useState("")
  const [urlTitle, setUrlTitle] = useState("")
  const [urlDesc, setUrlDesc] = useState("")

  const MAX_SIZE_MB = parseInt(import.meta.env.VITE_MAX_UPLOAD_SIZE_MB || "100", 10)

  // -- File Handlers --

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files)
    }
  }, [])

  const handleFileSelect = (selectedFiles: FileList) => {
    const validExtensions = [".pdf", ".docx", ".txt", ".md"]
    const newItems: UploadItem[] = []

    for (const file of Array.from(selectedFiles)) {
      const ext = file.name.substring(file.name.lastIndexOf(".")).toLowerCase()
      if (!validExtensions.includes(ext)) continue
      if (file.size > MAX_SIZE_MB * 1024 * 1024) continue

      newItems.push({
        id: Math.random().toString(36).substring(7),
        file,
        title: file.name.replace(/\.[^/.]+$/, ""),
        description: "",
        progress: 0,
        status: "pending",
      })
    }

    if (newItems.length > 0) {
      setQueue((prev) => [...prev, ...newItems])
    }
  }

  // -- URL Handlers --
  const handleAddUrl = () => {
    if (!urlInput.trim()) return
    const newItem: UploadItem = {
      id: Math.random().toString(36).substring(7),
      url: urlInput.trim(),
      title: urlTitle.trim() || urlInput.trim(),
      description: urlDesc.trim(),
      progress: 0,
      status: "pending",
    }
    setQueue((prev) => [...prev, newItem])
    setUrlInput("")
    setUrlTitle("")
    setUrlDesc("")
  }

  // -- Queue Processing --

  const processQueue = async () => {
    if (isProcessing) return
    setIsProcessing(true)

    const currentQueue = [...queue]
    for (let i = 0; i < currentQueue.length; i++) {
      const itemId = currentQueue[i].id
      const itemFile = currentQueue[i].file
      const itemUrl = currentQueue[i].url
      const itemTitle = currentQueue[i].title
      const itemDescription = currentQueue[i].description

      if (currentQueue[i].status === "success" || currentQueue[i].status === "uploading") continue

      // Skip if item was removed from queue (canceled) while waiting
      if (!queueRef.current.find(q => q.id === itemId)) continue

      const abortController = new AbortController()
      
      setQueue(prev => prev.map(q => q.id === itemId ? { ...q, status: "uploading", progress: 0, error: undefined, abortController } : q))

      try {
        if (itemFile) {
          await documentApi.upload(
            workspaceId,
            itemFile,
            (prog) => {
              setQueue(prev => prev.map(q => q.id === itemId ? { ...q, progress: prog } : q))
            },
            folderId,
            itemTitle,
            itemDescription,
            abortController.signal
          )
        } else if (itemUrl) {
          await documentApi.uploadUrl({
            workspace_id: workspaceId,
            folder_id: folderId,
            url: itemUrl,
            title: itemTitle,
            description: itemDescription,
          })
          setQueue(prev => prev.map(q => q.id === itemId ? { ...q, progress: 100 } : q))
        }
        setQueue(prev => prev.map(q => q.id === itemId ? { ...q, status: "success" } : q))
      } catch (err: any) {
        let errorMsg = err.response?.data?.detail || "Lỗi tải lên"
        if (axios.isCancel(err)) {
          errorMsg = "Đã hủy"
        }
        setQueue(prev => prev.map(q => q.id === itemId ? { ...q, status: "error", error: errorMsg } : q))
      }
    }
    
    void queryClient.invalidateQueries({ queryKey: ["documents", workspaceId] })
    setIsProcessing(false)
  }

  // -- Item Actions --

  const handleCancelItem = (id: string) => {
    setQueue((prev) => {
      const newQ = [...prev]
      const idx = newQ.findIndex(q => q.id === id)
      if (idx === -1) return prev
      
      const item = newQ[idx]
      if (item.status === "uploading" && item.abortController) {
        item.abortController.abort()
      } else {
        // Remove completely if pending or error
        newQ.splice(idx, 1)
      }
      return newQ
    })
  }

  const handleRetryItem = (id: string) => {
    setQueue((prev) => {
      const newQ = [...prev]
      const idx = newQ.findIndex(q => q.id === id)
      if (idx !== -1) {
        newQ[idx].status = "pending"
        newQ[idx].error = undefined
        newQ[idx].progress = 0
      }
      return newQ
    })
  }

  const handleClose = () => {
    if (isProcessing) {
      queue.forEach(item => {
        if (item.status === "uploading" && item.abortController) {
          item.abortController.abort()
        }
      })
    }
    setQueue([])
    setActiveTab("file")
    setUrlInput("")
    setUrlTitle("")
    setUrlDesc("")
    onOpenChange(false)
  }

  const pendingCount = queue.filter(q => q.status === "pending" || q.status === "error").length
  const allSuccess = queue.length > 0 && queue.every(q => q.status === "success")

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
      <DialogContent className="sm:max-w-[550px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Tải lên tài liệu</DialogTitle>
          <DialogDescription>
            Tải lên file từ máy tính hoặc nhập liên kết URL.
          </DialogDescription>
        </DialogHeader>

        <div className="flex w-full mb-2 mt-4 rounded-md border p-1 bg-muted">
          <button 
            className={`flex-1 rounded-sm py-1.5 text-sm font-medium transition-all ${activeTab === 'file' ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('file')}
          >
            Tải lên File
          </button>
          <button 
            className={`flex-1 rounded-sm py-1.5 text-sm font-medium transition-all ${activeTab === 'url' ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
            onClick={() => setActiveTab('url')}
          >
            Tải từ URL
          </button>
        </div>

        <div className="py-2">
          {activeTab === "file" && (
            <div
              className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
                isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50"
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <UploadCloud className="mb-4 h-10 w-10 text-muted-foreground" />
              <p className="mb-1 font-medium">Kéo thả file vào đây</p>
              <p className="text-sm text-muted-foreground mb-4">Hỗ trợ: PDF, DOCX, TXT, MD (Tối đa {MAX_SIZE_MB}MB)</p>
              <Input
                type="file"
                multiple
                className="hidden"
                id="file-upload"
                accept=".pdf,.docx,.txt,.md"
                onChange={(e) => {
                  if (e.target.files) handleFileSelect(e.target.files)
                }}
              />
              <Button variant="outline" onClick={() => document.getElementById("file-upload")?.click()}>
                Chọn file
              </Button>
            </div>
          )}

          {activeTab === "url" && (
            <div className="space-y-4 rounded-lg border p-4">
              <div className="space-y-2">
                <Label>Đường dẫn URL</Label>
                <Input 
                  placeholder="https://example.com/document.pdf" 
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Tên hiển thị (Tùy chọn)</Label>
                <Input 
                  placeholder="Tài liệu tham khảo" 
                  value={urlTitle}
                  onChange={(e) => setUrlTitle(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Mô tả (Tùy chọn)</Label>
                <Input 
                  placeholder="Mô tả ngắn gọn" 
                  value={urlDesc}
                  onChange={(e) => setUrlDesc(e.target.value)}
                />
              </div>
              <Button onClick={handleAddUrl} disabled={!urlInput.trim()} className="w-full">
                Thêm vào hàng đợi
              </Button>
            </div>
          )}

          {/* Queue View */}
          {queue.length > 0 && (
            <div className="mt-6 space-y-3">
              <h4 className="text-sm font-medium text-muted-foreground">Hàng đợi ({queue.length})</h4>
              <div className="max-h-[250px] overflow-y-auto pr-1 space-y-2">
                {queue.map((item) => (
                  <div key={item.id} className="relative overflow-hidden rounded-lg border p-3">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3 min-w-0">
                        <div className="bg-muted p-2 rounded shrink-0">
                          {item.file ? <FileText className="h-4 w-4" /> : <LinkIcon className="h-4 w-4" />}
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium truncate">{item.title}</p>
                          <p className="text-xs text-muted-foreground truncate">
                            {item.file ? `${(item.file.size / 1024 / 1024).toFixed(2)} MB` : item.url}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2 shrink-0">
                        {item.status === "success" && <CheckCircle2 className="h-5 w-5 text-green-500" />}
                        {item.status === "error" && (
                          <Button variant="ghost" size="icon" className="h-8 w-8 text-destructive" onClick={() => handleRetryItem(item.id)}>
                            <RefreshCw className="h-4 w-4" />
                          </Button>
                        )}
                        {item.status !== "success" && (
                          <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground hover:text-foreground" onClick={() => handleCancelItem(item.id)}>
                            <X className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </div>
                    
                    {item.status === "uploading" && (
                      <div className="mt-3 space-y-1.5">
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Đang xử lý...</span>
                          <span className="font-medium">{item.progress}%</span>
                        </div>
                        <Progress value={item.progress} className="h-1.5" />
                      </div>
                    )}
                    
                    {item.status === "error" && (
                      <p className="mt-2 text-xs text-destructive flex items-center gap-1">
                        <XCircle className="h-3 w-3" /> {item.error}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2 mt-2">
          {allSuccess ? (
            <Button onClick={handleClose}>Hoàn tất</Button>
          ) : (
            <>
              <Button variant="outline" onClick={handleClose} disabled={isProcessing}>
                Đóng
              </Button>
              <Button 
                onClick={() => void processQueue()} 
                disabled={pendingCount === 0 || isProcessing}
              >
                {isProcessing ? "Đang xử lý..." : "Tải lên"}
              </Button>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
