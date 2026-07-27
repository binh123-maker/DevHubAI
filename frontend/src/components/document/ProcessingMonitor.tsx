import { useState, useEffect } from "react"
import { CheckCircle2, Clock, Loader2, AlertCircle, RefreshCw, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"

interface ProcessingMonitorProps {
  status: string
  errorMessage?: string | null
  onRetry?: () => void
  isRetrying?: boolean
}

export function ProcessingMonitor({ status, errorMessage, onRetry, isRetrying = false }: ProcessingMonitorProps) {
  const [seconds, setSeconds] = useState(0)

  useEffect(() => {
    if (status === "PROCESSING" || status === "UPLOADING") {
      const timer = setInterval(() => setSeconds((s) => s + 1), 1000)
      return () => clearInterval(timer)
    }
  }, [status])

  const steps = [
    { key: "UPLOADING", label: "Uploading", progress: 20 },
    { key: "EXTRACTING", label: "Extracting Text", progress: 40 },
    { key: "OCR", label: "OCR Analysis", progress: 60 },
    { key: "CHUNKING", label: "Chunking", progress: 75 },
    { key: "EMBEDDING", label: "Embedding & Vector Index", progress: 90 },
    { key: "PROCESSED", label: "Completed", progress: 100 },
  ]

  const getStepStatus = (stepKey: string) => {
    if (status === "PROCESSED") return "completed"
    if (status === "FAILED") return "failed"
    if (status === stepKey || (status === "PROCESSING" && stepKey === "CHUNKING")) return "active"
    return "pending"
  }

  const currentProgress = status === "PROCESSED" ? 100 : status === "FAILED" ? 100 : Math.min(85, 20 + seconds * 5)

  return (
    <div className="rounded-2xl border border-border/60 bg-card/80 p-4 space-y-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          <h4 className="text-sm font-bold text-foreground">Trạng thái xử lý tài liệu</h4>
        </div>
        <span className="flex items-center gap-1 text-xs font-mono text-muted-foreground">
          <Clock className="h-3.5 w-3.5" />
          <span>Thời gian: {seconds}s</span>
        </span>
      </div>

      <Progress value={currentProgress} className="h-2 rounded-full" />

      {/* Steps Horizontal Bar */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 text-xs">
        {steps.map((step) => {
          const st = getStepStatus(step.key)
          return (
            <div
              key={step.key}
              className={`p-2 rounded-xl border flex flex-col items-center justify-center text-center gap-1 transition-all ${
                st === "completed"
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-600 dark:text-emerald-400 font-medium"
                  : st === "active"
                  ? "bg-blue-500/15 border-blue-500/50 text-blue-600 dark:text-blue-400 font-bold animate-pulse"
                  : st === "failed"
                  ? "bg-rose-500/10 border-rose-500/30 text-rose-600 dark:text-rose-400"
                  : "bg-muted/30 border-border/40 text-muted-foreground opacity-60"
              }`}
            >
              {st === "completed" ? (
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500" />
              ) : st === "active" ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin text-blue-500" />
              ) : st === "failed" ? (
                <AlertCircle className="h-3.5 w-3.5 text-rose-500" />
              ) : (
                <div className="h-2 w-2 rounded-full bg-muted-foreground/40" />
              )}
              <span className="text-[10px] leading-tight font-semibold">{step.label}</span>
            </div>
          )
        })}
      </div>

      {/* Failed Diagnostics & Retry Button (Parts 11 & 23) */}
      {status === "FAILED" && (
        <div className="p-3 rounded-xl border border-rose-500/40 bg-rose-500/10 text-rose-600 dark:text-rose-400 text-xs space-y-2 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <p className="font-bold flex items-center gap-1">
              <AlertCircle className="h-4 w-4 shrink-0" />
              Chẩn đoán nguyên nhân thất bại:
            </p>
            <p className="text-[11px] font-mono mt-0.5 opacity-90">
              {errorMessage || "Lỗi xử lý tài liệu không xác định (OCR failed / PDF encrypted / Timeout)."}
            </p>
          </div>
          {onRetry && (
            <Button
              size="sm"
              variant="destructive"
              disabled={isRetrying}
              onClick={onRetry}
              className="h-8 text-xs gap-1.5 font-bold shrink-0 shadow-sm"
            >
              {isRetrying ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <RefreshCw className="h-3.5 w-3.5" />}
              <span>Thử lại (Retry)</span>
            </Button>
          )}
        </div>
      )}
    </div>
  )
}
