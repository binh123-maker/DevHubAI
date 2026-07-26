import { useState, useEffect } from "react"
import { Globe, FolderOpen, Folder, FileText, MessageSquarePlus, Sparkles, Check } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { workspaceApi, Workspace } from "@/api/workspace.api"
import { folderApi, Folder as FolderType } from "@/api/folder.api"
import { documentApi, Document } from "@/api/document.api"
import { loadScopeMemory, saveScopeMemory } from "@/utils/scopeMemory"

export type ScopeType = "global" | "workspace" | "folder" | "documents"

export interface ScopeSelection {
  chatName: string
  chatMode: ScopeType
  workspaceId?: string
  folderId?: string
  selectedDocumentIds?: string[]
}

interface NewChatScopeDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onStartChat: (selection: ScopeSelection) => void
}

export function NewChatScopeDialog({ open, onOpenChange, onStartChat }: NewChatScopeDialogProps) {
  const [chatName, setChatName] = useState("")
  const [chatMode, setChatMode] = useState<ScopeType>("global")

  const [workspaces, setWorkspaces] = useState<Workspace[]>([])
  const [folders, setFolders] = useState<FolderType[]>([])
  const [allDocuments, setAllDocuments] = useState<Document[]>([])

  const [workspaceId, setWorkspaceId] = useState<string>("")
  const [folderId, setFolderId] = useState<string>("")
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([])

  useEffect(() => {
    if (open) {
      const memory = loadScopeMemory()
      setChatName("")
      setChatMode(memory.chatMode || "global")
      setWorkspaceId(memory.workspaceId || "")
      setFolderId(memory.folderId || "")
      setSelectedDocIds([])
      workspaceApi.list().then((res) => setWorkspaces(res.data)).catch(console.error)
      documentApi.listAll().then((res) => setAllDocuments(res.data)).catch(console.error)
    }
  }, [open])

  useEffect(() => {
    if (workspaceId && (chatMode === "folder" || chatMode === "workspace")) {
      folderApi.list(workspaceId).then((res) => setFolders(res.data)).catch(console.error)
    } else {
      setFolders([])
      setFolderId("")
    }
  }, [workspaceId, chatMode])

  const toggleDocSelection = (docId: string) => {
    setSelectedDocIds((prev) =>
      prev.includes(docId) ? prev.filter((id) => id !== docId) : [...prev, docId]
    )
  }

  const handleStart = () => {
    saveScopeMemory({
      chatMode,
      workspaceId,
      folderId,
    })

    onStartChat({
      chatName: chatName.trim() || (chatMode === "workspace" ? "Workspace Chat" : chatMode === "folder" ? "Folder Chat" : chatMode === "documents" ? "Selected Documents Chat" : "Global Knowledge Chat"),
      chatMode,
      workspaceId: workspaceId || undefined,
      folderId: folderId || undefined,
      selectedDocumentIds: selectedDocIds.length > 0 ? selectedDocIds : undefined,
    })
    onOpenChange(false)
  }

  const isFormValid = () => {
    if (chatMode === "workspace" && !workspaceId) return false
    if (chatMode === "folder" && (!workspaceId || !folderId)) return false
    if (chatMode === "documents" && selectedDocIds.length === 0) return false
    return true
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md p-0 overflow-hidden border border-border/60 bg-card text-card-foreground shadow-2xl rounded-2xl">
        <DialogHeader className="p-5 border-b border-border/40 pb-4">
          <DialogTitle className="text-base font-bold flex items-center gap-2">
            <MessageSquarePlus className="h-5 w-5 text-primary" />
            Tạo cuộc trò chuyện AI mới
          </DialogTitle>
        </DialogHeader>

        <div className="p-5 space-y-4 max-h-[420px] overflow-y-auto scrollbar-thin">
          {/* Scope Selector Grid */}
          <div className="space-y-2">
            <Label className="text-xs font-semibold">Phạm vi tra cứu kiến thức (Knowledge Scope)</Label>
            <div className="grid grid-cols-2 gap-2">
              <div
                onClick={() => setChatMode("global")}
                className={`flex flex-col justify-between p-2.5 rounded-xl border cursor-pointer transition-all ${
                  chatMode === "global"
                    ? "bg-primary/10 border-primary/50 ring-2 ring-primary/20 text-foreground font-semibold"
                    : "bg-muted/20 border-border/60 text-muted-foreground hover:bg-accent"
                }`}
              >
                <div className="flex items-center gap-1.5">
                  <Globe className="h-4 w-4 text-emerald-500 shrink-0" />
                  <span className="text-xs font-bold">Global Knowledge</span>
                </div>
                <p className="text-[10px] text-muted-foreground mt-1 line-clamp-2">
                  Toàn bộ tài liệu hệ thống
                </p>
              </div>

              <div
                onClick={() => setChatMode("workspace")}
                className={`flex flex-col justify-between p-2.5 rounded-xl border cursor-pointer transition-all ${
                  chatMode === "workspace"
                    ? "bg-amber-500/10 border-amber-500/50 ring-2 ring-amber-500/20 text-foreground font-semibold"
                    : "bg-muted/20 border-border/60 text-muted-foreground hover:bg-accent"
                }`}
              >
                <div className="flex items-center gap-1.5">
                  <FolderOpen className="h-4 w-4 text-amber-500 shrink-0" />
                  <span className="text-xs font-bold">Workspace</span>
                </div>
                <p className="text-[10px] text-muted-foreground mt-1 line-clamp-2">
                  Khóa trong 1 Workspace
                </p>
              </div>

              <div
                onClick={() => setChatMode("folder")}
                className={`flex flex-col justify-between p-2.5 rounded-xl border cursor-pointer transition-all ${
                  chatMode === "folder"
                    ? "bg-purple-500/10 border-purple-500/50 ring-2 ring-purple-500/20 text-foreground font-semibold"
                    : "bg-muted/20 border-border/60 text-muted-foreground hover:bg-accent"
                }`}
              >
                <div className="flex items-center gap-1.5">
                  <Folder className="h-4 w-4 text-purple-500 shrink-0" />
                  <span className="text-xs font-bold">Folder</span>
                </div>
                <p className="text-[10px] text-muted-foreground mt-1 line-clamp-2">
                  Khóa trong 1 Thư mục
                </p>
              </div>

              <div
                onClick={() => setChatMode("documents")}
                className={`flex flex-col justify-between p-2.5 rounded-xl border cursor-pointer transition-all ${
                  chatMode === "documents"
                    ? "bg-blue-500/10 border-blue-500/50 ring-2 ring-blue-500/20 text-foreground font-semibold"
                    : "bg-muted/20 border-border/60 text-muted-foreground hover:bg-accent"
                }`}
              >
                <div className="flex items-center gap-1.5">
                  <FileText className="h-4 w-4 text-blue-500 shrink-0" />
                  <span className="text-xs font-bold">Tài liệu đã chọn</span>
                </div>
                <p className="text-[10px] text-muted-foreground mt-1 line-clamp-2">
                  Chọn các tài liệu chỉ định
                </p>
              </div>
            </div>
          </div>

          {/* Workspace & Folder Pickers */}
          {(chatMode === "workspace" || chatMode === "folder") && (
            <div className="space-y-3 animate-in fade-in duration-200">
              <div className="space-y-1.5">
                <Label className="text-xs font-semibold">Chọn Workspace</Label>
                <Select value={workspaceId} onValueChange={setWorkspaceId}>
                  <SelectTrigger className="h-9 text-xs bg-background">
                    <SelectValue placeholder="Chọn Workspace..." />
                  </SelectTrigger>
                  <SelectContent>
                    {workspaces.map((w) => (
                      <SelectItem key={w.id} value={w.id}>
                        {w.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {chatMode === "folder" && workspaceId && (
                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold">Chọn Thư mục</Label>
                  <Select value={folderId} onValueChange={setFolderId}>
                    <SelectTrigger className="h-9 text-xs bg-background">
                      <SelectValue placeholder="Chọn Thư mục..." />
                    </SelectTrigger>
                    <SelectContent>
                      {folders.map((f) => (
                        <SelectItem key={f.id} value={f.id}>
                          {f.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}
            </div>
          )}

          {/* Document Multi-Select Picker */}
          {chatMode === "documents" && (
            <div className="space-y-2 animate-in fade-in duration-200">
              <div className="flex items-center justify-between">
                <Label className="text-xs font-semibold">Chọn các tài liệu tra cứu ({selectedDocIds.length} đã chọn)</Label>
              </div>
              <div className="max-h-36 overflow-y-auto space-y-1 p-2 rounded-xl border border-border/60 bg-muted/20 scrollbar-thin">
                {allDocuments.length === 0 ? (
                  <p className="text-xs text-muted-foreground p-2 text-center">Chưa có tài liệu nào</p>
                ) : (
                  allDocuments.map((doc) => {
                    const isSelected = selectedDocIds.includes(doc.id)
                    return (
                      <div
                        key={doc.id}
                        onClick={() => toggleDocSelection(doc.id)}
                        className={`flex items-center justify-between p-2 rounded-lg text-xs cursor-pointer transition-all ${
                          isSelected ? "bg-primary/10 font-semibold text-primary" : "hover:bg-accent text-muted-foreground"
                        }`}
                      >
                        <span className="truncate">{doc.title}</span>
                        {isSelected && <Check className="h-3.5 w-3.5 text-primary shrink-0" />}
                      </div>
                    )
                  })
                )}
              </div>
            </div>
          )}

          {/* Title Input */}
          <div className="space-y-1.5">
            <Label className="text-xs font-semibold">Tiêu đề cuộc trò chuyện (Tùy chọn)</Label>
            <Input
              placeholder="Ví dụ: Thảo luận về React Hooks..."
              value={chatName}
              onChange={(e) => setChatName(e.target.value)}
              className="h-9 text-xs"
            />
          </div>
        </div>

        <DialogFooter className="p-4 border-t border-border/40 bg-muted/20 gap-2">
          <Button variant="outline" size="sm" onClick={() => onOpenChange(false)} className="h-9 text-xs">
            Hủy
          </Button>
          <Button
            size="sm"
            onClick={handleStart}
            disabled={!isFormValid()}
            className="h-9 text-xs gap-1.5 shadow-sm font-bold"
          >
            <Sparkles className="h-3.5 w-3.5" />
            Tạo cuộc trò chuyện
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
