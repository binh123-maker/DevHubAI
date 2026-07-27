/* eslint-disable react-refresh/only-export-components */
import { Droppable } from "@hello-pangea/dnd"

import { Sparkles, BookOpen, CheckCircle, Archive } from "lucide-react"

import { KanbanCard } from "./KanbanCard"
import type { Document, KanbanStatus } from "@/api/document.api"

interface ColumnConfig {
  id: KanbanStatus
  title: string
  subtitle: string
  color: string
  bgColor: string
  borderColor: string
  icon: React.ElementType
}

export const COLUMN_CONFIGS: Record<KanbanStatus, ColumnConfig> = {
  new: {
    id: "new",
    title: "Mới",
    subtitle: "Tài liệu cần đọc & nghiên cứu",
    color: "text-blue-500",
    bgColor: "bg-blue-500/10",
    borderColor: "border-blue-500/30",
    icon: Sparkles,
  },
  learning: {
    id: "learning",
    title: "Đang học",
    subtitle: "Đang học tập & tương tác AI",
    color: "text-amber-500",
    bgColor: "bg-amber-500/10",
    borderColor: "border-amber-500/30",
    icon: BookOpen,
  },
  completed: {
    id: "completed",
    title: "Đã hoàn thành",
    subtitle: "Kiến thức đã làm chủ",
    color: "text-emerald-500",
    bgColor: "bg-emerald-500/10",
    borderColor: "border-emerald-500/30",
    icon: CheckCircle,
  },
  archived: {
    id: "archived",
    title: "Lưu trữ",
    subtitle: "Tài liệu đã tham khảo xong",
    color: "text-slate-500 dark:text-slate-400",
    bgColor: "bg-slate-500/10",
    borderColor: "border-slate-500/30",
    icon: Archive,
  },
}

interface KanbanColumnProps {
  columnId: KanbanStatus
  documents: Document[]
  workspaceMap: Record<string, string>
  folderMap: Record<string, string>
}

export function KanbanColumn({ columnId, documents, workspaceMap, folderMap }: KanbanColumnProps) {
  const config = COLUMN_CONFIGS[columnId]
  const Icon = config.icon

  return (
    <div className="flex flex-col rounded-xl border border-border/60 bg-muted/20 backdrop-blur-xs min-w-[280px] w-full max-w-full">
      {/* Column Header */}
      <div className="flex items-center justify-between p-3.5 border-b border-border/40">
        <div className="flex items-center gap-2">
          <div className={`flex h-7 w-7 items-center justify-center rounded-lg ${config.bgColor} ${config.color}`}>
            <Icon className="h-4 w-4" />
          </div>
          <div>
            <h3 className="text-sm font-bold flex items-center gap-2">
              {config.title}
              <span className={`rounded-full px-2 py-0.5 text-xs font-semibold ${config.bgColor} ${config.color}`}>
                {documents.length}
              </span>
            </h3>
          </div>
        </div>
      </div>

      {/* Droppable Area */}
      <Droppable droppableId={columnId}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`flex-1 p-3 min-h-[350px] transition-colors duration-200 rounded-b-xl ${
              snapshot.isDraggingOver ? "bg-primary/5 ring-2 ring-primary/20" : ""
            }`}
          >
            {documents.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full min-h-[220px] text-center p-4 border border-dashed border-border/50 rounded-lg">
                <Icon className={`h-8 w-8 mb-2 opacity-40 ${config.color}`} />
                <p className="text-xs font-medium text-muted-foreground">Kéo thả tài liệu vào đây</p>
                <p className="text-[11px] text-muted-foreground/70 mt-1">{config.subtitle}</p>
              </div>
            ) : (
              documents.map((doc, idx) => (
                <KanbanCard
                  key={doc.id}
                  document={doc}
                  index={idx}
                  workspaceName={workspaceMap[doc.workspace_id]}
                  folderName={doc.folder_id ? folderMap[doc.folder_id] : undefined}
                />
              ))
            )}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </div>
  )
}
