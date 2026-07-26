import React, { useState } from "react"
import { Copy, Check, Download, WrapText, Maximize2, Minimize2, ChevronDown, ChevronUp, Code } from "lucide-react"
import { Button } from "@/components/ui/button"

interface CodeBlockProps {
  language?: string
  code: string
}

export const CodeBlock = React.memo(function CodeBlock({ language = "code", code }: CodeBlockProps) {
  const [isCopied, setIsCopied] = useState(false)
  const [isWrapped, setIsWrapped] = useState(false)
  const [showLineNumbers, setShowLineNumbers] = useState(true)
  const [isExpanded, setIsExpanded] = useState(false)
  const [isFullscreen, setIsFullscreen] = useState(false)

  const lines = code.trim().split("\n")
  const isLongCode = lines.length > 15
  const displayedLines = isLongCode && !isExpanded ? lines.slice(0, 12) : lines

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setIsCopied(true)
    setTimeout(() => setIsCopied(false), 2000)
  }

  const handleDownload = () => {
    const extMap: Record<string, string> = {
      python: "py",
      javascript: "js",
      typescript: "ts",
      jsx: "jsx",
      tsx: "tsx",
      html: "html",
      css: "css",
      sql: "sql",
      json: "json",
      bash: "sh",
      markdown: "md",
    }
    const ext = extMap[language.toLowerCase()] || "txt"
    const blob = new Blob([code], { type: "text/plain;charset=utf-8" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `code_snippet.${ext}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <>
      <div
        className={`my-3 overflow-hidden rounded-xl border border-border/70 bg-muted/40 shadow-xs transition-all ${
          isFullscreen
            ? "fixed inset-4 z-50 flex flex-col bg-background/95 backdrop-blur-xl shadow-2xl border-primary/40 my-0"
            : ""
        }`}
      >
        {/* Header Toolbar */}
        <div className="flex items-center justify-between border-b border-border/50 bg-card/80 px-3 py-1.5 text-xs text-muted-foreground shrink-0">
          <div className="flex items-center gap-2 font-mono font-semibold text-primary">
            <Code className="h-3.5 w-3.5" />
            <span className="uppercase text-[11px] tracking-wider">{language || "text"}</span>
            <span className="text-[10px] text-muted-foreground/60">({lines.length} lines)</span>
          </div>

          <div className="flex items-center gap-1">
            {/* Wrap Lines Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsWrapped(!isWrapped)}
              className={`h-7 w-7 ${isWrapped ? "text-primary bg-primary/10" : ""}`}
              title="Bật/Tắt Tự động xuống dòng (Line Wrap)"
            >
              <WrapText className="h-3.5 w-3.5" />
            </Button>

            {/* Line Numbers Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowLineNumbers(!showLineNumbers)}
              className={`h-7 w-7 font-mono font-bold text-[11px] ${showLineNumbers ? "text-primary bg-primary/10" : ""}`}
              title="Hiện/Ẩn Số dòng"
            >
              #
            </Button>

            {/* Download Code */}
            <Button
              variant="ghost"
              size="icon"
              onClick={handleDownload}
              className="h-7 w-7 text-muted-foreground hover:text-foreground"
              title="Tải tập tin code về máy"
            >
              <Download className="h-3.5 w-3.5" />
            </Button>

            {/* Copy Button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleCopy}
              className="h-7 px-2 text-[11px] gap-1 font-semibold hover:text-foreground"
              title="Sao chép toàn bộ mã nguồn"
            >
              {isCopied ? (
                <>
                  <Check className="h-3.5 w-3.5 text-emerald-500" />
                  <span className="text-emerald-500">Đã chép</span>
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5" />
                  <span>Copy</span>
                </>
              )}
            </Button>

            {/* Fullscreen Toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsFullscreen(!isFullscreen)}
              className="h-7 w-7 text-muted-foreground hover:text-foreground"
              title={isFullscreen ? "Thu nhỏ xem thường" : "Xem Toàn màn hình (Fullscreen)"}
            >
              {isFullscreen ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
            </Button>
          </div>
        </div>

        {/* Code Content View */}
        <div className={`relative overflow-auto p-3 text-xs font-mono leading-relaxed scrollbar-hover flex-1 ${
          isWrapped ? "whitespace-pre-wrap break-words" : "whitespace-pre"
        }`}>
          <table className="w-full border-collapse">
            <tbody>
              {displayedLines.map((lineContent, idx) => (
                <tr key={idx} className="hover:bg-accent/40 transition-colors">
                  {showLineNumbers && (
                    <td className="w-8 select-none pr-3 text-right text-[10px] text-muted-foreground/50 border-r border-border/30 font-mono">
                      {idx + 1}
                    </td>
                  )}
                  <td className={`${showLineNumbers ? "pl-3" : "pl-1"} text-foreground`}>
                    {lineContent || " "}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Collapse / Expand Footer if Code > 15 lines */}
        {isLongCode && !isFullscreen && (
          <div className="border-t border-border/40 bg-card/60 p-1.5 text-center shrink-0">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="h-7 px-3 text-[11px] font-semibold text-primary gap-1"
            >
              {isExpanded ? (
                <>
                  <span>Thu gọn mã ({lines.length} dòng)</span>
                  <ChevronUp className="h-3.5 w-3.5" />
                </>
              ) : (
                <>
                  <span>Xem thêm {lines.length - 12} dòng còn lại</span>
                  <ChevronDown className="h-3.5 w-3.5" />
                </>
              )}
            </Button>
          </div>
        )}
      </div>

      {/* Backdrop overlay for Fullscreen mode */}
      {isFullscreen && (
        <div
          onClick={() => setIsFullscreen(false)}
          className="fixed inset-0 bg-background/80 backdrop-blur-md z-40"
        />
      )}
    </>
  )
})
