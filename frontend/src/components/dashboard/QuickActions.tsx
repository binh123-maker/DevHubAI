import { UploadCloud, FolderPlus, MessageSquarePlus, Kanban } from "lucide-react"

import { useNavigate } from "react-router-dom"
import { useNavigation } from "@/contexts/NavigationContext"
import { QuickActionCard } from "./QuickActionCard"

interface QuickActionsProps {
  onUploadClick?: () => void
  onCreateWorkspaceClick?: () => void
}

export function QuickActions({ onUploadClick, onCreateWorkspaceClick }: QuickActionsProps) {
  const navigate = useNavigate()
  const { scrollToSection } = useNavigation()

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
      <QuickActionCard
        icon={UploadCloud}
        title="Tải lên Tài liệu"
        description="Tải file PDF, DOCX, TXT hoặc URL để đưa vào kho tri thức."
        actionLabel="Bắt đầu tải"
        onClick={() => onUploadClick?.()}
        color="text-blue-500"
        bgColor="bg-blue-500/10"
      />
      <QuickActionCard
        icon={FolderPlus}
        title="Tạo Workspace Mới"
        description="Tổ chức tài liệu và phiên chat theo chủ đề & dự án."
        actionLabel="Tạo mới"
        onClick={() => onCreateWorkspaceClick?.()}
        color="text-amber-500"
        bgColor="bg-amber-500/10"
      />
      <QuickActionCard
        icon={MessageSquarePlus}
        title="Bắt đầu Chat AI"
        description="Đặt câu hỏi cho AI RAG dựa trên tài liệu đã tải lên."
        actionLabel="Trò chuyện"
        onClick={() => navigate("/history")}
        color="text-emerald-500"
        bgColor="bg-emerald-500/10"
      />
      <QuickActionCard
        icon={Kanban}
        title="Xem Tiến độ Kanban"
        description="Quản lý và kéo thả tài liệu qua các cột tiến độ học tập."
        actionLabel="Đến Kanban"
        onClick={() => scrollToSection("kanban")}
        color="text-purple-500"
        bgColor="bg-purple-500/10"
      />
    </div>
  )
}
