import { Tag } from "lucide-react"

interface ConversationTagPickerProps {
  tags: string[]
  selectedTag?: string
  onSelectTag: (tag?: string) => void
}

export function ConversationTagPicker({
  tags = ["Spring", "Flutter", "Database", "React", "Python"],
  selectedTag,
  onSelectTag,
}: ConversationTagPickerProps) {
  return (
    <div className="flex items-center gap-1 overflow-x-auto pb-1 scrollbar-none px-2 py-1">
      <button
        onClick={() => onSelectTag(undefined)}
        className={`inline-flex items-center gap-1 shrink-0 rounded-full px-2.5 py-0.5 text-[10px] font-bold transition-all ${
          !selectedTag ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground hover:bg-accent"
        }`}
      >
        Tất cả
      </button>

      {tags.map((tag) => {
        const isSelected = selectedTag === tag
        return (
          <button
            key={tag}
            onClick={() => onSelectTag(isSelected ? undefined : tag)}
            className={`inline-flex items-center gap-1 shrink-0 rounded-full px-2 py-0.5 text-[10px] font-bold border transition-all ${
              isSelected
                ? "bg-primary/10 border-primary/40 text-primary"
                : "border-border/40 bg-card/60 text-muted-foreground hover:text-foreground"
            }`}
          >
            <Tag className="h-2.5 w-2.5" />
            <span>#{tag}</span>
          </button>
        )
      })}
    </div>
  )
}
