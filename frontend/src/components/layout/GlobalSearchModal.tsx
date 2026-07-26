import { useState, useEffect } from "react"
import { Search, FileText, FolderOpen, MessageSquare, ArrowRight, Clock, Trash2 } from "lucide-react"
import { useNavigate } from "react-router-dom"
import { useQuery } from "@tanstack/react-query"
import { useGlobalSearch } from "@/contexts/GlobalSearchContext"
import { useKeyboardShortcut } from "@/hooks/useKeyboardShortcut"
import { workspaceApi } from "@/api/workspace.api"
import { documentApi } from "@/api/document.api"
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"

interface SearchResultItem {
  id: string
  type: "workspace" | "document" | "chat"
  title: string
  subtitle: string
  url: string
}

const SEARCH_HISTORY_KEY = "devhub-search-history"

export function GlobalSearchModal() {
  const navigate = useNavigate()
  const { isOpen, close, toggle } = useGlobalSearch()
  const [query, setQuery] = useState("")

  const [searchHistory, setSearchHistory] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem(SEARCH_HISTORY_KEY)
      return saved ? JSON.parse(saved) : []
    } catch {
      return []
    }
  })

  // Keybinding Ctrl + K
  useKeyboardShortcut("k", toggle, { ctrlKey: true, metaKey: true })

  // Fetch Workspaces & Documents
  const { data: workspaces = [] } = useQuery({
    queryKey: ["workspaces"],
    queryFn: async () => (await workspaceApi.list()).data,
    enabled: isOpen,
  })

  const { data: documents = [] } = useQuery({
    queryKey: ["documents"],
    queryFn: async () => (await documentApi.listAll()).data,
    enabled: isOpen,
  })

  useEffect(() => {
    if (!isOpen) setQuery("")
  }, [isOpen])

  const saveToHistory = (term: string) => {
    if (!term.trim()) return
    const filtered = searchHistory.filter((item) => item.toLowerCase() !== term.toLowerCase())
    const updated = [term.trim(), ...filtered].slice(0, 10)
    setSearchHistory(updated)
    localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(updated))
  }

  const removeHistoryItem = (term: string) => {
    const updated = searchHistory.filter((item) => item !== term)
    setSearchHistory(updated)
    localStorage.setItem(SEARCH_HISTORY_KEY, JSON.stringify(updated))
  }

  const clearHistory = () => {
    setSearchHistory([])
    localStorage.removeItem(SEARCH_HISTORY_KEY)
  }

  // Filter items
  const results: SearchResultItem[] = []
  if (query.trim() !== "") {
    const q = query.toLowerCase()

    workspaces.forEach((w) => {
      if (w.name.toLowerCase().includes(q) || w.description?.toLowerCase().includes(q)) {
        results.push({
          id: w.id,
          type: "workspace",
          title: w.name,
          subtitle: w.description || "Workspace không gian tri thức",
          url: `/workspaces/${w.id}`,
        })
      }
    })

    documents.forEach((d) => {
      if (d.title.toLowerCase().includes(q) || d.description?.toLowerCase().includes(q)) {
        results.push({
          id: d.id,
          type: "document",
          title: d.title,
          subtitle: `Tài liệu (${d.file_type})`,
          url: `/documents/${d.id}`,
        })
      }
    })
  }

  const handleSelect = (url: string, title?: string) => {
    if (query.trim()) {
      saveToHistory(query.trim())
    } else if (title) {
      saveToHistory(title)
    }
    close()
    navigate(url)
  }

  const getItemIcon = (type: string) => {
    switch (type) {
      case "workspace":
        return <FolderOpen className="h-4 w-4 text-amber-500" />
      case "document":
        return <FileText className="h-4 w-4 text-blue-500" />
      default:
        return <MessageSquare className="h-4 w-4 text-emerald-500" />
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={(val) => (!val ? close() : undefined)}>
      <DialogContent className="p-0 max-w-xl overflow-hidden border border-border/60 bg-popover text-popover-foreground shadow-2xl rounded-2xl">
        <div className="flex items-center px-4 border-b border-border/40">
          <Search className="h-4 w-4 text-muted-foreground mr-2 shrink-0" />
          <Input
            placeholder="Tìm kiếm workspace, tài liệu, chat AI... (Bấm Esc để đóng)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="border-0 focus-visible:ring-0 text-sm h-12 bg-transparent"
            autoFocus
          />
          <kbd className="hidden sm:inline-flex items-center gap-1 rounded border border-border/60 bg-muted px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground">
            ESC
          </kbd>
        </div>

        <div className="max-h-[350px] overflow-y-auto p-3 scrollbar-thin">
          {query.trim() === "" ? (
            <div className="space-y-4">
              {/* Search History Section */}
              {searchHistory.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between px-2 text-xs font-semibold text-muted-foreground">
                    <span className="flex items-center gap-1.5">
                      <Clock className="h-3.5 w-3.5" />
                      Tìm kiếm gần đây
                    </span>
                    <button onClick={clearHistory} className="hover:text-destructive text-[11px] flex items-center gap-1">
                      <Trash2 className="h-3 w-3" />
                      Xóa lịch sử
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {searchHistory.map((item) => (
                      <span
                        key={item}
                        className="inline-flex items-center gap-1.5 rounded-full bg-muted/60 px-3 py-1 text-xs font-medium text-foreground hover:bg-primary/10 hover:text-primary cursor-pointer transition-colors"
                      >
                        <span onClick={() => setQuery(item)}>{item}</span>
                        <button onClick={() => removeHistoryItem(item)} className="text-muted-foreground hover:text-destructive">
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="p-4 text-center text-xs text-muted-foreground space-y-1 bg-muted/20 rounded-xl">
                <p className="font-semibold text-foreground">Gợi ý tìm kiếm</p>
                <p>Nhập từ khóa như &quot;Python&quot;, &quot;CS&quot;, hoặc tên tài liệu để bắt đầu.</p>
              </div>
            </div>
          ) : results.length === 0 ? (
            <div className="p-8 text-center text-xs text-muted-foreground">
              Không tìm thấy kết quả nào cho &quot;<span className="font-semibold text-foreground">{query}</span>&quot;
            </div>
          ) : (
            <div className="space-y-1">
              {results.map((item) => (
                <div
                  key={item.id + item.type}
                  onClick={() => handleSelect(item.url, item.title)}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-accent cursor-pointer transition-colors group"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="flex h-8 w-8 items-center justify-center rounded-md bg-muted/60">
                      {getItemIcon(item.type)}
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-semibold truncate group-hover:text-primary transition-colors">
                        {item.title}
                      </p>
                      <p className="text-xs text-muted-foreground truncate">{item.subtitle}</p>
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              ))}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
