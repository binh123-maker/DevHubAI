/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useState, useCallback } from "react"

interface NavigationContextType {
  isCollapsed: boolean
  setIsCollapsed: (collapsed: boolean) => void
  toggleCollapse: () => void
  activeSectionId: string
  setActiveSectionId: (id: string) => void
  isMobileOpen: boolean
  setIsMobileOpen: (open: boolean) => void
  scrollToSection: (id: string) => void
}

const NavigationContext = createContext<NavigationContextType | undefined>(undefined)

export function NavigationProvider({ children }: { children: React.ReactNode }) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [activeSectionId, setActiveSectionId] = useState("overview")
  const [isMobileOpen, setIsMobileOpen] = useState(false)

  const toggleCollapse = useCallback(() => {
    setIsCollapsed((prev) => !prev)
  }, [])

  const scrollToSection = useCallback((id: string) => {
    setActiveSectionId(id)
    setIsMobileOpen(false)
    const element = document.getElementById(id)
    if (element) {
      const yOffset = -80 // Offset for sticky header
      const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset
      window.scrollTo({ top: y, behavior: "smooth" })
    }
  }, [])

  return (
    <NavigationContext.Provider
      value={{
        isCollapsed,
        setIsCollapsed,
        toggleCollapse,
        activeSectionId,
        setActiveSectionId,
        isMobileOpen,
        setIsMobileOpen,
        scrollToSection,
      }}
    >
      {children}
    </NavigationContext.Provider>
  )
}

export function useNavigation() {
  const context = useContext(NavigationContext)
  if (!context) {
    throw new Error("useNavigation must be used within a NavigationProvider")
  }
  return context
}
