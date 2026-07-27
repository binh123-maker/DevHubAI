import { useState } from "react"
import { useSearchParams, useNavigate } from "react-router-dom"
import { CitationService } from "@/services/citation.service"
import type { Citation } from "@/types/chat.types"

export function useCitationNavigation() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [isNavigating, setIsNavigating] = useState(false)

  const targetPage = parseInt(searchParams.get("page") || "1", 10)
  const targetChunk = parseInt(searchParams.get("chunk") || "0", 10)
  const highlightQuery = searchParams.get("highlight") || ""

  const navigateToCitation = (citation: Citation) => {
    if (!citation) return

    setIsNavigating(true)
    try {
      const url = CitationService.buildDeepLinkUrl(citation)
      navigate(url)
    } catch (err) {
      console.error("Navigation error:", err)
    } finally {
      setTimeout(() => setIsNavigating(false), 500)
    }
  }

  return {
    targetPage,
    targetChunk,
    highlightQuery,
    shouldHighlight: Boolean(highlightQuery),
    isNavigating,
    navigateToCitation,
  }
}
