export function generateAutoTitle(firstMessageContent: string): string {
  const text = firstMessageContent.trim()
  if (!text) return "Cuộc trò chuyện mới"

  // Remove slash command prefixes if any
  const cleaned = text.replace(/^\/[a-z]+\s*/i, "")

  // Take first 35 chars
  if (cleaned.length <= 35) return cleaned

  return cleaned.slice(0, 35) + "..."
}
