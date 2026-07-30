import React from "react"
import { motion } from "framer-motion"
import { 
  Upload, 
  Globe, 
  FolderPlus, 
  BookOpen, 
  HelpCircle, 
  MessageSquare, 
  Sparkles, 
  FileCheck 
} from "lucide-react"

interface QuickActionDockProps {
  onUploadClick: () => void
  onImportUrlClick: () => void
  onCreateFolderClick: () => void
  onStartChatClick: () => void
  onSummarizeClick: () => void
}

export const QuickActionDock: React.FC<QuickActionDockProps> = ({
  onUploadClick,
  onImportUrlClick,
  onCreateFolderClick,
  onStartChatClick,
  onSummarizeClick,
}) => {
  const actions = [
    {
      id: "upload",
      title: "Upload Files",
      description: "PDF, DOCX, MD, Code & ZIP",
      icon: Upload,
      color: "text-blue-500",
      bgColor: "bg-blue-500/10",
      onClick: onUploadClick,
    },
    {
      id: "import_url",
      title: "Import Web URL",
      description: "Scrape & chunk web pages",
      icon: Globe,
      color: "text-emerald-500",
      bgColor: "bg-emerald-500/10",
      onClick: onImportUrlClick,
    },
    {
      id: "create_folder",
      title: "Create Folder",
      description: "Organize into sub-categories",
      icon: FolderPlus,
      color: "text-indigo-500",
      bgColor: "bg-indigo-500/10",
      onClick: onCreateFolderClick,
    },
    {
      id: "start_chat",
      title: "Open AI Chat",
      description: "Query RAG knowledge engine",
      icon: MessageSquare,
      color: "text-purple-500",
      bgColor: "bg-purple-500/10",
      onClick: onStartChatClick,
    },
    {
      id: "summarize",
      title: "Summarize Hub",
      description: "Synthesize key insights",
      icon: Sparkles,
      color: "text-amber-500",
      bgColor: "bg-amber-500/10",
      onClick: onSummarizeClick,
    },
    {
      id: "flashcards",
      title: "Generate Cards",
      description: "AI study flashcard set",
      icon: BookOpen,
      color: "text-pink-500",
      bgColor: "bg-pink-500/10",
      onClick: onSummarizeClick,
    },
    {
      id: "quiz",
      title: "Generate Quiz",
      description: "Assess knowledge retention",
      icon: HelpCircle,
      color: "text-cyan-500",
      bgColor: "bg-cyan-500/10",
      onClick: onSummarizeClick,
    },
    {
      id: "docs",
      title: "Export Docs",
      description: "Generate structured wiki",
      icon: FileCheck,
      color: "text-teal-500",
      bgColor: "bg-teal-500/10",
      onClick: onSummarizeClick,
    },
  ]

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          Quick Actions & AI Utilities
        </h2>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
        {actions.map((act) => {
          const IconComp = act.icon
          return (
            <motion.button
              key={act.id}
              whileHover={{ y: -3, scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
              onClick={act.onClick}
              className="flex flex-col items-center justify-center p-3.5 rounded-2xl border border-border/60 glass-card text-center transition-all duration-200 hover:border-primary/40 hover:shadow-lg hover:shadow-primary/5 group"
            >
              <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${act.bgColor} ${act.color} mb-2.5 transition-transform group-hover:scale-110`}>
                <IconComp className="h-5 w-5" />
              </div>
              <span className="text-xs font-bold text-foreground line-clamp-1 group-hover:text-primary transition-colors">
                {act.title}
              </span>
              <span className="text-[10px] text-muted-foreground line-clamp-1 mt-0.5">
                {act.description}
              </span>
            </motion.button>
          )
        })}
      </div>
    </div>
  )
}
