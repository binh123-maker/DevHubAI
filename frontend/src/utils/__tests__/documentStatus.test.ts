import { describe, it, expect } from "vitest"
import {
  normalizeDocumentStatus,
  DocumentStatus,
  isDocumentProcessed,
  isDocumentProcessing,
  isDocumentFailed,
} from "../documentStatus"

describe("Document Status Mapper & Normalizer", () => {
  it("maps lowercase 'processed' to DocumentStatus.PROCESSED", () => {
    expect(normalizeDocumentStatus("processed")).toBe(DocumentStatus.PROCESSED)
  })

  it("maps uppercase 'PROCESSED' to DocumentStatus.PROCESSED", () => {
    expect(normalizeDocumentStatus("PROCESSED")).toBe(DocumentStatus.PROCESSED)
  })

  it("maps mixed case 'Processed' to DocumentStatus.PROCESSED", () => {
    expect(normalizeDocumentStatus("Processed")).toBe(DocumentStatus.PROCESSED)
  })

  it("maps alias strings ('completed', 'ready', 'indexed', 'vectorized', 'success') to DocumentStatus.PROCESSED", () => {
    const aliases = ["completed", "ready", "indexed", "vectorized", "success", "COMPLETED", "READY"]
    aliases.forEach((alias) => {
      expect(normalizeDocumentStatus(alias)).toBe(DocumentStatus.PROCESSED)
    })
  })

  it("maps processing variants ('processing', 'PROCESSING', 'uploading', 'extracting') to DocumentStatus.PROCESSING", () => {
    const variants = ["processing", "PROCESSING", "uploading", "UPLOADING", "extracting", "chunking", "embedding"]
    variants.forEach((v) => {
      expect(normalizeDocumentStatus(v)).toBe(DocumentStatus.PROCESSING)
    })
  })

  it("maps pending variants ('pending', 'queued') to DocumentStatus.PENDING", () => {
    expect(normalizeDocumentStatus("pending")).toBe(DocumentStatus.PENDING)
    expect(normalizeDocumentStatus("queued")).toBe(DocumentStatus.PENDING)
  })

  it("maps failed variants ('failed', 'FAILED', 'error') to DocumentStatus.FAILED", () => {
    expect(normalizeDocumentStatus("failed")).toBe(DocumentStatus.FAILED)
    expect(normalizeDocumentStatus("FAILED")).toBe(DocumentStatus.FAILED)
    expect(normalizeDocumentStatus("error")).toBe(DocumentStatus.FAILED)
  })

  it("defaults null or undefined to DocumentStatus.PENDING", () => {
    expect(normalizeDocumentStatus(null)).toBe(DocumentStatus.PENDING)
    expect(normalizeDocumentStatus(undefined)).toBe(DocumentStatus.PENDING)
    expect(normalizeDocumentStatus("")).toBe(DocumentStatus.PENDING)
  })

  it("maps unknown strings (e.g. 'abcxyz') to DocumentStatus.UNKNOWN", () => {
    expect(normalizeDocumentStatus("abcxyz")).toBe(DocumentStatus.UNKNOWN)
  })

  it("verifies boolean helper functions", () => {
    expect(isDocumentProcessed("processed")).toBe(true)
    expect(isDocumentProcessed("failed")).toBe(false)

    expect(isDocumentProcessing("processing")).toBe(true)
    expect(isDocumentProcessing("uploading")).toBe(true)
    expect(isDocumentProcessing("processed")).toBe(false)

    expect(isDocumentFailed("failed")).toBe(true)
    expect(isDocumentFailed("processed")).toBe(false)
  })
})
