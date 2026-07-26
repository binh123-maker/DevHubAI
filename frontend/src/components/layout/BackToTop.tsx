import { useState, useEffect } from "react"

import { ArrowUp } from "lucide-react"
import { Button } from "@/components/ui/button"

export function BackToTop() {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const toggleVisibility = () => {
      if (window.pageYOffset > 300) {
        setIsVisible(true)
      } else {
        setIsVisible(false)
      }
    }

    window.addEventListener("scroll", toggleVisibility, { passive: true })
    return () => window.removeEventListener("scroll", toggleVisibility)
  }, [])

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    })
  }

  if (!isVisible) return null

  return (
    <Button
      variant="secondary"
      size="icon"
      onClick={scrollToTop}
      aria-label="Về đầu trang"
      className="fixed bottom-6 right-6 z-50 h-10 w-10 rounded-full border border-border/80 shadow-lg backdrop-blur-md transition-all duration-300 hover:scale-110 hover:border-primary/50 animate-in fade-in slide-in-from-bottom-4"
    >
      <ArrowUp className="h-4 w-4 text-primary" />
    </Button>
  )
}
