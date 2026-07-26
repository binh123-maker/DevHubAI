import { Search, Filter, ArrowUpDown, X } from "lucide-react"

import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Button } from "@/components/ui/button"

export type SortOption = "newest" | "oldest" | "recently_updated" | "alphabetical"

interface WorkspaceItem {
  id: string
  name: string
}

interface FolderItem {
  id: string
  name: string
  workspace_id: string
}

interface KanbanFilterBarProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  selectedWorkspaceId: string
  onWorkspaceChange: (id: string) => void
  selectedFolderId: string
  onFolderChange: (id: string) => void
  sortBy: SortOption
  onSortChange: (sort: SortOption) => void
  workspaces: WorkspaceItem[]
  folders: FolderItem[]
  onClearFilters: () => void
}

export function KanbanFilterBar({
  searchQuery,
  onSearchChange,
  selectedWorkspaceId,
  onWorkspaceChange,
  selectedFolderId,
  onFolderChange,
  sortBy,
  onSortChange,
  workspaces,
  folders,
  onClearFilters,
}: KanbanFilterBarProps) {
  const filteredFolders = selectedWorkspaceId && selectedWorkspaceId !== "all"
    ? folders.filter((f) => f.workspace_id === selectedWorkspaceId)
    : folders

  const hasActiveFilters = searchQuery !== "" || selectedWorkspaceId !== "all" || selectedFolderId !== "all"

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-border/50 bg-card/60 p-3.5 backdrop-blur-sm sm:flex-row sm:items-center sm:justify-between">
      {/* Search Input */}
      <div className="relative flex-1 min-w-[200px]">
        <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Tìm kiếm tài liệu..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="pl-9 h-9 text-sm bg-background/80"
        />
        {searchQuery && (
          <button
            onClick={() => onSearchChange("")}
            className="absolute right-2.5 top-2.5 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* Select Filters */}
      <div className="flex flex-wrap items-center gap-2">
        {/* Workspace Filter */}
        <Select value={selectedWorkspaceId} onValueChange={onWorkspaceChange}>
          <SelectTrigger className="h-9 w-[160px] text-xs bg-background/80">
            <Filter className="h-3.5 w-3.5 mr-1.5 text-muted-foreground" />
            <SelectValue placeholder="Tất cả Workspace" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tất cả Workspace</SelectItem>
            {workspaces.map((ws) => (
              <SelectItem key={ws.id} value={ws.id}>
                {ws.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Folder Filter */}
        <Select value={selectedFolderId} onValueChange={onFolderChange}>
          <SelectTrigger className="h-9 w-[150px] text-xs bg-background/80">
            <SelectValue placeholder="Tất cả thư mục" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tất cả thư mục</SelectItem>
            {filteredFolders.map((folder) => (
              <SelectItem key={folder.id} value={folder.id}>
                {folder.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {/* Sort Dropdown */}
        <Select value={sortBy} onValueChange={(val) => onSortChange(val as SortOption)}>
          <SelectTrigger className="h-9 w-[150px] text-xs bg-background/80">
            <ArrowUpDown className="h-3.5 w-3.5 mr-1.5 text-muted-foreground" />
            <SelectValue placeholder="Sắp xếp" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="newest">Mới nhất</SelectItem>
            <SelectItem value="oldest">Cũ nhất</SelectItem>
            <SelectItem value="recently_updated">Cập nhật gần đây</SelectItem>
            <SelectItem value="alphabetical">Tên (A-Z)</SelectItem>
          </SelectContent>
        </Select>

        {/* Clear Filters button */}
        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={onClearFilters} className="h-9 text-xs text-muted-foreground hover:text-foreground">
            <X className="h-3.5 w-3.5 mr-1" />
            Xóa bộ lọc
          </Button>
        )}
      </div>
    </div>
  )
}
