import { useMutation, useQueryClient } from "@tanstack/react-query"
import { UploadCloud, X, RefreshCw, XCircle } from "lucide-react"
import { useCallback, useRef, useState } from "react"
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

export function UploadDocumentModal({ open, onOpenChange, workspaceId, folderId }: UploadDocumentModalProps) {
  const queryClient = useQueryClient()
  const abortControllerRef = useRef<AbortController | null>(null)
  const [files, setFiles] = useState<File[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [progress, setProgress] = useState(0)
  const [currentFileIndex, setCurrentFileIndex] = useState(0)
  const [completedFiles, setCompletedFiles] = useState(0)
  const [currentFileName, setCurrentFileName] = useState("")
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [error, setError] = useState<string | null>(null)

  const MAX_SIZE_MB = parseInt(import.meta.env.VITE_MAX_UPLOAD_SIZE_MB || "100", 10)

  const uploadMutation = useMutation({
    mutationFn: async () => {
    abortControllerRef.current = new AbortController()

    let completed = 0

    for (let i = 0; i < files.length; i++) {
      const file = files[i]

      setCurrentFileIndex(i + 1)
      setCurrentFileName(file.name)
      setProgress(0)

      try {
        const uploadTitle =
          files.length === 1
            ? (title || file.name.replace(/\.[^/.]+$/, ""))
            : file.name.replace(/\.[^/.]+$/, "")

        await documentApi.upload(
          workspaceId,
          file,
          setProgress,
          folderId,
          uploadTitle,
          description,
          abortControllerRef.current.signal
        )

        completed++
        setCompletedFiles(completed)

      } catch (err) {
        console.error(file.name, err)
      }
    }
  },
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["documents", workspaceId] })
      handleClose()
      setCompletedFiles(0)
      setCurrentFileIndex(0)
      setCurrentFileName("")
    },
    onError: (err) => {
      if (axios.isCancel(err)) {
        setError("Tải lên đã bị hủy.")
      } else if (axios.isAxiosError(err) && err.response) {
        if (err.response.status === 413) {
          setError(`File quá lớn. Vui lòng chọn file nhỏ hơn ${MAX_SIZE_MB}MB.`)
        } else if (err.response.status === 415 || err.response.status === 422) {
          setError("Định dạng file không được hỗ trợ.")
        } else {
          setError(err.response.data?.detail || "Không thể tải lên tài liệu.")
        }
      } else {
        setError("Đã xảy ra lỗi không xác định.")
      }
      setProgress(0)
      abortControllerRef.current = null
    },
  })

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

    const accepted: File[] = []

    for (const selectedFile of Array.from(selectedFiles)) {
      const ext = selectedFile.name
        .substring(selectedFile.name.lastIndexOf("."))
        .toLowerCase()

      if (!validExtensions.includes(ext)) {
        continue
      }

      if (selectedFile.size > MAX_SIZE_MB * 1024 * 1024) {
        continue
      }

      accepted.push(selectedFile)
    }

    if (accepted.length === 0) {
      setError("Không có file hợp lệ.")
      return
    }

    setFiles(accepted)
    setError(null)

    if (!title) {
      setTitle(accepted[0].name.replace(/\.[^/.]+$/, ""))
    }
  }

  const handleClose = () => {
    if (uploadMutation.isPending && abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
    setFiles([])
    setTitle("")
    setDescription("")
    setProgress(0)
    setError(null)
    uploadMutation.reset()
    onOpenChange(false)
  }

  const handleUpload = () => {
    if (files.length === 0) return
    setError(null)
    setProgress(0)
    uploadMutation.mutate()
  }

  const handleCancel = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort()
    }
  }

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Tải lên tài liệu</DialogTitle>
          <DialogDescription>
            Hỗ trợ các định dạng: PDF, DOCX, TXT, MD. Dung lượng tối đa {MAX_SIZE_MB}MB.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {files.length === 0 ? (
            <div
              className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-10 text-center transition-colors ${
                isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/25 hover:border-primary/50"
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <UploadCloud className="mb-4 h-10 w-10 text-muted-foreground" />
              <p className="mb-1 font-medium">Kéo thả file vào đây</p>
              <p className="text-sm text-muted-foreground mb-4">hoặc</p>
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
                Chọn file từ máy tính
              </Button>
            </div>
          ) : (
            <div className="rounded-lg border p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3 overflow-hidden">
                  <div className="bg-blue-100 p-2 rounded text-blue-600">
                    <UploadCloud className="h-5 w-5" />
                  </div>
                  <div className="space-y-2">
                    {files.map((file) => (
                      <div key={`${file.name}-${file.size}-${file.lastModified}`}>
                        <p className="truncate font-medium text-sm">{file.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
                {!uploadMutation.isPending && (
                  <Button variant="ghost" size="icon" onClick={() => setFiles([])}>
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
              
              {files.length === 1 && (
                <div className="space-y-3">
                  <div className="space-y-1">
                    <Label className="text-xs text-muted-foreground">
                      Tên hiển thị
                    </Label>

                    <Input
                      value={title}
                      onChange={(e) => setTitle(e.target.value)}
                      disabled={uploadMutation.isPending}
                      className="h-8"
                    />
                  </div>

                  <div className="space-y-1">
                    <Label className="text-xs text-muted-foreground">
                      Mô tả (tuỳ chọn)
                    </Label>

                    <Input
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      disabled={uploadMutation.isPending}
                      className="h-8"
                    />
                  </div>
                </div>
              )}
              
              {uploadMutation.isPending && (
                <div className="mt-4 space-y-2">
                  <div className="space-y-1">

                      <p className="text-sm font-medium">

                          Đang tải

                          {currentFileIndex}/{files.length}

                      </p>

                      <p className="text-xs text-muted-foreground truncate">

                          {currentFileName}

                      </p>

                  </div>
                  <Progress value={progress} className="h-2" />
                  <div className="mt-4 space-y-2">

                      <div className="flex justify-between text-xs text-muted-foreground">
                          <span>Tiến độ tổng</span>
                          <span>
                              {completedFiles} / {files.length} file hoàn thành
                          </span>
                      </div>

                      <Progress
                          value={
                              files.length === 0
                                  ? 0
                                  : (completedFiles / files.length) * 100
                          }
                      />

                  </div>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="flex flex-col items-center justify-center p-3 mt-2 rounded-md bg-destructive/10 text-destructive text-sm border border-destructive/20 gap-2">
              <div className="flex items-center gap-2">
                <XCircle className="h-4 w-4" />
                <p>{error}</p>
              </div>
              {files.length > 0 && !uploadMutation.isPending && (
                <Button variant="outline" size="sm" onClick={handleUpload} className="mt-1 border-destructive text-destructive hover:bg-destructive hover:text-destructive-foreground">
                  <RefreshCw className="mr-2 h-3 w-3" />
                  Thử lại
                </Button>
              )}
            </div>
          )}
        </div>

        <div className="flex justify-end gap-2">
          {!uploadMutation.isPending ? (
            <>
              <Button variant="outline" onClick={handleClose}>
                Đóng
              </Button>
              <Button 
                onClick={handleUpload} 
                disabled={files.length === 0}
              >
                Tải lên
              </Button>
            </>
          ) : (
            <Button variant="destructive" onClick={handleCancel}>
              Hủy tải lên
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
