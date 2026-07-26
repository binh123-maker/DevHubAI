import React from "react"
import type { ChatMessage } from "@/types/chat.types"
import { ChatMessageItem } from "./ChatMessageItem"

interface VirtualMessageListProps {
  messages: ChatMessage[]
  activeChatMode?: string
  workspaceName?: string
  onSendActionPrompt: (promptText: string) => void
  onRegenerate: () => void
}

export const VirtualMessageList = React.memo(function VirtualMessageList({
  messages,
  activeChatMode = "global",
  workspaceName,
  onSendActionPrompt,
  onRegenerate,
}: VirtualMessageListProps) {
  // Container enforces maximum reading width of 900px for optimal readability
  return (
    <div className="w-full max-w-[900px] mx-auto space-y-4 px-2 sm:px-4">
      {messages.map((msg, index) => (
        <ChatMessageItem
          key={msg.id}
          message={msg}
          isLastAssistantMessage={index === messages.length - 1 && msg.role !== "user"}
          chatMode={activeChatMode}
          workspaceName={workspaceName}
          onSendActionPrompt={onSendActionPrompt}
          onRegenerate={onRegenerate}
        />
      ))}
    </div>
  )
})
