import { useEffect } from "react"
import { useNavigation } from "@/contexts/NavigationContext"

export function useScrollSpy(sectionIds: string[]) {
  const { setActiveSectionId } = useNavigation()

  useEffect(() => {
    const scrollContainer = document.querySelector("main")

    const observerCallback: IntersectionObserverCallback = (entries) => {
      const visibleEntries = entries.filter((entry) => entry.isIntersecting)
      if (visibleEntries.length > 0) {
        // Find entry with top boundary closest to root container top
        visibleEntries.sort((a, b) => Math.abs(a.boundingClientRect.top) - Math.abs(b.boundingClientRect.top))
        if (visibleEntries[0]?.target?.id) {
          setActiveSectionId(visibleEntries[0].target.id)
        }
      }
    }

    const observerOptions: IntersectionObserverInit = {
      root: scrollContainer || null,
      rootMargin: "-5% 0px -55% 0px",
      threshold: [0.05, 0.2, 0.5, 0.8],
    }

    const observer = new IntersectionObserver(observerCallback, observerOptions)

    const observedElements: HTMLElement[] = []
    // Delay slightly to ensure elements are mounted
    const timer = setTimeout(() => {
      sectionIds.forEach((id) => {
        const element = document.getElementById(id)
        if (element) {
          observer.observe(element)
          observedElements.push(element)
        }
      })
    }, 100)

    return () => {
      clearTimeout(timer)
      observer.disconnect()
    }
  }, [sectionIds, setActiveSectionId])
}

