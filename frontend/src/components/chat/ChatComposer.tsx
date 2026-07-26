import React, { useRef, useEffect, useState } from "react"
import { Send, Paperclip, AtSign, Mic, Sparkles, Square, X, FileText } from "lucide-react"
import { SlashCommandPopover, SlashCommand } from "./SlashCommandPopover"
import { MentionPopover } from "./MentionPopover"
import { Button } from "@/components/ui/button"

interface ChatComposerProps {
  input: string
  setInput: (value: string) => void
  onSend: () => void
  activeChatId?: string
  isLoading?: boolean
  disabled?: boolean
  onStop?: () => void
  onPromptChipClick?: (text: string) => void
  showChips?: boolean
  attachedFiles?: File[]
  onAttachFiles?: (files: File[]) => void
  onRemoveFile?: (index: number) => void
}

export const ChatComposer = React.memo(function ChatComposer({
  input,
  setInput,
  onSend,
  activeChatId = "default",
  isLoading = false,
  disabled = false,
  onStop,
  onPromptChipClick,
  showChips = false,
  attachedFiles = [],
  onAttachFiles,
  onRemoveFile,
}: ChatComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [showSlashPopover, setShowSlashPopover] = useState(false)
  const [slashFilter, setSlashFilter] = useState("")
  const [showMentionPopover, setShowMentionPopover] = useState(false)
  const [mentionFilter, setMentionFilter] = useState("")

  // Draft Recovery per chat using localStorage
  const draftKey = `devhub_draft_${activeChatId}`

  useEffect(() => {
    const savedDraft = localStorage.getItem(draftKey)
    if (savedDraft && !input) {
      setInput(savedDraft)
    }
  }, [activeChatId])

  useEffect(() => {
    if (input) {
      localStorage.setItem(draftKey, input)
    } else {
      localStorage.removeItem(draftKey)
    }
  }, [input, draftKey])

  // Auto-focus input on mount and after send
  useEffect(() => {
    textareaRef.current?.focus()
  }, [activeChatId, isLoading])

  // Auto-resize textarea height up to 200px
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }, [input])

  // Detect Slash and @ Mention command typing
  useEffect(() => {
    if (input.startsWith("/")) {
      setShowSlashPopover(true)
      setSlashFilter(input.split(" ")[0])
    } else {
      setShowSlashPopover(false)
    }

    if (input.includes("@")) {
      const match = input.match(/@\w*$/)
      if (match) {
        setShowMentionPopover(true)
        setMentionFilter(match[0])
      } else {
        setShowMentionPopover(false)
      }
    } else {
      setShowMentionPopover(false)
    }
  }, [input])

  const handleSelectCommand = (cmd: SlashCommand) => {
    setInput(cmd.template)
    setShowSlashPopover(false)
    textareaRef.current?.focus()
  }

  const handleSelectMention = (item: any) => {
    const newInput = input.replace(/@\w*$/, `@${item.type.toUpperCase()}:${item.title} `)
    setInput(newInput)
    setShowMentionPopover(false)
    textareaRef.current?.focus()
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Escape") {
      setShowSlashPopover(false)
      setShowMentionPopover(false)
    }
    if (e.key === "Enter" && !e.shiftKey && !showSlashPopover && !showMentionPopover) {
      e.preventDefault()
      if (!isLoading && input.trim() && !disabled) {
        localStorage.removeItem(draftKey)
        onSend()
      }
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0 && onAttachFiles) {
      onAttachFiles(Array.from(e.target.files))
    }
  }

  const promptChips = [
    "Giải thích khái niệm này",
    "Tóm tắt các tài liệu đã tải",
    "Tạo trắc nghiệm trích xuất RAG",
    "Tạo Flashcards học tập",
  ]

  return (
    <div className="w-full max-w-4xl mx-auto space-y-3 p-2 sm:p-4 pb-[max(0.75rem,env(safe-area-inset-bottom))] relative">
      {/* Hidden File Input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        multiple
        accept=".pdf,.docx,.txt,.md"
        className="hidden"
      />

      {/* Slash Command Autocomplete Popover */}
      {showSlashPopover && (
        <SlashCommandPopover
          filter={slashFilter}
          onSelectCommand={handleSelectCommand}
          onClose={() => setShowSlashPopover(false)}
        />
      )}

      {/* Workspace Mention Autocomplete Popover */}
      {showMentionPopover && (
        <MentionPopover
          filter={mentionFilter}
          onSelectMention={handleSelectMention}
          onClose={() => setShowMentionPopover(false)}
        />
      )}

      {/* Quick Prompt Chips (Placed 12px directly above Composer) */}
      {showChips && onPromptChipClick && (
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
          <Sparkles className="h-3.5 w-3.5 text-primary shrink-0" />
          {promptChips.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => onPromptChipClick(chip)}
              className="inline-flex items-center gap-1 shrink-0 rounded-full border border-border/60 bg-card px-3 py-1 text-xs text-muted-foreground hover:border-primary/40 hover:text-foreground hover:bg-accent transition-all cursor-pointer shadow-2xs"
            >
              <span>{chip}</span>
            </button>
          ))}
        </div>
      )}

      {/* Attached Files Queue */}
      {attachedFiles.length > 0 && (
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {attachedFiles.map((file, idx) => (
            <div
              key={idx}
              className="inline-flex items-center gap-1.5 rounded-xl border border-primary/30 bg-primary/10 px-2.5 py-1 text-xs text-primary font-medium shadow-2xs"
            >
              <FileText className="h-3.5 w-3.5" />
              <span className="truncate max-w-[120px]">{file.name}</span>
              {onRemoveFile && (
                <button
                  onClick={() => onRemoveFile(idx)}
                  className="hover:text-destructive transition-colors ml-1"
                >
                  <X className="h-3 w-3" />
                </button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Composer Input Box */}
      <div className="relative rounded-2xl border border-border/80 bg-card shadow-lg backdrop-blur-md focus-within:border-primary/50 focus-within:ring-2 focus-within:ring-primary/20 transition-all">
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Hỏi AI bất kỳ điều gì (Gõ '/' cho lệnh, '@' để nhắc Workspace/Tài liệu)..."
          disabled={disabled || isLoading}
          className="w-full resize-none border-0 bg-transparent px-4 pt-3.5 pb-12 text-sm text-foreground placeholder:text-muted-foreground/70 focus:outline-none focus:ring-0 max-h-[200px] scrollbar-thin"
        />

        {/* Toolbar Footer */}
        <div className="absolute bottom-2 left-3 right-3 flex items-center justify-between pointer-events-auto border-t border-border/30 pt-1.5">
          <div className="flex items-center gap-1">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => fileInputRef.current?.click()}
              className="h-8 w-8 text-muted-foreground hover:text-foreground"
              title="Đính kèm tài liệu (PDF, DOCX, TXT)"
            >
              <Paperclip className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => {
                setInput("/ ")
                textareaRef.current?.focus()
              }}
              className="h-8 w-8 text-muted-foreground hover:text-foreground font-mono font-bold text-xs"
              title="Lệnh Slash (/)"
            >
              /
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={() => {
                setInput(input + "@")
                textareaRef.current?.focus()
              }}
              className="h-8 w-8 text-muted-foreground hover:text-foreground"
              title="Nhắc tên Workspace/Tài liệu (@)"
            >
              <AtSign className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-muted-foreground hover:text-foreground hidden sm:flex"
              title="Nhập bằng giọng nói (Voice)"
            >
              <Mic className="h-4 w-4" />
            </Button>
          </div>

          <div className="flex items-center gap-1.5">
            {/* Stop Streaming Button */}
            {isLoading && onStop && (
              <Button
                type="button"
                variant="destructive"
                size="sm"
                onClick={onStop}
                className="h-8 px-2.5 text-xs gap-1 shadow-sm rounded-xl font-bold"
                title="Dừng phản hồi AI"
              >
                <Square className="h-3 w-3 fill-current" />
                <span>Stop</span>
              </Button>
            )}

            {/* Send Button */}
            <Button
              type="button"
              size="sm"
              onClick={() => {
                localStorage.removeItem(draftKey)
                onSend()
              }}
              disabled={!input.trim() || isLoading || disabled}
              className="h-8 px-3 text-xs gap-1.5 shadow-sm rounded-xl font-bold"
            >
              <span>{isLoading ? "Đang trả lời..." : "Gửi"}</span>
              <Send className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
})

