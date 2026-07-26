import { Search, X } from "lucide-react"
import { Input } from "@/components/ui/input"

interface SearchConversationProps {
  query: string
  onQueryChange: (query: string) => void
}

export function SearchConversation({ query, onQueryChange }: SearchConversationProps) {
  return (
    <div className="relative w-full">
      <Search className="absolute left-2.5 top-2.5 h-3.5 w-3.5 text-muted-foreground" />
      <Input
        placeholder="Tìm kiếm cuộc trò chuyện... (Ctrl+K)"
        value={query}
        onChange={(e) => onQueryChange(e.target.value)}
        className="h-8 pl-8 pr-7 text-xs bg-muted/30 border-border/60 focus-visible:ring-1 focus-visible:ring-primary"
      />
      {query && (
        <button
          onClick={() => onQueryChange("")}
          className="absolute right-2 top-2 text-muted-foreground hover:text-foreground"
        >
          <X className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  )
}
