import React, { createContext, useContext, useState, useCallback } from "react"

interface GlobalSearchContextType {
  isOpen: boolean
  open: () => void
  close: () => void
  toggle: () => void
}

const GlobalSearchContext = createContext<GlobalSearchContextType | undefined>(undefined)

export function GlobalSearchProvider({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)

  const open = useCallback(() => setIsOpen(true), [])
  const close = useCallback(() => setIsOpen(false), [])
  const toggle = useCallback(() => setIsOpen((prev) => !prev), [])

  return (
    <GlobalSearchContext.Provider value={{ isOpen, open, close, toggle }}>
      {children}
    </GlobalSearchContext.Provider>
  )
}

export function useGlobalSearch() {
  const context = useContext(GlobalSearchContext)
  if (!context) {
    throw new Error("useGlobalSearch must be used within a GlobalSearchProvider")
  }
  return context
}
