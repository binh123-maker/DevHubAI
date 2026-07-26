import { useState } from "react"
import ReactMarkdown from "react-markdown"
import remarkMath from "remark-math"
import rehypeKatex from "rehype-katex"
import rehypeRaw from "rehype-raw"
import "katex/dist/katex.min.css"
import { motion } from "framer-motion"
import { Bot, User, ThumbsUp, ThumbsDown, Copy, RefreshCw, Bookmark, Check, ChevronDown, Globe, FolderOpen } from "lucide-react"

import type { ChatMessage } from "@/types/chat.types"
import { CitationPanel } from "./CitationPanel"
import { AnswerSourcesSummary } from "./AnswerSourcesSummary"
import { MessageActions } from "./MessageActions"
import { SuggestedFollowUps } from "./SuggestedFollowUps"
import { CodeBlock } from "./CodeBlock"
import { InlineCitationPopover } from "./InlineCitationPopover"
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

  const handleCopyCitations = () => {
    let text = message.content
    if (message.citations && message.citations.length > 0) {
      text += "\n\n--- Trích dẫn nguồn (Sources) ---\n"
      message.citations.forEach((c, idx) => {
        text += `[${idx + 1}] ${c.document_name} ${c.page_number ? `(Trang ${c.page_number})` : ""}\n`
      })
    }
    navigator.clipboard.writeText(text)
    setIsCopied(true)
    setTimeout(() => setIsCopied(false), 2000)
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`flex gap-3 text-sm ${isUser ? "justify-end" : "justify-start"}`}
    >
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground font-bold shadow-xs">
          <Bot className="h-4 w-4" />
        </div>
      )}

      <div
        className={`max-w-2xl rounded-2xl p-4 shadow-xs space-y-3 ${
          isUser
            ? "bg-primary text-primary-foreground font-medium rounded-tr-xs"
            : "bg-card border border-border/60 text-card-foreground rounded-tl-xs"
        }`}
      >
        {/* Search Scope Badge if Assistant */}
        {!isUser && (
          <div className="flex items-center justify-between border-b border-border/40 pb-2">
            <span
              className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-extrabold uppercase tracking-wider ${
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

        {/* Answer Sources Summary Box if Assistant */}
        {!isUser && (
          <AnswerSourcesSummary
            documentCount={message.citations?.length || 2}
            chunkCount={(message.citations?.length || 2) * 3}
            searchTimeMs={380}
          />
        )}

        {/* Message Content with Custom CodeBlock & Citation Popovers */}
        <div className="prose dark:prose-invert max-w-none text-xs sm:text-sm leading-relaxed">
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
                  <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-[12px] text-primary" {...props}>
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

        {/* Citations Panel */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <CitationPanel citations={message.citations} />
        )}

        {/* AI Action Chips */}
        {!isUser && <MessageActions onActionClick={onSendActionPrompt} />}

        {/* Toolbar & Feedback Actions */}
        {!isUser ? (
          <div className="flex items-center justify-between border-t border-border/30 pt-2 text-xs text-muted-foreground">
            <div className="flex items-center gap-1 flex-wrap">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setFeedback(feedback === "up" ? null : "up")}
                className={`h-7 px-2 text-[11px] gap-1 ${feedback === "up" ? "text-emerald-500 font-bold bg-emerald-500/10" : ""}`}
                title="Hữu ích"
              >
                <ThumbsUp className="h-3.5 w-3.5" />
                <span>Hữu ích</span>
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setFeedback(feedback === "down" ? null : "down")}
                className={`h-7 px-2 text-[11px] gap-1 ${feedback === "down" ? "text-destructive font-bold bg-destructive/10" : ""}`}
                title="Chưa tốt"
              >
                <ThumbsDown className="h-3.5 w-3.5" />
              </Button>

              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="h-7 px-2 text-[11px] gap-1">
                    {isCopied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
                    <span>Sao chép</span>
                    <ChevronDown className="h-3 w-3" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="start" className="w-44 text-xs">
                  <DropdownMenuItem onClick={handleCopyMarkdown} className="cursor-pointer">
                    Copy dạng Markdown
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleCopyPlainText} className="cursor-pointer">
                    Copy văn bản thuần (Plain Text)
                  </DropdownMenuItem>
                  <DropdownMenuItem onClick={handleCopyCitations} className="cursor-pointer">
                    Copy kèm Nguồn trích dẫn
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              {isLastAssistantMessage && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={onRegenerate}
                  className="h-7 px-2 text-[11px] gap-1 hover:text-foreground"
                  title="Tạo lại câu trả lời"
                >
                  <RefreshCw className="h-3.5 w-3.5" />
                  <span>Tạo lại</span>
                </Button>
              )}

              <Button
                variant="ghost"
                size="sm"
                onClick={() => setIsSaved(!isSaved)}
                className={`h-7 px-2 text-[11px] gap-1 ${isSaved ? "text-amber-500 font-bold" : ""}`}
                title="Lưu vào ghi chú"
              >
                <Bookmark className="h-3.5 w-3.5" />
                <span>{isSaved ? "Đã lưu" : "Lưu"}</span>
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

        {/* Suggested Follow-up Questions */}
        {!isUser && isLastAssistantMessage && (
          <SuggestedFollowUps onFollowUpClick={onSendActionPrompt} />
        )}
      </div>

      {isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-muted text-foreground font-bold border border-border">
          <User className="h-4 w-4 text-primary" />
        </div>
      )}
    </motion.div>
  )
}

