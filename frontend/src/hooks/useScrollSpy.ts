import { useEffect } from "react"
import { useNavigation } from "@/contexts/NavigationContext"

export function useScrollSpy(sectionIds: string[], offset: number = 100) {
  const { setActiveSectionId } = useNavigation()

  useEffect(() => {
    const handleScroll = () => {
      const scrollPosition = window.scrollY + offset
      let currentSection = sectionIds[0]

      for (const id of sectionIds) {
        const element = document.getElementById(id)
        if (element) {
          const top = element.offsetTop
          const height = element.offsetHeight
          if (scrollPosition >= top && scrollPosition < top + height) {
            currentSection = id
            break
          }
        }
      }

      if (currentSection) {
        setActiveSectionId(currentSection)
      }
    }

    window.addEventListener("scroll", handleScroll, { passive: true })
    handleScroll() // Initial check

    return () => window.removeEventListener("scroll", handleScroll)
  }, [sectionIds, offset, setActiveSectionId])
}
