import type { LucideIcon } from "lucide-react"
import { CheckCircle2, Loader2, AlertCircle, HelpCircle, Clock } from "lucide-react"

export enum DocumentStatus {
  PENDING = "PENDING",
  PROCESSING = "PROCESSING",
  PROCESSED = "PROCESSED",
  FAILED = "FAILED",
  UNKNOWN = "UNKNOWN",
}

export interface StatusConfigItem {
  key: DocumentStatus
  label: string
  shortLabel: string
  colorClass: string
  badgeVariant: "default" | "secondary" | "destructive" | "outline"
  icon: LucideIcon
  spinIcon?: boolean
}

export const DOCUMENT_STATUS_CONFIG: Record<DocumentStatus, StatusConfigItem> = {
  [DocumentStatus.PROCESSED]: {
    key: DocumentStatus.PROCESSED,
    label: "Ready for RAG",
    shortLabel: "Đã xử lý",
    colorClass: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
    badgeVariant: "outline",
    icon: CheckCircle2,
    spinIcon: false,
  },
  [DocumentStatus.PROCESSING]: {
    key: DocumentStatus.PROCESSING,
    label: "Processing RAG",
    shortLabel: "Đang xử lý",
    colorClass: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
    badgeVariant: "outline",
    icon: Loader2,
    spinIcon: true,
  },
  [DocumentStatus.PENDING]: {
    key: DocumentStatus.PENDING,
    label: "Pending",
    shortLabel: "Chờ xử lý",
    colorClass: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
    badgeVariant: "outline",
    icon: Clock,
    spinIcon: false,
  },
  [DocumentStatus.FAILED]: {
    key: DocumentStatus.FAILED,
    label: "Failed",
    shortLabel: "Thất bại",
    colorClass: "bg-destructive/10 text-destructive border-destructive/20",
    badgeVariant: "destructive",
    icon: AlertCircle,
    spinIcon: false,
  },
  [DocumentStatus.UNKNOWN]: {
    key: DocumentStatus.UNKNOWN,
    label: "Unknown",
    shortLabel: "Không xác định",
    colorClass: "bg-muted text-muted-foreground border-border",
    badgeVariant: "secondary",
    icon: HelpCircle,
    spinIcon: false,
  },
}
