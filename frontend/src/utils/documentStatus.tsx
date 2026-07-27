import React from "react"
import { DocumentStatus, DOCUMENT_STATUS_CONFIG } from "@/constants/documentStatusConfig"

export { DocumentStatus }

/**
 * Normalizes any raw string status returned from backend APIs or local state into a standard DocumentStatus enum.
 * Supports legacy backend strings, aliases ("completed", "ready", "indexed", "vectorized", "success"), and case insensitivity.
 */
export function normalizeDocumentStatus(rawStatus?: string | null): DocumentStatus {
  if (!rawStatus || typeof rawStatus !== "string") {
    return DocumentStatus.PENDING
  }

  const s = rawStatus.trim().toLowerCase()

  // PROCESSED aliases
  if (
    s === "processed" ||
    s === "completed" ||
    s === "ready" ||
    s === "indexed" ||
    s === "vectorized" ||
    s === "success"
  ) {
    return DocumentStatus.PROCESSED
  }

  // PROCESSING aliases
  if (s === "processing" || s === "uploading" || s === "extracting" || s === "chunking" || s === "embedding") {
    return DocumentStatus.PROCESSING
  }

  // PENDING aliases
  if (s === "pending" || s === "queued") {
    return DocumentStatus.PENDING
  }

  // FAILED aliases
  if (s === "failed" || s === "error") {
    return DocumentStatus.FAILED
  }

  // Defensive fallback for unknown status strings
  console.warn(`[DocumentStatusMapper] Unrecognized status string received: "${rawStatus}". Mapping to DocumentStatus.UNKNOWN.`)
  return DocumentStatus.UNKNOWN
}

/** Helper: Returns true if normalized status is PROCESSED */
export function isDocumentProcessed(status?: string | null): boolean {
  return normalizeDocumentStatus(status) === DocumentStatus.PROCESSED
}

/** Helper: Returns true if normalized status is PROCESSING or PENDING */
export function isDocumentProcessing(status?: string | null): boolean {
  const norm = normalizeDocumentStatus(status)
  return norm === DocumentStatus.PROCESSING || norm === DocumentStatus.PENDING
}

/** Helper: Returns true if normalized status is FAILED */
export function isDocumentFailed(status?: string | null): boolean {
  return normalizeDocumentStatus(status) === DocumentStatus.FAILED
}

/** Helper: Returns true if normalized status is PENDING */
export function isDocumentPending(status?: string | null): boolean {
  return normalizeDocumentStatus(status) === DocumentStatus.PENDING
}

interface DocumentStatusBadgeProps {
  status?: string | null
  useShortLabel?: boolean
  className?: string
}

export const DocumentStatusBadge: React.FC<DocumentStatusBadgeProps> = ({
  status,
  useShortLabel = false,
  className = "",
}) => {
  const normStatus = normalizeDocumentStatus(status)
  const config = DOCUMENT_STATUS_CONFIG[normStatus] || DOCUMENT_STATUS_CONFIG[DocumentStatus.UNKNOWN]
  const Icon = config.icon

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-bold border transition-colors ${config.colorClass} ${className}`}
    >
      <Icon className={`h-3 w-3 ${config.spinIcon ? "animate-spin" : ""}`} />
      <span>{useShortLabel ? config.shortLabel : config.label}</span>
    </span>
  )
}
