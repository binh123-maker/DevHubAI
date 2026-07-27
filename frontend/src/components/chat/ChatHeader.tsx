import React, { useState } from "react"
import { Globe, FolderOpen, Cpu, Info, BookOpen, ChevronDown, Check, Zap } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"

interface ChatHeaderProps {
  chatMode?: "global" | "workspace" | "folder" | "documents"
  title?: string
  workspaceName?: string
  citationCount?: number
  provider?: string
  model?: string
  contextTokens?: number
  maxContextTokens?: number
  retrievedChunks?: number
  latencyMs?: number
  providerStatus?: "online" | "streaming" | "idle"
  onOpenMetadata?: () => void
  onToggleCitationDock?: () => void
  onModelChange?: (model: string) => void
}

export const ChatHeader = React.memo(function ChatHeader({
  chatMode = "global",
  title,
  workspaceName,
  citationCount = 0,
  provider = "Google DeepMind",
  model = "Gemini 2.5 Pro (RAG)",
  contextTokens = 14200,
  maxContextTokens = 128000,
  retrievedChunks = 4,
  latencyMs = 185,
  providerStatus = "online",
  onOpenMetadata,
  onToggleCitationDock,
  onModelChange,
}: ChatHeaderProps) {
  const [selectedModel, setSelectedModel] = useState(model)

  const models = [
    { id: "gemini", name: "Gemini 2.5 Pro (RAG)", provider: "Google DeepMind", active: true },
    { id: "gpt5", name: "GPT-5 (RAG Enterprise)", provider: "OpenAI", active: false },
    { id: "gpt4o", name: "OpenAI GPT-4o (RAG)", provider: "OpenAI", active: false },
    { id: "claude", name: "Claude 3.5 Sonnet (RAG)", provider: "Anthropic", active: false },
    { id: "groq", name: "Groq Llama 3 (Ultra-Fast)", provider: "Groq Cloud", active: false },
    { id: "ollama", name: "Ollama Llama 3.2 (Local)", provider: "Local LLM", active: false },
  ]

  const handleSelectModel = (m: (typeof models)[0]) => {
    setSelectedModel(m.name)
    if (onModelChange) {
      onModelChange(m.name)
    }
  }

  const isGlobal = chatMode === "global"
  const formattedTokens = `${Math.round(contextTokens / 1000)}k / ${Math.round(maxContextTokens / 1000)}k`

  return (
    <header className="h-[76px] shrink-0 flex items-center justify-between gap-3 border-b border-border/40 bg-card/60 px-4 py-2.5 backdrop-blur-md z-20">
      {/* Scope & Title */}
      <div className="flex items-center gap-3 min-w-0">
        <div
          className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl font-bold shadow-xs ${
            isGlobal ? "bg-primary/10 text-primary" : "bg-amber-500/10 text-amber-500"
          }`}
        >
          {isGlobal ? <Globe className="h-5 w-5" /> : <FolderOpen className="h-5 w-5" />}
        </div>

        <div className="min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h2 className="text-sm sm:text-base font-bold text-foreground truncate max-w-xs sm:max-w-md">
              {title || (isGlobal ? "🌍 Global Knowledge Chat" : `📁 Workspace: ${workspaceName || "Đang chọn"}`)}
            </h2>
            <span
              className={`rounded-full px-2 py-0.5 text-[10px] font-extrabold uppercase tracking-wider shrink-0 ${
                isGlobal
                  ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20"
                  : "bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20"
              }`}
            >
              {isGlobal ? "Global Scope" : "Scope Locked"}
            </span>

            {/* Provider Live Badge */}
            <span className="hidden lg:inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[10px] font-semibold bg-purple-500/10 text-purple-600 dark:text-purple-400 border border-purple-500/20">
              <span className={`h-1.5 w-1.5 rounded-full ${providerStatus === "streaming" ? "bg-amber-500 animate-pulse" : "bg-emerald-500"}`} />
              {provider}
            </span>
          </div>

          {/* Context Window & Runtime Latency Metrics */}
          <div className="flex items-center gap-2 text-[11px] text-muted-foreground mt-0.5 flex-wrap">
            <span className="truncate">{isGlobal ? "Tra cứu toàn bộ tri thức" : `Chỉ tra cứu trong ${workspaceName || "Workspace"}`}</span>
            <span>•</span>
            <span className="inline-flex items-center gap-1 font-mono text-[10px] text-purple-500 font-bold shrink-0">
              <Zap className="h-3 w-3" />
              Context: {formattedTokens}
            </span>
            <span>•</span>
            <span className="font-mono text-[10px] text-emerald-600 dark:text-emerald-400 font-semibold shrink-0">
              Chunks: {retrievedChunks} ({latencyMs}ms)
            </span>
          </div>
        </div>
      </div>

      {/* Action Controls & AI Model Picker Dropdown */}
      <div className="flex items-center gap-2 shrink-0">
        {/* Model Selector Dropdown */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="outline" size="sm" className="h-8 text-xs gap-1.5 border-border/60 bg-background font-semibold">
              <Cpu className="h-3.5 w-3.5 text-purple-500" />
              <span className="hidden sm:inline">{selectedModel}</span>
              <ChevronDown className="h-3 w-3 text-muted-foreground" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-60 p-1 border border-border/60 bg-popover text-popover-foreground shadow-2xl rounded-2xl">
            <div className="px-2 py-1.5 text-[10px] font-bold uppercase tracking-wider text-muted-foreground border-b border-border/40 flex items-center justify-between">
              <span>Chọn Mô hình AI Tra cứu</span>
              <span className="text-[9px] text-emerald-500 font-semibold">{providerStatus === "streaming" ? "Streaming" : "Active"}</span>
            </div>
            {models.map((m) => (
              <DropdownMenuItem
                key={m.id}
                onClick={() => handleSelectModel(m)}
                className="flex items-center justify-between cursor-pointer text-xs py-2"
              >
                <div>
                  <p className="font-semibold">{m.name}</p>
                  <p className="text-[10px] text-muted-foreground">{m.provider}</p>
                </div>
                {selectedModel === m.name && <Check className="h-4 w-4 text-primary shrink-0" />}
              </DropdownMenuItem>
            ))}
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Citation Dock Toggle Button */}
        {citationCount > 0 && onToggleCitationDock && (
          <Button
            variant="secondary"
            size="sm"
            onClick={onToggleCitationDock}
            className="h-8 text-xs gap-1.5 font-semibold text-primary border border-primary/30"
          >
            <BookOpen className="h-3.5 w-3.5" />
            <span>Nguồn ({citationCount})</span>
          </Button>
        )}

        {/* Metadata Info Button */}
        {onOpenMetadata && (
          <Button
            variant="ghost"
            size="icon"
            onClick={onOpenMetadata}
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
            title="Xem thông tin & thống kê cuộc trò chuyện"
          >
            <Info className="h-4 w-4" />
          </Button>
        )}
      </div>
    </header>
  )
})

