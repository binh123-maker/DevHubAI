import { useState } from "react"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import rehypeRaw from "rehype-raw"
import "katex/dist/katex.min.css"
import { motion } from "framer-motion"
import {
  Bot,
  User,
  ThumbsUp,
  ThumbsDown,
  Copy,
  RefreshCw,
  Bookmark,
  Check,
  Globe,
  FolderOpen,
  ShieldCheck,
  MoreHorizontal,
  ChevronDown,
  ChevronUp,
  Sparkles,
  HelpCircle,
  Layers,
  Maximize2,
  Play,
} from "lucide-react"

import type { ChatMessage, Citation } from "@/types/chat.types"
import { CodeBlock } from "./CodeBlock"
import { InlineCitationPopover } from "./InlineCitationPopover"
import { CitationCard } from "./CitationCard"
import { AITraceabilityDrawer } from "./AITraceabilityDrawer"
import { SourceComparisonPanel } from "./SourceComparisonPanel"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"

interface ChatMessageItemProps {
  message: ChatMessage
  isLastAssistantMessage: boolean
  chatMode?: string
  workspaceName?: string
  onSendActionPrompt: (promptText: string) => void
  onRegenerate: () => void
  onOpenCitationDock?: () => void
}

export function ChatMessageItem({
  message,
  isLastAssistantMessage,
  chatMode = "global",
  workspaceName,
  onSendActionPrompt,
  onRegenerate,
  onOpenCitationDock,
}: ChatMessageItemProps) {
  const isUser = message.role === "user"
  const [feedback, setFeedback] = useState<"up" | "down" | null>(null)
  const [isCopied, setIsCopied] = useState(false)
  const [isSaved, setIsSaved] = useState(false)
  const [showTraceability, setShowTraceability] = useState(false)
  const [compareCitation, setCompareCitation] = useState<Citation | null>(null)
  const [isCitationsExpanded, setIsCitationsExpanded] = useState(false)

  const handleCopyMarkdown = () => {
    navigator.clipboard.writeText(message.content)
    setIsCopied(true)
    setTimeout(() => setIsCopied(false), 2000)
  }

  const handleCopyPlainText = () => {
    const plain = message.content.replace(/[#*`_]/g, "")
    navigator.clipboard.writeText(plain)
    setIsCopied(true)
    setTimeout(() => setIsCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex gap-4 text-base my-4 max-w-[920px] mx-auto ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser && (
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-primary text-primary-foreground font-bold shadow-xs">
          <Bot className="h-5 w-5" />
        </div>
      )}

      <div
        className={`w-full max-w-[900px] rounded-[20px] p-6 shadow-xs space-y-4 ${
          isUser
            ? "bg-primary text-primary-foreground font-medium rounded-tr-xs ml-auto max-w-[700px]"
            : "bg-card border border-border/60 text-card-foreground rounded-tl-xs"
        }`}
      >
        {/* Scope Badge if Assistant */}
        {!isUser && (
          <div className="flex items-center justify-between border-b border-border/40 pb-2">
            <span
              className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[10px] font-extrabold uppercase tracking-wider ${
                chatMode === "global"
                  ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"
                  : "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20"
              }`}
            >
              {chatMode === "global" ? <Globe className="h-3 w-3" /> : <FolderOpen className="h-3 w-3" />}
              <span>{chatMode === "global" ? "GLOBAL SCOPE" : `WORKSPACE: ${workspaceName || "LOCKED"}`}</span>
            </span>
          </div>
        )}

        {/* Message Content with Typography 16px / line-height 1.8 */}
        <div className="prose dark:prose-invert max-w-none text-[16px] leading-[1.8] tracking-normal text-foreground">
          <ReactMarkdown
            remarkPlugins={[remarkMath]}
            rehypePlugins={[rehypeKatex, rehypeRaw]}
            components={{
              code({ node, inline, className, children, ...props }: any) {
                const match = /language-(\w+)/.exec(className || "")
                const codeString = String(children).replace(/\n$/, "")
                if (!inline && (match || codeString.includes("\n"))) {
                  return <CodeBlock language={match ? match[1] : "text"} code={codeString} />
                }
                return (
                  <code className="rounded-md bg-muted px-1.5 py-0.5 font-mono text-[13px] text-primary" {...props}>
                    {children}
                  </code>
                )
              },
              a({ node, children, href, ...props }: any) {
                const text = String(children)
                const citationIndexMatch = text.match(/^\[(\d+)\]$/)
                if (citationIndexMatch && message.citations) {
                  const citIdx = parseInt(citationIndexMatch[1], 10) - 1
                  const citationObj = message.citations[citIdx]
                  if (citationObj) {
                    return (
                      <InlineCitationPopover
                        index={citIdx + 1}
                        citation={citationObj}
                        onOpenDock={onOpenCitationDock}
                      />
                    )
                  }
                }
                return (
                  <a href={href} target="_blank" rel="noreferrer" className="text-primary underline font-medium" {...props}>
                    {children}
                  </a>
                )
              },
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>

        {/* Single Accordion Sources Card (RAG Evidence) */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <div className="rounded-xl border border-border/60 bg-muted/20 p-3 space-y-2">
            <div
              onClick={() => setIsCitationsExpanded(!isCitationsExpanded)}
              className="flex items-center justify-between cursor-pointer select-none"
            >
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold text-foreground">Sources ({message.citations.length})</span>
                <span className="text-xs text-muted-foreground truncate max-w-[300px]">
                  {message.citations[0]?.document_name} · 95% relevance · {message.citations.length * 3} chunks found
                </span>
              </div>
              <Button variant="ghost" size="sm" className="h-7 text-xs font-bold text-primary gap-1">
                <span>{isCitationsExpanded ? "Thu gọn" : "Expand"}</span>
                {isCitationsExpanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
              </Button>
            </div>

            {/* Lazy Accordion Content */}
            {isCitationsExpanded && (
              <div className="space-y-2 pt-2 border-t border-border/40 max-h-[300px] overflow-y-auto pr-1 scrollbar-thin animate-in fade-in duration-200">
                {message.citations.map((cit, idx) => (
                  <CitationCard
                    key={idx}
                    citation={cit}
                    rankIndex={idx}
                    onCompareClick={(c) => setCompareCitation(c)}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Progressive Answer Toolbar */}
        {!isUser ? (
          <div className="flex items-center justify-between border-t border-border/30 pt-2 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              {/* Copy Icon Button */}
              <Button
                variant="ghost"
                size="icon"
                onClick={handleCopyMarkdown}
                className="h-8 w-8 rounded-xl hover:text-foreground"
                title="Sao chép câu trả lời"
              >
                {isCopied ? <Check className="h-4 w-4 text-emerald-500" /> : <Copy className="h-4 w-4" />}
              </Button>

              {/* Regenerate Icon Button */}
              {isLastAssistantMessage && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={onRegenerate}
                  className="h-8 w-8 rounded-xl hover:text-foreground"
                  title="Tạo lại câu trả lời"
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              )}

              {/* Continue Action */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onSendActionPrompt("Hãy tiếp tục viết và phát triển thêm ý cho nội dung trên.")}
                className="h-8 px-2.5 rounded-xl text-xs gap-1 hover:text-foreground font-semibold"
                title="Viết tiếp"
              >
                <Play className="h-3.5 w-3.5 fill-current" />
                <span>Continue</span>
              </Button>

              {/* Thumbs Up / Down */}
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setFeedback(feedback === "up" ? null : "up")}
                className={`h-8 w-8 rounded-xl ${feedback === "up" ? "text-emerald-500 bg-emerald-500/10" : ""}`}
                title="Hữu ích"
              >
                <ThumbsUp className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setFeedback(feedback === "down" ? null : "down")}
                className={`h-8 w-8 rounded-xl ${feedback === "down" ? "text-destructive bg-destructive/10" : ""}`}
                title="Chưa tốt"
              >
                <ThumbsDown className="h-4 w-4" />
              </Button>

              {/* More (...) Progressive Dropdown Menu */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="h-8 w-8 rounded-xl text-muted-foreground hover:text-foreground">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-52 text-xs rounded-xl p-1">
                  <DropdownMenuItem
                    onClick={() => onSendActionPrompt("Hãy giải thích câu trả lời trên một cách đơn giản, dễ hiểu.")}
                    className="cursor-pointer gap-2 rounded-lg py-1.5"
                  >
                    <Sparkles className="h-3.5 w-3.5 text-primary" />
                    <span>Explain simpler</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => onSendActionPrompt("Hãy mở rộng và bổ sung thêm các chi tiết nâng cao cho câu trả lời trên.")}
                    className="cursor-pointer gap-2 rounded-lg py-1.5"
                  >
                    <Maximize2 className="h-3.5 w-3.5 text-indigo-500" />
                    <span>More detail</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => onSendActionPrompt("Tạo 3 câu hỏi trắc nghiệm RAG kiểm tra kiến thức về nội dung trên.")}
                    className="cursor-pointer gap-2 rounded-lg py-1.5"
                  >
                    <HelpCircle className="h-3.5 w-3.5 text-amber-500" />
                    <span>Quiz</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={() => onSendActionPrompt("Tạo bộ 5 thẻ ghi nhớ Flashcard từ nội dung trên.")}
                    className="cursor-pointer gap-2 rounded-lg py-1.5"
                  >
                    <Layers className="h-3.5 w-3.5 text-emerald-500" />
                    <span>Flashcards</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setIsSaved(!isSaved)} className="cursor-pointer gap-2 rounded-lg py-1.5">
                    <Bookmark className="h-3.5 w-3.5 text-purple-500" />
                    <span>{isSaved ? "Đã lưu ghi chú" : "Lưu vào ghi chú"}</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleCopyPlainText} className="cursor-pointer gap-2 rounded-lg py-1.5">
                    <Copy className="h-3.5 w-3.5 text-blue-500" />
                    <span>Sao chép văn bản thuần</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              {/* Traceability Trigger Button */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowTraceability(true)}
                className="h-8 px-2.5 rounded-xl text-xs gap-1 text-purple-600 dark:text-purple-400 hover:bg-purple-500/10 font-bold ml-2"
                title="Tại sao AI đưa ra câu trả lời này?"
              >
                <ShieldCheck className="h-3.5 w-3.5" />
                <span>AI Trace</span>
              </Button>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-end border-t border-primary-foreground/20 pt-1 text-[11px] text-primary-foreground/80 gap-2">
            <button onClick={handleCopyMarkdown} className="hover:underline flex items-center gap-1">
              <Copy className="h-3 w-3" />
              Copy
            </button>
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-2xl bg-muted text-foreground font-bold border border-border">
          <User className="h-5 w-5 text-primary" />
        </div>
      )}

      {/* Traceability Glass Center Modal */}
      <AITraceabilityDrawer
        isOpen={showTraceability}
        onClose={() => setShowTraceability(false)}
        userQuery={message.content.slice(0, 80)}
        citations={message.citations || []}
      />

      {/* Source Comparison Panel Modal */}
      <SourceComparisonPanel
        isOpen={Boolean(compareCitation)}
        onClose={() => setCompareCitation(null)}
        aiAnswer={message.content}
        citation={compareCitation}
      />
    </motion.div>
  )
}
